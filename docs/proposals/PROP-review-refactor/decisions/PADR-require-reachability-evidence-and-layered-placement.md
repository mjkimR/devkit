---
id: PADR-require-reachability-evidence-and-layered-placement
title: Require reachability evidence and layered placement for consolidations
summary: For review-refactor consolidations and removals, we require static and dynamic reachability evidence, verification before and after, and placement at the lowest common owner under declared layering, to keep behavior and layers intact, accepting extra evidence per change.
proposal: PROP-review-refactor
status: draft
created_at: 2026-10-26
---

# [PADR-require-reachability-evidence-and-layered-placement] Require reachability evidence and layered placement for consolidations

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Each behavior-preserving consolidation or removal needs an acceptance bar. Dead-code and clone tools give textual
candidates only and miss dynamic dispatch such as entry points and plugin registries, and a passing test suite proves
nothing for paths it does not exercise. Shortening guidance can remove constraints that change agent behavior.
A consolidated helper placed in the wrong module breaks the target repository's layer direction or grows a catch-all
module; in devkit, package-level `utils` and `base` are created only when needed and `devkit_core` never imports
application packages.

## 2. Decision Drivers

- A removed or merged path that is still reached is caught before the change lands.
- Evidence cost follows missing coverage, not a fixed ritual, so the reduction goal is not offset by new test volume.
- Guidance reductions keep every operational constraint they carry.
- Consolidation respects the target repository's declared layering and dependency direction.

## 3. Considered Options

- **Preservation evidence**: reachability (static plus dynamic reach) with verification before and after and a
  characterization test only where coverage is missing (medium cost); a characterization test before every change
  (high cost, adds test volume against the reduction goal); existing verification passing (untested paths pass
  trivially).
- **Helper placement**: the lowest common owner under declared layering, with a new cross-package or foundation
  module as a decision (judgment on what is generic); always a common `utils` in the nearest shared package (breaks
  layer direction, catch-all module); existing shared modules only (blocks most consolidations the `user`
  direction asks for).

## 4. Decision Outcome

- Every consolidation or removal records reachability evidence covering static references and the repository's
  dynamic reach: entry points, plugin registries, configuration, documentation and string dispatch.
- The repository's relevant verification passes before and after the change, with both results recorded.
- A characterization test is added only when no existing test exercises every merged caller, so tests are added
  only where coverage is missing.
- A guidance change records a retained-constraint map: each constraint of the removed or merged text and where it
  remains. When the removal relies on a behavioral check, it also records a representative-task run with and without
  the text.
- A consolidated helper lives at the lowest common owner every caller may already depend on under the target
  repository's declared layering. A new cross-package or foundation module, or a repository without declared
  layering, becomes a decision in the round. In devkit the order is feature-local first, then package-level `utils`
  (technical helpers) or `base` (contracts), then `devkit_core` only for generic primitives with no application
  dependency.

## 5. Consequences

- Positive: still-reached paths and dropped constraints are caught per change; helpers do not invert layers.
- Negative: each change carries a reachability record and two verification results; guidance changes carry a
  constraint map.
- Risk: dynamic reach the repository does not declare can still be missed; the record names what was searched, so a
  miss is traceable.
- Follow-up: none.

## 6. Confirmation

- Spec-review checklist of the Development maps each evidence part and the placement order to a playbook section.
- Fixture exercise records the reachability evidence, before-and-after verification output and the helper's
  placement for its consolidation, helper fold and removal (proposal section 3).
