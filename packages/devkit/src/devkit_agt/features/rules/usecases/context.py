"""Explicit changed-file context and optional session-bounded considerations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase

from devkit_agt.features.rules.models.contracts import RuleContext, Severity, Violation, rule_file
from devkit_agt.features.rules.models.errors import ChangeEvidenceNotice, RulesRunError, TargetError
from devkit_agt.features.rules.repositories.read_sessions import source_fingerprint, suppress
from devkit_agt.features.rules.services.changes import excerpts, refresh_context_changes
from devkit_agt.features.rules.services.evaluator import evaluate_rules
from devkit_agt.features.rules.services.targets import normalized_change_targets
from devkit_agt.features.rules.usecases.project import load_project_rules


@dataclass
class RuleReadContext:
    file: str
    change: dict[str, Any]
    hunks: list[dict[str, Any]]
    findings: list[Violation]
    suppressed: int
    omitted: dict[str, int]
    notices: list[AdvisoryError]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "change": self.change,
            "hunks": self.hunks,
            "findings": [v.to_dict() for v in self.findings],
            "suppressed": self.suppressed,
            "omitted": self.omitted,
            "notices": [n.to_dict() for n in self.notices],
        }


class ReadRuleContextUseCase(BaseUseCase):
    def execute(
        self, root: Path, file: str, *, rules_dir: Path | None = None, session: str | None = None
    ) -> RuleReadContext:
        root = root.resolve()
        path = Path(file)
        absolute = path if path.is_absolute() else root / path
        resolved = absolute.resolve()
        if not resolved.is_relative_to(root) or resolved == root:
            raise TargetError("read context target must be a file inside the workspace", target_files=[file])
        relative = normalized_change_targets(root, [resolved])[0]
        if relative.startswith((".devkit/managed/", ".devkit/overrides/")) or resolved.is_dir():
            raise TargetError("read context target is not a project-owned file", target_files=[file])
        project = load_project_rules(root, rules_dir)
        if project.errors:
            raise RulesRunError(project.errors)
        ctx = RuleContext(
            root,
            changed_files=[relative],
            exclude=project.config.exclude,
            phase_overrides=dict(project.config.phase_overrides),
            severity_overrides=dict(project.config.severity_overrides),
            rule_settings=dict(project.config.settings),
        )
        if ctx._excluded(relative):
            return RuleReadContext(
                relative, {"status": "excluded"}, [], [], 0, {"hunks": 0, "lines": 0, "bytes": 0}, []
            )
        refresh_context_changes(ctx)
        change = ctx.changes.get(relative)
        if not resolved.is_file() and (change is None or change.status != "deleted"):
            raise TargetError("read context target does not exist in working or before source", target_files=[file])
        if change is None or not ctx.change_available or not change.available:
            return RuleReadContext(
                relative,
                {"status": "unavailable"},
                [],
                [],
                0,
                {"hunks": 0, "lines": 0, "bytes": 0},
                [ChangeEvidenceNotice("exact textual change evidence is unavailable", target_files=[relative])],
            )
        selected = [
            r
            for r in project.rules
            if getattr(r, "change_scope", False)
            and project.config.severity_overrides.get(r.id, r.severity) is Severity.NOTICE
        ]
        ids = {r.id for r in selected}
        ctx.phase_overrides = {k: v for k, v in ctx.phase_overrides.items() if k in ids}
        ctx.severity_overrides = {k: v for k, v in ctx.severity_overrides.items() if k in ids}
        ctx.rule_settings = {k: v for k, v in ctx.rule_settings.items() if k in ids}
        result = evaluate_rules(ctx, selected)
        if result.errors:
            raise RulesRunError(result.errors)
        hunks, omitted = excerpts(change)
        response = RuleReadContext(relative, change.to_dict(), hunks, result.violations, 0, omitted, [])
        # Validate rendering before recording delivered fingerprints; a rendering failure must not suppress later output.
        json.dumps(response.to_dict())
        if session is None:
            return response
        by_id = {r.id: r for r in selected}
        fingerprints: list[str] = []
        for finding in response.findings:
            rule = by_id[finding.rule_id]
            span = finding.change_span
            assert span is not None
            text = change.before if span.side == "before" else change.after
            construct = "".join(text.splitlines(keepends=True)[span.start - 1 : span.end - 1])
            relevant = [h for h in change.hunks if getattr(h, span.side).intersects(span.start, span.end)]
            paired = [
                (
                    "".join(change.before.splitlines(keepends=True)[h.before.start - 1 : h.before.end - 1]),
                    "".join(change.after.splitlines(keepends=True)[h.after.start - 1 : h.after.end - 1]),
                )
                for h in relevant
            ]
            settings = ctx.settings(rule, relative)
            values = asdict(settings) if is_dataclass(settings) and not isinstance(settings, type) else settings
            payload = [
                rule.id,
                source_fingerprint(rule_file(rule), type(rule).__qualname__),
                values,
                relative,
                span.side,
                construct,
                paired,
            ]
            fingerprints.append(hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest())
        duplicate, notice = suppress(root, session, fingerprints)
        response.suppressed = sum(f in duplicate for f in fingerprints)
        response.findings = [v for v, f in zip(response.findings, fingerprints, strict=True) if f not in duplicate]
        if notice is not None:
            response.notices.append(notice)
        return response
