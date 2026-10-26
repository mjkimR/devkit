---
id: PADR-localized-handbook-language-exception
title: Localized handbook exception to English-only documentation
summary: For a handbook people read in their own language, we allow non-English text only under handbook/<lang>/ for languages other than en, starting with ko, to keep every other document English, accepting translations that must track the English pages.
proposal: PROP-release-handbook
status: draft
created_at: 2026-10-26
---

# [PADR-localized-handbook-language-exception] Localized handbook exception to English-only documentation

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

`AGENTS.md` requires all documentation, architecture specifications and guide materials in English. No rule enforces
it and no ADR records it. The handbook exists for people, and its first readers include Korean speakers, so it needs
translated pages; without a recorded, bounded exception, non-English text has no defined place in the repository.

## 2. Decision Drivers

- Every agent-facing and Living Spec document stays English.
- People can read the handbook in their language.
- The exception is bounded by path, so a reviewer can tell at a glance whether non-English text is allowed.

## 3. Considered Options

- **en and ko now, exception limited to `handbook/<lang>/` for non-en languages**: serves Korean readers in the
  first handbook; the exception is one path pattern.
- **en only first, ko and the exception later**: no exception yet, but the first handbook misses its Korean readers.
- **Keep the current state** (English only, no handbook translations): contradicts the handbook's purpose.

## 4. Decision Outcome

- The first handbook carries `en` and `ko`. English is the pivot, synthesized from `docs/`; `ko` is translated from
  English.
- Non-English text is allowed only under `handbook/<lang>/` for languages other than `en`. `handbook/en/`,
  `handbook/manifest.json`, `docs/`, `specs/`, guides, READMEs and agent assets stay English.
- Identifiers (commands, error codes, document IDs) are never translated, and Living Spec sources linked from the
  handbook stay untranslated.
- `AGENTS.md` names this exception next to the English-only rule.

## 5. Consequences

- Positive: Korean readers get the handbook; every other document keeps one language.
- Negative: each refresh also translates the stale English pages and needs a review of the translation.
- Follow-up: adding a language adds `handbook/<lang>/`, its `terms.yaml` and a `langs` entry in the manifest, within
  this exception.

## 6. Confirmation

- The handbook script's parity check: every language in `manifest.json` has the English file set and a current
  `translated_from` per page.
- Review only for non-English text outside `handbook/<lang>/`; no rule checks document language.
