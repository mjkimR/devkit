---
id: PLAN-guidance-followups
spec: SPEC-guidance-followups
---

# Technical Plan: `SPEC-guidance-followups` Align milestone tone, role shell notes and traceability follow-ups

## 1. Constitution & Invariant Review

- `ADR-milestone-merging` already records granularity as a recommendation; the capability edit implements that
  decision, so no ADR is needed. The RFC 2119 obligation is unchanged (SHOULD already meant "recommended").
- `RULE-traceability-link` requires both sides of a use case and capability link; both frontmatter edits land in one
  commit.
- Bundle self-containment: `spec-sync` links the `spec` skill's `references/envelope.md` by a relative path, as it
  already does for `references/source-feedback.md`; the bundle budget test checks the link and the size.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `docs/capabilities/harness/CAP-HARN-agent-guidance.md` | Milestone granularity sentences rewritten as a preference matching `docs/roadmap/README.md`. |
| `docs/usecases/delivery/UC-drive-development-to-integration.md` | `capabilities` gains `CAP-MCP-runtime-registration`. |
| `docs/capabilities/mcp/CAP-MCP-runtime-registration.md` | New `usecases` field listing `UC-drive-development-to-integration`. |
| Spec bundle `skills/spec-delegate/references/payload.md` | `challenger` row drops "(it has no shell)". |
| Spec bundle `skills/spec-sync/SKILL.md` | Step 5 names the `reconcile-check` envelope command and links `references/envelope.md`. |
| `packages/devkit-spec/tests/integration/bundles/spec/test_role_shell_guidance.py` (new) | Pins AC-02 and AC-04. |

Projected copies under `.devkit/managed/` and `.claude/` change only through `uv run devkit sync`.

## 3. Component & Interface Design

New capability sentence (replacing the two SHOULD sentences): "Milestones are loosely managed themes: prefer a
multi-unit phase, release or architectural theme advancing `ARCH-01-introduction-and-goals`, with observable
phase-level outcomes and capability boundaries, over a milestone that only sequences one proposal; a theme may begin
with one proposal while broader intended scope is not authored."

`spec-sync` step 5 addition: record it with `devkit workflow envelope new --unit <dir> --kind reconcile-check --stage
living-spec-draft`, with a relative link to the `spec` skill's `references/envelope.md` for the remaining flags.

## 4. Verification & Test Plan

- `just test-affected` (selects the bundle guidance and budget tests).
- `uv run devkit rules check`, `uv run devkit sync --check`, `git diff --check`.
- `rg -n "SHOULD" docs/capabilities | rg -i milestone` prints nothing.
- Reconcile at `low`: self-checked reconcile recorded as a `reconcile-check` envelope.
