---
id: PLAN-remove-github-milestones
spec: SPEC-remove-github-milestones
---

# Technical Plan: Remove GitHub milestone guidance

## 1. Constitution & Invariant Review

No conflicts. The change implements `ADR-roadmap-in-repository` and preserves
`CAP-DIST-content-packages`: catalog bundles remain opt-in content wheels.

## 2. Components

Delete the github_milestones resource module and entry point. Keep host-observer as the README example and
architecture catalog example. Remove installation questions and recommendations for the obsolete bundle.
Use the existing host-observer smoke lifecycle to preserve catalog opt-in coverage; assert its absence before
selection and assert the catalog's wheel-discovered bundle set is exactly host-observer.
No dependencies, schema changes, migrations or external tracker operations are needed.

## 3. Verification

Run catalog lint, type checks and existing bundle tests; build and inspect the catalog wheel; run consumer smoke
and repository governance checks. Run existing milestone tests to verify preservation. Review the full diff and
search active sources for obsolete bundle references. Development effort is low: this is a single-package content deletion.
