"""SDD rule applicability to explicitly retained workflow ownership."""

from pathlib import PurePosixPath

from devkit_agt.features.rules import RuleContext, RuleOmission, Violation, committed_anchors, workflow_ids
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_core.core import FrontmatterError
from devkit_dist.features.project import read_development_approach


def sdd_anchors(ctx: RuleContext) -> set[str]:
    return ctx.cache.get_or_compute("spec.sdd-ownership", lambda: _sdd_anchors(ctx))


def _sdd_anchors(ctx: RuleContext) -> set[str]:
    found = set()
    for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
        text = ctx.cache.read_text(path)
        if not text or not text.startswith("---") or "workflow" not in text.split("---", 2)[1]:
            continue
        try:
            data = ctx.cache.get_frontmatter(path)
        except FrontmatterError:
            continue
        if any(w.startswith("sdd-") for w in workflow_ids(data or {})):
            found.add(ctx.cache.relative_name(path))
    if ctx.snapshot is not None:
        found.update(
            p
            for p, ids in committed_anchors(ctx.snapshot.root, ctx.snapshot.base).items()
            if any(w.startswith("sdd-") for w in ids)
        )
    return found


def applies(ctx: RuleContext, path: str) -> bool:
    if read_development_approach(ctx.workspace_root).approach == "sdd":
        return True
    return any(
        str(PurePosixPath(anchor).parent) == "."
        or path == anchor
        or path.startswith(str(PurePosixPath(anchor).parent) + "/")
        for anchor in sdd_anchors(ctx)
    )


class LifecycleRule(BaseRule):
    def omission(self, ctx: RuleContext) -> RuleOmission | None:
        if read_development_approach(ctx.workspace_root).approach == "sdd":
            return None
        candidates = tuple(ctx.targets) + (ctx.snapshot.deleted if ctx.snapshot else ())
        if any(
            not candidates
            or any(
                str(PurePosixPath(anchor).parent) == "."
                or path == anchor
                or path.startswith(str(PurePosixPath(anchor).parent) + "/")
                for path in candidates
            )
            for anchor in sdd_anchors(ctx)
        ):
            return None
        return RuleOmission(self.id, "SDD_LIFECYCLE_INACTIVE", "adaptive-dev: no targeted retained SDD unit")


def binding_violations(ctx: RuleContext, rule_id: str) -> list[Violation]:
    if ctx.snapshot is None or read_development_approach(ctx.workspace_root).approach != "adaptive-dev":
        return []
    prior = committed_anchors(ctx.snapshot.root, ctx.snapshot.base)
    changed = ctx.snapshot.changed + ctx.snapshot.deleted
    found = []
    for anchor, ids in prior.items():
        directory = str(PurePosixPath(anchor).parent)
        if not any(w.startswith("sdd-") for w in ids) or not any(
            directory == "." or p == anchor or p.startswith(directory + "/") for p in changed
        ):
            continue
        try:
            data = ctx.cache.get_frontmatter(anchor) or {}
        except (OSError, FrontmatterError):
            data = {}
        if not any(w.startswith("sdd-") for w in workflow_ids(data)):
            found.append(
                Violation(
                    rule_id,
                    anchor,
                    1,
                    "Retained SDD anchor or binding was removed; adaptive-dev does not convert retained lifecycle artifacts",
                    remediation="Preserve the retained anchor and lifecycle binding; settle its existing Unit through SDD",
                )
            )
    return found
