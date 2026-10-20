"""Preserve citations to dropped proposal records as verified Git evidence, without writing Git."""

from __future__ import annotations

import os
from pathlib import Path

from devkit.core import FrontmatterError, GitError, atomic_write_text, run_git
from devkit.core.frontmatter import locate
from devkit.rules import extract_links
from devkit.rules.workspace.markdown import local_target

from devkit_spec.documents import visible_lines
from devkit_spec.proposals.rewrite import (
    _CODE_SPAN_PATH,
    LINK,
    PATH,
    UNREADABLE,
    UNWRITABLE,
    RelocationPlan,
    RewriteReport,
    Rewritten,
    Unresolved,
)


def _origin(file: str, plan: RelocationPlan) -> str:
    if file in plan.moved_files:
        return plan.moved_files[file]
    for destination, source in sorted(plan.moved.items(), key=lambda item: len(item[0]), reverse=True):
        if file.startswith(destination + os.sep):
            return source + file[len(destination) :]
    return file


def rewrite_history(
    root: Path, files: list[str], plan: RelocationPlan, records: list[Path], report: RewriteReport
) -> None:
    """Rewrite only citations of exact dropped records whose current bytes are available at HEAD.

    Unknown history leaves spans unresolved; ordinary relocation reports unresolved Markdown links. The existing
    handoff remains available outside Git. Nothing archives records or manufactures a commit.
    """
    if not records:
        return
    dropped = {str(record) for record in records}
    pins: dict[str, str | None] = {}
    try:
        head = run_git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    except GitError:
        head = ""

    def pin(path: str) -> str | None:
        if path not in pins:
            pins[path] = None
            if head:
                relative = Path(path).relative_to(root).as_posix()
                revision = f"{head}:{relative}"
                try:
                    if run_git(root, "show", revision) == Path(path).read_bytes():
                        pins[path] = revision
                except (GitError, OSError):
                    pass
        return pins[path]

    for file in files:
        display = Path(file).relative_to(root).as_posix()
        try:
            with open(file, encoding="utf-8", newline="") as handle:
                text = handle.read()
            block = locate(text)
        except (OSError, UnicodeDecodeError, FrontmatterError):
            report.unresolved.append(Unresolved(display, 0, PATH, "", UNREADABLE))
            continue
        origin = _origin(file, plan)
        edits: list[tuple[int, int, str]] = []
        changed: list[Rewritten] = []
        body_start, body_line = (block.end, block.body_line) if block else (0, 1)
        visible = list(visible_lines(text, start=body_start, first_line=body_line))
        lines = text.split("\n")
        links = extract_links(text)
        # Code-span paths have always been unit-relative, and only apply to carried proposal prose.
        if origin != file:
            for line in visible:
                for match in _CODE_SPAN_PATH.finditer(lines[line.number - 1]):
                    if any(link.line == line.number and link.start <= match.start() < link.end for link in links):
                        continue
                    old = match.group(1)
                    path = os.path.normpath(os.path.join(plan.proposal, old))
                    if path not in dropped:
                        continue
                    revision = pin(path)
                    if revision is None:
                        report.unresolved.append(Unresolved(display, line.number, PATH, old, "unmapped"))
                        continue
                    replacement = f"historical Git `{revision}`"
                    edits.append((line.offset + match.start(), line.offset + match.end(), replacement))
                    changed.append(Rewritten(display, line.number, PATH, old, replacement))
        offsets = {line.number: line.offset for line in visible}
        for link in links:
            if link.line not in offsets:
                continue
            target = local_target(link.target)
            if target is None:
                continue
            path = os.path.normpath(os.path.join(os.path.dirname(origin), target.path))
            if path not in dropped or (revision := pin(path)) is None:
                continue
            suffix = f" (selector `{target.suffix}`)" if target.suffix else ""
            replacement = f"{link.text} (historical Git `{revision}`{suffix})"
            edits.append((offsets[link.line] + link.start, offsets[link.line] + link.end, replacement))
            changed.append(Rewritten(display, link.line, LINK, link.target, replacement))
        if not edits:
            continue
        for start, end, replacement in sorted(edits, reverse=True):
            text = text[:start] + replacement + text[end:]
        try:
            atomic_write_text(Path(file), text)
        except OSError:
            report.unresolved.append(Unresolved(display, 0, PATH, "", UNWRITABLE))
            continue
        report.files.append(display)
        report.rewritten.extend(changed)
