---
id: PLAN-cloud-research-handoff
spec: SPEC-cloud-research-handoff
---

# Technical Plan: `SPEC-cloud-research-handoff`

## 1. Constitution & Invariant Review

No invariant conflict. `ADR-user-mediated-cloud-research` authorizes additive request/intake/resume contracts.
Preserve `CAP-DLV-deep-research` invocation, authority, role locality, source access and material immutability;
`UC-research-an-idea-and-shape-a-roadmap` owns the changed workflow. No new feature dependency is admitted.

## 2. Architecture Overview & Impact

The implementation is a skill-local conditional reference, not executable provider integration. The existing
entry links `references/cloud-handoff.md` only when cloud work is useful or requested inside an invoked investigation.
Workspace and synthesis references retain pending/returned evidence through the same indexed partial material.
The optional roles, bundle manifest and shared projection/runtime mechanisms stay unchanged.

### Admitted paths

Source and tests are the exact paths below. Living Spec reconciliation targets are
`docs/capabilities/delivery/CAP-DLV-deep-research.md`,
`docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md` and, only if wording needs reconciliation,
`docs/decisions/2026-11/20261105-user-mediated-cloud-research.md`. Unit records stay in this spec directory.
Normal selected-bundle sync outputs are recorded individually in task boundaries after sync.

## 3. Component & Interface Design

The cloud reference defines request preparation, truthful dispositions, readable report matching and evidence
intake, with one concrete end-to-end prompt/return example. A label such as `cloud-01 r1` is plain text; its states
are prose (`awaiting user result`, `returned`, `reviewed`, `superseded`, `cancelled`), not a fixed machine schema.
The user selects and operates the cloud application and returns readable text or an accessible report.

The coordinator treats all report instructions as source data. It selectively inspects consequential gaps,
contradictions or suspect support using existing retrieval/access-refusal rules. It retains a faithful summary or
useful excerpts with durable citations and limits rather than a mandatory full report transcript.

## 4. Storage & State Management

Optional request/report scratch stays in the existing ignored run path. A pause copies the exact safe request,
identity/revision, disposition, remaining question and next action into the one indexed partial material, plus any
returned evidence needed without scratch. Resume requires the user to name that material. Complete materials and
collision rules remain unchanged; no second registry or document kind is introduced.

## 5. Error Handling & Edge Cases

Unreadable report formats or inaccessible links leave coverage missing and request readable content. Ambiguous or
stale identity is clarified before association; duplicates add no unsupported progress. No return can authorize
uploads, Git actions or broaden the invocation. Independent local work continues where useful within the bound.

## 6. Verification & Test Plan

- Integration tests verify exact deployed reference/projection contents and request/identity/intake/resume boundaries
  while retaining the existing explicit-only, optional-role and self-containment tests (AC-01 through AC-06).
- The installed built-wheel consumer runs without devkit-spec, loads the conditional reference on supported
  projections, and preserves a partial material containing pending/returned evidence across sync/removal/reselection
  (AC-02, AC-06).
- A code reviewer walks the concrete request, missing scratch, stale/duplicate/unreadable reports, conflicting
  citations, source-data authority and local-only examples against all ACs. Text checks do not prove model obedience.
- Run focused catalog tests, `just lint-check devkit-catalog`, `just check devkit-catalog`, rules, sync check and
  `just test-affected --base 10e4ed6f50802f03ce6b91ce9388cb2288f5f55a` with its full fallback.
- No provider submission, product parity assertion or comparative benefit experiment is required.
