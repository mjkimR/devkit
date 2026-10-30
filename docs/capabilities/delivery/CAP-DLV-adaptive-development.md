---
id: CAP-DLV-adaptive-development
aliases:
  - CAP-DLV-idea-incubation
title: Adaptive Development
summary: "An opt-in content bundle supports iterative product work with optional support roles and resumes from mutable current facts without SDD records; retained research is linked by its material ID, not run by this bundle."
area: delivery
status: active
usecases:
  - UC-advance-an-idea
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md
---

# [CAP-DLV-adaptive-development] Adaptive Development

## 1. Summary

The opt-in `adaptive-dev` catalog bundle supplies `/adaptive-dev` for adaptive product iteration, three optional
support roles and a current-context template. The invoking agent is the coordinator (master). A product can remain
in adaptive development; no amount of work implies eventual SDD adoption. Explicit research teams are a separate bundle
(`CAP-DLV-deep-research`); this bundle neither invokes nor suggests them and links their retained material by ID.

`ADR-split-deep-research-bundle` owns the bundle's contents and its retained approach check and current context.
`ADR-retain-research-as-cited-materials` owns linking a research material by its ID. `ADR-adaptive-dev-approach-name`
owns the approach, bundle, entry and context-file names.

## 2. Scope and Boundary

- **In-Scope**: adaptive clarification, bounded research/experiments, representative implementation and actual
  usage, optional support roles, mutable current facts and resume.
- **Out-of-Scope**: explicit research teams and their retained materials (`CAP-DLV-deep-research`), shared approach
  policy (`CAP-DLV-project-policy`), generic projection (`CAP-DIST-agent-projections`), document formats
  (`CAP-DOCS-document-model`), project build/test tools and the separate baseline readiness/activation procedure
  (`CAP-DLV-sdd-baseline-adoption`).
- **Scope Excluded**: a runtime scheduler, agent bus, new wheel, mandatory role sequence, model routing, fixed
  management hierarchy, automatic approach switching, automatic implementation/publication, per-change SDD
  artifacts and reconstructed experiment history.

## 3. Business Rules and Policies

1. **Explicit selection**: WHERE `adaptive-dev:core` is selected, sync MUST deploy the bundle's entry and roles
   without seeding context or product documents. Test: `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py`.
2. **Independent installation**: The bundle MUST install with docs/catalog without a devkit-spec distribution.
   Test: `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`.
3. **Approach inspection**: WHEN the entry starts product work, the coordinator MUST inspect the effective common
   development approach rather than infer it from bundle selection.
4. **Inactive entry**: IF the approach is not `adaptive-dev`, THEN the entry MUST stop product actions and report the
   shared configuration action before any user-directed approach change.
5. **Unreadable policy**: IF policy inspection fails, THEN the coordinator MUST report the actual error and next
   configuration action without performing product work.
6. **Adaptive clarification**: WHEN the next action needs a product decision, the coordinator SHOULD reuse known
   answers and ask only the consequential missing decision.
7. **Bounded evidence**: WHEN research or an experiment informs work, the coordinator MUST distinguish observations,
   assumptions, limitations and the decision informed; an experiment names its write boundary and stop condition.
8. **Representative implementation**: WHEN implementation is retained, the coordinator MUST provide executable run
   and verification instructions for its representative flow.
9. **Truthful verification**: WHEN reporting a check, the coordinator MUST identify actual source/artifact-specific
   execution and limitations; skipped, unavailable or inconclusive evidence remains unverified.
10. **Iteration scope**: WHILE the product goal and constraints hold, the coordinator MAY reconstruct retained code,
    tests and documents without per-change SDD Units, approvals, envelopes or immutable experiment history.
11. **Changed direction**: IF the goal or constraints change, THEN the coordinator MUST obtain user direction before
    dependent work.
12. **Optional support**: WHERE a separable question or usage scope warrants delegation, the coordinator MAY invoke
    the corresponding support role; no action requires all roles or a fixed team count.
13. **Role boundaries**: WHEN a role is invoked, the coordinator MUST supply one goal, absolute boundaries,
    source/artifact identity, permitted actions, stop condition and expected output before verifying the actual
    return. The role reports native/emulated availability truthfully.
14. **Current context ownership**: WHEN retained resume facts change or work pauses, the coordinator MUST update
    project-owned `.devkit/adaptive-dev.md`; roles return evidence or drafts instead of editing that file.
15. **Context preservation**: WHEN sync, removal or re-selection runs, sync MUST preserve existing project-owned
    context and product notes. Tests: catalog integration and installed-consumer tests.
16. **Voluntary adoption**: WHEN the user explicitly requests SDD adoption, the coordinator MUST leave activation to
    the separately available baseline procedure while explaining preparation with adaptive development still active.
17. **Useful alternatives**: WHEN research choices affect resume, current facts SHOULD link retained notes, surviving
    alternatives and conditions that would reopen a choice, and link a retained research material by its `MAT-<slug>`
    ID rather than copy it.

Distribution checks enforce file/metadata contracts. Clarification, evidence, optionality and resume are semantic
agent contracts; keyword assertions alone do not establish them.

## 4. Interfaces and Data Contracts

### Distribution and entry

Install devkit-docs and devkit-catalog, then select `uv run devkit add adaptive-dev` (`adaptive-dev:core`).
The skill and three common role contracts use existing projection mechanisms. No adaptive-development runtime or CLI is
added.

`uv run devkit config show` exposes `configuration.development.approach` and its source.
The entry requires `adaptive-dev`; invalid policy propagates `DEVELOPMENT_CONFIG_INVALID`, exit 2.
A valid SDD result produces a guidance-level stop with the shared `[development] approach = "adaptive-dev"` action,
not a new error code. Selection/invocation changes no approach. Read `get-context adaptive-dev` once and the docs
context/instructions before relevant document work.

`/adaptive-dev` keeps small questions inline and invokes no other bundle's entry. A retained research material is an
input it reads by its `MAT-<slug>` ID when the user supplies or the current context links it.

### Optional roles

| Role | Result | Source and Git boundary |
| --- | --- | --- |
| product-clarifier | Candidate users/problems, alternatives and missing questions | Read-only; no invented user decision |
| product-researcher | Evidence for one product decision, or an explicitly bounded experiment | Read-only by default; assigned scratch notes or prototype writes only |
| usage-reviewer | Expected versus observed representative usage | Read-only product source; assigned test-data interactions only |

Every role leaves the index and HEAD unchanged and commits/publishes nothing. A result contains status
(`completed`, `needs_input` or `failed`), summary, source/artifact identity, observations with evidence/failure
conditions, recommendation or draft, assumptions and unverified areas. An experiment also returns actual changed
paths, commands and outcomes. The Host verifies boundaries and evidence before fold-back; direct communication
is optional host functionality and never changes authority. There is no SDD envelope requirement.

### Product notes and resume

Product notes reuse existing destinations and are written only when they help the next decision or describe
retained behavior. Native capability/use-case/decision/milestone semantics apply only when their subject warrants
them.

`.devkit/adaptive-dev.md` remains mutable project-owned Markdown, not managed/transient state or a parsed lifecycle.
Keep current goals, choices versus assumptions, source-specific checks, unresolved evidence and exact note links,
retained research material IDs, useful surviving alternatives/reopening conditions and the next action. Remove superseded experiments only when
they no longer inform work. A fresh context rechecks identities and applicability instead of replaying history.
