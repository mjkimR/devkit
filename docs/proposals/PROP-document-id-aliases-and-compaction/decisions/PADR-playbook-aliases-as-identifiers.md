---
id: PADR-playbook-aliases-as-identifiers
title: Playbook aliases as identifiers
summary: A playbook's aliases field stops being search keywords and declares previous or alternate identifiers of the playbook under the same aliases specification as Living Spec documents; playbook search ranks name and description only.
proposal: PROP-document-id-aliases-and-compaction
status: draft
created_at: 2026-10-22
---

# [PADR-playbook-aliases-as-identifiers] Playbook aliases as identifiers

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

A playbook's optional `aliases` frontmatter array holds English search keywords that `devkit playbook search`
indexes beside `name` and `description` (`CAP-DIST-context-and-playbooks`). Living Spec documents gain an `aliases`
field with another meaning: previous or alternate identifiers (`PADR-document-id-aliases`). One field name with two
meanings in one toolkit misleads authors and agents. The playbooks in the devkit-spec, devkit-agt, devkit-catalog
and devkit-starter bundles use the keyword form today.

## 2. Decision Drivers

- One meaning for `aliases` across devkit: an identifier, never a keyword.
- Search quality must not depend on a keyword list: hybrid ranking over `name` and `description` already carries the
  meaning, and the description can absorb any phrase worth keeping.
- No external consumers exist, so the format changes in place without a migration path or a deprecated reader.

## 3. Considered Options

1. **Keep keyword aliases** and give document identifiers another field name: two concepts stay, one is renamed.
2. **Rename the playbook keyword field** (for example `keywords`): keeps the keyword mechanism under a new name.
3. **Unify under the identifier meaning (chosen)**: the keyword mechanism is removed.

## 4. Decision Outcome

Option 3, decided by the user.

- A playbook's `aliases` declares previous or alternate identifiers of that playbook, validated as identifiers
  rather than free English text. What exactly a playbook alias identifies is the open Planning question
  `q1` of `envelopes/worker-02.yaml`; the recommended answer is a previous manifest asset ID in the same bundle, so
  `devkit playbook get <bundle>/<alias>` returns the canonical playbook and reports the alias it was reached through.
- Aliases are unique against the bundle's playbook IDs and the other playbooks' aliases, checked when the bundle
  manifest is validated.
- `devkit playbook search` indexes only `name` and `description`; aliases are not ranked.
- The bundled playbooks drop their keyword lists, moving any phrase worth keeping into the description.

## 5. Consequences

- Breaking change to the playbook asset format, made in place: a keyword list that is not a valid identifier list is
  refused at bundle validation.
- `CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`, `CAP-SRCH-document-search` (the metadata example),
  the projected playbook skill text and the bundled playbooks change with it.
