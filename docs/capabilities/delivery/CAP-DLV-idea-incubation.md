---
id: CAP-DLV-idea-incubation
title: Idea Incubation
summary: "An opt-in catalog bundle coordinates adaptive product discovery, research, implementation and usage verification, retaining mutable current context without SDD delivery records."
area: delivery
status: active
usecases:
  - UC-incubate-an-idea
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/incubation/bundle/skills/incubate/SKILL.md
---

# [CAP-DLV-idea-incubation] Idea Incubation

## 1. Summary

The opt-in `incubation` catalog bundle supplies `/incubate`, three optional support roles and a current-context
template. The coordinator advances the next useful product action from an incomplete idea or retained current
facts. A small app can finish and remain maintained in incubation. `ADR-keep-incubation-guidance-opt-in-and-current-state-based`
records asset and context ownership.

## 2. Scope & Boundary

- **In-Scope**: adaptive clarification, bounded research/experiments, representative implementation and actual usage,
  optional delegation, mutable current facts, resume and the voluntary adoption doorway.
- **Out-of-Scope**: shared runtime approach policy (`CAP-DLV-project-policy`), generic distribution and projection
  (`CAP-DIST-content-packages`), document formats (`CAP-DOCS-document-model`), the project's build/test tools and
  baseline readiness/activation owned by the separate `sdd-baseline` playbook when installed.
- **Scope Excluded**: another wheel, application framework/scaffold catalog, a runtime process or context parser,
  mandatory role sequence, per-change SDD artifacts, automatic approach switching and reconstructed experiment history.

## 3. Business Rules & Policies

1. **Explicit selection**: WHERE `incubation:core` is selected, sync MUST deploy its catalog-owned assets without
   seeding product context or documents. Test: `packages/devkit-catalog/tests/integration/bundles/test_incubation.py`.
2. **Independent installation**: The incubation bundle MUST install with devkit-docs and devkit-catalog without a
   devkit-spec distribution. Test: `packages/devkit-catalog/tests/e2e/bundles/incubation/test_installed_consumer.py`.
3. **Approach inspection**: WHEN `/incubate` starts product work, the coordinator MUST inspect the common effective
   development approach rather than infer it from bundle selection or installed packages.
4. **Inactive entry**: IF the approach is not incubation, THEN the coordinator MUST stop product work with the shared
   configuration action and obtain user direction before changing approach.
5. **Unreadable policy**: IF policy inspection fails, THEN the coordinator MUST report the actual error and next
   configuration action without performing product work.
6. **Adaptive clarification**: WHEN the next useful action needs a product decision, the coordinator SHOULD reuse
   known answers and ask only the missing decision without requiring a complete backlog, architecture or document set.
7. **Bounded evidence**: WHEN research or an experiment informs implementation, the coordinator MUST distinguish
   observations, assumptions, limitations and the decision informed; an experiment names its write boundary and stop condition.
8. **Representative implementation**: WHEN implementation is retained, the coordinator MUST provide executable run
   and verification instructions for its representative flow.
9. **Truthful verification**: WHEN reporting a check, the coordinator MUST identify actual source/artifact-specific
   execution and limitations; skipped, unavailable or inconclusive evidence remains unverified.
10. **Iteration scope**: WHILE the product goal and constraints hold, the coordinator MAY reconstruct retained code,
    tests and documents without per-change SDD Units, approvals, envelopes or immutable experiment history.
11. **Changed direction**: IF the goal or constraints change, THEN the coordinator MUST obtain user direction before
    dependent work.
12. **Optional support**: WHERE a separable question or usage scope warrants delegation, the coordinator MAY invoke
    the corresponding support role; no iteration requires all roles.
13. **Role boundaries**: WHEN a role is invoked, the coordinator MUST supply one goal, absolute boundaries,
    source/artifact identity, permitted actions and expected output, then verify its actual return before fold-back.
14. **Current context ownership**: WHEN retained resume facts change or work pauses, the coordinator MUST update
    project-owned `.devkit/incubation.md`; roles return evidence instead of editing that file.
15. **Context preservation**: WHEN sync, removal or re-selection runs, sync MUST preserve existing project-owned
    context bytes. Test: `packages/devkit-catalog/tests/integration/bundles/test_incubation.py`.
16. **Voluntary adoption**: WHEN the user explicitly requests SDD adoption, the coordinator MUST leave activation to
    the separately available `sdd-baseline` procedure after explaining spec-asset preparation while incubation remains active.

Discovery, evidence, iteration and resume are semantic agent contracts. The recorded bounded app exercises in
`SPEC-incubation-development-guidance` supply observed examples; token assertions alone do not prove them.
Independent project checks and existing retained SDD artifact protections remain applicable.

## 4. Interfaces & Data Contracts

### Distribution and entry

Install devkit-docs and devkit-catalog, then explicitly select `uv run devkit add incubation` (`incubation:core`).
The bundle owns its constitution, guidance pointer, `/incubate`, conditional skill references, three subagent
contracts and `.devkit/managed/incubation/templates/current-context.md`. Selecting assets changes no approach.

`uv run devkit config show` exposes `configuration.development.approach` and `sources["development.approach"]`.
The entry requires `incubation`; invalid policy propagates `DEVELOPMENT_CONFIG_INVALID`, exit 2, from the command.
A valid SDD result produces a guidance-level stop with the shared `[development] approach = "incubation"` action,
not a new command error code. Read `get-context incubation` once per agent context and `get-context docs` before
relevant document work. No incubation-specific CLI/API or lifecycle workflow is added.

### Optional roles

| Role | Result | Source and Git boundary |
| --- | --- | --- |
| `product-clarifier` | Candidate users/problems, alternatives and missing questions; no invented user decisions | Read-only; no index or HEAD change |
| `incubation-researcher` | Decision-specific evidence or explicitly bounded experiment, actual paths/commands and limits | Read-only by default; assigned prototype writes only; no commits |
| `usage-reviewer` | Expected versus observed representative usage, evidence and failure conditions | Read-only product source; assigned test-data interactions only; no commits |

A result contains status (`completed`, `needs_input` or `failed`), summary, source/artifact identity, observations
with evidence/failure conditions, recommendation, assumptions and unverified areas. An experiment additionally
returns changed paths, commands and outcomes. The coordinator reports emulated boundaries as emulated and checks
the actual diff; role availability grants no product decision or publication authority. No SDD envelope is required.

### Current context

`.devkit/incubation.md` is mutable project-owned Markdown, not managed/transient state, a Unit or an immutable log.
The template contains current goal/users/constraints/flow, retained user decisions versus implementation choices
and assumptions, run/check commands and identity-bound observed evidence, limitations/questions and next useful
action. It has no document ID, lifecycle status, parser or governance schema. Keep pointers to retained current
documents when useful; remove superseded experiments that no longer inform the product. A later session rechecks
relevant identities and affected evidence rather than trusting stale context or reconstructing the conversation.
