---
id: PLAN-post-merge-hygiene
spec: SPEC-post-merge-hygiene
---

# Technical Plan: Post-integration hygiene

## 1. Constitution & Invariant Review

No invariant changes. `CAP-HARN-agent-guidance` keeps seeding opt-in and project-owned; document discovery follows
`CAP-DOCS-document-model`. Core package layering and public interfaces are unchanged.

## 2. Architecture Overview & Impact

- Quote seed frontmatter summaries; extend the existing real sync/package test to verify the document index and
  preservation of existing content.
- Preserve base-only smoke coverage, then install the SDD wheel into that consumer, verify its CLI and seeded IDs,
  and run its rules. Add its explicit wheel installation command to generated release notes.
- Refresh the package README, root package list, CI guide, container/deployment views and relevant guidance contract.
- No new dependencies or migration: already seeded files remain consumer-owned.

## 3. Verification & Test Plan

Run the strengthened package test before the seed fix (Red) and after it (Green). Run workspace lint, types, tests,
consumer smoke and governance rules. Verify documented Git sources with a temporary consumer using a local Git URL
and inspect release-note generation. Independent code review and reconcile verification use medium effort; the
change affects one runtime package plus repository scripts and documentation.
