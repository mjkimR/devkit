---
id: MS-catalog-and-context-scaling
title: Opt-in catalog expansion and bounded context loading at scale
summary: "Expands devkit-catalog with reusable domain and operational bundles while keeping agent context loading bounded as instruction and playbook catalogs grow."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-catalog-and-context-scaling] Opt-in catalog expansion and bounded context loading at scale

## Goal

Advances `ARCH-01-introduction-and-goals` §1.1 (Asset Distribution & Guidance Delivery), §1.8 (Document Search), and §2 (Bounded Context) by expanding `devkit-catalog` (`CAP-DIST-content-packages`) beyond `host-observer` and addressing bounded context exposure as bundle instruction catalogs grow (`ARCH-08-2-resource-taxonomy`, `CAP-DIST-context-and-playbooks`).

## Exit condition

- `devkit-catalog` ships additional opt-in domain governance and operational playbook bundles verified by package and smoke tests, with matching bundle recommendation signals.
- Bundle context loading (`devkit get-context`) preserves full constitution delivery and on-demand instruction bodies while keeping context overhead bounded as bundle instruction counts scale.

## Non-goals

- **Scope Excluded**: Bundles that require new runtime Python code inside `devkit-catalog` (which belong in `devkit-agt`), and automatic playbook triggering without explicit user invocation (`ARCH-08-2-resource-taxonomy`).
