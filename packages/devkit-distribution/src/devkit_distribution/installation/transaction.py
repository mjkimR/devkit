from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import os
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath

from devkit_distribution.bundles import BundleError

from .inventory import Content

RECEIPT = ".devkit/installation.json"
JOURNAL = ".devkit/transient/sync-journal.json"
CONFIG = ".devkit/config.toml"
OVERRIDES = ".devkit/overrides"


def project_path(root: Path, name: str) -> Path:
    rel = PurePosixPath(name)
    allowed = name in {RECEIPT, JOURNAL} or any(
        name.startswith(prefix)
        for prefix in (".devkit/managed/", ".agents/skills/", ".claude/skills/", ".codex/agents/", ".claude/agents/")
    )
    if not allowed or rel.is_absolute() or ".." in rel.parts or "\\" in name or str(rel) != name:
        raise BundleError(f"unsafe deployment path: {name}")
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise BundleError(f"deployment symlink: {name}")
    if path.exists() and not path.is_file():
        raise BundleError(f"nonregular deployment path: {name}")
    return path


def snapshot(root: Path, name: str) -> Content | None:
    path = project_path(root, name)
    if not path.exists():
        return None
    return Content(path.read_bytes(), stat.S_IMODE(path.stat().st_mode))


def signature(content: Content) -> dict[str, str | int]:
    return {"sha256": hashlib.sha256(content.data).hexdigest(), "mode": content.mode}


def json_content(value: object) -> Content:
    return Content((json.dumps(value, sort_keys=True, indent=2) + "\n").encode(), 0o644)


def read_json(root: Path, name: str) -> dict:
    content = snapshot(root, name)
    if content is None:
        return {}

    def unique(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise BundleError(f"{name}: duplicate JSON key {key}")
            result[key] = value
        return result

    try:
        value = json.loads(content.data, object_pairs_hook=unique)
    except (ValueError, UnicodeError) as exc:
        raise BundleError(f"invalid {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise BundleError(f"invalid {name}: expected object")
    return value


def atomic_write(root: Path, name: str, content: Content | None) -> None:
    path = project_path(root, name)
    if content is None:
        path.unlink(missing_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".devkit-write-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                os.fchmod(stream.fileno(), content.mode)
                stream.write(content.data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)
    if path.parent.exists():
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


@contextmanager
def project_lock(root: Path) -> Iterator[None]:
    key = hashlib.sha256(str(root).encode()).hexdigest()
    lock = Path(tempfile.gettempdir()) / f"devkit-{os.getuid()}-{key}.lock"
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise BundleError("unsafe lock file")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BundleError("another devkit operation holds the project lock") from exc
        yield
    finally:
        os.close(fd)


def _encode(content: Content | None) -> dict | None:
    return None if content is None else {"data": base64.b64encode(content.data).decode(), "mode": content.mode}


def _decode(value: object) -> Content | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"data", "mode"}:
        raise BundleError("invalid journal content")
    if not isinstance(value["data"], str) or type(value["mode"]) is not int or not 0 <= value["mode"] <= 0o777:
        raise BundleError("invalid journal content types")
    try:
        return Content(base64.b64decode(value["data"], validate=True), value["mode"])
    except ValueError as exc:
        raise BundleError("invalid journal bytes") from exc


def recover_locked(root: Path) -> int:
    journal = read_json(root, JOURNAL)
    if not journal:
        if snapshot(root, JOURNAL) is not None:
            raise BundleError("invalid empty recovery journal")
        return 0
    if (
        set(journal) != {"schema", "changes"}
        or type(journal["schema"]) is not int
        or journal["schema"] != 1
        or not isinstance(journal["changes"], dict)
    ):
        raise BundleError("invalid recovery journal")
    changes = {}
    for name, values in journal["changes"].items():
        if name == JOURNAL or not isinstance(values, dict) or set(values) != {"before", "after"}:
            raise BundleError("invalid recovery entry")
        before, after = _decode(values["before"]), _decode(values["after"])
        if snapshot(root, name) not in (before, after):
            raise BundleError(f"recovery blocked by subsequent edit: {name}")
        changes[name] = before
    for name, before in reversed(list(changes.items())):
        atomic_write(root, name, before)
    atomic_write(root, JOURNAL, None)
    return len(changes)


def apply_changes(root: Path, changes: dict[str, Content | None]) -> None:
    if not changes:
        return
    journal = {
        "schema": 1,
        "changes": {
            name: {"before": _encode(snapshot(root, name)), "after": _encode(content)}
            for name, content in changes.items()
        },
    }
    atomic_write(root, JOURNAL, Content(json_content(journal).data, 0o600))
    try:
        for name, content in changes.items():
            atomic_write(root, name, content)
    except Exception:
        recover_locked(root)
        raise
    atomic_write(root, JOURNAL, None)
