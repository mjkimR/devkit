from __future__ import annotations

from .manifest import BundleError


def prepend_context(data: bytes, bundle: str) -> bytes:
    """Add the prerequisite after frontmatter without modifying source bytes."""
    lines = data.splitlines(keepends=True)
    offset = 0
    if lines and lines[0].strip() == b"---":
        offset = len(lines[0])
        for line in lines[1:]:
            offset += len(line)
            if line.strip() in {b"---", b"..."}:
                break
        else:
            raise BundleError("skill has unclosed YAML frontmatter")
    guidance = (
        "<!-- DEVKIT:CONTEXT -->\n"
        "Before performing this skill, load this bundle's context by running\n"
        f"`uv run devkit get-context {bundle}` from the consumer project.\n"
        "Run this only once per bundle in the current agent context, shared across\n"
        "all skills from this bundle. If its guidance is already available, skip\n"
        "the command. Read and apply the full constitution. The instruction catalog\n"
        "exposes headers and paths only; read an instruction body when relevant.\n"
        "If loading fails, resolve the failure before performing this skill.\n"
        "Reload only if\n"
        "the guidance is no longer available, for example after context compaction\n"
        "or in a new agent context.\n"
        "<!-- /DEVKIT:CONTEXT -->\n\n"
    ).encode()
    prefix = data[:offset]
    if prefix:
        prefix += b"\n" if prefix.endswith(b"\n") else b"\n\n"
    return prefix + guidance + data[offset:]
