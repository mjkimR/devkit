from __future__ import annotations

import os
from pathlib import Path

from agent_rule_engine.models import Autofixable, Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules.base import BaseRule


class MarkdownLinkRule(BaseRule, Autofixable):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-markdown-link",
            name="relative-markdown-link-check",
            description="Validates relative markdown link targets and automatically corrects broken relative paths.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
        )

    def _is_relative_file_link(self, target: str) -> bool:
        if not target or target.startswith(("#", "http://", "https://", "mailto:", "ftp://")):
            return False
        # Remove anchor if present
        target_path = target.split("#", 1)[0]
        return bool(target_path and not target_path.startswith("/"))

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        catalog = ctx.cache.get_catalog(ctx.workspace_root)
        all_md = ctx.cache.find_files(ctx.workspace_root, extensions=(".md",))

        for p in all_md:
            rel = p.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue

            links = ctx.cache.get_links(p)
            for link in links:
                if not self._is_relative_file_link(link.target):
                    continue

                raw_target = link.target.split("#", 1)[0]
                target_resolved = (p.parent / raw_target).resolve()

                if not target_resolved.exists():
                    # Check if basename exists elsewhere in workspace
                    target_basename = Path(raw_target).name
                    candidates = catalog.find_paths_by_basename(target_basename)
                    can_fix = len(candidates) == 1

                    violations.append(
                        Violation(
                            rule_id=self.id,
                            file=rel,
                            line=link.line,
                            message=f"Broken relative markdown link '{link.target}'",
                            remediation=(
                                f"Update path to '{candidates[0]}'"
                                if can_fix
                                else f"Verify relative path '{raw_target}' exists"
                            ),
                            fixable=can_fix,
                            severity=self.severity,
                            phase=self.phase,
                        )
                    )

        return violations

    def fix(self, ctx: RuleContext) -> list[str]:
        modified: list[str] = []
        catalog = ctx.cache.get_catalog(ctx.workspace_root)
        all_md = ctx.cache.find_files(ctx.workspace_root, extensions=(".md",))

        for p in all_md:
            rel = p.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue

            links = ctx.cache.get_links(p)
            text = ctx.cache.read_text(p)
            changed = False

            for link in links:
                if not self._is_relative_file_link(link.target):
                    continue

                parts = link.target.split("#", 1)
                raw_target = parts[0]
                anchor = f"#{parts[1]}" if len(parts) > 1 else ""
                target_resolved = (p.parent / raw_target).resolve()

                if not target_resolved.exists():
                    target_basename = Path(raw_target).name
                    candidates = catalog.find_paths_by_basename(target_basename)
                    if len(candidates) == 1:
                        target_abs = ctx.workspace_root / candidates[0]
                        # Compute relative path from p.parent to target_abs
                        new_rel = os.path.relpath(target_abs, p.parent)
                        new_target = f"{new_rel}{anchor}"
                        old_link_str = f"[{link.text}]({link.target})"
                        new_link_str = f"[{link.text}]({new_target})"
                        if old_link_str in text:
                            text = text.replace(old_link_str, new_link_str, 1)
                            changed = True

            if changed:
                ctx.cache.write_text(p, text, dry_run=ctx.dry_run)
                modified.append(rel)

        return modified
