---
id: PLAN-incubation-development-guidance
spec: SPEC-incubation-development-guidance
---

# Technical Plan: Incubation development guidance

## 1. Constitution & Invariant Review

The accepted catalog ownership decision aligns with `ARCH-05-2-components`: a content-only package keeps its
bundle-only layout. No new runtime behavior or dependency enters catalog. The selected shared approach remains
owned by the policy feature; this change adds no parser, CLI, workflow or governance rule.

## 2. Architecture Overview & Impact

Add `devkit_catalog.incubation/bundle/` and one devkit.bundles entry point. Explicit selection deploys the entry,
three roles, a constitution/pointer and a context template. Package metadata and resource inventory tests exercise
ownership. Shared current-state docs and guides are reflected only after the policy base is incorporated.

## 3. Component & Interface Design

- `incubation:core`: opt-in, default preset core, no auto_select flag and no seeded product files.
- `skills/incubate/SKILL.md`: checks the common approach, reads current context, routes the next useful action.
- Conditional references cover discovery, bounded evidence/implementation, optional delegation and resume/adoption.
- `subagents/{product-clarifier,incubation-researcher,usage-reviewer}.md`: payload/result and read/write/Git contracts.
- `templates/current-context.md`: mutable current facts, not a Unit, transcript or managed state writer.
- `AGENTS.md` and guidance pointer: approach-aware entry without redirecting SDD projects.

The common inspection command is `uv run devkit config show`; its effective value is `configuration.development.approach`, with
`sources["development.approach"]` describing its source. Guidance consumes that interface rather than adding a second configuration reader.

## 4. Storage & State Management

The coordinator creates `.devkit/incubation.md` only when useful. Sync owns only the pristine template in managed
storage and never creates, rewrites or deletes current context. Roles return evidence for coordinator fold-back.

## 5. Error Handling & Edge Cases

Unreadable or non-incubation approach stops product actions with the next shared-config action. Missing current
context starts discovery from available facts. Stale source-specific evidence is rechecked only where affected.
An explicit adoption request prepares spec assets while approach remains incubation, then routes to sdd-baseline
when delivered; the baseline playbook owns readiness/activation/recovery.

## 6. Verification & Test Plan

- AC-01/AC-05: real manifest/sync/projection/selection round-trip and context byte preservation; final built-wheel docs+catalog consumer without spec.
- AC-02/AC-03/AC-04/AC-05: labelled synthetic scenario inputs, executable representative app and fresh-context resume; optional isolated roles when useful.
- AC-06: actual common-policy mismatch/incubation consumer scenarios after policy implementation, plus asset wording/ownership checks.
- `just lint-check catalog`, `just check catalog`, catalog integration tests and `just test-affected` with full fallback.
- Run source sync check; incubation is unselected in this development repository, so it produces no tracked projection changes.
- Independent medium code review and reconcile verification follow full implementation. Final verification covers the whole guidance feature and excludes separately reviewed Host-owned policy changes.
