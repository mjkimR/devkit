---
id: PLAN-design-document-foundation
spec: SPEC-design-document-foundation
---

# Technical Plan: `SPEC-design-document-foundation`

## 1. Constitution & Invariant Review

`ADR-documentation-ownership-and-linked-design-entries` supplies the accepted direction. Existing
`CAP-DOCS-document-model`, `CAP-DOCS-namespaces`, `CAP-DIST-sync-and-transactions` and
`ARCH-05-2-components` retain identity, namespace, safety and component boundaries. No new feature edge or runtime
change is needed. Review-only semantic ownership and ordinary links do not become invented validators.

## 2. Architecture Overview & Impact

Add the shared ownership capability and clarify the architecture overview. Adapt the retained pilot into a
maintained ID-free transaction entry/detail, reached by one selected capability link. Keep the capability's safety,
recovery and readiness guarantees unchanged. Update generic living-spec/architecture authoring instructions and
ship an optional template through the existing templates asset. Confirm the accepted ADR's restatement traces.

Choose no glossary additions: role definitions belong to the new ownership capability and existing glossary terms
remain adequate. Small designs may use one entry; this mechanism uses one useful detail. Detail size and numeric
content do not decide document ownership. Sources execute behavior; designs explain it.

## 6. Verification & Test Plan

AC-01: compare every preserved routing case and pilot passage ownership against the actual diff.
AC-02: inspect transaction symbols and open every relative link; confirm no design identity.
AC-03: independent reader starts with only transaction capability and original question, recording actual route;
contrast qualitatively with recorded Planning R1/V1 baseline without checking out base.
AC-04: isolated namespace fixture under ignored `.venv/spec-probes/foundation-development`, existing CLI list/search/
resolve/refs plus a fresh reader's route from package source cwd; unrelated namespace and global negative controls.
AC-05: consumer fixture sync of selected docs bundle; inspect delivered instructions/template and no scaffold.
AC-06: `uv run devkit sync --check`, scoped docs/source asset rules, CI rules with `--base main`,
`just test-affected --base 6aaddb58a48aa81c6a0c23417801e9b4542f758a` preserving full fallback, envelope and whitespace checks.
Product lint/type and frontend checks are inapplicable to Markdown-only edits. Run required initial Code Reviewer
and separate Reconcile Reviewer with quiesced snapshots and absolute worktree read scopes. Keep all scratch fixtures
ignored; commit stage boundaries and final records. Host owns integration/post-landing checks.
