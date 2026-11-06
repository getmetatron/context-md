#!/usr/bin/env python3
"""Bounded subprocess guardian. Raw output stays on disk if its parent dies.

The worker keeps stdin open and sends confirmed lease expiries as JSON lines.
EOF means the worker died; the guardian terminates the child's process group.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as output:
        json.dump(value, output, sort_keys=True, allow_nan=False)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def artifact(path):
    path = Path(path).resolve()
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"uri": path.as_uri(), "sha256": digest.hexdigest()}


class StreamStatus:
    """Read provider error envelopes, never arbitrary model/tool text."""

    def __init__(self):
        self.reason = None
        self.reset_at = None
        self.productive_progress = False
        self.terminal = False
        self.paid_fallback = False

    def consume(self, event):
        if not isinstance(event, dict):
            return False
        kind = event.get("type")
        info = event.get("rate_limit_info", {}) if kind == "rate_limit_event" else {}
        info = info if isinstance(info, dict) else {}
        if kind == "assistant" and event.get("error") == "rate_limit":
            parameters = event.get("api_error_params") or {}
            info = parameters.get("rate_limit_info", {}) if isinstance(parameters, dict) else {}
            info = info if isinstance(info, dict) else {}
            self.reason = "quota"
        if info.get("isUsingOverage") or info.get("overageInUse"):
            self.paid_fallback = True
        elif info.get("status") == "rejected":
            self.reason = "quota"
        if info.get("status") == "rejected" or (kind == "assistant" and event.get("error") == "rate_limit"):
            reset = info.get("resetsAt", info.get("resets_at"))
            if isinstance(reset, (float, int)) and not isinstance(reset, bool) and math.isfinite(reset):
                if reset > 10**12:
                    reset /= 1000
                self.reset_at = max(self.reset_at or 0, reset)
        error = event.get("error")
        code = error.get("type") if isinstance(error, dict) else error
        code = code if isinstance(code, str) else None
        if code in {"authentication_failed", "authentication_error", "invalid_api_key", "not_logged_in"}:
            self.reason = "authentication"
        elif code in {"overloaded_error", "api_error", "timeout_error"} and self.reason is None:
            self.reason = "service"
        elif code in {"billing_error", "credits_required", "model_not_found", "configuration"}:
            self.reason = "configuration"
        if kind == "result":
            self.terminal = True
            subtype = event.get("subtype", "")
            if self.reason is None:
                if subtype == "error_max_turns":
                    self.reason = "research_budget_exhausted"
                elif subtype == "success" and not event.get("is_error"):
                    self.reason = "outputs_ready"
                else:
                    # Fail closed on unknown provider formats rather than
                    # calling an authentication failure a failed coding task.
                    status = event.get("api_error_status")
                    self.reason = "quota" if status == 429 else "authentication" if status == 401 else "unknown_failure"
        message, partial = event.get("message") or {}, event.get("event") or {}
        progress = ((kind == "assistant" and not error)
                    or (kind == "user" and isinstance(message, dict) and bool(message.get("content")))
                    or (kind == "stream_event" and isinstance(partial, dict) and partial.get("type") in
                        {"content_block_start", "content_block_delta"}))
        if self.paid_fallback:
            self.reason = "paid_fallback"
        self.productive_progress |= bool(progress)
        return bool(progress)


def validate_policy(policy):
    defaults = {"startup_seconds": 120, "idle_seconds": 600, "wall_seconds": 1800,
                "terminal_grace_seconds": 5, "kill_grace_seconds": 2,
                "lease_safety_seconds": 30, "lease_seconds": 300,
                "sync_seconds": 5, "poll_seconds": 0.1, "min_free_bytes": 256 * 1024 * 1024}
    policy = {**defaults, **policy}
    for key in defaults:
        value = policy[key]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be positive and finite")
    if policy["lease_safety_seconds"] >= policy["lease_seconds"]:
        raise ValueError("lease safety margin must be shorter than the lease")
    return policy


def stop_group(process, grace):
    # The group may still contain tool subprocesses after the CLI exits.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    end = time.monotonic() + grace
    while time.monotonic() < end:
        process.poll()
        time.sleep(min(0.02, grace))
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=max(1, grace))


def process_identity(pid):
    # Interpreter launchers can exec a different binary without changing PID.
    # Match process birth and group, not its transient executable path or state.
    result = subprocess.run(["ps", "-o", "lstart=", "-o", "pgid=", "-o", "stat=", "-p", str(pid)],
                            text=True, capture_output=True, timeout=2)
    fields = result.stdout.split()
    if result.returncode or not fields or fields[-1].startswith("Z"):
        return None
    return " ".join(fields[:-1])


def emergency_cleanup(directory):
    """Best-effort fallback if the guardian itself is killed before its report."""
    path = Path(directory) / "running.json"
    if not path.exists():
        return
    record = json.loads(path.read_text())
    pid = record["pid"]
    if record.get("identity") and process_identity(pid) == record["identity"]:
        try:
            os.killpg(pid, signal.SIGTERM)
            time.sleep(0.1)
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def guard(spec, directory, control_fd=0):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    policy = validate_policy(spec.get("policy", {}))
    started_wall, started = time.time(), time.monotonic()
    status = StreamStatus()
    report = {"started_at": started_wall, "reason": "spawn_error", "productive_progress": False}
    process = None
    interrupted = [False]
    previous_handlers = {}
    for signum in (signal.SIGTERM, signal.SIGINT):
        previous_handlers[signum] = signal.signal(signum, lambda *_: interrupted.__setitem__(0, True))
    streams = []
    try:
        argv = spec["argv"]
        if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) for arg in argv):
            raise ValueError("argv must be a nonempty string list")
        if spec.get("protocol", "claude_stream_json") not in {"claude_stream_json", "exit_code"}:
            raise ValueError("unsupported output protocol")
        if spec["lease_expires_at"] - time.time() <= policy["lease_safety_seconds"]:
            report["reason"] = "lease_lost"
            return report
        # Reserve room to save diagnostics before spending any inference.
        if os.statvfs(directory).f_bavail * os.statvfs(directory).f_frsize < policy["min_free_bytes"]:
            report["reason"] = "disk_full"
            return report
        for name in ("stdout.log", "stderr.log"):
            streams.append((directory / name).open("wb", buffering=0))
        stdout_log, stderr_log = streams
        process = subprocess.Popen(argv, cwd=spec["cwd"], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        atomic_json(directory / "running.json", {"pid": process.pid, "identity": process_identity(process.pid), "started_at": started_wall})
        last_progress = started
        terminal_at = None
        lease_deadline = started + min(policy["lease_seconds"], spec["lease_expires_at"] - started_wall) - policy["lease_safety_seconds"]
        previous_wall, previous_mono, last_sync = started_wall, started, started
        buffers = {"stdout": b"", "control": b""}
        with selectors.DefaultSelector() as selector:
            for stream, tag in ((process.stdout, "stdout"), (process.stderr, "stderr"), (control_fd, "control")):
                descriptor = stream if isinstance(stream, int) else stream.fileno()
                os.set_blocking(descriptor, False)
                selector.register(descriptor, selectors.EVENT_READ, tag)
            while True:
                now, wall = time.monotonic(), time.time()
                reason = None
                if interrupted[0]:
                    reason = "cancelled"
                elif abs((wall - previous_wall) - (now - previous_mono)) > 30:
                    reason = "clock_or_suspend"
                elif now >= lease_deadline:
                    reason = "lease_lost"
                elif now - started >= policy["wall_seconds"]:
                    reason = "research_budget_exhausted"
                elif status.reason and status.reason not in {"outputs_ready", "research_budget_exhausted", "unknown_failure"}:
                    reason = status.reason
                elif terminal_at is not None and now - terminal_at >= policy["terminal_grace_seconds"]:
                    reason = status.reason
                elif not status.productive_progress and terminal_at is None and now - started >= policy["startup_seconds"]:
                    reason = "startup_timeout"
                elif status.productive_progress and terminal_at is None and now - last_progress >= policy["idle_seconds"]:
                    reason = "idle_timeout"
                if reason:
                    report["reason"] = reason
                    break
                previous_wall, previous_mono = wall, now
                if now - last_sync >= policy["sync_seconds"]:
                    for stream in streams:
                        os.fsync(stream.fileno())
                    if os.statvfs(directory).f_bavail * os.statvfs(directory).f_frsize < policy["min_free_bytes"]:
                        report["reason"] = "disk_full"
                        break
                    atomic_json(directory / "progress.json", {"updated_at": wall, "last_progress_seconds_ago": now - last_progress,
                                "productive_progress": status.productive_progress, "terminal": status.terminal})
                    last_sync = now
                for key, _ in selector.select(policy["poll_seconds"]):
                    data = os.read(key.fd, 65536)
                    tag = key.data
                    if not data:
                        selector.unregister(key.fd)
                        if tag == "control":
                            report["reason"] = "parent_lost"
                            reason = "parent_lost"
                            break
                        continue
                    if tag in {"stdout", "stderr"}:
                        (stdout_log if tag == "stdout" else stderr_log).write(data)
                        if spec.get("protocol", "claude_stream_json") == "exit_code":
                            status.productive_progress = True
                            last_progress = time.monotonic()
                    if tag in buffers:
                        buffers[tag] += data
                        while b"\n" in buffers[tag]:
                            line, buffers[tag] = buffers[tag].split(b"\n", 1)
                            try:
                                event = json.loads(line)
                            except (ValueError, UnicodeError):
                                continue
                            if tag == "control":
                                expiry = event.get("lease_expires_at") if isinstance(event, dict) else None
                                if isinstance(expiry, (int, float)) and math.isfinite(expiry):
                                    lease_deadline = time.monotonic() + min(policy["lease_seconds"], expiry - time.time()) - policy["lease_safety_seconds"]
                            elif status.consume(event):
                                last_progress = time.monotonic()
                            if status.terminal and terminal_at is None:
                                terminal_at = time.monotonic()
                        if len(buffers[tag]) > 4 * 1024 * 1024:
                            # Raw bytes are retained; an unbounded malformed
                            # line must not exhaust the guardian's memory.
                            buffers[tag] = b""
                if reason == "parent_lost":
                    break
                code = process.poll()
                output_open = any(key.data in {"stdout", "stderr"} for key in selector.get_map().values())
                if code is not None and not output_open:
                    # Parse a final JSON event even without a trailing newline.
                    if buffers["stdout"]:
                        try:
                            status.consume(json.loads(buffers["stdout"]))
                        except (ValueError, UnicodeError):
                            pass
                    if status.reason in {"quota", "authentication", "service", "configuration", "paid_fallback"}:
                        report["reason"] = status.reason
                    elif code < 0:
                        report["reason"] = "process_crash"
                    elif spec.get("protocol", "claude_stream_json") == "exit_code":
                        report["reason"] = "outputs_ready" if code == 0 else "unknown_failure"
                    else:
                        report["reason"] = "unknown_failure" if status.reason == "outputs_ready" and code != 0 else status.reason or "incomplete_stream"
                    break
    except (OSError, ValueError, KeyError, TypeError) as error:
        report["reason"] = "disk_full" if getattr(error, "errno", None) == 28 else "guard_error" if process else "spawn_error"
        report["error_type"] = type(error).__name__
    finally:
        if process:
            stop_group(process, policy["kill_grace_seconds"])
            report["exit_code"] = process.returncode
            # Drain bytes emitted during termination into the durable trace.
            for pipe, output in zip((process.stdout, process.stderr), streams):
                try:
                    while chunk := os.read(pipe.fileno(), 65536):
                        output.write(chunk)
                except (BlockingIOError, OSError):
                    pass
                pipe.close()
        for stream in streams:
            try:
                os.fsync(stream.fileno())
            finally:
                stream.close()
        report.update(finished_at=time.time(), elapsed_seconds=time.monotonic() - started,
                      productive_progress=status.productive_progress, reset_at=status.reset_at)
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
        atomic_json(directory / "report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    guard(json.loads(args.spec.read_text()), args.directory)


if __name__ == "__main__":
    main()
