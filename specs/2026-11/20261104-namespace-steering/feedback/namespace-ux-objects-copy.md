---
id: FB-namespace-ux-objects-copy
title: A registered namespace has no UX object register beside its steering directory
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-namespace-ux-objects-copy] A registered namespace has no UX object register beside its steering directory

Deferred work of `SPEC-namespace-steering` (`ADR-namespace-steering-directories`, Follow-ups), outside the completed
scope of `MS-monorepo-namespace-support`. This feedback remains open; reconsider the namespace-local register when
a real namespace UX document demonstrates the need. The root register continues to serve namespaces meanwhile.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ux-writing` names one root register, `docs/steering/ux-objects.md`; a registered
  namespace's `docs/packages/<name>/steering/` now holds its background, but its UX documents still register their
  objects in the root file, and `RULE-ux-links` reads the root register only.
- **Proposed Procedure**: let a namespace keep `docs/packages/<name>/steering/ux-objects.md` for its own UX
  documents, read together with the root register by `ux-writing` and the UX rules, under the namespace steering
  contract (listed in that package's context).
- **Expected Benefit**: a monorepo of independent products keeps each product's UI vocabulary with that product;
  the root register stays bounded.
- **Cost & Risk**: two registers to search for a shared object; the UX rules gain a namespace lookup.
- **Attempted**: hypothesis; declared a non-goal of `SPEC-namespace-steering`.

## Diagnostic Details

- **Reproduction**: not applicable (a design follow-up).
- **Expected / Actual**: not applicable.
- **Versions**: devkit workspace at the Development branch of `SPEC-namespace-steering`.
- **Conditions**: a workspace with `[[tool.docs.namespaces]]` and UX documents under `docs/packages/<name>/ux/`.
- **Workarounds Attempted**: not attempted; the root register serves every namespace today.
- **Related Assets**: `ux-writing`, `RULE-ux-links`, `docs/steering/ux-objects.md`, `MS-monorepo-namespace-support`.

## Evidence

```text
ADR-namespace-steering-directories, section 5 Follow-ups: "A namespace copy of docs/steering/ux-objects.md for the
UX rules work of MS-monorepo-namespace-support." SPEC-namespace-steering Non-Goals exclude it.
```
