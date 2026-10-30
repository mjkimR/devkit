"""The registry of generated artifacts: devkit's built-in entries merged with ``.devkit/generated.toml``.

```toml
# .devkit/generated.toml
[artifacts.uv-lock]
paths = ["uv.lock"]                         # files the command owns: conflicts there are settled by regenerating
command = "uv lock"                         # shell command, run with `sh -c` from the project root
inputs = ["pyproject.toml", "packages/*/pyproject.toml"]  # default []: the command may read any file
updates = []                                # files the command also rewrites in part (a managed block)
after = []                                  # artifacts regenerated first
seed = "ours"                               # "ours" | "theirs": the side left in place before the command runs
optional = false                            # true: skipped while none of its paths is tracked
enabled = true                              # false drops the artifact (a built-in one too)
```

Built-in artifacts come from ``builtin.toml`` beside this module, in the same format. A project table with a built-in
id changes only the fields it sets; a missing ``.devkit/generated.toml`` leaves the built-in artifacts alone. Patterns are relative to the project root, ``/``-separated; ``*``, ``?`` and ``[...]`` match
within one path segment and a ``**`` segment matches any number of segments. ``{devkit}`` in a command is the
running devkit (``<python> -P -m devkit``).
"""

from __future__ import annotations

import fnmatch
import re
import shlex
import sys
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from importlib import resources
from pathlib import Path
from typing import Any

from devkit_core.core.git import run_git
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.project import config_table, read_toml

from devkit_agt.features.generated.models.errors import GeneratedConfigError

SEEDS = ("ours", "theirs")
DEVKIT_PLACEHOLDER = "{devkit}"
ARTIFACT_ID = re.compile(r"[a-z0-9][a-z0-9_-]*\Z")
FIELDS = frozenset({"paths", "command", "inputs", "updates", "after", "seed", "optional", "enabled"})
BUILTIN = "builtin.toml"
PROJECT_FILE = ".devkit/generated.toml"


@cache
def _segment(pattern: str) -> re.Pattern[str]:
    return re.compile(fnmatch.translate(pattern))


def _match(parts: tuple[str, ...], path: tuple[str, ...]) -> bool:
    if not parts:
        return not path
    head, rest = parts[0], parts[1:]
    if head == "**":
        return any(_match(rest, path[index:]) for index in range(len(path) + 1))
    return bool(path) and _segment(head).match(path[0]) is not None and _match(rest, path[1:])


def matches(pattern: str, path: str) -> bool:
    """Whether the ``/``-separated relative ``path`` matches ``pattern`` (see the module docstring)."""
    return _match(tuple(pattern.split("/")), tuple(path.split("/")))


def devkit_command() -> str:
    """The shell words that run this devkit: what ``{devkit}`` stands for in an artifact's command."""
    return shlex.join([sys.executable, "-P", "-m", "devkit_dist"])


@dataclass(frozen=True)
class Artifact:
    """One generated artifact; ``builtin`` is ``True`` for an entry of devkit's ``builtin.toml``."""

    id: str
    paths: tuple[str, ...]
    command: str
    inputs: tuple[str, ...] = ()
    updates: tuple[str, ...] = ()
    after: tuple[str, ...] = ()
    seed: str = "ours"
    optional: bool = False
    builtin: bool = False

    def owns(self, path: str) -> bool:
        return any(matches(pattern, path) for pattern in self.paths)

    def may_write(self, path: str) -> bool:
        return self.owns(path) or any(matches(pattern, path) for pattern in self.updates)

    def may_read(self, path: str) -> bool:
        """Whether a change to ``path`` can change the output: always, when no ``inputs`` are declared."""
        return not self.inputs or any(matches(pattern, path) for pattern in self.inputs)

    @property
    def shell(self) -> str:
        """The command with ``{devkit}`` replaced, as ``sh -c`` runs it."""
        return self.command.replace(DEVKIT_PLACEHOLDER, devkit_command())

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "paths": list(self.paths),
            "command": self.command,
            "inputs": list(self.inputs),
            "updates": list(self.updates),
            "after": list(self.after),
            "seed": self.seed,
            "optional": self.optional,
            "builtin": self.builtin,
        }


@dataclass(frozen=True)
class Registry:
    """The enabled artifacts, each after the artifacts it names in ``after`` (ties in id order)."""

    artifacts: tuple[Artifact, ...] = ()

    def get(self, artifact_id: str) -> Artifact | None:
        return next((item for item in self.artifacts if item.id == artifact_id), None)

    def owner(self, path: str) -> Artifact | None:
        """The artifact whose ``paths`` match ``path``; two of them is ``GENERATED_CONFIG_INVALID``."""
        owners = [item for item in self.artifacts if item.owns(path)]
        if len(owners) > 1:
            names = ", ".join(item.id for item in owners)
            raise GeneratedConfigError(f"{PROJECT_FILE}: {path} is owned by more than one artifact: {names}")
        return owners[0] if owners else None

    def closure(self, ids: Iterable[str]) -> tuple[Artifact, ...]:
        """The artifacts ``ids`` and every artifact that comes after one of them, transitively, in registry order."""
        selected = set(ids)
        for item in self.artifacts:  # dependencies precede dependents, so one pass reaches every dependent
            if selected.intersection(item.after):
                selected.add(item.id)
        return tuple(item for item in self.artifacts if item.id in selected)


def _strings(table: Mapping[str, Any], key: str, context: str) -> tuple[str, ...] | None:
    if key not in table:
        return None
    value = table[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise GeneratedConfigError(f"{context}: {key} must be an array of strings")
    return tuple(value)


def _check_pattern(pattern: str, context: str) -> None:
    parts = pattern.split("/")
    if not pattern or "\\" in pattern or any(part in ("", ".", "..") for part in parts):
        raise GeneratedConfigError(
            f"{context}: {pattern!r} is not a relative /-separated pattern without empty, . or .. segments"
        )


def _fields(table: Mapping[str, Any], context: str) -> dict[str, Any]:
    """The fields set in one artifact table, checked for type; an unset field is absent."""
    unknown = sorted(set(table) - FIELDS)
    if unknown:
        raise GeneratedConfigError(f"{context}: unknown fields: {unknown}")
    found: dict[str, Any] = {}
    for key in ("paths", "inputs", "updates"):
        patterns = _strings(table, key, context)
        if patterns is not None:
            for pattern in patterns:
                _check_pattern(pattern, context)
            found[key] = patterns
    after = _strings(table, "after", context)
    if after is not None:
        found["after"] = after
    if "command" in table:
        command = table["command"]
        if not isinstance(command, str) or not command.strip():
            raise GeneratedConfigError(f"{context}: command must be a non-empty shell command")
        found["command"] = command
    if "seed" in table:
        if table["seed"] not in SEEDS:
            raise GeneratedConfigError(f'{context}: seed must be "ours" or "theirs"')
        found["seed"] = table["seed"]
    for key in ("optional", "enabled"):
        if key in table:
            if not isinstance(table[key], bool):
                raise GeneratedConfigError(f"{context}: {key} must be true or false")
            found[key] = table[key]
    return found


def _artifacts(data: object, context: str) -> dict[str, dict[str, Any]]:
    """The ``[artifacts.<id>]`` tables of one file (``context`` names it), by id, their fields checked."""
    found: dict[str, dict[str, Any]] = {}
    for artifact_id, value in config_table(data, context, GeneratedConfigError).items():
        if not ARTIFACT_ID.match(artifact_id):
            raise GeneratedConfigError(f"{context}: artifact id {artifact_id!r} must match {ARTIFACT_ID.pattern}")
        where = f"{context} artifacts.{artifact_id}"
        found[artifact_id] = _fields(config_table(value, where, GeneratedConfigError), where)
    return found


def builtin_artifacts() -> dict[str, dict[str, Any]]:
    """The fields of devkit's built-in artifacts, by id, from ``builtin.toml``."""
    text = resources.files(__package__).joinpath(BUILTIN).read_text("utf-8")
    return _artifacts(tomllib.loads(text).get("artifacts", {}), BUILTIN)


def _ordered(artifacts: dict[str, Artifact]) -> tuple[Artifact, ...]:
    for item in artifacts.values():
        unknown = sorted(set(item.after) - set(artifacts))
        if unknown:
            raise GeneratedConfigError(
                f"{PROJECT_FILE} artifacts.{item.id}: after names unknown or disabled artifacts: {unknown}"
            )
    ordered: list[Artifact] = []
    done: set[str] = set()
    pending = dict(artifacts)
    while pending:
        ready = sorted(name for name, item in pending.items() if done.issuperset(item.after))
        if not ready:
            raise GeneratedConfigError(f"{PROJECT_FILE}: after forms a cycle among {sorted(pending)}")
        for name in ready:
            ordered.append(pending.pop(name))
            done.add(name)
    return tuple(ordered)


def _registry(data: dict[str, Any]) -> Registry:
    """The enabled artifacts: the built-in ones changed by ``data``, the parsed ``.devkit/generated.toml``."""
    builtin = builtin_artifacts()
    unknown = sorted(set(data) - {"artifacts"})
    if unknown:
        raise GeneratedConfigError(f"{PROJECT_FILE}: unknown fields: {unknown}")
    project = _artifacts(data.get("artifacts", {}), PROJECT_FILE)
    artifacts: dict[str, Artifact] = {}
    for artifact_id in sorted({*builtin, *project}):
        fields = {**builtin.get(artifact_id, {}), **project.get(artifact_id, {})}
        if not fields.pop("enabled", True):
            continue
        missing = [key for key in ("paths", "command") if not fields.get(key)]
        if missing:
            raise GeneratedConfigError(f"{PROJECT_FILE} artifacts.{artifact_id}: missing {' and '.join(missing)}")
        artifacts[artifact_id] = Artifact(id=artifact_id, builtin=artifact_id in builtin, **fields)
    return Registry(_ordered(artifacts))


def load_registry(root: Path) -> Registry:
    """The enabled artifacts of the project at ``root``: the built-in ones, then ``.devkit/generated.toml``.

    An unreadable file is the core ``ConfigError`` (``CONFIG_INVALID``); a malformed one ``GeneratedConfigError``.
    """
    return _registry(read_toml(root / PROJECT_FILE, PROJECT_FILE) or {})


def load_registry_at(root: Path, commit: str) -> Registry:
    """The enabled artifacts with the ``.devkit/generated.toml`` committed at ``commit`` in the repository at ``root``.

    The built-in artifacts come from the running devkit; a commit that does not track the file has only those. The
    working tree is never read, so every caller reading one commit gets one registry. A committed file that is not
    UTF-8 or not TOML is ``ConfigError`` (``CONFIG_INVALID``); a malformed one ``GeneratedConfigError``; a commit Git
    cannot read ``GitError``.
    """
    if not run_git(root, "ls-tree", "--name-only", commit, "--", PROJECT_FILE).strip():
        return _registry({})
    try:
        data = tomllib.loads(run_git(root, "show", f"{commit}:{PROJECT_FILE}").decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        name = f"{PROJECT_FILE} at commit {commit[:12]}"
        raise ConfigError(f"invalid config {name}: {exc}", target_files=[PROJECT_FILE]) from exc
    return _registry(data)
