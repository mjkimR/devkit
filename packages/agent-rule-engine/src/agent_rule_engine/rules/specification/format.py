from __future__ import annotations

import re
from pathlib import Path

import yaml

from agent_rule_engine.engine.models import Autofixable, Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules.base import BaseRule

_H1_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_TARGET_DIRS = ("docs/capabilities", "docs/stories", "docs/proposals", "docs/specs", "specs")


class SpecFormatRule(BaseRule, Autofixable):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-spec-format",
            name="spec-markdown-frontmatter-check",
            description="Enforces required YAML frontmatter (id, title, status) across all specification documents.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
        )

    def _get_target_files(self, ctx: RuleContext) -> list[Path]:
        all_md = ctx.cache.find_files(ctx.workspace_root, extensions=(".md",))
        target_files: list[Path] = []
        for p in all_md:
            if p.name == "README.md":
                continue
            rel = p.relative_to(ctx.workspace_root).as_posix()
            if any(rel.startswith(f"{td}/") for td in _TARGET_DIRS) and ctx.is_file_targeted(rel):
                target_files.append(p)
        return target_files

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        files = self._get_target_files(ctx)

        for p in files:
            rel = p.relative_to(ctx.workspace_root).as_posix()
            fm, _body, _ = ctx.cache.get_frontmatter(p)

            if fm is None:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message="Document is missing standard YAML frontmatter block (starts with ---)",
                        remediation="Add standard RFC YAML frontmatter block (--- ... ---) with id, title, and status",
                        fixable=True,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )
                continue

            missing: list[str] = []
            for req_field in ("id", "title", "status"):
                if not fm.get(req_field):
                    missing.append(req_field)

            if missing:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message=f"Document frontmatter is missing required field(s): {', '.join(missing)}",
                        remediation=f"Add {', '.join(missing)} to the frontmatter header",
                        fixable=True,
                        severity=self.severity,
                        phase=self.phase,
                    )
                )

        return violations

    def fix(self, ctx: RuleContext) -> list[str]:
        modified: list[str] = []
        files = self._get_target_files(ctx)

        for p in files:
            rel = p.relative_to(ctx.workspace_root).as_posix()
            raw_text = ctx.cache.read_text(p)
            fm, body, _ = ctx.cache.get_frontmatter(p)

            stem = p.stem
            # Derive default title from first H1 or stem
            h1_match = _H1_PATTERN.search(body if fm is not None else raw_text)
            title = h1_match.group(1).strip() if h1_match else stem.replace("-", " ").capitalize()

            if fm is None:
                new_fm = {
                    "id": stem,
                    "title": title,
                    "status": "draft",
                }
                fm_yaml = yaml.dump(new_fm, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{fm_yaml}\n---\n\n{raw_text.lstrip()}"
                ctx.cache.write_text(p, new_content, dry_run=ctx.dry_run)
                modified.append(rel)
            else:
                updated = False
                if not fm.get("id"):
                    fm["id"] = stem
                    updated = True
                if not fm.get("title"):
                    fm["title"] = title
                    updated = True
                if not fm.get("status"):
                    fm["status"] = "draft"
                    updated = True

                if updated:
                    fm_yaml = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
                    new_content = f"---\n{fm_yaml}\n---\n{body}"
                    ctx.cache.write_text(p, new_content, dry_run=ctx.dry_run)
                    modified.append(rel)

        return modified
