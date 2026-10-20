"""Exact, checkout-local MCP registrations. No dependency on an optional runtime or domain package."""

from __future__ import annotations

import base64
import contextlib
import json
import os
import stat
import tempfile
import tomllib
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Any

import tomlkit

from devkit.advisory import AdvisoryError, Level
from devkit.core.git import run_git
from devkit.core.local_config import read_effective_config
from devkit.core.locks import file_lock
from devkit.core.mcp_context import guard_execution
from devkit.host.errors import HostError

LEDGER = ".devkit/transient/mcp/registrations.json"
JOURNAL = ".devkit/transient/mcp/journal.json"
DESTINATIONS = {"codex": ".codex/config.toml", "claude": ".mcp.json"}
GROUP = "devkit.mcp.registrations"


class RegistrationError(HostError):
    code = "MCP_REGISTRATION_CONFLICT"
    guardrail = True
    fix = "Restore the exact recorded project entry after inspecting local edits, then run devkit sync; use an independently authorized CLI/PR route meanwhile"


class RegistrationUnavailable(RegistrationError):
    code = "MCP_REGISTRATION_UNAVAILABLE"
    fix = "Use host-owned setup or an independently authorized CLI/PR route; keep tracked and foreign host settings unchanged"


class RuntimeUnavailable(RegistrationError):
    code = "MCP_RUNTIME_UNAVAILABLE"
    fix = "Install devkit-mcp with the same service packages in a retained base/tool runtime, then run devkit mcp setup --executable PATH; or use an independently authorized CLI/PR route"


@dataclass(frozen=True)
class LaunchDescriptor:
    command: str
    args: tuple[str, ...]
    executor: str
    workspace: str
    profile: str

    def entry(self) -> dict[str, Any]:
        return {"command": self.command, "args": list(self.args)}


def _git(root: Path, *args: str) -> str:
    return run_git(root, *args).decode("utf-8", errors="surrogateescape").strip()


def common_dir(root: Path) -> Path | None:
    try:
        if Path(_git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
            return None
        return Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    except AdvisoryError:
        return None


def _safe(path: Path, anchor: Path) -> None:
    if not path.is_relative_to(anchor):
        raise RegistrationError("registration path escaped its owner")
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise RegistrationError("symbolic links are not registration destinations")
        if candidate == anchor:
            break
    if path.exists() and not path.is_file():
        raise RegistrationError("registration destination is not a regular file")


def _snapshot(path: Path, anchor: Path) -> tuple[bytes, int] | None:
    _safe(path, anchor)
    return (path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) if path.exists() else None


def _pairs(items: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _json(raw: bytes) -> dict:
    value = json.loads(raw, object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _document(host: str, raw: bytes | None) -> dict:
    try:
        value = (tomllib.loads(raw.decode()) if host == "codex" else _json(raw)) if raw else {}
        key = "mcp_servers" if host == "codex" else "mcpServers"
        if not isinstance(value.get(key, {}), dict):
            raise ValueError("server map must be an object")
        return value
    except (ValueError, UnicodeError) as exc:
        raise RegistrationError("malformed or duplicate-key host configuration") from exc


def _entry(host: str, raw: bytes | None) -> Any:
    return _document(host, raw).get("mcp_servers" if host == "codex" else "mcpServers", {}).get("devkit")


def _render(host: str, raw: bytes | None, entry: dict | None) -> bytes:
    key = "mcp_servers" if host == "codex" else "mcpServers"
    if host == "codex":
        value = tomlkit.parse(raw.decode()) if raw else tomlkit.document()
        if key not in value:
            value[key] = tomlkit.table()
        table = value[key]
        if entry is None:
            del table["devkit"]  # type: ignore[index]
        else:
            table["devkit"] = entry  # type: ignore[index]
        return tomlkit.dumps(value).encode()
    value = _document(host, raw)
    servers = value.setdefault(key, {})
    if entry is None:
        servers.pop("devkit", None)
    else:
        servers["devkit"] = entry
    return (json.dumps(value, indent=2) + "\n").encode()


def _tracked(root: Path, relative: str) -> bool:
    return bool(_git(root, "ls-files", "--", relative))


def _ignored(root: Path, relative: str) -> bool:
    try:
        return bool(_git(root, "check-ignore", "--", relative))
    except AdvisoryError:
        return False


def _foreign_worktree(root: Path, relative: str) -> bool:
    for part in _git(root, "worktree", "list", "--porcelain", "-z").split("\0"):
        if part.startswith("worktree "):
            other = Path(part[9:])
            if (
                other != root
                and (other / relative).exists()
                and not _tracked(other, relative)
                and not _ignored(other, relative)
            ):
                return True
    return False


def _ledger(root: Path) -> dict:
    snapshot = _snapshot(root / LEDGER, root)
    if snapshot is None:
        return {"workspace": str(root), "entries": {}, "excludes": []}
    try:
        value = _json(snapshot[0])
        if set(value) != {"workspace", "entries", "excludes"} or value["workspace"] != str(root):
            raise ValueError("wrong ledger workspace")
        if not isinstance(value["entries"], dict) or not isinstance(value["excludes"], list):
            raise ValueError("invalid ledger collections")
        if any(line not in {"/" + name for name in DESTINATIONS.values()} for line in value["excludes"]):
            raise ValueError("unknown exclusion")
        for host, record in value["entries"].items():
            if host not in DESTINATIONS or set(record) != {"destination", "server", "entry", "descriptor"}:
                raise ValueError("invalid ledger entry")
            if (
                record["destination"] != DESTINATIONS[host]
                or record["server"] != "devkit"
                or not isinstance(record["entry"], dict)
            ):
                raise ValueError("invalid ledger ownership")
        return value
    except (ValueError, TypeError, KeyError) as exc:
        raise RegistrationError("malformed MCP ownership ledger; no entries were changed") from exc


def provider(root: Path, executable: str | None = None, environment: str | None = None) -> LaunchDescriptor | None:
    entries = list(metadata.entry_points(group=GROUP))
    if not entries:
        return None
    if len(entries) != 1:
        raise RegistrationError("multiple MCP registration providers are installed")
    try:
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
            result = entries[0].load()(root, executable=executable, environment=environment)
        if result is not None and not isinstance(result, LaunchDescriptor):
            raise TypeError("provider must return LaunchDescriptor or None")
        return result
    except RuntimeUnavailable:
        raise
    except Exception as exc:
        raise RegistrationError(
            f"installed MCP registration provider failed ({type(exc).__name__}); this is not uninstall"
        ) from exc


def collisions(root: Path, host: str) -> list[str]:
    """Known same-name layers, read-only. Never copy environment values or foreign settings into results."""
    paths: list[tuple[Path, str]] = []
    if host == "codex":
        paths.append((Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml", "user"))
        paths.extend((parent / ".codex/config.toml", "ancestor") for parent in root.parents)
    else:
        paths.append((Path.home() / ".claude.json", "user/local"))
        paths.append((Path("/Library/Application Support/ClaudeCode/managed-mcp.json"), "managed"))
        paths.append((Path("/etc/claude-code/managed-mcp.json"), "managed"))
    found = []
    for path, layer in paths:
        if not path.exists():
            continue
        try:
            doc = _document(host, path.read_bytes())
            key = "mcp_servers" if host == "codex" else "mcpServers"
            present = "devkit" in doc.get(key, {})
            if host == "claude":
                projects = doc.get("projects", {})
                present = present or (
                    isinstance(projects, dict) and "devkit" in projects.get(str(root), {}).get("mcpServers", {})
                )
            if present:
                found.append(layer)
        except (OSError, AdvisoryError, TypeError, AttributeError):
            found.append(layer + ":unknown")
    return sorted(set(found))


@dataclass
class RegistrationPlan:
    root: Path
    common: Path | None
    before: dict[str, tuple[bytes, int] | None] = field(default_factory=dict)
    after: dict[str, tuple[bytes, int] | None] = field(default_factory=dict)
    notices: list[AdvisoryError] = field(default_factory=list)
    desired: dict[str, Any] = field(default_factory=dict)
    states: dict[str, str] = field(default_factory=dict)

    @property
    def changes(self) -> list[str]:
        return [key for key in self.after if self.before[key] != self.after[key]]

    def path(self, key: str) -> Path:
        if key == "exclude":
            assert self.common is not None
            return self.common / "info/exclude"
        if key not in {*DESTINATIONS.values(), LEDGER}:
            raise RegistrationError("unknown registration transaction destination")
        return self.root / key

    def capture(self, key: str) -> tuple[bytes, int] | None:
        value = _snapshot(self.path(key), self.common if key == "exclude" else self.root)  # type: ignore[arg-type]
        self.before[key] = value
        return value


def plan(
    root: Path,
    agents: list[str] | tuple[str, ...],
    *,
    remove: bool = False,
    executable: str | None = None,
    environment: str | None = None,
) -> RegistrationPlan:
    root = root.resolve()
    result = RegistrationPlan(root, common_dir(root))
    if (root / JOURNAL).exists():
        raise RegistrationError("interrupted registration transaction; run ordinary devkit sync to recover")
    ledger = _ledger(root)
    installed = bool(metadata.entry_points(group=GROUP))
    if not installed and not ledger["entries"]:
        return result
    if result.common is None:
        result.notices.append(
            RegistrationUnavailable("native project registration requires a Git checkout").with_level(Level.WARNING)
        )
        return result
    enabled = not remove and read_effective_config(root).values["mcp"]["register"]
    launch = None
    unavailable = False
    if installed and enabled:
        try:
            launch = provider(root, executable, environment)
        except RuntimeUnavailable as exc:
            result.notices.append(exc.with_level(Level.WARNING))
            unavailable = True
    desired_hosts = (
        {"claude" if agent == "claude-code" else agent for agent in agents} if enabled and installed else set()
    )
    entries = dict(ledger["entries"])
    excludes = list(ledger["excludes"])
    for host in sorted(desired_hosts | entries.keys()):
        if host not in DESTINATIONS:
            result.notices.append(
                RegistrationUnavailable(f"selected host {host} has no supported MCP adapter").with_level(Level.WARNING)
            )
            continue
        relative = DESTINATIONS[host]
        before = result.capture(relative)
        current = _entry(host, before[0] if before else None)
        record = entries.get(host)
        desired = launch.entry() if launch is not None and host in desired_hosts else None
        result.desired[host] = desired
        if _tracked(root, relative) or (before is not None and not _ignored(root, relative)):
            result.notices.append(
                RegistrationUnavailable(f"{relative}: tracked or visible foreign host file left unchanged").with_level(
                    Level.WARNING
                )
            )
            result.states[host] = "unavailable"
            continue
        if record is not None and before is not None and current != record["entry"]:
            raise RegistrationError(f"{relative}: owned entry was edited or removed")
        if record is None and current is not None:
            result.states[host] = "independently-managed"
            raise RegistrationError(f"{relative}: unowned devkit entry cannot be adopted")
        if unavailable and host in desired_hosts:
            result.states[host] = "runtime-unavailable"
            continue
        if desired is not None:
            layers = collisions(root, host)
            if layers:
                result.notices.append(
                    RegistrationUnavailable(
                        f"{host}: same-name or unreadable layers: {', '.join(layers)}; resolve using host tools"
                    ).with_level(Level.WARNING)
                )
                result.states[host] = "shadowed-or-unknown"
                continue
        if desired == current and (
            (desired is None and record is None) or (desired is not None and record is not None)
        ):
            result.states[host] = "matching" if desired else "absent"
            continue
        if _tracked(root, relative) or (before is not None and not _ignored(root, relative)):
            result.notices.append(
                RegistrationUnavailable(f"{relative}: tracked or visible foreign host file left unchanged").with_level(
                    Level.WARNING
                )
            )
            result.states[host] = "unavailable"
            continue
        if desired is not None and not _ignored(root, relative):
            if _foreign_worktree(root, relative):
                result.notices.append(
                    RegistrationUnavailable(
                        f"{relative}: exclusion would hide a foreign linked-worktree file"
                    ).with_level(Level.WARNING)
                )
                continue
            if "exclude" not in result.before:
                result.capture("exclude")
            old = result.after.get("exclude", result.before["exclude"])
            data, mode = old if old else (b"", 0o644)
            line = "/" + relative
            if line.encode() not in data.splitlines():
                data += (b"\n" if data and not data.endswith(b"\n") else b"") + line.encode() + b"\n"
                excludes.append(line)
            result.after["exclude"] = (data, mode)
        if desired is None:
            entries.pop(host, None)
            result.after[relative] = (_render(host, before[0], None), before[1]) if before else None
            result.states[host] = "remove"
        else:
            assert launch is not None
            entries[host] = {
                "destination": relative,
                "server": "devkit",
                "entry": desired,
                "descriptor": {"executor": launch.executor, "workspace": launch.workspace, "profile": launch.profile},
            }
            result.after[relative] = (
                _render(host, before[0] if before else None, desired),
                before[1] if before else 0o600,
            )
            result.states[host] = "write"
    updated = {"workspace": str(root), "entries": entries, "excludes": sorted(set(excludes))}
    if updated != ledger:
        result.capture(LEDGER)
        result.after[LEDGER] = ((json.dumps(updated, indent=2) + "\n").encode(), 0o600)
    if excludes and not entries:
        result.notices.append(
            RegistrationUnavailable(
                "clone-local MCP exclusions retained; inspect every linked worktree before manually removing the exact lines from Git info/exclude"
            ).with_level(Level.NOTICE)
        )
    return result


def _write(path: Path, value: tuple[bytes, int] | None, anchor: Path) -> None:
    guard_execution()
    _safe(path, anchor)
    if value is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".mcp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(value[0])
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, value[1])
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def _encoded(value: tuple[bytes, int] | None) -> list | None:
    return [base64.b64encode(value[0]).decode(), value[1]] if value else None


def _decoded(value: Any) -> tuple[bytes, int] | None:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2 or type(value[1]) is not int or not 0 <= value[1] <= 0o777:
        raise ValueError("invalid journal snapshot")
    return base64.b64decode(value[0], validate=True), value[1]


def apply(result: RegistrationPlan, *, locked: bool = False) -> None:
    if not result.changes:
        return
    if locked:
        raise RegistrationError("locked sync found changed local registration; run ordinary devkit sync")
    assert result.common is not None
    for key, expected in result.before.items():
        if _snapshot(result.path(key), result.common if key == "exclude" else result.root) != expected:
            raise RegistrationError("registration destination changed after planning")
    for relative in DESTINATIONS.values():
        if relative not in result.changes:
            continue
        if _tracked(result.root, relative) or (
            result.before[relative] is not None and not _ignored(result.root, relative)
        ):
            raise RegistrationError("destination Git eligibility changed before registration write")
        if not _ignored(result.root, relative) and _foreign_worktree(result.root, relative):
            raise RegistrationError("a linked-worktree foreign file appeared before exclusion write")
    if not _ignored(result.root, LEDGER):
        raise RegistrationUnavailable("the local ledger must be ignored before registration; run devkit sync first")
    journal = {
        "workspace": str(result.root),
        "common": str(result.common),
        "changes": {
            key: {"before": _encoded(result.before[key]), "after": _encoded(result.after[key])}
            for key in result.changes
        },
    }
    _write(result.root / JOURNAL, ((json.dumps(journal) + "\n").encode(), 0o600), result.root)
    for key in result.changes:
        anchor = result.common if key == "exclude" else result.root
        if _snapshot(result.path(key), anchor) != result.before[key]:
            raise RegistrationError("external edit interrupted registration transaction; recovery required")
        if key in DESTINATIONS.values() and (_tracked(result.root, key) or not _ignored(result.root, key)):
            raise RegistrationError("host destination became tracked or visible before write; recovery required")
        _write(result.path(key), result.after[key], anchor)
    guard_execution()
    (result.root / JOURNAL).unlink()


def recover(root: Path) -> None:
    path = root / JOURNAL
    snap = _snapshot(path, root)
    if snap is None:
        return
    try:
        data = _json(snap[0])
        common = common_dir(root)
        if (
            common is None
            or data["workspace"] != str(root)
            or data["common"] != str(common)
            or not isinstance(data["changes"], dict)
        ):
            raise ValueError("journal identity mismatch")
        result = RegistrationPlan(root, common)
        for key, change in data["changes"].items():
            result.path(key)
            result.before[key], result.after[key] = _decoded(change["before"]), _decoded(change["after"])
        for key in result.changes:
            anchor = common if key == "exclude" else root
            if _snapshot(result.path(key), anchor) not in (result.before[key], result.after[key]):
                raise RegistrationError("external edits prevent registration recovery")
        # Exclusions are clone-local setup: another checkout may have started using one
        # after this transaction released the common lock. Never roll installed lines back.
        retained = result.after.get("exclude")
        if retained is not None and _snapshot(result.path("exclude"), common) == retained:
            prior = result.before.get(LEDGER)
            ledger = _json(prior[0]) if prior else {"workspace": str(root), "entries": {}, "excludes": []}
            old_lines = set((result.before.get("exclude") or (b"", 0))[0].splitlines())
            added = {line.decode() for line in retained[0].splitlines() if line not in old_lines}
            owned = {"/" + name for name in DESTINATIONS.values()}
            ledger["excludes"] = sorted(set(ledger["excludes"]) | (added & owned))
            result.after[LEDGER] = _snapshot(root / LEDGER, root)
            result.before[LEDGER] = ((json.dumps(ledger, indent=2) + "\n").encode(), prior[1] if prior else 0o600)
            result.before["exclude"] = retained
            # Persist the revised rollback target before mutation, so recovery is itself repeatable.
            data["changes"] = {
                key: {"before": _encoded(result.before[key]), "after": _encoded(result.after[key])}
                for key in result.before
            }

        def eligible(key: str) -> None:
            if key in {*DESTINATIONS.values(), LEDGER} and (
                _tracked(root, key) or (result.path(key).exists() and not _ignored(root, key))
            ):
                raise RegistrationError("destination Git eligibility changed before registration recovery")

        for key in result.changes:
            eligible(key)
        _write(path, ((json.dumps(data) + "\n").encode(), snap[1]), root)
        for key in reversed(result.changes):
            eligible(key)
            anchor = common if key == "exclude" else root
            if _snapshot(result.path(key), anchor) not in (result.before[key], result.after[key]):
                raise RegistrationError("external edits interrupted registration recovery")
            _write(result.path(key), result.before[key], anchor)
        guard_execution()
        path.unlink()
    except (ValueError, KeyError, TypeError) as exc:
        raise RegistrationError("malformed registration journal; mutation refused") from exc


@contextlib.contextmanager
def clone_lock(root: Path, *, dry_run: bool = False):
    """Fixed order: common Git lock, then caller's project lock. Planning creates no lock file."""
    common = common_dir(root)
    if (
        dry_run
        or common is None
        or (not metadata.entry_points(group=GROUP) and not (root / LEDGER).exists() and not (root / JOURNAL).exists())
    ):
        yield
    else:
        with file_lock(common / "devkit-mcp.lock", timeout=20):
            yield


def inspect(root: Path, agents: list[str] | tuple[str, ...]) -> dict[str, Any]:
    """Read registration facts without adopting entries or exposing unrelated host configuration."""
    root = root.resolve()
    ledger = _ledger(root)
    notices = []
    desired: dict[str, Any] = {}
    runtime = "absent" if not metadata.entry_points(group=GROUP) else "unknown"
    try:
        planned = plan(root, agents)
        desired = planned.desired
        notices.extend(planned.notices)
        if runtime != "absent":
            runtime = "unavailable" if any(n.code == "MCP_RUNTIME_UNAVAILABLE" for n in notices) else "available"
    except RegistrationError as exc:
        notices.append(exc)
    project = {}
    for host in sorted({"claude" if agent == "claude-code" else agent for agent in agents} | ledger["entries"].keys()):
        if host not in DESTINATIONS:
            project[host] = {"state": "unsupported"}
            continue
        snap = _snapshot(root / DESTINATIONS[host], root)
        current = _entry(host, snap[0] if snap else None)
        record = ledger["entries"].get(host)
        project[host] = {
            "state": "absent"
            if current is None
            else ("owned" if record and current == record["entry"] else "independently-managed"),
            "collisions": collisions(root, host),
        }
    return {
        "desired": desired,
        "recorded": sorted(ledger["entries"]),
        "project": project,
        "package": "installed" if metadata.entry_points(group=GROUP) else "absent",
        "runtime": runtime,
        "effective": "unknown",
        "connection": "unknown",
        "form": "unknown",
        "trust": "unknown",
        "permissions": "unknown",
        "notices": notices,
    }
