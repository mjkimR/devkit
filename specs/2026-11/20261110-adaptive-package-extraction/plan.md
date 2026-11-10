---
id: PLAN-adaptive-package-extraction
spec: SPEC-adaptive-package-extraction
---

# Technical Plan: `SPEC-adaptive-package-extraction`

## 1. Constitution & Invariant Review

`ADR-adaptive-dev-distribution` partially supersedes ownership only. `ARCH-05-2-components` keeps content packages dependency-free; no features or cross-feature edges are added. The bundle tree must retain its Git identity. `ARCH-07-deployment` already requires unchanged bundles to retain their versions.

## 2. Architecture Overview & Impact

Move adaptive-dev into `devkit_adaptive.bundles.adaptive_dev`, with three docstring-only initializers and a single `devkit.bundles` registration. Move six test/support files to the new package. The catalog drops its registration and adds only a development dependency for the research role-conflict test. Root configuration, short names, citation coverage and smoke install wiring follow the owner. No runtime dependencies or commands are added.

## 3. Component & Interface Design

The entry point is `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"`; dependencies remain empty. Release preparation first checks the same package, then finds a baseline bundle with the same name across baseline packages. Fingerprint equality retains its prior version; changed content receives the release version.

## 6. Verification & Test Plan

AC-01–04: package metadata assertion, moved integration tests, installed consumer without spec/catalog, catalog tests and bundle tree identity. AC-08: unchanged and changed moved-bundle release fixtures. AC-06: `uv lock --check`, `just lint-check`, `just check`, `just rules-check`, `just test adaptive`, `just test catalog`, `just test dev`, `just test-dist`, `just test-affected` and `just smoke`. Required unit/integration checks are synchronous; selected E2E run at a committed fixed SHA through `devkit exec`. AC-07: Living Spec comparison and stale-path search. The Host measured baseline smoke failure at `9ab4f8e`; the planned catalog assertion update addresses it. Final landed checks belong to the Host.
