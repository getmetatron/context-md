"""Owner-private, fully indexed archives with no-clobber publication."""

import io
import json
import os
from pathlib import Path
import tarfile
import uuid

from grade_cached import sha256


def write_bundle(roots, destination, expected_artifacts, *, excluded_names=(), max_raw_bytes=None):
    roots = [Path(root).resolve() for root in roots]
    expected_artifacts = {Path(path).resolve(): digest for path, digest in expected_artifacts.items()}
    destination = Path(destination).resolve()
    if len({root.name for root in roots}) != len(roots):
        raise ValueError("archive roots require distinct generic names")
    if any(destination.is_relative_to(root) for root in roots):
        raise ValueError("archive output must be outside its source roots")
    if any(first != second and first.is_relative_to(second) for first in roots for second in roots):
        raise ValueError("archive roots must not overlap")
    if any(not root.is_dir() for root in roots):
        raise ValueError("archive source root is missing")
    files, index, raw_bytes = {}, [], 0
    for root in roots:
        for path in sorted(root.rglob("*")):
            if path.name in excluded_names:
                continue
            if path.is_symlink():
                raise ValueError("raw provenance must not contain symbolic links")
            if not path.is_file():
                continue
            raw_bytes += path.stat().st_size
            if max_raw_bytes is not None and raw_bytes > max_raw_bytes:
                raise ValueError("archive source exceeds its raw byte allowance")
            member = (Path(root.name)/path.relative_to(root)).as_posix()
            data = path.read_bytes()
            digest = sha256(data)
            if path in expected_artifacts and digest != expected_artifacts[path]:
                raise ValueError("accepted artifact changed before archival")
            files[path] = member
            index.append({"member": member, "bytes": len(data), "sha256": digest})
    if set(expected_artifacts)-files.keys():
        raise ValueError("archive omits an accepted artifact from a recovery root")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = destination.with_name(destination.name+".partial-"+uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            os.chmod(temporary, 0o600)
            with tarfile.open(fileobj=stream, mode="w:gz") as output:
                for path, item in zip(files, index):
                    data = path.read_bytes()
                    if sha256(data) != item["sha256"]:
                        raise ValueError("source changed while constructing archive")
                    header = tarfile.TarInfo(item["member"])
                    header.size, header.mode = len(data), 0o600
                    header.uid = header.gid = 0
                    header.uname = header.gname = "research"
                    output.addfile(header, io.BytesIO(data))
                data = (json.dumps({"schema": 1, "files": index}, sort_keys=True)+"\n").encode()
                header = tarfile.TarInfo("artifact-index.json")
                header.size, header.mode = len(data), 0o600
                header.uname = header.gname = "research"
                output.addfile(header, io.BytesIO(data))
            stream.flush()
            os.fsync(stream.fileno())
        with tarfile.open(temporary, "r:gz") as stored:
            names = stored.getnames()
            if len(names) != len(set(names)) or set(names) != {item["member"] for item in index}|{"artifact-index.json"}:
                raise ValueError("archive member inventory differs from the source index")
            for item in index:
                data = stored.extractfile(item["member"]).read()
                if len(data) != item["bytes"] or sha256(data) != item["sha256"]:
                    raise ValueError("archived bytes differ from the full provenance index")
        current = {path for root in roots for path in root.rglob("*") if path.is_file() and path.name not in excluded_names}
        if current != set(files) or any(sha256(path.read_bytes()) != item["sha256"] for path, item in zip(files, index)):
            raise ValueError("source changed before archive publication")
        os.link(temporary, destination)  # Never replace a previous archive.
        parent = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        temporary.unlink(missing_ok=True)
    return {"archive": destination.name, "bytes": destination.stat().st_size,
            "sha256": sha256(destination.read_bytes()), "members": len(index)+1,
            "all_regular_files_verified": len(index), "accepted_artifacts_verified": len(expected_artifacts),
            "permissions": "owner-private", "tar_owner_labels": "generic research"}


def verify_attempt_bundle(directory, archive, *, excluded_names=("journal.json",), max_raw_bytes=16*1024**2):
    """Resume publication only if every saved member still matches the attempt."""
    directory = Path(directory).resolve()
    with tarfile.open(archive, "r:gz") as stored:
        members = stored.getmembers()
        if len({member.name for member in members}) != len(members) or any(not member.isfile() for member in members):
            raise ValueError("attempt archive contains duplicate or non-file members")
        index_member = stored.getmember("artifact-index.json")
        if index_member.size > 1024**2:
            raise ValueError("attempt archive index is too large")
        index = json.load(stored.extractfile(index_member))["files"]
        if sum(item["bytes"] for item in index) > max_raw_bytes:
            raise ValueError("attempt archive exceeds its raw byte allowance")
        expected = {item["member"] for item in index}
        actual = {(Path(directory.name)/path.relative_to(directory)).as_posix(): path
                  for path in directory.rglob("*") if path.is_file() and path.name not in excluded_names}
        if expected != set(actual) or {member.name for member in members} != expected|{"artifact-index.json"}:
            raise ValueError("attempt archive inventory differs from the saved attempt")
        for item in index:
            member = stored.getmember(item["member"])
            if member.size != item["bytes"] or sha256(stored.extractfile(member).read()) != item["sha256"]:
                raise ValueError("attempt archive payload failed hash verification")
            if sha256(actual[item["member"]].read_bytes()) != item["sha256"]:
                raise ValueError("attempt files changed after bundling")
    return {"sha256": sha256(Path(archive).read_bytes()), "bytes": Path(archive).stat().st_size,
            "indexed_files": len(index)}

