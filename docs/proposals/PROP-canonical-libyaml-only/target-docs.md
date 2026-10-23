---
id: PROP-canonical-libyaml-only-target
title: Target Living Spec Structure for PROP-canonical-libyaml-only
status: draft
proposal: PROP-canonical-libyaml-only
created_at: 2026-10-23
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
---

# [Blueprint] PROP-canonical-libyaml-only: Target Living Spec Structure for Require libyaml for consistent YAML parsing

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-canonical-libyaml-only is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

Modify `CAP-DOCS-document-model` to define PyYAML's LibYAML C loader as the required YAML parser, including the
supported installation assumptions, missing-binding failure, parse diagnostics and shared behavior for parsing
frontmatter.

---

## 2. Use Cases Plan (docs/usecases/)

No use case changes are expected unless Planning finds an existing user-visible validation or fixer use case whose
contract must capture the new parse failure.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

No architecture change is expected. Planning will decide whether the parser and deployment choice needs a PADR.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

Update the source `document-writing` instruction with concise, actionable guidance for valid frontmatter YAML, and
update affected CLI validation or fixer behavior to return actionable parse diagnostics. Do not add unrelated YAML
style preferences.

---

## 5. System Before & After Comparison (Before & After)

| As-Is | To-Be |
| --- | --- |
| Frontmatter and YAML call sites may fall back to Python parsing when LibYAML is absent or rejects an input. | In-scope parsing uses `CSafeLoader`; unsupported input and missing C bindings produce explicit failures. |
