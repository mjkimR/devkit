---
id: PADR-adaptive-dev-approach-name
title: Name the non-SDD development approach adaptive-dev
summary: For the development approach that iterates without per-change SDD records, we name the approach value and its catalog bundle adaptive-dev, to give each development concept one unambiguous name beside sdd, accepting a breaking rename of a consumer-facing setting and bundle.
proposal: PROP-rename-incubation-to-adaptive-dev
status: draft
created_at: 2026-10-30
---

# [PADR-adaptive-dev-approach-name] Name the non-SDD development approach adaptive-dev

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

"Incubation" names two concepts: the non-SDD development approach with its catalog bundle
(`[development] approach = "incubation"`, `CAP-DLV-idea-incubation`) and the SDD proposal lifecycle
(`CAP-DLV-proposal-incubation`). With both installed, a request to "incubate" an idea does not identify which one
the user means. The approach value and the bundle name are consumer-facing: a consumer writes them in
`.devkit/config.toml`.

## 2. Decision Drivers

- One name per concept, so no current setting, bundle, entry or document uses "incubation".
- The name pairs with spec-driven development (`sdd`) as the other development approach.
- The name holds for a product that stays in the approach indefinitely; SDD adoption is optional
  (`CAP-DLV-incubation-sdd-baseline`).
- The name does not read as adapting devkit to a project.

## 3. Considered Options

1. **Keep `incubation`**: no migration; the ambiguity stays.
2. **`project-incubation`**: keeps the ambiguous word.
3. **`project-bootstrap`**: reads as a temporary phase, while the approach may remain a project's approach.
4. **`project-adaptive`**: reads as "adapts to the project"; the `project-` prefix distinguishes nothing.
5. **`adaptive`**: a bare adjective that does not name development.
6. **`adaptive-dev` (chosen)**.

## 4. Decision Outcome

Option 6, decided by the user.

- The approach value is `[development] approach = "adaptive-dev"` beside `"sdd"`.
- The catalog bundle is `adaptive-dev` (entry point `adaptive-dev = "devkit_catalog.adaptive_dev"`).
- Documents call the approach "adaptive development"; identifiers and commands use `adaptive-dev`.
- The approach contract is unchanged: a product may stay in adaptive development, and SDD adoption stays the
  explicit `sdd-baseline` procedure.
- This decision replaces the value set `sdd` and `incubation` in `ADR-own-development-approach-policy-outside-sdd`
  and the bundle, entry and context-file names in `ADR-keep-incubation-guidance-opt-in-and-current-state-based` and
  `ADR-extend-incubation-with-optional-discovery-teams`.
  Each of those ADRs carries a one-line pointer to this decision; their other statements stay in force.

## 5. Consequences

- Positive: "incubation" no longer names the approach, the bundle or its entry.
- Negative: an existing consumer configuration that names `incubation` must change; the migration path is a
  separate decision of this proposal.
- Follow-up: decision records and completed specs that use the old name stay as history and resolve through
  document aliases.
- Risk: a reader of an accepted ADR without the pointer would write the old value, which the working configuration
  refuses.

## 6. Confirmation

- `packages/devkit-dist/tests/integration/features/project/test_development.py` accepts `adaptive-dev` and `sdd`.
- `packages/devkit-catalog/tests/integration/bundles/` selects and projects the `adaptive-dev` bundle.
- `tests/e2e/smoke.sh` lists `adaptive-dev` in the catalog bundle set.
- Review: each replaced ADR carries the pointer.
