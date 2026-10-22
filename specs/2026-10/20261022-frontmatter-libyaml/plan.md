---
id: PLAN-frontmatter-libyaml
spec: SPEC-frontmatter-libyaml
---

# Technical Plan: `SPEC-frontmatter-libyaml`

## 1. Constitution & Invariant Review

None. Preserve the shared grammar and error behavior of `CAP-DOCS-document-model`. No architectural change or
dependency is required. Development effort is medium.

## 2. Architecture Overview & Impact

Only devkit-core's frontmatter implementation changes. Document consumers retain the same public functions and
FrontmatterError mapping. The document memo already fingerprints this module and libyaml availability.

## 3. Component & Interface Design

Build strict loaders with the existing duplicate-key validation for Python and optional C bases. Inspect C parser
events to detect syntax nesting above an internal routing threshold, then use the Python loader for those inputs.
The threshold selects a parser; it is not an input rejection limit. Alias events do not increase syntax depth.
For ordinary headers use the strict C loader. If C parsing or construction raises a YAML, value or recursion error,
retry with the strict Python loader to retain the original diagnostics. Without CSafeLoader use Python directly.
Keep load_header, locate and parse signatures unchanged.

## 5. Error Handling & Edge Cases

Exercise duplicate resolved keys at every nesting level, merge overrides, recursive aliases, malformed syntax,
impossible dates, non-mapping headers and non-string keys. Check deep syntax that Python accepts as well as syntax
it rejects. Compare full error messages, not only exception classes.

## 6. Verification & Test Plan

AC-01 through AC-04: extend the existing frontmatter tests across both parser routes and simulate absent
CSafeLoader at module import. AC-05: preload the workspace headers; alternate Python and guarded C runs nine times,
compare values and record medians. The baseline runs in this worktree, so no second Git checkout is needed.
Run just lint-check core, just check core, just test-affected and devkit rules check --ci --base main.
Build the core wheel and run an independent code review. Update the document capability and resolve the source
feedback with the verification evidence.
