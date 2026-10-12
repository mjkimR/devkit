"""Host-neutral subagent role contracts and their per-agent projections.

A ``subagent`` asset may ship native files per agent (``variants``) or one
Markdown contract (``source``) whose frontmatter declares the role, its
description and a ``hosts`` table with one block per agent (``claude-code``,
``codex``, ``antigravity``). Each block carries
a ``status`` and only host-native keys from an allowlist; projection is a
deterministic rendering of that block, never a heuristic conversion. A host
with ``status: unsupported`` gets no file. The body is the role's prompt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit.core import frontmatter
from devkit.core.errors import FrontmatterError

from ..errors import BundleError
from .common import SLUG

STATUSES = ("native", "emulated", "unsupported", "unverified")
ALLOWED_KEYS: dict[str, tuple[str, ...]] = {
    "claude-code": (
        "tools",
        "disallowedTools",
        "model",
        "permissionMode",
        "maxTurns",
        "skills",
        "memory",
        "background",
        "omitClaudeMd",
        "effort",
        "isolation",
        "color",
    ),
    "codex": ("model", "model_reasoning_effort", "sandbox_mode"),
    "antigravity": ("tools", "model", "commandExecutionPolicy", "skills", "plugins"),
}
HOST_FILES = {"claude-code": ".md", "codex": ".toml", "antigravity": ".md"}
# Frontmatter every Antigravity subagent file carries in addition to the contract's keys.
ANTIGRAVITY_FIXED: tuple[tuple[str, Any], ...] = (("subagent", True), ("mainAgent", False))
FIELDS = {"role", "title", "description", "skill", "hosts"}
# Extension keys: carried by the contract for other tools, never rendered or interpreted by devkit.
EXTENSION_KEY = re.compile(r"x-[a-z][a-z0-9-]*\Z")


@dataclass(frozen=True)
class HostBlock:
    status: str
    settings: tuple[tuple[str, Any], ...]


@dataclass(frozen=True)
class Contract:
    role: str
    title: str
    description: str
    skill: str | None
    hosts: dict[str, HostBlock]
    body: str
    # ``x-*`` frontmatter keys in document order, verbatim; devkit does not interpret them.
    extensions: tuple[tuple[str, Any], ...] = ()


def subagent_entry(root: Path, source: str) -> Path:
    path = root / source
    if not path.is_file() or path.suffix.lower() != ".md":
        raise BundleError(f"{source}: subagent contract must be a single Markdown file")
    return path


def _setting(value: Any) -> Any:
    if isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise ValueError


def read_contract(data: bytes, context: str, asset_id: str | None = None) -> Contract:
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise BundleError(f"{context}: subagent contract must be UTF-8") from exc
    try:
        document = frontmatter.parse(text)
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc
    if document.data is None:
        raise BundleError(f"{context}: subagent contract requires YAML frontmatter")
    metadata = document.data
    body = document.body.replace("\r\n", "\n").strip("\n")
    if unknown := {key for key in metadata if key not in FIELDS and not EXTENSION_KEY.fullmatch(key)}:
        raise BundleError(f"{context}: unknown frontmatter keys {sorted(unknown)} (extensions use x-<name>)")
    extensions = tuple((key, value) for key, value in metadata.items() if key not in FIELDS)
    role = metadata.get("role")
    if not isinstance(role, str) or not SLUG.fullmatch(role):
        raise BundleError(f"{context}: role must be a lowercase slug")
    if asset_id is not None and role != asset_id:
        raise BundleError(f"{context}: role {role!r} must equal the asset id {asset_id!r}")
    title = metadata.get("title")
    description = metadata.get("description")
    if not isinstance(title, str) or not title.strip():
        raise BundleError(f"{context}: title is required")
    if not isinstance(description, str) or not description.strip():
        raise BundleError(f"{context}: description is required")
    skill = metadata.get("skill")
    if skill is not None and (not isinstance(skill, str) or not SLUG.fullmatch(skill)):
        raise BundleError(f"{context}: skill must be a lowercase slug")
    raw_hosts = metadata.get("hosts")
    if not isinstance(raw_hosts, dict) or not raw_hosts:
        raise BundleError(f"{context}: hosts must be a nonempty mapping of agent to projection block")
    hosts: dict[str, HostBlock] = {}
    for name, block in raw_hosts.items():
        if name not in ALLOWED_KEYS:
            raise BundleError(f"{context}: unknown host {name!r}; expected one of {sorted(ALLOWED_KEYS)}")
        if isinstance(block, str):
            block = {"status": block}
        if not isinstance(block, dict):
            raise BundleError(f"{context}: hosts.{name}: expected a status or a mapping")
        status = block.get("status")
        if status not in STATUSES:
            raise BundleError(f"{context}: hosts.{name}.status must be one of {list(STATUSES)}")
        settings = []
        for key in block:
            if key == "status":
                continue
            if key not in ALLOWED_KEYS[name]:
                raise BundleError(
                    f"{context}: hosts.{name}: key {key!r} is not allowed; allowed: {', '.join(ALLOWED_KEYS[name])}"
                )
            try:
                settings.append((key, _setting(block[key])))
            except ValueError:
                raise BundleError(
                    f"{context}: hosts.{name}.{key} must be a string, integer, boolean or list of strings"
                ) from None
        hosts[name] = HostBlock(status, tuple(settings))
    if not body.strip():
        raise BundleError(f"{context}: subagent contract body (the prompt) is empty")
    return Contract(role, title.strip(), description.strip(), skill, hosts, body, extensions)


SUBAGENT_DIRS = {"claude-code": ".claude/agents", "codex": ".codex/agents", "antigravity": ".agents/agents"}


def projection_path(agent: str, role: str) -> str:
    return f"{SUBAGENT_DIRS[agent]}/{role}{HOST_FILES[agent]}"


def render(agent: str, contract: Contract, contract_path: str) -> bytes | None:
    """Projection bytes for ``agent``; ``None`` when the host is unsupported for this role.

    ``contract_path`` is the workspace-relative location of the contract, cited in the prompt.
    """
    block = contract.hosts.get(agent)
    if block is None:
        raise BundleError(f"{contract.role}: contract declares no projection for {agent}")
    if block.status == "unsupported":
        return None
    description = f"{contract.title}. {contract.description}"
    header = [f"Role contract: `{contract_path}`.", f"Host projection: {block.status}."]
    if contract.skill:
        header.insert(1, f"Procedure: skill `{contract.skill}`.")
    if block.status in {"emulated", "unverified"}:
        header.append(
            "The host does not enforce the contract's boundaries itself; state the substitute "
            "measures explicitly and never claim a native guarantee."
        )
    prompt = " ".join(header) + "\n\n" + contract.body.rstrip("\n") + "\n"
    if agent == "codex":
        return _render_codex(contract, block, description, prompt)
    fixed = ANTIGRAVITY_FIXED if agent == "antigravity" else ()
    return _render_markdown(contract, block, description, prompt, fixed)


def _render_markdown(
    contract: Contract, block: HostBlock, description: str, prompt: str, fixed: tuple[tuple[str, Any], ...] = ()
) -> bytes:
    lines = ["---", f"name: {contract.role}", f"description: {_yaml_quote(description)}"]
    lines.extend(f"{key}: {_yaml_value(value)}" for key, value in (*fixed, *block.settings))
    lines.append("---")
    return ("\n".join(lines) + "\n" + prompt).encode()


def _render_codex(contract: Contract, block: HostBlock, description: str, prompt: str) -> bytes:
    lines = [f"name = {_toml_string(contract.role)}", f"description = {_toml_string(description)}"]
    lines.extend(f"{key} = {_toml_value(value)}" for key, value in block.settings)
    lines.append('developer_instructions = """\n' + _toml_multiline(prompt) + '"""')
    return ("\n".join(lines) + "\n").encode()


_YAML_PLAIN = re.compile(r"^[A-Za-z][A-Za-z0-9_./-]*$")
_YAML_RESERVED = {"true", "false", "null", "yes", "no", "on", "off", "y", "n"}


def _yaml_quote(value: str) -> str:
    """A YAML double-quoted scalar; line breaks and control characters are escaped, never folded."""
    out = ['"']
    for char in value:
        code = ord(char)
        if char in {"\\", '"'}:
            out.append("\\" + char)
        elif char == "\n":
            out.append("\\n")
        elif char == "\t":
            out.append("\\t")
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\x{code:02X}")
        else:
            out.append(char)
    out.append('"')
    return "".join(out)


def _yaml_scalar(value: str) -> str:
    if _YAML_PLAIN.match(value) and value.lower() not in _YAML_RESERVED:
        return value
    return _yaml_quote(value)


def _yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return _yaml_scalar(value)
    return "[" + ", ".join(_yaml_scalar(item) for item in value) + "]"


def _toml_string(value: str) -> str:
    out = ['"']
    for char in value:
        code = ord(char)
        if char == "\\":
            out.append("\\\\")
        elif char == '"':
            out.append('\\"')
        elif char == "\n":
            out.append("\\n")
        elif char == "\t":
            out.append("\\t")
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\u{code:04X}")
        else:
            out.append(char)
    out.append('"')
    return "".join(out)


def _toml_multiline(value: str) -> str:
    out = []
    for char in value:
        code = ord(char)
        if char == "\\":
            out.append("\\\\")
        elif char in {"\n", "\t"}:
            out.append(char)
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\u{code:04X}")
        else:
            out.append(char)
    return "".join(out).replace('"""', '""\\"')


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return _toml_string(value)
    return "[" + ", ".join(_toml_string(item) for item in value) + "]"
