---
id: PLAN-consolidated-record-length
spec: SPEC-consolidated-record-length
---

# Technical Plan: `SPEC-consolidated-record-length`

## 1. Constitution & Invariant Review

No conflict with `ARCH-05-2-components` or `CAP-GOV-evaluation-lifecycle`.
`ADR-consolidated-record-budgets` settles the rule-local option and heuristic. No feature edge, public settings
model or engine change is needed. The input implementation matches Planning premises.

## 2. Architecture Overview & Impact

Add `FileLengthSettings.consolidated_max_lines: int | None = None` and validate positivity locally.
Keep path resolution, targeting, suffix filtering and line counting unchanged (AC-01, AC-04).
Only when enabled, Markdown exceeds its ordinary limit, read the cached header. Catch FrontmatterError and
retain the ordinary limit. Require a nonempty ID and a valid alias list; count distinct nonempty strings.
ADRs need two, terminal consolidated feedback needs one; namespaced area slugs remain valid (AC-02, AC-03).
Use max of both resolved budgets. Eligible over-budget findings retain numeric formatting and advise topic review
without losing retained content. No automatic fix is added.

Update the rule guide, reference, capability and ADR confirmation; add grouping guidance and relevant content tests
in both playbooks. Opt this repository into 600 while retaining the capability override (AC-05).
Selected bundle projections are produced only by sync and listed in the owning task's boundary.

## 3. Error Handling & Edge Cases

Existing typed validation rejects bool/string; internal None disables the option and TOML uses omission. local validation rejects nonpositive values with the existing
RULES_SETTINGS_INVALID and exit 2 contract. Invalid headers never suppress a length warning. Eligibility is only a
heuristic for ADRs renamed twice. A path may override either budget; enabling the option never lowers max_lines.

## 6. Verification & Test Plan

Rule-owned pytest covers defaults, exact thresholds, final newlines, eligibility failures, cache short-circuiting,
per-path precedence and typed settings. CLI integration proves invalid inputs return exit 2 and the stable code.
Spec content tests cover grouping, fidelity and retained completion commands.
Run relevant Ruff lint/format, Pyright, pytest, just test-affected --base 5eb97c6e (retaining mode=full fallback),
sync --check and rules --ci. Compare disabled/enabled findings through the existing in-memory testing evaluator
on the same final files; preserve settings/overrides and report six known ADR identities, not a fixed total (AC-06).
Mandatory independent code and reconcile reviewers verify the committed diff and Living Spec reflection.
