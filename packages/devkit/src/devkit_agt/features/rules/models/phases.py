"""Phase resolution: default phases, project overrides, and promotion tracking.

A rule declares a default ``phase``. A project may park a linter rule in the
hygiene phase through ``[rules.phase_overrides]`` while its existing violations
are cleared. A rule authored for a codebase with pre-existing violations can
declare ``promote_to = Phase.LINTER`` on a ``hygiene`` rule to record that it is
meant to become a linter rule once clean. Both transitions are reported by the
CLI with the count of remaining violations; ``remaining=0`` is the signal to
drop the override or flip the rule's declared phase, and ``promotion_notices``
turns it into a ``RULES_PROMOTION_READY`` notice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH

from devkit_agt.features.rules.models.contracts import Phase, Rule, Violation
from devkit_agt.features.rules.models.errors import PolicyError, PromotionReadyNotice


@dataclass(frozen=True)
class PhaseEntry:
    """Resolved phase state of one rule."""

    rule_id: str
    default_phase: Phase
    effective_phase: Phase
    overridden: bool = False
    promote_to: Phase | None = None

    @property
    def transition(self) -> Phase | None:
        """Phase this rule is expected to return or advance to, if any."""
        if self.overridden:
            return self.default_phase
        return self.promote_to

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "default_phase": self.default_phase.value,
            "effective_phase": self.effective_phase.value,
            "overridden": self.overridden,
            "promote_to": self.promote_to.value if self.promote_to else None,
        }


def declared_promotion(rule: Rule) -> Phase | None:
    """Read the optional ``promote_to`` attribute without requiring it on the protocol."""
    value = getattr(rule, "promote_to", None)
    if value is None:
        return None
    return Phase(value)


def validate_phase_overrides(rules: Sequence[Rule], overrides: Mapping[str, Phase]) -> list[PolicyError]:
    """Problems for phase overrides that cannot apply to ``rules``."""
    by_id = {r.id: r for r in rules}
    errors: list[PolicyError] = []
    for rule_id in sorted(overrides):
        rule = by_id.get(rule_id)
        if rule is None:
            errors.append(PolicyError(f"phase override for unknown rule: {rule_id}", rule_id=rule_id))
            continue
        if rule.phase == overrides[rule_id]:
            errors.append(
                PolicyError(
                    f"phase override for {rule_id} is redundant: the rule already runs in the "
                    f"{rule.phase.value} phase; remove the entry",
                    rule_id=rule_id,
                )
            )
    return errors


def resolve_phases(rules: Sequence[Rule], overrides: Mapping[str, Phase] | None = None) -> list[PhaseEntry]:
    """Compute the effective phase of every rule, honoring project overrides."""
    overrides = overrides or {}
    entries: list[PhaseEntry] = []
    for rule in rules:
        override = overrides.get(rule.id)
        entries.append(
            PhaseEntry(
                rule_id=rule.id,
                default_phase=rule.phase,
                effective_phase=override or rule.phase,
                overridden=override is not None and override != rule.phase,
                promote_to=declared_promotion(rule),
            )
        )
    return entries


def effective_phase(rule: Rule, overrides: Mapping[str, Phase] | None = None) -> Phase:
    """Phase a rule runs in once project overrides are applied."""
    if overrides and rule.id in overrides:
        return overrides[rule.id]
    return rule.phase


def runs_in_phase(rule_phase: Phase, active: Phase) -> bool:
    """Hygiene runs include every rule; linter runs include only linter rules."""
    return active == Phase.HYGIENE or rule_phase == Phase.LINTER


def transition_entries(entries: Sequence[PhaseEntry], active: Phase) -> list[PhaseEntry]:
    """Entries with a pending transition whose rule is active in ``active``."""
    return [e for e in entries if e.transition is not None and runs_in_phase(e.effective_phase, active)]


def remaining_by_rule(violations: Sequence[Violation]) -> dict[str, int]:
    """Count unfixed violations per rule ID."""
    counts: dict[str, int] = {}
    for v in violations:
        if v.fixed:
            continue
        counts[v.rule_id] = counts.get(v.rule_id, 0) + 1
    return counts


def promotion_notices(
    entries: Sequence[PhaseEntry],
    active: Phase,
    violations: Sequence[Violation],
    sources: Mapping[str, str] | None = None,
) -> list[AdvisoryError]:
    """One ``RULES_PROMOTION_READY`` notice naming every pending transition with no unfixed violation left.

    ``[TARGET]`` names the files to edit: ``.devkit/config.toml`` for a phase
    override, the file defining the rule (``sources``, by rule ID) for a promotion.
    """
    remaining = remaining_by_rule(violations)
    ready = [e for e in transition_entries(entries, active) if remaining.get(e.rule_id, 0) == 0]
    if not ready:
        return []
    edits = [
        f"drop {e.rule_id} from [rules.phase_overrides] in {CONFIG_PATH}"
        if e.overridden
        else f"declare {e.rule_id} with phase={e.promote_to.value if e.promote_to else Phase.LINTER.value} and drop promote_to"
        for e in ready
    ]
    ids = [e.rule_id for e in ready]
    files = [CONFIG_PATH if e.overridden else (sources or {}).get(e.rule_id) for e in ready]
    return [
        PromotionReadyNotice(
            f"phase transitions are ready (remaining=0): {', '.join(ids)}",
            target_files=list(dict.fromkeys(path for path in files if path)),
            fix="; ".join(edits),
        )
    ]
