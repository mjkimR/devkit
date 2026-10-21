"""Who starts a skill: ``invocation`` in ``bundle.toml``, written into each agent's native setting at projection.

``auto`` (the default) lets the agent start the skill on its own; ``user`` leaves it to an explicit user
invocation. Claude Code reads the setting from ``SKILL.md`` frontmatter, Codex from ``agents/openai.yaml`` in the
``.agents/skills`` directory it shares with Antigravity, which has no setting of its own and follows the skill body.
The manifest is the only place a bundle declares it: a skill source that sets either native key is invalid.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from devkit_core.base.errors import FrontmatterError
from devkit_core.core.frontmatter import load_header

from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles.common import SHARED_SKILL_AGENTS, locate_frontmatter

INVOCATIONS = ("auto", "user")
CLAUDE_KEY = "disable-model-invocation"
CODEX_FILE = "agents/openai.yaml"
CODEX_KEY = "allow_implicit_invocation"
FIX = 'Remove it and declare invocation = "user" on the skill asset in bundle.toml'


def codex_policy(implicit: bool) -> bytes:
    """An ``agents/openai.yaml`` that sets only whether Codex may start the skill on its own."""
    return f"policy:\n  {CODEX_KEY}: {'true' if implicit else 'false'}\n".encode()


def _skill_header(data: bytes, context: str) -> dict[str, Any]:
    _, block = locate_frontmatter(data, context, "skill")
    if block is None:
        return {}
    try:
        return load_header(block.header)
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc


def _codex_settings(data: bytes, context: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(data.decode("utf-8"))
    except (UnicodeError, yaml.YAMLError, RecursionError) as exc:
        raise BundleError(f"{context}: invalid YAML: {exc}") from exc
    if value is None:
        return {}
    if not isinstance(value, dict) or not isinstance(value.get("policy", {}), dict):
        raise BundleError(f"{context}: expected a YAML mapping with an optional policy mapping")
    return value


def check_skill_file(relative: str, data: bytes, context: str) -> None:
    """Reject a skill file that declares a native invocation setting; ``context`` names the file."""
    if relative == "SKILL.md" and CLAUDE_KEY in _skill_header(data, context):
        raise BundleError(f"{context}: {CLAUDE_KEY} is set by invocation in bundle.toml", fix=FIX)
    if relative == CODEX_FILE and CODEX_KEY in _codex_settings(data, context).get("policy", {}):
        raise BundleError(f"{context}: policy.{CODEX_KEY} is set by invocation in bundle.toml", fix=FIX)


def check_skill_source(path: Path, context: str) -> None:
    """Load-time check of a skill source directory; ``context`` is its ``<asset-id>/<source>`` prefix."""
    for relative in ("SKILL.md", CODEX_FILE):
        if (path / relative).is_file():
            check_skill_file(relative, (path / relative).read_bytes(), f"{context}/{relative}")


def skill_entry(path: Path, context: str) -> Path:
    """Resolve exactly one authored entry; template contents are validated after rendering."""
    entries = [path / name for name in ("SKILL.md", "SKILL.md.jinja") if (path / name).is_file()]
    if not path.is_dir() or len(entries) != 1:
        raise BundleError(f"{context}: skill source must contain exactly one of SKILL.md or SKILL.md.jinja")
    return entries[0]


def user_only(relative: str, data: bytes, agent: str, context: str) -> bytes:
    """One projected file of a ``user`` skill as ``agent`` reads it; ``context`` names the file in errors.

    A project override is checked here: it may not set a native key either.
    """
    check_skill_file(relative, data, context)
    if relative == "SKILL.md" and agent == "claude-code":
        text, block = locate_frontmatter(data, context, "skill")
        line = f"{CLAUDE_KEY}: true"
        if block is None:
            offset = 1 if text.startswith("﻿") else 0
            return (text[:offset] + f"---\n{line}\n---\n" + text[offset:]).encode("utf-8")
        newline = block.newline or "\n"
        return (text[: block.header_end] + line + newline + text[block.header_end :]).encode("utf-8")
    if relative == CODEX_FILE and agent in SHARED_SKILL_AGENTS:
        settings = _codex_settings(data, context)
        if "policy" in settings:
            settings["policy"][CODEX_KEY] = False
            return yaml.safe_dump(settings, sort_keys=False, allow_unicode=True).encode("utf-8")
        separator = b"" if not data or data.endswith(b"\n") else b"\n"
        return data + separator + codex_policy(False)
    return data


def user_only_extras(agent: str, relatives: set[str]) -> dict[str, bytes]:
    """Files a ``user`` skill's projection for ``agent`` gains when its source does not ship them."""
    if agent in SHARED_SKILL_AGENTS and CODEX_FILE not in relatives:
        return {CODEX_FILE: codex_policy(False)}
    return {}
