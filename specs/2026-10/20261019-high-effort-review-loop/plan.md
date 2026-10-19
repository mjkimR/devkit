---
id: PLAN-high-effort-review-loop
spec: SPEC-high-effort-review-loop
---

# Technical Plan: `SPEC-high-effort-review-loop` Bounded high-effort review procedure

## 1. Constitution & Invariant Review

- `ADR-bounded-high-effort-review-loop` (accepted, supersedes `ADR-medium-review-delegation`) is the decision this
  plan implements. Its `medium` and `low` rules are restated unchanged; only `high` text changes.
- `ADR-reconcile-check-envelope` keeps holding: every reconcile verification is still a `reconcile-check` envelope
  read by the `living-spec-draft` exit, and the initial `high` reconcile verification stays independent. Only a batch
  of minor reconcile fixes after it may be self-verified, which the new ADR records as a supplement.
- `ADR-worker-delivers-committed-result` and `ADR-run-records-and-activity-branches`: the hand-over uses the existing
  `worker` problem and question records; no new kind or key.
- Shared stage definitions (`SHARED_STAGE_MISMATCH`) are untouched: workflow bodies change below the frontmatter only.
- No architecture constraint is affected: no Python module, import or package boundary changes. `packages/devkit/`
  (the envelope engine) is not touched.

## 2. Architecture Overview & Impact

All bundle paths are under `packages/devkit-spec/src/devkit_spec/bundle/`.

- **Impacted Components**:
  - `skills/spec/references/review-loop.md` (new): the `high` loop (round, fixing, next round, end, round count),
    hand-over table and its aftermath, minor-fix table, severity table, mandatory `scout` in `high` Planning. Linked
    from effort.md, so `test_skill_links_resolve_and_every_reference_is_linked` holds.
  - `skills/spec/references/effort.md`: the table's `high` cells cite the loop; Planning `high` requires `scout`; the
    rules gain a `high` loop rule and the session reclassification advice (SHOULD); the medium repeat-call rule no
    longer refers to "high re-review obligations".
  - `skills/spec/references/envelope.md`: the example severity becomes `P2`; the bullet states the levels, where they
    are required and that they do not affect checks.
  - `skills/spec/references/completion.md`: the reconcile sentence cites the loop for `high`.
  - `skills/spec-review/SKILL.md`: the delegated-execution paragraph replaces "High retains re-review" with the loop
    and severity rule; the report example carries `severity`.
  - `skills/spec-sync/SKILL.md` Principle 5: `high` cites the loop.
  - `skills/spec-delegate/SKILL.md` Step 1 and `references/payload.md`: `high` cites the loop; reviewer and
    challenger rows add the round inputs (earlier rounds' findings, the round's diff scope, the effort).
  - `skills/spec-orchestrate/SKILL.md` step 4: the accept request names a missing `scout` at `high`.
  - Role contracts `code-reviewer`, `reconcile-reviewer`, `challenger`: input gains the earlier findings and the
    round's diff scope; return gains `severity` on every finding and the `recurs:` marker. `scout`: unchanged
    procedure; its purpose notes the `high` Planning use (the caller passes the `refs` starting points).
  - `development-worker`, `planning-worker`: step 4 cites the loop for `high` and the hand-over records (problem,
    questions); `On a problem` names the hand-over as a stop reason.
  - Workflow bodies `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`, `sdd-spec-bugfix` (no effort
    text today; it gets the same role-invocation sentence as `sdd-spec-feature` only if it already restates effort,
    otherwise nothing), `sdd-proposal`: prose only.
  - `packages/devkit-spec/tests/test_effort_procedure.py` (new): AC-01 to AC-08.
  - Living Spec: `CAP-DLV-delivery-workflows` rule 7 (hand-over stop reasons) and rule 15 (the `high` rules,
    severity, `scout`, gap report), `CAP-DLV-workflow-envelopes` (what the spec bundle's levels mean; the engine still
    accepts any non-empty string). Quick references under `docs/development/reference/` are checked for effort text.
- **New Dependencies**: none.

Decisions made here (recommended option, inside the agreed scope):

- `sdd-spec-bugfix.md` has no effort sentence today (`rg effort` finds only the `dev-integration` line). AC-07 asks
  every workflow body to cite the loop, so it gets the role-invocation sentence the other spec workflow carries.
- The ADR file in the write scope (`docs/decisions/2026-10/20261019-bounded-high-effort-review-loop.md`) needs no
  edit: it is accepted and its consequences already match. The superseded ADR's frontmatter is outside the write
  scope (spec 1.1).

## 3. Verification & Test Plan

- Targeted during development: `uv run pytest packages/devkit-spec/tests/test_effort_procedure.py
  packages/devkit-spec/tests/test_role_contracts.py packages/devkit-spec/tests/test_bundle_budgets.py
  packages/devkit-spec/tests/test_workflows.py`.
- AC-09: `uv run devkit workflow validate` (exit 0) and
  `git diff 8ca289b -- packages/devkit-spec/src/devkit_spec/bundle/workflows/` inspected for frontmatter lines.
- Before review: `just lint-check`, `just check devkit-spec`, `just test devkit-spec`, `just rules-check`; `just smoke`
  only if bundle wiring (`bundle.toml`) changes, which this plan does not intend (a new reference inside a skill
  folder ships with the skill).
- `uv run devkit sync` after the bundle edits so `.devkit/managed/` and the projected agent files match the source
  (`.devkit/installation.json` changes only as `devkit sync` writes it).
