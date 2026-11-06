#!/usr/bin/env python3
"""Immutable, content-addressed research archives over an explicitly configured Git remote.

Each payload has its own ref, so a receiver fetches one archive rather than the
entire growing artifact history. This module never invokes models or reads auth.
"""

import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import uuid

from git_queue import GitQueue, QueueError
from grade_cached import sha256
from process_guard import atomic_json


class GitArtifacts:
    def __init__(self, remote, prefix="artifacts-v1", max_bytes=16*1024**2, wall_seconds=120):
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}", prefix):
            raise ValueError("artifact ref prefix must be a safe short identifier")
        if (not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0 or
                not isinstance(wall_seconds, (int, float)) or isinstance(wall_seconds, bool) or
                not math.isfinite(wall_seconds) or not 25 <= wall_seconds <= 600):
            raise ValueError("artifact size/time limits must be positive")
        self.remote = GitQueue(remote, branch=prefix).remote
        self.prefix, self.max_bytes, self.wall_seconds = prefix, max_bytes, wall_seconds

    def call(self, deadline, directory, *args, check=True):
        if deadline-time.monotonic() < 20:
            raise QueueError("artifact transfer reached its bounded time allowance")
        return GitQueue._git(directory, *args, check=check)

    def reference(self, digest):
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("artifact identity requires lowercase SHA256")
        return "refs/heads/"+self.prefix+"/"+digest

    def head(self, deadline, ref):
        result = self.call(deadline, None, "ls-remote", "--exit-code", self.remote, ref, check=False)
        if result.returncode == 2:
            return None
        if result.returncode:
            raise QueueError(result.stderr.strip() or "cannot inspect artifact remote")
        return result.stdout.split()[0]

    def read_payload(self, deadline, directory, expected_size):
        size = int(self.call(deadline, directory, "cat-file", "-s", "FETCH_HEAD:artifact.bin").stdout)
        if size != expected_size or size > self.max_bytes:
            raise QueueError("remote artifact size differs from its descriptor")
        if deadline-time.monotonic() < 20:
            raise QueueError("artifact transfer reached its bounded time allowance")
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "cat-file", "blob", "FETCH_HEAD:artifact.bin"],
                                cwd=directory, capture_output=True, timeout=20)
        if result.returncode:
            raise QueueError("cannot read the fetched artifact blob")
        return result.stdout

    def descriptor(self, digest, size, commit):
        return {"uri": "git-artifact://sha256/"+digest, "sha256": digest, "bytes": size,
                "ref": self.reference(digest), "commit": commit}

    def publish(self, path):
        with Path(path).open("rb") as source:
            data = source.read(self.max_bytes+1)
        if len(data) > self.max_bytes:
            raise ValueError("artifact exceeds the configured size allowance")
        digest, deadline = sha256(data), time.monotonic()+self.wall_seconds
        ref = self.reference(digest)
        last = None
        for _ in range(4):
            try:
                head = self.head(deadline, ref)
                with tempfile.TemporaryDirectory(prefix="research-artifact-") as directory:
                    self.call(deadline, directory, "init", "--quiet")
                    if head:
                        self.call(deadline, directory, "fetch", "--quiet", "--no-tags", "--depth=1", self.remote, ref)
                        payload = self.read_payload(deadline, directory, len(data))
                        if sha256(payload) != digest:
                            raise ValueError("immutable artifact ref contains different data")
                        commit = self.call(deadline, directory, "rev-parse", "FETCH_HEAD").stdout.strip()
                        return self.descriptor(digest, len(data), commit)
                    (Path(directory)/"artifact.bin").write_bytes(data)
                    self.call(deadline, directory, "add", "artifact.bin")
                    self.call(deadline, directory, "commit", "--quiet", "-m", "Store research artifact "+digest[:16])
                    commit = self.call(deadline, directory, "rev-parse", "HEAD").stdout.strip()
                    self.call(deadline, directory, "push", "--quiet", "--force-with-lease="+ref+":", self.remote, "HEAD:"+ref)
                    return self.descriptor(digest, len(data), commit)
            except (QueueError, subprocess.SubprocessError) as error:
                last = error
        raise QueueError("artifact publication failed within its bounded retries: "+type(last).__name__)

    def fetch(self, reference, destination):
        digest, size = reference["sha256"], reference["bytes"]
        ref = self.reference(digest)
        if reference.get("ref") != ref or not isinstance(size, int) or isinstance(size, bool) or not 0 <= size <= self.max_bytes:
            raise ValueError("artifact descriptor differs from the configured store")
        destination = Path(destination).resolve()
        if destination.exists():
            if destination.stat().st_size == size and sha256(destination.read_bytes()) == digest:
                return reference
            raise ValueError("existing destination has a different artifact identity")
        deadline = time.monotonic()+self.wall_seconds
        with tempfile.TemporaryDirectory(prefix="research-artifact-fetch-") as directory:
            self.call(deadline, directory, "init", "--quiet")
            self.call(deadline, directory, "fetch", "--quiet", "--no-tags", "--depth=1", self.remote, ref)
            data = self.read_payload(deadline, directory, size)
            if sha256(data) != digest:
                raise ValueError("fetched artifact SHA256 differs from the descriptor")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name+".partial-"+uuid.uuid4().hex)
        try:
            with temporary.open("xb") as output:
                os.chmod(temporary, 0o600)
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            try:
                os.link(temporary, destination)
            except FileExistsError:
                if destination.stat().st_size != size or sha256(destination.read_bytes()) != digest:
                    raise ValueError("destination changed during artifact retrieval")
            descriptor = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        finally:
            temporary.unlink(missing_ok=True)
        return reference


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", required=True, help="Explicit private artifact repository or local bare Git path")
    commands = parser.add_subparsers(dest="action", required=True)
    publish = commands.add_parser("publish")
    publish.add_argument("archive", type=Path)
    publish.add_argument("--descriptor", type=Path, required=True)
    fetch = commands.add_parser("fetch")
    fetch.add_argument("descriptor", type=Path)
    fetch.add_argument("destination", type=Path)
    args = parser.parse_args()
    store = GitArtifacts(args.remote)
    if args.action == "publish":
        result = store.publish(args.archive)
        atomic_json(args.descriptor, result)
    else:
        result = store.fetch(json.loads(args.descriptor.read_text()), args.destination)
    print(json.dumps(result, sort_keys=True))
