"""Host guidance block: the managed orientation index in the root ``AGENTS.md``.

``devkit sync`` writes one marker-delimited block into the consumer's root
``AGENTS.md`` so that any agent session, including one started without a
skill, learns that devkit-managed assets exist and how to load their context.
Everything outside the markers belongs to the project and is preserved byte
for byte. The receipt records the block's SHA-256; a block edited by hand is
a conflict, exactly like a modified managed file. Line endings are not
content: a file checked out with CRLF keeps CRLF, and the digest is taken over
the block with LF line endings.
"""

from __future__ import annotations

import re

from devkit.core.receipt import GUIDANCE_END, GUIDANCE_START
from devkit.distribution.content import sha256
from devkit.distribution.errors import DistributionError, GuidanceBlockError
from devkit.distribution.installation.workspace import AGENTS_FILE

START = GUIDANCE_START
END = GUIDANCE_END

# One line per generated entry skill, keyed by the asset kind that triggers it.
ENTRY_SKILLS = {
    "playbook": "`devkit-playbook`: find and run an operational playbook (explicit user invocation only)",
    "workflow": "`devkit-workflow`: diagnose and follow the delivery workflow stage of a work unit",
}

_START_LINE = re.compile(rf"^{re.escape(START)}[ \t]*\r?$", re.MULTILINE)
_END_LINE = re.compile(rf"^{re.escape(END)}[ \t]*\r?$", re.MULTILINE)


def render(bundles: list[str], entry_skills: list[str], fragments: list[str] | tuple[str, ...] = ()) -> str:
    """Return the block text (markers included, no trailing newline) for a selection.

    ``fragments`` are the selection's rendered ``guidance`` assets, placed after
    devkit's own lines in the order the caller fixes (bundle, then asset ID).
    """
    lines = [
        START,
        "## devkit",
        "",
        "This repository installs agent assets with `devkit`. `.devkit/config.toml` selects",
        "bundles; `.devkit/installation.json` records what is deployed.",
        "",
    ]
    if bundles:
        lines.append(
            "- Before work that touches a bundle's assets, run `uv run devkit get-context <bundle>` once"
            " per bundle in the current agent context. Installed bundles: " + ", ".join(f"`{b}`" for b in bundles) + "."
        )
    else:
        lines.append(
            "- No bundle is selected. `uv run devkit list` shows installed bundles;"
            " `uv run devkit add <bundle>` selects one."
        )
    for kind in sorted(entry_skills):
        if kind not in ENTRY_SKILLS:
            raise DistributionError(f"unknown entry skill kind: {kind}")
    for kind in sorted(entry_skills):
        lines.append(f"- Entry skill {ENTRY_SKILLS[kind]}.")
    lines.extend(
        [
            "- Never edit `.devkit/managed/` or projected agent files; change the source bundle"
            " or use `devkit override`.",
            *fragments,
            "",
            "This block is managed by `devkit sync`; edit outside the markers only.",
            END,
        ]
    )
    return "\n".join(lines)


def normalize(block: str) -> str:
    """The block with LF line endings: what is compared and hashed."""
    return block.replace("\r\n", "\n")


def digest(block: str) -> str:
    return sha256(normalize(block).encode("utf-8"))


def _locate(text: str) -> tuple[int, int] | None:
    starts = list(_START_LINE.finditer(text))
    ends = list(_END_LINE.finditer(text))
    if not starts and not ends and START not in text and END not in text:
        return None
    if (
        len(starts) != 1
        or len(ends) != 1
        or text.count(START) != 1
        or text.count(END) != 1
        or ends[0].start() < starts[0].end()
    ):
        raise GuidanceBlockError(
            f"malformed guidance block in {AGENTS_FILE}: expected exactly one {START} line and one {END} line,"
            " each on a line of its own"
        )
    end = ends[0].end()
    if text[end - 1 : end] == "\r":
        end -= 1
    return starts[0].start(), end


def decode(data: bytes | None) -> str | None:
    if data is None:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GuidanceBlockError(f"{AGENTS_FILE} is not UTF-8") from exc


def extract(text: str | None) -> str | None:
    """Return the current block (markers included) or ``None`` when the file has none."""
    if text is None:
        return None
    span = _locate(text)
    if span is None:
        return None
    return text[span[0] : span[1]]


def compose(text: str | None, block: str) -> str:
    """Create, append or replace the block, preserving every byte outside the markers.

    The block is written with the file's line ending (CRLF when the file uses it).
    """
    if text is None:
        return block + "\n"
    newline = "\r\n" if "\r\n" in text else "\n"
    block = normalize(block).replace("\n", newline)
    span = _locate(text)
    if span is None:
        if not text:
            return block + newline
        separator = "" if text.endswith(newline * 2) else (newline if text.endswith(newline) else newline * 2)
        return text + separator + block + newline
    return text[: span[0]] + block + text[span[1] :]


def strip(text: str) -> str | None:
    """Remove the block; ``None`` means nothing but the block was in the file."""
    span = _locate(text)
    if span is None:
        return text
    newline = "\r\n" if "\r\n" in text else "\n"
    before, after = text[: span[0]], text[span[1] :]
    if after.startswith(newline):
        after = after[len(newline) :]
    head = before.rstrip("\r\n")
    remainder = head + (newline if head else "") + after.lstrip("\r\n")
    if remainder.strip() == "":
        return None
    if not remainder.endswith("\n"):
        remainder += newline
    return remainder
