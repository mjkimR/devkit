---
id: PLAN-idea-discovery
spec: SPEC-idea-discovery
---

# Technical Plan: `SPEC-idea-discovery`

## 1. Constitution & Invariant Review

No existing invariant changes. Preserve `CAP-DLV-deep-research` and its explicit-only research entry, retention,
local role paths and no-suggestion rule. Add the distinct discovery behavior under CAP-DLV-idea-discovery.
The content stays in the catalog under `ARCH-05-2-components`; add no Python feature edge or dependency.

## 2. Architecture Overview & Impact

Add `skills/discovery/` and a user-invoked manifest asset to the existing core preset. The discovery router owns the
minimum interview, bounded first wave, proposal synthesis and uncertainty-driven routing. Conditional references own
team execution and optional material retention. Discovery-local roles use `role-worker`; no private sibling imports,
asset moves or global registered roles. Common research files stay byte-for-byte compatible.

The spec intake template exempts explicit discovery invocations just as it exempts research; subsequent implementation
remains ordinary intake. Document this in `CAP-HARN-agent-guidance`, add the discovery capability/use case and glossary
term, and update package and install guidance. No additional runtime or command boundary is introduced.

## 3. Component & Interface Design

`/discovery <idea, request or decision>` returns concrete candidate directions and a recommended next route in chat.
Its role payload names goal, supplied facts/decisions, premise/question, exact sources, absolute boundaries,
permitted actions, expected return and an observable stop condition. Explorer first returns do not see peers.
Criticism follows candidate development and cannot substitute team agreement for the owner's preference.

The default route preserves unknown preferences as assumptions. Ask only when a missing user-only answer changes
the first proposals or makes exploration wasteful. Subsequent uncertainty routes to question, research, proposed
example/experiment, reframing/hold/rejection or brief. No route starts another explicit entry or development.
Keep optional material retention self-contained and consistent with existing materials; no mandatory report.

## 4. Storage & State Management

Use a collision-free run under `.devkit/transient/deep-research/` only when scratch is needed; verify ignored and
untracked state before writing. Requested retention uses `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` and a
MAT index. Resume only a user-named partial material; complete materials stay immutable.

## 5. Error Handling & Edge Cases

Missing delegation leaves a reported coverage gap; small tasks can be handled inline without claiming independent
review. Denied access stops that resource. Open preferences do not force a questionnaire. A rejected idea is a
successful discovery result. Tests cover an upgrade from the research-only preset, not just a new installation.

## 6. Verification & Test Plan

- AC-01, AC-05, AC-06: real manifest/sync integration tests and the existing installed wheel consumer, extended for
  discovery and upgrade/removal compatibility.
- AC-02, AC-03, AC-04, AC-05, AC-06: isolated realistic forward exercise and independent semantic review.
- Run `just lint-check`, `just check`, `just test-affected --base main` with its full fallback intact, selective
  catalog wheel E2E, `devkit sync`, skill validation and `uv run devkit rules check --ci --base main`.
