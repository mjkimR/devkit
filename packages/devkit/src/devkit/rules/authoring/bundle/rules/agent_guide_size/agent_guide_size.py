"""``RULE-agent-guide-size``: warn when an always-loaded agent guide outgrows its byte budget.

Shipped by the ``authoring`` bundle (preset ``agent-guide-authoring``) and
loaded by ``devkit rules`` from the synchronized copy. The measured size is
the whole file, including the guidance block ``devkit sync`` writes into the
root ``AGENTS.md``: every byte reaches the agent. The message reports the
block's share separately because the project cannot edit it directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from devkit.core import GUIDANCE_END, GUIDANCE_START
from devkit.rules.engine.models import Phase, RuleContext, Severity, Violation
from devkit.rules.engine.settings import match_path, validate_pattern
from devkit.rules.rules.base import BaseRule

REMEDIATION = (
    "Keep the guide to orientation, boundaries, invariants and verification commands. Drop project"
    " structure trees; move module-specific details to the module's README or docs behind a link,"
    " judgment rules to instructions, procedures to playbooks or skills, mechanical checks to rules,"
    " and directory-specific guidance to a nested guide."
    ' Follow the agent-guide-authoring playbook (`uv run devkit playbook search "curate agent guide"`).'
    " The devkit block shrinks only by deselecting presets that contribute guidance."
    " For a justified exception, raise max_bytes for this exact path in"
    " [[rules.settings.RULE-agent-guide-size.overrides]] with a comment giving the reason"
)


@dataclass(frozen=True)
class AgentGuideSizeSettings:
    max_bytes: int = 8192
    paths: list[str] = field(default_factory=lambda: ["**/AGENTS.md", "**/CLAUDE.md"])
    # Bundle constitutions are read once per bundle through `devkit get-context`, not on every turn.
    exclude: list[str] = field(default_factory=lambda: ["**/bundle/AGENTS.md"])


def _block_bytes(data: bytes) -> int:
    """Size of the devkit guidance block in ``data`` (markers included); 0 without exactly one block."""
    start, end = GUIDANCE_START.encode(), GUIDANCE_END.encode()
    if data.count(start) != 1 or data.count(end) != 1:
        return 0
    first, last = data.index(start), data.index(end) + len(end)
    return last - first if last > first else 0


class AgentGuideSizeRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-agent-guide-size",
            name="agent-guide-size-check",
            description="Warn when an agent guide (AGENTS.md, CLAUDE.md) exceeds its byte budget.",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            settings=AgentGuideSizeSettings(),
            guide="agent_guide_size.md",
        )

    def validate_settings(self, settings: AgentGuideSizeSettings) -> None:
        if settings.max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        for pattern in [*settings.paths, *settings.exclude]:
            validate_pattern(pattern)

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            # A symlinked guide (CLAUDE.md -> AGENTS.md) is measured once, through its target.
            if path.is_symlink() or not ctx.is_file_targeted(rel):
                continue
            settings: AgentGuideSizeSettings = ctx.settings(self, rel)
            if not any(match_path(p, rel) for p in settings.paths) or any(match_path(p, rel) for p in settings.exclude):
                continue
            data = ctx.cache.read_bytes(path)
            if len(data) <= settings.max_bytes:
                continue
            block = _block_bytes(data)
            share = f", including {block} bytes of the devkit guidance block" if block else ""
            violations.append(
                Violation(
                    rule_id=self.id,
                    file=rel,
                    line=1,
                    message=f"Guide has {len(data)} bytes{share}; effective max_bytes is {settings.max_bytes}",
                    remediation=REMEDIATION,
                    fixable=False,
                    severity=self.severity,
                    phase=self.phase,
                )
            )
        return violations
