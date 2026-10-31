---
id: PLAN-decision-supersession-check
spec: SPEC-decision-supersession-check
---

# Technical Plan: `SPEC-decision-supersession-check`

## 1. Constitution & Invariant Review

No architectural invariant changes. `ARCH-05-2-components` assigns document rules to the governance feature and
rule tests to their bundle directory. Existing governance-to-documents imports suffice. The contract change adds
an enforcing check to `CAP-DOCS-document-model` without changing whole or partial replacement semantics.

## 2. Architecture Overview & Impact

Add RULE-decision-supersession as a linter/error rule in the docs core preset. Read indexed ADR frontmatter and
visible partial-pointer prose through the snapshot cache. Preserve the index's relation graph and parser.
Check accepted and historical ADR records; exclude PADRs and non-decisions. No autofix is provided.

## 3. Component & Interface Design

A governance usecase module owns a BaseRule subclass with typed check(ctx) returning list[Violation]. A bundle
wrapper, guide and deployed tests expose it. Deterministic findings use the stable rule ID, source field lines
and remediation. Uniquely resolving aliases normalize both metadata and partial pointers before comparison.
Scalar superseded_by and scalar/list supersedes are accepted; malformed fields report rather than crash.

## 6. Verification & Test Plan

Bundle tests cover AC-01 through AC-04, including malformed metadata, ambiguity, canonical aliases, masking,
targeting, exclusion and fix immutability. Run just lint-check docs, just check docs, just test-affected,
devkit rules test RULE-decision-supersession, sync --check and full rules check. Reuse passing tests unless review
changes their inputs. Compare the seeded invalid relationship with the baseline absence of this checker.
