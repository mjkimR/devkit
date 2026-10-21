"""Handoff evaluation results shared by workflow services and use cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from devkit_agt.features.workflow.models.checks import CheckResult
from devkit_agt.features.workflow.models.decision_records import Decision


@dataclass(frozen=True)
class CandidateResult:
    workflow: str
    recommended: bool
    eligible: bool
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "recommended": self.recommended,
            "eligible": self.eligible,
            "checks": [c.to_dict() for c in self.checks],
        }


@dataclass(frozen=True)
class Handoff:
    """The handoff decision once the bound workflow is complete.

    ``chosen`` comes from a recorded, still-eligible choice under either
    policy, else under ``auto`` from the first eligible candidate; under
    ``ask`` without a recorded choice a person picks.
    """

    policy: str
    candidates: tuple[CandidateResult, ...]
    chosen: str | None = None
    decision: Decision | None = None  # recorded choice that produced ``chosen``, if any

    @property
    def eligible(self) -> tuple[str, ...]:
        return tuple(c.workflow for c in self.candidates if c.eligible)

    @property
    def recommended(self) -> tuple[str, ...]:
        return tuple(c.workflow for c in self.candidates if c.recommended and c.eligible)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "candidates": [c.to_dict() for c in self.candidates],
            "eligible": list(self.eligible),
            "recommended": list(self.recommended),
            "chosen": self.chosen,
            "decision": self.decision.file if self.decision else None,
        }
