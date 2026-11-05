---
id: PROP-multi-runtime-project-harness
title: Deferred Runtime Discovery and External Rule Integration
summary: "Defers runtime discovery and external rule integration until pilot evidence shows a need beyond existing command gates and onboarding guidance."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: harness/
priority: low                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high
dev_effort: high                      # low | medium | high
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit/src/devkit_agt/features/gate/
    - packages/devkit-cli/src/devkit_cli/
    - docs/capabilities/harness/
    - docs/capabilities/gate/
    - docs/usecases/
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-multi-runtime-project-harness] Deferred Runtime Discovery and External Rule Integration

## 1. Background & Disposition

This draft is deferred. CAP-GATE-commit-gates already runs arbitrary project shell commands from the repository
root, and the installation guide covers non-Python repositories. Native command execution does not require a
RuntimeAdapter. The concrete onboarding examples are owned by PROP-justfile-standard-templates.

The pilot concerns do not yet justify built-in adapters for Python, Node, Go, Rust and Godot, composite runtime
detection, or a new external-rule protocol. No implementation or toolchain installation is planned here.

## 2. Remaining Questions

- Do repeated pilot failures remain after explicit native commands, their working directories and prerequisites
  are documented? Capture the repository, command, failure and why guidance cannot solve it.
- Does a consumer need individual external linter findings inside devkit rule results, rather than a command's
  pass/fail result in a commit gate? Capture the required finding fields and staged-file behavior.

Runtime discovery and external-rule integration are separate needs. Re-scope this draft to the evidenced need
before Planning; do not accept the original combined framework by default.

## 3. Restart Conditions & Acceptance Checks

Resume runtime discovery only when repeated concrete failures establish a benefit beyond setup examples.
A future proposal must identify the supported stack and verify diagnostics for its actual missing prerequisites
without guessing a test framework or installing toolchains.

Resume external-rule integration only when a consumer requires structured findings that the existing gate
cannot provide. A future proposal must define and test its output contract, failure and timeout behavior,
and interaction with staged-file evaluation.

## 4. Excluded Scope

- No runtime adapter ABC, built-in language adapter suite or automatic gate configuration.
- No toolchain installer or multi-runtime doctor expansion.
- No external JSON rule provider or linter-format converter without the finding-level use case above.
- No requirement for PROP-justfile-standard-templates to wait for this draft.
