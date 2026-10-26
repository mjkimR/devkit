---
id: PADR-steering-documents-directory
title: Keep project background in one flat steering directory
summary: For project-wide background without a place in the Living Spec, we keep ID-free steering documents in one flat docs/steering/ directory, one file per topic, and move the glossary into it, to give background one known place, accepting about twenty path edits and a new seed path.
proposal: PROP-foundation-documents
status: draft
created_at: 2026-10-26
---

# [PADR-steering-documents-directory] Keep project background in one flat steering directory

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Project-wide background (product purpose, tone, style direction, a domain overview) has no place in the Living Spec:
written into capabilities it bends the contract shape, written into materials it loses its standing as current. The
glossary is the only such document and sits alone at `docs/glossary.md`. "Foundation" was the draft's name, but it
already names devkit's lowest code layer (`devkit-core`, `ARCH-05-1-containers`).

## 2. Decision Drivers

- One known place per repository that agents and people find without search.
- No new document kind, ID or relation fields.
- A name free of existing repository vocabulary.

## 3. Considered Options

### Option 1: One flat `docs/steering/` directory, glossary inside (Selected)
- **Overview**: one Markdown file per topic, ID-free, with `title` and `summary` frontmatter; `glossary.md` and
  `glossary.yaml` move in; no subdirectories and no namespace copy.
- **Pros**: one place; the glossary is its first member; nothing enters the document index.
- **Cons**: about twenty literal glossary paths change (`materials/spike-findings.md` F3); existing consumers of the
  seed receive a new glossary path.

### Option 2: ID-free background files at the existing docs root
- **Overview**: no new directory; a pointer names each file.
- **Pros**: smallest change; the glossary stays.
- **Cons**: background mixes with `docs/README.md` and other root files; no directory to list.

### Option 3: A per-namespace copy as well
- **Overview**: `docs/packages/<name>/steering/` beside the root directory.
- **Pros**: package-specific background.
- **Cons**: no registered namespace needs it today; multiplies the always-loaded list.

## 4. Decision Outcome

We decided to adopt **Option 1** (`user`): the directory gives background one known place (driver 1) as ID-free
files (driver 2), and "steering" collides with no existing term (driver 3). Package glossaries stay at
`docs/packages/<name>/glossary.md`.

## 5. Consequences

- **Positive**: background has a place; the glossary gains the row **Steering document** (Avoid: foundation,
  background).
- **Negative / Risks**: a missed glossary path fails silently; each is an acceptance item with a test. Existing
  consumers move their glossary by hand (no migration, `AGENTS.md` Compatibility).
- **Follow-ups**: a namespace copy when a registered namespace needs package background that its package glossary
  cannot hold.

## 6. Confirmation

`RULE-steering-documents` (shape, frontmatter, caps); tests under `packages/devkit-spec/tests/` that the Owner check
and synonym expansion read `docs/steering/` and no longer `docs/glossary.md`; the handbook script tests in
`tools/devkit-dev/tests/integration/test_handbook_script.py` for both layouts.
