from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from devkit.core import MANAGED_PATH, OVERRIDES_PATH
from devkit.rules.engine.models import Autofixable, Phase, RuleContext, Severity, Violation
from devkit.rules.engine.settings import match_path
from devkit.rules.rules.base import BaseRule
from devkit.rules.workspace.markdown import LocalTarget, MarkdownLink, encode_destination, local_target, split_lines


def _exists(path: Path) -> bool:
    try:
        return path.exists()
    except (OSError, ValueError):
        return False


@dataclass(frozen=True)
class BrokenLink:
    """A relative link whose file does not exist, with its unique repair candidate if any."""

    file: Path
    rel: str
    link: MarkdownLink
    target: LocalTarget
    candidate: str | None


class MarkdownLinkRule(BaseRule, Autofixable):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-markdown-link",
            name="relative-markdown-link-check",
            description="Validates relative markdown link targets and automatically corrects broken relative paths.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
        )

    def _broken_links(self, ctx: RuleContext) -> Iterator[BrokenLink]:
        """Broken relative links of every targeted Markdown file, in file and document order.

        A broken link is repairable when its destination stays inside the
        workspace and exactly one Markdown file in the workspace has the same
        basename.

        A symlinked Markdown file is an alias of its target, which is checked
        (and repaired) at its own path: resolving the alias's links from the
        symlink's directory would report valid links as broken, and a repair
        written through the symlink would break the target. A symlink named
        as an explicit target checks its target instead (once, and only when
        the run does not target it already), so ``check docs/alias.md`` never
        passes without checking anything.
        """
        root = ctx.workspace_root
        catalog = ctx.cache.get_catalog(root)
        aliased: set[Path] = set()
        for path in ctx.cache.find_files(root, extensions=(".md",)):
            rel = path.relative_to(root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            if path.is_symlink():
                target = self._alias_target(ctx, path)
                if target is None or target in aliased:
                    continue
                aliased.add(target)
                path, rel = target, target.relative_to(root).as_posix()
            for link in ctx.cache.get_links(path):
                target = local_target(link.target)
                if target is None:
                    continue
                if _exists(path.parent / target.path):
                    continue
                lexical = Path(os.path.normpath(path.parent / target.path))
                candidate = None
                if lexical.is_relative_to(root):
                    candidates = catalog.find_paths_by_basename(lexical.name)
                    candidate = candidates[0] if len(candidates) == 1 else None
                yield BrokenLink(path, rel, link, target, candidate)

    @staticmethod
    def _alias_target(ctx: RuleContext, alias: Path) -> Path | None:
        """The Markdown file an explicitly targeted symlink stands for, when the run would not check it otherwise.

        ``None`` in a whole-workspace run (the target is listed on its own), and for a target outside the
        workspace, not a regular ``.md`` file, receipt-pinned, excluded or already targeted.
        """
        if not ctx.has_targets:
            return None
        root = ctx.workspace_root
        try:
            target = alias.resolve(strict=True)
        except (OSError, RuntimeError):
            return None
        if not target.is_relative_to(root) or target.suffix != ".md" or not target.is_file():
            return None
        rel = target.relative_to(root).as_posix()
        if any(target.is_relative_to(root / pinned) for pinned in (MANAGED_PATH, OVERRIDES_PATH)):
            return None
        if any(match_path(pattern, rel) for pattern in ctx.exclude) or ctx.is_file_targeted(rel):
            return None
        return target

    def check(self, ctx: RuleContext) -> list[Violation]:
        return [
            Violation(
                rule_id=self.id,
                file=broken.rel,
                line=broken.link.line,
                column=broken.link.start + 1,
                message=f"Broken relative markdown link '{broken.link.target}'",
                remediation=(
                    f"Update path to '{broken.candidate}'"
                    if broken.candidate
                    else f"Verify relative path '{broken.target.path}' exists"
                ),
                fixable=broken.candidate is not None,
                severity=self.severity,
                phase=self.phase,
            )
            for broken in self._broken_links(ctx)
        ]

    def fix(self, ctx: RuleContext) -> list[str]:
        """Rewrite each repairable destination in place, keeping link text, title, query and fragment.

        A file that is not valid UTF-8 is left untouched (rewriting it would
        replace its undecodable bytes); its findings stay unfixed.
        """
        by_file: dict[Path, list[BrokenLink]] = {}
        for broken in self._broken_links(ctx):
            if broken.candidate is not None:
                by_file.setdefault(broken.file, []).append(broken)
        modified: list[str] = []
        for path, items in by_file.items():
            text = ctx.cache.read_text_strict(path)
            if text is None:
                continue
            lines = split_lines(text)
            # Right to left, so earlier offsets on the same line stay valid.
            for broken in sorted(items, key=lambda b: (b.link.line, b.link.target_start), reverse=True):
                link = broken.link
                assert broken.candidate is not None
                new_path = Path(os.path.relpath(ctx.workspace_root / broken.candidate, path.parent)).as_posix()
                destination = encode_destination(new_path, broken.target.suffix, angle=link.angle)
                line = lines[link.line - 1]
                lines[link.line - 1] = line[: link.target_start] + destination + line[link.target_end :]
            ctx.cache.write_text(path, "\n".join(lines), dry_run=ctx.dry_run)
            modified.append(items[0].rel)
        return modified
