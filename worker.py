#!/usr/bin/env python3
"""Recoverable host worker for explicitly configured command-adapter jobs.

No model defaults, credential extraction, or automatic account switching.
The benchmark sandbox and condition-block adapter remain separate components.
"""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import signal
import subprocess
import sys
import tarfile
import time
import uuid

from git_queue import GitQueue, QueueError
from process_guard import atomic_json, artifact, emergency_cleanup, validate_policy


def read_json(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default


def retry_time(reason, reset_at, streak, now, seed=""):
    """Honor all known reset windows; unknown resets get bounded backoff."""
    if reason in {"authentication", "configuration", "paid_fallback", "disk_full"}:
        return None
    if reset_at is not None and reset_at > now + 366 * 86400:
        return None  # malformed/far-future reset requires review, not a year of sleep
    if reason == "quota" and reset_at is not None and reset_at > now:
        return reset_at + 30
    if streak >= 8:
        return None
    base = min(900 if reason == "quota" else 300,
               (60 if reason == "quota" else 15) * 2 ** min(max(streak - 1, 0), 8))
    jitter = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) / 0xffffffff
    return now + base * (1 + 0.1 * jitter)


class Worker:
    def __init__(self, config, queue=None):
        self.config = config
        self.name = config["worker"]
        self.root = Path(config["state_dir"]).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.queue = queue or GitQueue(config["remote"], config.get("branch", "queue-v1"))
        self.policy = validate_policy(config.get("policy", {}))
        self.artifact_store = None
        if config.get("artifact_store"):
            from git_artifacts import GitArtifacts
            self.artifact_store = GitArtifacts(**config["artifact_store"])
            if self.policy["lease_seconds"] < self.artifact_store.wall_seconds + self.policy["lease_safety_seconds"] + 30:
                raise ValueError("artifact transfer allowance must fit inside a renewed publication lease")
        self.heartbeat_seconds = config.get("heartbeat_seconds", 30)
        self.poll_seconds = config.get("poll_seconds", 30)
        if not 0 < self.heartbeat_seconds < (self.policy["lease_seconds"] - self.policy["lease_safety_seconds"]) / 3:
            raise ValueError("heartbeat interval must leave at least three renewals before lease safety expiry")
        if not 0 < self.poll_seconds <= 60:
            raise ValueError("poll_seconds must be between zero and 60")
        self.active_path = self.root / "active.json"
        self.pause_path = self.root / "pause.json"
        self.stopping = False

    def status(self, status, **fields):
        record = {"worker": self.name, "status": status, "updated_at": time.time(), **fields}
        previous = read_json(self.root / "health.json", {})
        atomic_json(self.root / "health.json", record)
        keys = ("status", "job", "reason", "retry_at")
        if status in {"needs_action", "coordination_error", "coordination_degraded", "paused"} and any(previous.get(key) != record.get(key) for key in keys):
            with (self.root / "alerts.jsonl").open("a") as alerts:
                alerts.write(json.dumps(record, sort_keys=True) + "\n")
                alerts.flush()
                os.fsync(alerts.fileno())
            if self.config.get("desktop_notifications") and sys.platform == "darwin":
                message = f"{self.name}: {status}; {fields.get('reason', fields.get('action', 'inspect health.json'))}"
                try:
                    subprocess.run(["osascript", "-e", 'on run argv\ndisplay notification (item 1 of argv) with title "Context Inheritance"\nend run', message],
                                   capture_output=True, timeout=3)
                except (OSError, subprocess.SubprocessError):
                    pass  # Durable alerts remain available when desktop delivery fails.
        print(json.dumps(record, sort_keys=True), flush=True)
        return record

    def save(self, active):
        atomic_json(self.active_path, active)
        atomic_json(Path(active["directory"]) / "journal.json", active)

    def clear(self, active):
        active["phase"] = "published"
        self.save(active)
        self.active_path.unlink(missing_ok=True)

    @staticmethod
    def owner(active):
        claim = active["claim"]
        return claim["job_id"], claim["worker"], claim["attempt_id"], claim["generation"]

    def evidence(self, active, allow_remote=True):
        if self.artifact_store is not None and allow_remote:
            try:
                if active.get("artifact_publication_failures", 0) >= 3:
                    raise QueueError("artifact publication requires action after bounded failures")
                return self.remote_evidence(active)
            except (QueueError, OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
                active["artifact_publication_failures"] = active.get("artifact_publication_failures", 0)+1
                self.save(active)
                if active["artifact_publication_failures"] >= 3:
                    reason = "artifact_publication_failed"
                    self.queue.pause_worker(self.name, reason)
                    self.queue.hold(*self.owner(active), reason, self.evidence(active, allow_remote=False))
                    atomic_json(self.pause_path, {"reason": reason, "retry_at": None, "streak": 1})
                    self.status("needs_action", reason=reason, job=active["claim"]["job_id"])
                    self.clear(active)
                raise QueueError("artifact publication failed: "+type(error).__name__) from error
        directory = Path(active["directory"])
        return [artifact(directory / name) for name in ("report.json", "stdout.log", "stderr.log")
                if (directory / name).is_file()]

    def remote_evidence(self, active):
        directory = Path(active["directory"])
        if self.artifact_store is not None:
            if active.get("remote_artifacts"):
                return active["remote_artifacts"]
            from artifact_bundle import verify_attempt_bundle, write_bundle
            # Renew before bundling/uploading. A failed transfer keeps the local
            # finished outbox and claim, so recovery never invokes the command.
            self.queue.heartbeat(*self.owner(active), self.policy["lease_seconds"])
            self.status("publishing_artifacts", job=active["claim"]["job_id"])
            binding = {"schema": 1, "job_id": active["claim"]["job_id"], "worker": self.name,
                       "attempt_id": active["claim"]["attempt_id"], "generation": active["claim"]["generation"],
                       "job_spec_sha256": hashlib.sha256(json.dumps(active["claim"]["spec"], sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode()).hexdigest()}
            binding_path = directory/"attempt-binding.json"
            if binding_path.exists() and read_json(binding_path) != binding:
                raise ValueError("artifact binding differs from its queue attempt")
            atomic_json(binding_path, binding)
            outbox = self.root/"artifact-outbox"/(active["request_id"]+".tar.gz")
            if not outbox.exists():
                write_bundle([directory], outbox, {}, excluded_names=("journal.json",),
                             max_raw_bytes=self.artifact_store.max_bytes)
            verified = verify_attempt_bundle(directory, outbox, max_raw_bytes=self.artifact_store.max_bytes)
            descriptor = self.artifact_store.publish(outbox)
            if any(descriptor[key] != verified[key] for key in ("sha256", "bytes")):
                raise ValueError("published archive differs from the verified local outbox")
            # Durable acknowledgement precedes queue completion. A lost finish
            # acknowledgement can replay this exact descriptor, not rebuild it.
            active["remote_artifacts"] = [descriptor]
            self.save(active)
            return active["remote_artifacts"]

    def publish(self, active):
        report = read_json(Path(active["directory"]) / "report.json")
        if report is None:
            # A supervisor can crash between persisting its claim and spawning
            # the guardian. There is no result to silently turn into success.
            emergency_cleanup(active["directory"])
            report = {"reason": "supervisor_restart" if active.get("phase") == "claimed" else "guard_report_missing",
                      "productive_progress": False}
        reason = report["reason"]
        evidence = self.evidence(active)
        if reason in {"outputs_ready", "research_budget_exhausted"}:
            self.queue.finish(*self.owner(active), {"outcome": reason, "artifacts": evidence})
            self.pause_path.unlink(missing_ok=True)
            self.status("completed", job=active["claim"]["job_id"], outcome=reason)
        else:
            if "recovery" not in active:
                prior = read_json(self.pause_path, {})
                streak = prior.get("streak", 0) + 1
                retry_at = retry_time(reason, report.get("reset_at"), streak, time.time(), active["request_id"])
                active["recovery"] = {"reason": reason, "retry_at": retry_at, "streak": streak}
                self.save(active)
            recovery = active["recovery"]
            # Persist the circuit before changing the remote. A worker restart
            # must never erase a known quota pause or a manual-action state.
            atomic_json(self.pause_path, recovery)
            if reason in {"quota", "authentication", "service", "process_crash", "parent_lost", "supervisor_restart", "cancelled"}:
                interruption = reason if reason in {"quota", "authentication", "service"} else "environment"
                self.queue.interrupt(*self.owner(active), interruption, evidence,
                                     pause_worker=True, retry_at=recovery["retry_at"],
                                     availability_only=(reason in {"quota", "authentication"} and not report.get("productive_progress")))
            else:
                # Silence, malformed output, disk faults and lost leases are
                # ambiguous. Preserve them for review, not outcome-based retry.
                recovery["retry_at"] = None
                atomic_json(self.pause_path, recovery)
                self.queue.pause_worker(self.name, reason)
                self.queue.hold(*self.owner(active), reason, evidence)
            self.status("paused" if recovery["retry_at"] else "needs_action", job=active["claim"]["job_id"], **recovery)
        self.clear(active)

    def recover(self):
        active = read_json(self.active_path)
        if active is None:
            return False
        if active.get("phase") == "published":
            self.active_path.unlink(missing_ok=True)
            return False
        if "claim" not in active:
            # The request ID was durable before the network call. Reusing it
            # reconciles a push whose acknowledgement was lost on process death.
            self.queue.maintenance()
            snapshot = self.queue.snapshot()
            existing = next(((job_id, job, attempt) for job_id, job in snapshot["jobs"].items()
                             for attempt in job["attempts"] if attempt["attempt_id"] == active["request_id"]), None)
            if existing:
                job_id, job, attempt = existing
                if job["state"] != "leased" or job["attempts"][-1]["attempt_id"] != attempt["attempt_id"]:
                    self.clear(active)
                    return True
                if attempt["lease_expires_at"] <= time.time():
                    self.queue.maintenance()
                    self.status("recovering_expired_claim", job=job_id)
                    # No child was launched before the claim was confirmed.
                    # Let ordinary expiry reclamation run; never spin forever
                    # retrying the same expired request ID.
                    self.clear(active)
                    return True
                specification = next(spec for spec in snapshot["manifest"]["jobs"] if spec["job_id"] == job_id)
                claim = {"job_id": job_id, **attempt, "spec": specification["spec"]}
            else:
                own_leases = [(name, job) for name, job in snapshot["jobs"].items()
                              if job["state"] == "leased" and job["attempts"][-1]["worker"] == self.name]
                if own_leases:
                    name, job = own_leases[0]
                    if job["attempts"][-1]["lease_expires_at"] <= time.time():
                        self.status("recovering_expired_claim", job=name)
                    else:
                        atomic_json(self.pause_path, {"reason": "worker_identity_conflict", "retry_at": None, "streak": 1})
                        self.status("needs_action", reason="worker_identity_conflict", job=name)
                    self.clear(active)
                    return True
                # The old request is absent from a fresh remote snapshot. No
                # command could have started without its confirmed claim.
                # Abandon the reservation and let a normal tick claim work;
                # do not create a new lease merely to "recover" it as a crash.
                self.status("claim_not_applied")
                self.clear(active)
                return True
            if claim is None:
                self.clear(active)
                return True
            active["claim"] = claim
            active["phase"] = "claimed"
            self.save(active)
        # The old worker's control pipe closes on death. Give its guardian a
        # bounded opportunity to stop children and flush its final report.
        end = time.monotonic() + self.policy["kill_grace_seconds"] + 3
        report_path = Path(active["directory"]) / "report.json"
        while active.get("phase") == "running" and not report_path.exists() and time.monotonic() < end:
            time.sleep(0.05)
        current = self.queue.snapshot()["jobs"][active["claim"]["job_id"]]
        if current["attempts"][-1]["attempt_id"] != active["claim"]["attempt_id"] or current["state"] not in {"leased", "completed"}:
            # Another worker/coordinator already reclaimed or quarantined it.
            # Keep its local journal and traces; never publish over the winner.
            self.status("recovered_stale_attempt", job=active["claim"]["job_id"])
            self.clear(active)
            return True
        if current["state"] == "leased" and current["attempts"][-1]["lease_expires_at"] <= time.time():
            self.queue.pause_worker(self.name, "expired_unpublished_attempt")
            self.queue.hold(*self.owner(active), "expired_unpublished_attempt", self.evidence(active, allow_remote=False))
            atomic_json(self.pause_path, {"reason": "expired_unpublished_attempt", "retry_at": None, "streak": 1})
            self.status("needs_action", reason="expired_unpublished_attempt")
            self.clear(active)
            return True
        self.publish(active)
        return True

    def execute(self, active):
        claim = active["claim"]
        specification = claim["spec"]
        if specification.get("kind") != "supervised_command" or specification.get("profile") not in self.config.get("profiles", {}):
            self.queue.pause_worker(self.name, "unsupported_execution_profile")
            self.queue.hold(*self.owner(active), "unsupported_execution_profile")
            atomic_json(self.pause_path, {"reason": "unsupported_execution_profile", "retry_at": None, "streak": 1})
            self.clear(active)
            return self.status("needs_action", reason="unsupported_execution_profile")
        profile = self.config["profiles"][specification["profile"]]
        directory = Path(active["directory"])
        atomic_json(directory / "job.json", specification)
        argv = [arg.replace("{job_spec}", str(directory / "job.json")).replace("{attempt_dir}", str(directory))
                for arg in profile["argv"]]
        spec = {"argv": argv, "cwd": str(Path(profile["cwd"]).expanduser().resolve()),
                "protocol": profile.get("protocol", "claude_stream_json"), "policy": self.policy,
                "lease_expires_at": claim["lease_expires_at"]}
        atomic_json(directory / "execution.json", spec)
        active["phase"] = "running"
        self.save(active)
        with (directory / "guard.stderr.log").open("wb") as guard_stderr:
            guardian = subprocess.Popen([sys.executable, str(Path(__file__).with_name("process_guard.py")),
                                         "--spec", str(directory / "execution.json"), "--directory", str(directory)],
                                        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=guard_stderr,
                                        start_new_session=True)
        active["guard_pid"] = guardian.pid
        self.save(active)
        next_heartbeat = time.monotonic()  # confirm ownership immediately after spawn
        self.status("running", job=claim["job_id"], attempt=claim["attempt_id"])
        try:
            while guardian.poll() is None and not self.stopping:
                if time.monotonic() >= next_heartbeat:
                    try:
                        heartbeat = self.queue.heartbeat(*self.owner(active), self.policy["lease_seconds"])
                    except (QueueError, OSError, subprocess.SubprocessError) as error:
                        self.status("coordination_degraded", job=claim["job_id"], error_type=type(error).__name__,
                                    action="Retry renewal within the last confirmed lease; guardian enforces its safety deadline")
                        next_heartbeat = time.monotonic() + min(5, self.heartbeat_seconds)
                    else:
                        try:
                            guardian.stdin.write((json.dumps({"lease_expires_at": heartbeat["lease_expires_at"]}) + "\n").encode())
                            guardian.stdin.flush()
                        except BrokenPipeError:
                            break
                        self.status("running", job=claim["job_id"], attempt=claim["attempt_id"],
                                    lease_expires_at=heartbeat["lease_expires_at"],
                                    progress=read_json(directory / "progress.json"))
                        next_heartbeat = time.monotonic() + self.heartbeat_seconds
                time.sleep(min(0.1, self.heartbeat_seconds))
        finally:
            # EOF also handles SIGKILL, because the OS closes this pipe. The
            # guardian owns cleanup and cannot continue spending indefinitely.
            try:
                guardian.stdin.close()
            except BrokenPipeError:
                pass
            try:
                guardian.wait(timeout=self.policy["kill_grace_seconds"] + 5)
            finally:
                if not (directory / "report.json").exists():
                    emergency_cleanup(directory)
        active["phase"] = "finished"
        self.save(active)
        self.publish(active)

    def tick(self):
        if self.recover():
            return
        report = self.queue.maintenance()
        pause = read_json(self.pause_path)
        if pause and (pause["retry_at"] is None or time.time() < pause["retry_at"]):
            return self.status("needs_action" if pause["retry_at"] is None else "paused", **pause, queue=report["health"])
        active = {"request_id": uuid.uuid4().hex, "phase": "claiming"}
        active["directory"] = str(self.root / "attempts" / active["request_id"])
        Path(active["directory"]).mkdir(parents=True)
        self.save(active)
        claim = self.queue.claim(self.name, self.config["capabilities"], self.policy["lease_seconds"], request_id=active["request_id"])
        if claim is None:
            self.clear(active)
            # No attempt was claimed: remove this empty reservation rather
            # than accumulating one directory per idle poll indefinitely.
            (Path(active["directory"]) / "journal.json").unlink()
            Path(active["directory"]).rmdir()
            health = report["health"]
            status = "all_completed" if health["counts"]["completed"] == sum(health["counts"].values()) else "waiting"
            return self.status(status, queue=health)
        active["claim"] = claim
        active["phase"] = "claimed"
        self.save(active)
        self.execute(active)

    def monitor(self):
        health = self.queue.maintenance()["health"]
        now = time.time()
        path = self.root / "monitor.json"
        previous = read_json(path, {})
        unfinished = health["counts"]["pending"] + health["counts"]["blocked"]
        idle = unfinished > 0 and health["counts"]["leased"] == 0
        idle_since = previous.get("idle_since", now) if idle else now
        atomic_json(path, {"idle_since": idle_since, "updated_at": now})
        if health["counts"]["blocked"] or health["blocked_dependencies"] or health["stale_heartbeats"]:
            return self.status("needs_action", reason="blocked_jobs_or_stale_workers", queue=health)
        manual_pause = any(pause["retry_at"] is None for pause in health["paused_workers"].values())
        if manual_pause:
            return self.status("needs_action", reason="worker_requires_action", queue=health)
        if idle and now - idle_since >= 120:
            # This is an operational alert, not a claim that every possible
            # worker is quota-blocked. Healthy workers may still be absent.
            reason = "capacity_pause_observed" if health["paused_workers"] else "unfinished_queue_has_no_running_jobs"
            return self.status("paused" if health["paused_workers"] else "needs_action", reason=reason, queue=health)
        return self.status("monitoring", queue=health)

    def run(self, once=False, monitor_only=False):
        # Lock is held for the worker's lifetime, including pauses. An OS service
        # restart cannot start two local supervisors with this state directory.
        with (self.root / "worker.lock").open("a+") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("another supervisor holds this worker state directory")
            handlers = {signum: signal.signal(signum, lambda *_: setattr(self, "stopping", True))
                        for signum in (signal.SIGINT, signal.SIGTERM)}
            try:
                while not self.stopping:
                    try:
                        self.monitor() if monitor_only else self.tick()
                    except (QueueError, OSError, ValueError, subprocess.SubprocessError) as error:
                        self.status("coordination_error", error_type=type(error).__name__,
                                    action="Preserve local outbox; retry coordination without launching another command")
                    if once:
                        break
                    end = time.monotonic() + self.poll_seconds
                    while not self.stopping and time.monotonic() < end:
                        time.sleep(min(0.2, self.poll_seconds))
            finally:
                for signum, handler in handlers.items():
                    signal.signal(signum, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--monitor-only", action="store_true", help="sweep leases and detect stalled work without claiming commands")
    parser.add_argument("--resume", action="store_true", help="explicitly clear this worker's local and remote pause")
    parser.add_argument("--print-launchd", action="store_true", help="print a user-agent plist; do not install it")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.print_launchd:
        directory = str(Path(config["state_dir"]).expanduser().resolve())
        label = config["worker"]
        if not __import__("re").fullmatch(r"worker-[0-9]{2,}", label):
            parser.error("worker must be a generic worker ID")
        command = [sys.executable, str(Path(__file__).resolve()), "--config", str(args.config.resolve())]
        if args.monitor_only:
            command.append("--monitor-only")
        sys.stdout.buffer.write(plistlib.dumps({"Label": f"org.context-inheritance.{label}",
            "ProgramArguments": command, "RunAtLoad": True, "KeepAlive": True, "ThrottleInterval": 30,
            "EnvironmentVariables": {"PATH": os.environ.get("PATH", "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"),
                                     "PYTHONUNBUFFERED": "1"},
            "StandardOutPath": str(Path(directory) / "service.stdout.log"),
            "StandardErrorPath": str(Path(directory) / "service.stderr.log")}))
        return
    worker = Worker(config)
    if args.resume:
        if worker.active_path.exists():
            parser.error("recover the outstanding attempt before explicitly resuming")
        worker.queue.resume_worker(worker.name)
        worker.pause_path.unlink(missing_ok=True)
    worker.run(args.once, args.monitor_only)
    if args.once:
        status = read_json(worker.root / "health.json", {}).get("status")
        if status in {"needs_action", "coordination_error"}:
            parser.exit(2, f"worker needs attention: {status}\n")


if __name__ == "__main__":
    main()
