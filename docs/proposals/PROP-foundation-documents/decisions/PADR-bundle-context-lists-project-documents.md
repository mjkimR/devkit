---
id: PADR-bundle-context-lists-project-documents
title: List project context documents in bundle context
summary: For a bundle whose agents need project documents listed in every context, we let its manifest declare a workspace directory whose Markdown titles and summaries devkit get-context returns at run time, to keep devkit-dist SDD-agnostic and the list current, accepting a new manifest field.
proposal: PROP-foundation-documents
status: draft
created_at: 2026-10-26
---

# [PADR-bundle-context-lists-project-documents] List project context documents in bundle context

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Steering documents must be listed in every agent context, current at run time (`user`). `devkit get-context
<bundle>` already runs once per agent context and returns the constitution and instruction headers, but it is part of
`devkit-dist`, which stays SDD-agnostic (`ARCH-05-1-containers` section 2.4). Options and costs are compared in
`materials/steering-design.md` D1.

## 2. Decision Drivers

- The list is current at run time, without a sync.
- `devkit-dist` holds no SDD concept or path.
- Loading a context never fails because of a project document.

## 3. Considered Options

### Option 1: A manifest-declared context document directory (Selected)
- **Overview**: a bundle's `bundle.toml` names one workspace directory; `get-context` adds `documents` (`path`,
  `title`, `summary` of each Markdown file directly in it) to its result, read under the shared project lock.
- **Pros**: data, not code; any bundle can use it; the list is read at run time.
- **Cons**: a new manifest field and result key.

### Option 2: An entry-point context provider
- **Overview**: `devkit-spec` registers a provider that `get-context` calls.
- **Pros**: arbitrary content.
- **Cons**: a plugin contract and package code running inside every context load, beyond the need.

### Option 3: A literal `docs/steering` in `devkit-dist`
- **Pros**: smallest change.
- **Cons**: puts an SDD path into the SDD-agnostic package.

### Option 4: Sync renders the list into the constitution
- **Pros**: no get-context change.
- **Cons**: stale between syncs; the `user` chose run-time reading.

## 4. Decision Outcome

We decided to adopt **Option 1**: it reads at run time (driver 1) from a directory the bundle names, so `devkit-dist`
knows no steering path (driver 2). A file with malformed frontmatter or a missing `title` or `summary` is listed with
`null` for the missing value, never an error (driver 3); `RULE-steering-documents` reports it. The `spec` bundle
declares `docs/steering`.

## 5. Consequences

- **Positive**: one mechanism for any bundle that needs project documents in context.
- **Negative / Risks**: a large directory raises every context's cost; the spec rule caps it, but `devkit-dist`
  itself enforces no cap.
- **Follow-ups**: none.

Read rules: the field follows the seeded `target` grammar; get-context reads the declaration from the
receipt-verified managed `bundle.toml`; it lists only regular, non-symlink `*.md` files other than `README.md` directly
inside a non-symlinked directory, reading at most a 4096-byte header prefix; `documents` is always present (`[]` when
undeclared or absent), with absolute `path`, sorted. `CAP-DIST-workspace-ownership` is amended so a declared context
directory may list seeded files.

## 6. Confirmation

Tests under `packages/devkit-dist/tests/` for the manifest field's validation and for `documents` in the
`get-context` result (present, undeclared, absent directory, symlinked directory or file, non-regular entry,
non-UTF-8, oversized file, malformed frontmatter, non-string values, order); `CAP-DIST-manifest-spec` and
`CAP-DIST-context-and-playbooks` document both.
