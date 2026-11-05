---
id: PLAN-justfile-standard-templates
spec: SPEC-justfile-standard-templates
---

# Technical Plan: SPEC-justfile-standard-templates

## 1. Constitution & Invariant Review

No conflicting invariant or ADR change. CAP-DIST-content-packages owns catalog distribution and
CAP-GATE-commit-gates keeps verification commands project-selected. `cli-tool` retains Python implementation
rules. The catalog bundle adds no runtime code, framework dependency or new feature edge.

## 2. Architecture Overview & Impact

Register `command-design = devkit_catalog.command_design` with an empty initializer and one manifest instruction.
Use a conditional description for creation/configuration/extension tasks and no AGENTS guidance pointer.
Document the bundle in catalog/install recommendations and a capability plus use case. Put native command reuse
and optional recipe examples in the installation guides. Keep existing CI/hook checks explicit.

## 6. Verification & Test Plan

Existing parametrized catalog manifest tests validate entry point, opt-in and version. Add a deployment test for
selection, context discovery and absence of extra projections. Review the instruction against all three creation
scenarios rather than testing exact prose. Run a temporary Node command fixture for the documented native
verification example, `just test-affected`, catalog lint/types and document/asset rules. Do not claim pilot validation.
