---
id: PLAN-affected-test-granularity
spec: SPEC-affected-test-granularity
---

# Technical Plan: `SPEC-affected-test-granularity`

## Constitution and invariant review

None: this implements `ADR-select-tests-by-file-with-finer-spec-dependency-nodes` within
`ADR-nightly-ci-verification`. Existing full fallbacks and the MCP runtime mapping remain.

## Components and interfaces

`scripts/affected_tests.py` retains Selection and CLI contracts. Each test file becomes a group.
An inventory maps devkit_spec module names to files; other production owners remain coarse.
Exact module dependencies include executed initializers. A separate broad owner marker represents opaque/root
consumers without joining unrelated fine modules. Reverse traversal propagates changes through source imports.
ASTs are cached once per run. Local helper traversal uses a visited set per closure to terminate cycles without
caching incomplete closures. Ancestor conftests contribute dependencies. Parse/inventory failure selects full.
Known dynamic CLI, bundle and source-tree consumers retain explicit broad edges; no runtime import is executed.

## Failure modes

Missing changed fine modules, unreadable syntax and ambiguous source modules select full. Static import uncertainty
widens to the owner. A missing foreign module remains external unless a known local helper or owner applies.
No persisted state, migration or production package changes are required.

## Verification

Independent fixture tests assert selected and excluded files for imports, reexports, initializers, helper cycles,
conftests, root consumers and unsafe paths. Existing selector regression tests retain CLI, frontend, data, full
trigger and Git coverage. Same-revision baseline/new file sets, parametrized collection counts and selector timings
cover six devkit areas and scope/documents/proposals. Run focused pytest, lint/type checks, just test-affected,
governance checks, mandatory independent code review and separate reconcile verification.
