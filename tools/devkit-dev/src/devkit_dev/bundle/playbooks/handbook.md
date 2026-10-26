---
name: handbook
description: Refresh the release handbook under handbook/ (en, ko) from the Living Spec during release preparation, verify it and record the human review; run only when the user requests a refresh.
---

# Handbook refresh

Run only when the user explicitly requests a handbook refresh (`devkit-playbook` or
`devkit playbook get devkit-dev/handbook`). There is no cadence: a release without a request keeps the previous
handbook. The contract is `CAP-DLV-release-handbook`; the handbook is a derived view, never a source of truth, and
no Living Spec document changes for it.

## 1. Preconditions

1. The release is in preparation: `VERSION` already names the upcoming release, and the `just version-sync` metadata
   commit and the tag come after this playbook. A refresh started for one version and released under another counts
   as no refresh at release.
2. `docs/` has no uncommitted change (`git status --short -- docs`); the handbook describes `HEAD`.
3. Optionally preview first: `just handbook generate --preview` writes `dist/handbook-preview/` (untracked) and
   `just handbook verify --preview` checks it; neither touches `handbook/`.

## 2. Find the work

Run `just handbook status`. It reports:

- `HANDBOOK_STALE`: an English page whose cited sources changed;
- `HANDBOOK_TRANSLATION_STALE`: a translated page whose English narrative changed;
- `HANDBOOK_GAP`: a use case or capability no English page cites;
- `HANDBOOK_PARITY`: a page missing from, or extra in, a language;
- `HANDBOOK_TERM_MISSING`: a glossary term without a rendering in `handbook/<lang>/terms.yaml`.

On the first refresh there is no `handbook/` yet: every use case and capability is a gap.

## 3. Write the English pages

Edit only stale pages, gap pages and pages the user names; leave fresh pages as they are.

- Layout: `en/README.md` (what devkit is, the overall model, where to start), `en/concepts.md`, one
  `en/journeys/<slug>.md` per use case and one `en/areas/<area>.md` per capability area. `decisions.md`,
  `changes.md` and `glossary.md` are generated; never edit them.
- Read each cited source at `HEAD` and reorganize it by user journey and concept; do not copy contract text.
  Use plain descriptive wording: no capitalized normative keywords outside code. Link detail to its source instead of
  restating it.
- List every cited document ID under the frontmatter `sources` key (values may be empty). Never add `id:`.
- Insert generated sections where they help: `<!-- handbook:generated toc -->`, `usecases` or `capabilities`, each
  closed by `<!-- /handbook:generated -->`. Text inside them is replaced on every run.
- Link a source as `https://github.com/<owner>/<repo>/blob/<tag>/<path>` with the tag the manifest will name
  (`v` plus `VERSION`); link other handbook pages relatively.
- Run `just handbook stamp en/<path>` for each page you wrote or reviewed as current.

## 4. Translate

For every language in the manifest other than `en` (`ko` first):

- Translate each English page you changed into the same relative path; keep identifiers (commands, error codes,
  document IDs, paths) untranslated and give the English term on a term's first use.
- Use `handbook/<lang>/terms.yaml` for every glossary term; add the missing renderings first.
- Mark each source link as an English original; never translate a Living Spec source.
- Run `just handbook stamp <lang>/<path>` for each translated page.

## 5. Generate and verify

1. `just handbook generate`: writes `handbook/manifest.json` (tag `v` plus `VERSION`, source commit `HEAD`), the
   provenance header of every page, the generated sections and the generated pages.
2. `just handbook verify`: every finding is a `[HANDBOOK_INVALID: page=... line=... code=...]` line. Fix the page,
   stamp it again when its narrative or sources changed, then rerun generate and verify until it prints
   `[HANDBOOK_VERIFIED: ...]`.
3. `just rules-check handbook/` stays clean.

## 6. Human review and commit

1. Ask the user to review each refreshed page against its cited sources and each translation against its English
   page. Contradictions with the Living Spec are found only here.
2. Record the review in the completion report: the pages reviewed, the reviewer, the outcome and any page left out.
   A page that fails review is fixed and verified again before the commit.
3. Commit `handbook/` alone, before the `just version-sync` metadata commit and the tag. Do not change `docs/`
   after generating: `scripts/release.sh` fails a release whose tag equals the manifest tag when `docs/` differs
   from the manifest source commit or verification fails.

Finish by naming the manifest tag and source commit, the refreshed pages per language, the verification result and
the review outcome.
