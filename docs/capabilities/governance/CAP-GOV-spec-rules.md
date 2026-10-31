---
id: CAP-GOV-spec-rules
title: Spec Governance Rules
summary: "Document and SDD lifecycle governance, milestone status/location validation, snapshot targeting and safe fixes, including ADR supersession consistency, steering and glossary alias repairs, lifecycle omissions during adaptive development and retained workflow ownership checks."
area: governance
status: active
usecases:
  - UC-keep-the-living-spec-consistent
  - UC-adopt-in-an-existing-repository
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/governance/
  - packages/devkit-docs/src/devkit_docs/features/governance/
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/
  - packages/devkit-spec/src/devkit_spec/features/governance/usecases/hygiene.py
created_at: 2026-10-13
---

# [CAP-GOV-spec-rules] Spec Governance Rules

## 1. Summary

Fifteen deterministic rules keep the Living Spec and the feature specs consistent: the `docs` bundle ships the ten
document rules and the `spec` bundle the five spec lifecycle rules. `devkit sync` deploys them with each bundle's `core`
preset, and devkit's rule engine runs them beside its own rules:
`devkit rules check` (whole workspace or named targets), `check --staged` (the commit gate), `check --ci --base <ref>`
and `devkit rules fix`. This capability is the catalog and the contract summary of each rule; the full guide of a rule
(examples, remediation steps) is what `devkit rules explain <RULE-id>` prints, deployed beside the rule.

## 2. Scope & Boundary

- **In-Scope**: the rule catalog, behavior every spec rule shares (document index, targeting, history, namespaces,
  configuration failures), each rule's checks and fix, and how the rules are packaged.
- **Out-of-Scope** (Non-Goals):
  - The rule engine (phases, severities, `[rules]` configuration, `explain`, `phases`, output sentinels, exit codes):
    devkit's ([devkit rules reference](https://github.com/mjkimR/devkit/blob/main/docs/development/reference/rules.md)).
  - The document model the rules read: `CAP-DOCS-document-model`.
  - The entrypoint path contract and derivation: `CAP-TRACE-code-entrypoints` (this capability summarizes
    `RULE-code-entrypoints` only).
  - Judging content quality (whether tasks fulfil criteria, whether a summary is accurate). Scope Excluded: the rules
    check structure and links; tests and review judge substance.
  - Moving files. Scope Excluded: no fix ever moves or renames a file.

## 3. Business Rules & Policies

### 3.1 Catalog

Every rule is phase `linter` and is deployed by the `core` preset; every rule is severity `error` except
`RULE-spec-progress`, `RULE-proposal-boundaries` and `RULE-ux-coverage` (`warning`), hints that never block a
commit.

| Rule | Checks | Fix |
| --- | --- | --- |
| `RULE-document-reference` | Relation fields hold full IDs of the right kind; references resolve to exactly one document except missing historical feedback IDs; prose uses the code-span form; current documents use canonical IDs, not aliases; no relative links to ID-bearing documents; no duplicate IDs; well-formed, non-colliding aliases; no proposal sharing its slug with a spec; IDs cited in steering files, glossary Owners and the configured quick references resolve. | Bracket form to code-span form; a handed-off `PROP-<slug>` to its canonical spec ID; an alias reference, a steering or quick-reference code-span alias, or a glossary Owner alias to the canonical ID. |
| `RULE-decision-supersession` | ADR whole and partial replacement status, metadata resolution and reciprocal partial pointers agree; historical ADRs checked, materials and PADRs excluded. | none |
| `RULE-id-convention` | Dated partitions and path-derived IDs; Living Spec stems; `area` matching the directory; the first H1's ID token; duplicate path-derived IDs; no date- or number-based references. | `id`, `reconcile_id`, `area` and the H1 token aligned to the path. |
| `RULE-spec-format` | Capabilities, use cases and proposals have a frontmatter block with string `id`, `title`, `status`; a proposal's `planning_effort` and `dev_effort` are `low`, `medium` or `high`; a proposal's or spec's `namespace` is `global` or registered. | Adds a missing block or missing fields. |
| `RULE-traceability-link` | A use case's `capabilities` and a capability's `usecases` link both ways. | Appends the missing reverse ID. |
| `RULE-task-coverage` | Acceptance-criterion IDs of a spec and the task references of its `tasks.md` cover each other. | none |
| `RULE-spec-lifecycle` | A spec's `status`, its task checklist and its `reconcile.md` status agree. | Sets `status: completed` on a stale `spec.md`. |
| `RULE-spec-progress` | A `draft` or `planned` spec with a checked task is marked `in-progress`. | Sets `status: in-progress`. |
| `RULE-reconcile-contract` | A `reconcile.md` is well formed; in a snapshot run its `modified` targets changed in the diff. | none |
| `RULE-code-entrypoints` | Every `entrypoints` path of a capability or use case is a valid, existing workspace path. | none |
| `RULE-proposal-boundaries` | A current proposal's `target_area` and `boundaries.owns` entries name existing paths. | none |
| `RULE-document-summary` | Searchable documents carry a short English `summary`. | none |
| `RULE-steering-documents` | `docs/steering/` is flat and holds ID-free files with a `title` and a short English `summary`, within the file-count and body-size caps. | none |
| `RULE-ux-links` | A UX document has a valid `element` and Interactions table; its Step cells, `usecases`, targets, exits and reachability agree with the use case steps that cite it. | none |
| `RULE-ux-coverage` | The steps of a use case a UX document lists cite a UX document, and every interaction names its step. | none |

### 3.2 Shared Behavior

1. **Document index**: every rule reads documents through the run's workspace cache (`CAP-DOCS-document-model`), so
   `--staged` and `--ci` evaluate the snapshot they name (devkit's `ctx.snapshot`) and a fix is seen by the recheck.
   Within a single rules evaluation run, the document index is loaded once on first access and cached in memory across
   rules via `ctx.cache.get_or_compute`.
2. **Targeting**: as with every devkit rule, a violation is reported only in the files the run targets: a commit
   checks the files it changes, `devkit rules check` without targets the whole workspace. A rule whose relation spans
   several files (task coverage, lifecycle, traceability, entrypoints) states below where it reports when only one
   side is targeted.
3. **History**: files of completed spec bundles, their `feedback/` aside, are work history: checked only when named as explicit targets, never
   rewritten by a fix. `RULE-spec-lifecycle` is the exception: its conditions concern completed bundles, so it checks
   them in every run.
4. **Materials**: `docs/materials/` (and any `/materials/` directory, including `docs/packages/<name>/materials/`)
   is free-form and exempt from every authoring rule.
5. **Namespaces**: `docs/packages/<name>/` follows the conventions of `docs/` (`CAP-DOCS-namespaces`); IDs and
   references stay repository-wide.
6. **Malformed `[tool.docs]`**: a malformed `[tool.docs]` table is not a violation. It MUST fail the run
   (`DOCS_CONFIG_INVALID` naming the table, attributed to the rule, exit `2`), as devkit fails on its own malformed configuration, because
   the rules cannot tell which documents follow which conventions.
7. **Fixes**: fixes are deterministic, idempotent, honor `devkit rules fix --dry-run`, write only targeted current
   files, and change only the bytes they own.
8. **Kind facts**: the rules read each kind's Living Spec membership and directory, area scoping, summary
   requirement, entrypoint-bearing flag, `RULE-spec-format` scope, fix-time default status, heading-token prefix and
   relation-field prefixes from the kind definition table (`CAP-DOCS-document-model` section 3.2) when they run; rule
   codes, messages and remediations do not depend on where a fact is kept. A Living Spec kind without a path grammar
   in `RULE-id-convention`, an area-scoped kind whose grammar sets no area, or an identifier target without a path
   remediation MUST fail the run as a rule execution error (`RULES_RUN_FAILED`, raised from `KindTableError`) instead
   of being checked under another kind's rule.
9. **Tuning**: a project tunes phases, severities, exclusions and settings in `[rules]` of `.devkit/config.toml`
   (devkit's), for example `[rules.phase_overrides]` to move `RULE-document-summary` to `hygiene` while summaries are
   written, and `[rules.settings.RULE-document-summary] max_length`.

### 3.3 `RULE-document-reference`

Documents reference each other by exact, resolvable full IDs. Checks every current document that is not a material.
A UX document's `usecases` take `UC` and its `capabilities` take `CAP` IDs, as on any document; the UX IDs a use case
step or an Interactions Target cites in backticks are ordinary prose references.

The root glossary `docs/steering/glossary.md` is an additional, ID-free input: in five-column tables headed
`Term | Definition | Owner | Avoid | Code identifiers` with a Markdown separator row, backticked or bracketed full
IDs in the Owner column MUST resolve to exactly one indexed document. Missing and ambiguous owners produce errors
at their source line. WHEN an Owner names a uniquely resolved alias, the rule MUST report it as fixable and
`devkit rules fix` MUST replace only the alias ID, preserving backtick or bracket delimiters, whitespace and table
layout. Empty cells and non-reference text are allowed. The header fixes the Owner column;
rows may omit trailing cells or have surplus cells without moving that column. There are no mandatory owners,
glossary indexing or graph edges. Other columns, surrounding prose, legacy tables,
package glossaries and other ID-free files are outside the Owner check. Existing prose masking, file targeting,
exclusions and snapshot cache rules apply.

The steering files (the Markdown files directly in `docs/steering/` other than `README.md`, the glossary included)
are a second ID-free input: every backticked full ID in their visible text MUST resolve to exactly one indexed
document, and one naming an alias is reported as fixable with `` <alias> is an alias of <ID>; name `<ID>` ``.
WHEN a steering code-span alias resolves uniquely, `devkit rules fix` MUST replace only its ID with the canonical ID.
An ID the Owner check already examined on the same line is not reported again. No indexing or graph edges.
The fix MUST retain existing masking, targeting and exclusion boundaries; missing or ambiguous references stay
unchanged. A second fix MUST change no file.

The quick references are a third ID-free input: the Markdown files the rule setting `quick_references` matches
(workspace path patterns in the `**` grammar of `[rules] exclude`; default `docs/development/**/*.md`,
`guides/**/*.md`, `packages/*/README.md` and `tools/*/README.md`; `[]` turns the check off; an invalid pattern is
`RULES_SETTINGS_INVALID`), read per file so path overrides apply. Every backticked full ID in their visible text MUST
resolve to exactly one indexed document, reported with the messages of indexed documents; one naming another
document's alias is reported as `` <alias> is an alias of <ID>; reference `<ID>` `` and is fixable: `devkit rules
fix` rewrites the code span to the canonical ID and nothing else in the file. A matching file that is an indexed
document is checked once, as a document; a steering file keeps the steering check. Only targeted files are reported
or rewritten (`[rules] exclude` applies); the rule keeps `inputs` unset, so a run targeting a quick reference
evaluates it. No indexing or graph edges; plain-text IDs and feedback `target` fields are not checked.

- MUST report: a relation field of the wrong shape, a value that is not a full ID, or an ID of the wrong kind
  (`usecases`, `related_usecases` take `UC`; `capabilities`, `related_capabilities` take `CAP`; `spec` takes `SPEC`;
  `plan` takes `PLAN`; proposal `milestone` and milestone `depends_on` take `MS`; unit `depends_on` takes exact PROP/SPEC anchors).
- MUST report a reference to an ID no document declares or several documents declare, except a missing `FB-*` ID in historical documents. Ambiguous historical feedback IDs remain errors. A reported ID is fixed by hand (the rule never guesses which document was meant).
- MUST report a bracket reference in prose (fixable: converted to the code-span form).
- MUST report a `PROP-<slug>` reference that does not resolve when exactly one `SPEC-<slug>` exists, declared or as
  an alias, typically added on another branch after the handoff (fixable: rewritten to the canonical ID of that spec,
  so one fix pass converges). The fix never changes a spec's `proposal` provenance field and skips completed specs
  and materials. In historical files such a reference, in prose or in a unit `depends_on`, was valid when written and
  resolves silently through that spec; a `PROP-<slug>` with no matching spec is reported there as in current documents.
- References resolve through the canonical mapping of `CAP-DOCS-document-model` (section 3.5). MUST report a
  reference written with another document's alias in a current document (fixable: rewritten to the canonical ID in
  frontmatter and prose); relation-field prefix typing applies to the ID as written. Decision records (ADRs and PADRs) are
  current documents here (`ADR-immutable-decisions-editable-records`). In historical files an alias reference resolves
  silently and `devkit rules fix` never rewrites it. A
  document mentioning its own alias is not reported. A reference to a colliding alias is reported as ambiguous and
  left unchanged.
- MUST report a relative Markdown link to a document that has an ID. External URLs, images, code files, documents
  without IDs and links with a fragment or query keep Markdown links.
- MUST report an ID declared by several documents (on each), and a `PROP-<slug>` beside a `SPEC-<slug>`, declared or
  as an alias (handoff deletes the proposal, so the pair is an unfinished handoff or a reused slug).
- MUST report, as identity checks over every targeted document (materials and completed specs included), each
  malformed `aliases` item and each alias another document declares as its ID or several documents declare (on every
  document involved). The `depends_on` cycle checks follow alias edges to their documents.
- Reference extraction follows `CAP-DOCS-document-model`: code, comments, escapes, link labels and
  `~~strikethrough~~` are not prose, so a historical mention of a removed document MAY stay in strikethrough.

### 3.4 `RULE-id-convention`

A document's ID is a slug derived from its path; dates order dated partitions and are never part of an ID, and
sequence numbers are forbidden (they collide across parallel branches).

- **Dated partitions**: ADR `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md` with `ADR-<slug>`; spec bundle
  `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/{spec,plan,tasks,reconcile}.md` with `SPEC-`, `PLAN-`, `TASKS-<slug>` and
  `reconcile_id: REC-<slug>`; feedback `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/feedback/<name>.md` (no date prefix) or
  `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<name>.md`, or proposal-local
  `docs/proposals/PROP-<slug>/feedback/<name>.md` (no date prefix), with `FB-<name>`. Slugs are kebab-case, their first segment MUST
  contain a letter (a year or number there would read as a retired number-based ID), and the month partition MUST
  match the date prefix.
- **Living Spec stems** (the ID is the file stem): `docs/capabilities/<area>/CAP-<AREA>-<slug>.md` (`<AREA>`
  upper-case letters and digits, `area: <area>`); `docs/usecases/<area>/UC-<slug>.md` (`area: <area>`; only
  `README.md` directly under `docs/usecases/`); `docs/ux/<area>/UX-<slug>.md` (`area: <area>`); `docs/architecture/ARCH-<slug>.md` or `ARCH-<NN>[-<n>]-<slug>.md` with
  `<NN>` an arc42 chapter (`01`-`11` except `09`, decisions, and `12`, the glossary) and `<n>` a sub-document `1`-`9`
  (`05-1` containers, `05-2` components). The first slug segment MUST contain a letter. Namespace docs roots use the
  same layout.
- MUST report: a path off the convention (nothing else is reported for that file until it moves; `README.md` files
  are not checked); no frontmatter; an `id`/`reconcile_id` or `area` other than the path requires (fixable); a first
  `# ` heading opened by a bracket or code-span ID token that is not the ID (fixable; in a spec bundle file the token
  MAY follow a leading `<label>: `, and a plan, tasks or reconcile heading MAY name `SPEC-<slug>`; an ID later in the
  heading is a reference, not the document's own, and never rewritten); in any file but a spec bundle file
  (`spec.md`, `plan.md`, `tasks.md`, `reconcile.md`; feedback, in a bundle or not, is checked), a first `# ` heading
  that does not open with an ID token but names an ID of the document's own kind (`# Capability [CAP-X-old] Title`;
  reported, not fixable: the heading should read `# [<ID>] <title>`); an ID another file's path also derives (slugs are unique per document type across partitions and
  areas, feedback slugs within their bundle; detected across the whole workspace); a date- or number-based reference
  (such as ``ADR-0006``, ``UC-010``, ``CAP-HARN-007``, ``SPEC-20261006`` or an `ARCH-<NN>` without slug) in the
  frontmatter or prose of any Markdown file under `docs/` (materials excepted) or `specs/`. Code blocks, indented
  code, inline code, HTML comments and escapes are not checked; Markdown link labels and targets are.
- Fields are read from their top-level frontmatter lines as written.

### 3.5 `RULE-spec-format`

Every capability, use case, UX document, proposal and global milestone starts with a YAML frontmatter block that sets `id`, `title` and `status` as
non-blank strings.

- **Scope**: Markdown files under `docs/capabilities/`, `docs/usecases/`, `docs/ux/`, `docs/proposals/`, `docs/roadmap/`,
  and `capabilities/`, `usecases/`, `ux/` of each namespace docs root, except `README.md`, templates, directories starting with `.` and
  `materials/`. Unlike the index, a file is checked even when it declares no ID.
- MUST report: no block (`---` on the first line, closed by `---`); a malformed block (unclosed, invalid YAML,
  duplicate keys, not a mapping; fixed by hand); a missing, blank or non-string `id`, `title` or `status`; a
  `planning_effort` or `dev_effort` in a proposal anchor (`docs/proposals/PROP-<slug>/proposal.md` or
  `docs/proposals/PROP-<slug>.md`) that is present and not a string naming `low`, `medium` or `high` (not fixable;
  omission is allowed for legacy proposals); a `namespace` in `proposal.md` (under `docs/proposals/`) or `spec.md`
  that is not a string naming `global` or a registered namespace (not fixable). The `namespace` field is checked in
  current proposals and specs, and in every one of them when the run targets `.devkit/config.toml`.
- **Fix**: fills what is missing and leaves present values alone: `id` the ID the path derives, `title` the first
  `# ` heading (a leading ID token dropped) else the file stem, `status: draft` (`open` for proposal feedback, `planned` for milestones), and `created_at` today when none of
  `created_at`, `created`, `date` is set. The path derives the file stem for a capability, use case, single-file
  proposal or PADR, `PROP-<slug>` for a bundle's `proposal.md` and `PROP-<slug>-target` for its `target-docs.md`, and
  `FB-<name>` for its direct `feedback/<name>.md`; any other file under `docs/proposals/` derives none, and its missing `id` is reported without a fix.

### 3.6 `RULE-traceability-link`

Use cases and capabilities form an M:N relation recorded on both sides by exact ID: a use case's `capabilities`, a
capability's `usecases` (under `docs/` and every namespace docs root; links MAY cross packages).

- MUST report a one-sided link on the document missing the reverse link; when the run does not target that document,
  on the document that declares the link instead.
- **Fix**: appends the source ID to the target's list, creating the field when absent and keeping a flow or block
  list in its style. It fixes a link only when both IDs are declared by exactly one document and the field is absent
  or a list, and only in targeted documents (`devkit rules fix <target document>` when the run targets only the
  source).
- A link written with an alias of the other document counts as a link to it in both directions, so the fix never adds
  the canonical ID beside an alias; `RULE-document-reference` rewrites the alias.
- Missing targets, duplicate IDs, wrong kinds and malformed fields are `RULE-document-reference`'s.

### 3.7 `RULE-task-coverage`

Each `specs/**/tasks.md` is checked against the `spec.md` beside it; a spec without `tasks.md`, and a completed spec
unless explicitly targeted, is not checked.

- **Criteria**: every H3 under the H2 whose title contains `Acceptance Criteria` MUST carry exactly one `[AC-NN]`
  (`AC-` and two or more digits, compared as written); IDs MUST be unique and the spec MUST define at least one.
- **Coverage**: a checklist task (`- [ ]`, `- [x]`, also `*` or `+`, nested tasks included) covers an ID written in
  its text as `[AC-NN]` or listed on a direct child line `- _Requirements: AC-01, AC-02_`. Tables, prose, blockquotes,
  frontmatter, fenced or indented code, HTML comments and a `_Requirements:_` line that is not a direct child of a task
  cover nothing. A task is exactly a checklist item the shared Markdown scanner reports, the same item `count_tasks`
  counts.
- MUST report: a criterion heading without exactly one valid ID, a duplicate ID or no criteria; acceptance criteria
  without a task; tasks referencing undefined criteria; an invalid requirement ID; a missing or unreadable `spec.md`
  or unparsable spec frontmatter.
- **Targeting**: the pair is checked when either file is targeted, and each violation is reported on the file it
  belongs to; files matched by `[rules] exclude` are never reported. Not fixable.

### 3.8 `RULE-spec-lifecycle`

In a spec bundle the `status` of `spec.md`, the checklist of `tasks.md` and the `status` of `reconcile.md` MUST agree
(statuses compared trimmed and case-insensitively), because workflow stages are derived from them.

- MUST report: `spec.md` `completed` without `reconcile.md`; `spec.md` `completed` with a `reconcile.md` other than
  `resolved`; `spec.md` not `completed` while every task is checked (at least one, none open, counted as devkit's
  `tasks-checked` check counts them) and `reconcile.md` is `resolved` (stale status; a bundle without tasks is never
  stale).
- Every `spec.md` under `specs/` is checked, completed ones included. A targeted run checks a bundle when it targets
  its `spec.md`, `tasks.md` or `reconcile.md`; the violation is on `spec.md` (line 1) when that is targeted, else on
  the targeted `reconcile.md` or `tasks.md`.
- **Fix**: sets `status: completed` by rewriting only the value of the top-level `status:` line of a targeted
  `spec.md`, keeping a trailing comment (`# draft | planned | ...`; a `#` counts as one only after whitespace and
  outside a quoted value, so `status: "draft #2"` becomes `status: completed`); a `spec.md` without a `status:` line is fixed by
  hand.

### 3.9 `RULE-spec-progress`

A spec's `status` says where its work is; nothing else moves it to `in-progress`. devkit gives each rule one severity,
so this hint is a rule of its own (`SPEC-open-feedback-and-progress`).

- SHOULD report (severity `warning`): `spec.md` `draft` or `planned` (trimmed, case-insensitive) while at least one
  task of `tasks.md` is checked. A bundle in `RULE-spec-lifecycle`'s stale state (every task checked, `reconcile.md`
  `resolved`) is left to that rule, so the two fixes never disagree.
- Targeting and placement are `RULE-spec-lifecycle`'s, with `tasks.md` as the only other file.
- **Fix**: sets `status: in-progress` by rewriting only the value of the top-level `status:` line of a targeted
  `spec.md`, keeping a trailing comment.

### 3.10 `RULE-reconcile-contract`

`reconcile.md` records how a change was reconciled into the Living Spec (written by the `spec-sync` skill).

- MUST report: no or malformed frontmatter, or no `reconcile_id`; `status` other than `pending` or `resolved`;
  `targets` missing or not a list (`targets: []` when nothing is affected); a target that is not a mapping, a `file`
  that is not a unique workspace-relative path in canonical form (`docs/a.md`, not `./docs/a.md`), a `resolution` other than `modified` or `waived`, or a waiver whose
  `rationale` has fewer than 20 non-whitespace characters.
- **Diff evidence**: in a snapshot run (`--staged`, `--ci`), a `resolved` record the diff changes MUST have every
  `modified` target changed or deleted by that diff. `--ci` judges the whole branch against its merge base. A record
  whose frontmatter is unchanged from the base is not rechecked. A plain `devkit rules check` checks the form only.
- Every targeted record of a current bundle; a completed bundle's record only when explicitly targeted. Not fixable.

### 3.11 `RULE-code-entrypoints`

Every `entrypoints` item of a capability or use case (`docs/` and namespace docs roots) MUST be a string, a literal
workspace-relative path, and an existing file or directory inside the workspace. In a snapshot run it also reports
every current document that declares a path the diff deletes. Not fixable. The full contract is
`CAP-TRACE-code-entrypoints`.

### 3.12 `RULE-proposal-boundaries`

A proposal's boundary is copied into its spec at handoff, so it names real paths by `plan-accept`
(`ADR-proposal-acceptance`).

- SHOULD report (severity `warning`), on the entry's line: for a proposal anchor (`docs/proposals/PROP-<slug>/proposal.md`
  or `docs/proposals/PROP-<slug>.md`) whose `status` is `draft`, `reviewing` or `accepted`, a `target_area` or
  `boundaries.owns` entry containing `<...>` (the template placeholder, its own message), one that is not a literal
  repository-relative path, and one that resolves to no existing path. A non-string `target_area`, a non-mapping
  `boundaries`, a non-list `owns` and a non-string item are malformed. `boundaries.excludes` is not checked.
- Resolution, in order: relative to the repository root; relative to the proposal's namespace docs root (when
  `namespace` names a registered namespace), then to `docs/`; as a capability area under the namespace's, then the
  global `capabilities/`. A trailing `/` requires a directory. A snapshot run resolves in the snapshot's tree.
- Reported for targeted anchors and in a whole-workspace run, whatever their history; no deleted-path rescan. Not
  fixable.

### 3.13 `RULE-document-summary`

`summary` is the main signal of `devkit docs search` (`CAP-DOCS-document-search`).

- MUST report: a capability, use case, UX document, decision, architecture document, milestone, `proposal.md` or `spec.md` without `summary`
  (a file still carrying the skeleton marker `<!-- devkit:skeleton -->` is exempt until written); a `summary` that is
  not a non-empty string; a letter outside the Latin script in any `summary` (digits, punctuation and symbols are
  allowed); a `summary` longer than `max_length` characters.
- Setting: `max_length` (default `300`, a positive integer). Materials are exempt. Not fixable: a summary is written,
  never generated.

### 3.14 `RULE-steering-documents`

Steering documents are listed in every agent context (`ADR-background-pointer-in-constitution`), so the directory stays
small and each entry readable. Only the root `docs/steering/` is checked, and only when the run targets a file in it.

- MUST report: a file in a subdirectory of `docs/steering/`; a file that is neither `*.md` nor `glossary.yaml`;
  a file that is not UTF-8; frontmatter that does not parse or that closes after the first 4096 bytes (what
  `devkit get-context` reads); an `id` key; a missing or empty `title`; a missing or empty `summary`, a letter
  outside the Latin script in it, or one longer than `max_summary_length` characters; a body (the text after the
  frontmatter) larger than `max_body_bytes` UTF-8 bytes; each Markdown file beyond `max_files` in sorted order,
  whenever any steering file is targeted, so a commit adding a file is refused even when the new file sorts first.
- `README.md` is neither checked nor counted.
- Settings: `max_files` (default `10`), `max_body_bytes` (default `24576`) and `max_summary_length` (default `300`),
  each a positive integer. Not fixable.

### 3.15 `RULE-ux-links`

A UX document and the use cases it serves do not contradict each other (`ADR-ux-step-links-and-coverage`). Checks
every current UX document outside materials against every current use case. A use case's steps are the `N.` items
at column 0 under its `Main Success Scenario` H2 (a nested numbered list continues its step) and the `- **<key>.**` bullets under its `Extensions` H2 (`2a`, `*a`, also
written `\*a`); a line indented by a space continues the item, and any other line ends it, so intro paragraphs,
free prose and `Covers` lines belong to no step. A step cites a screen through a body reference whose canonical
target is a UX document (aliases and the bracket form count). An extension resumes at the step its
`resumes at [step] <key>` names (`resumes at the same step`: the step it branches from), and ends the use case
otherwise.

- MUST report on the UX document: a missing `element` or one other than `screen`, `modal` or `panel`; no
  `Interactions` H2, or one whose first table header is not `Trigger | Step | From | To | Target | Capability |
  Feedback`; a Step cell that is neither empty (`-` counts) nor `` `UC-<slug>` <key> `` pairs separated by commas; a
  Target cell that is neither empty, a UX document's ID, `close`, `back` nor `end`; a `modal` without a `close` or
  `back` row.
- MUST report, on the UX document or, when only the use case is targeted, on the use case at the step's line: a Step
  pair naming a use case `usecases` does not list, a key the use case has no step for, or a step that does not cite
  the document; a `usecases` entry no Step cell names; a use case step citing the document while its `usecases` does
  not list the use case.
- MUST report per listed use case whose steps cite the document (panels exempt): a `screen` with no row targeting
  another UX document, `close`, `back` or `end` that no terminal step cites (the last main step, an extension that
  ends the use case, or a step whose next step cites no screen); a `screen` or `modal` not reachable from the use
  case's entries (the screens cited by the first step, by a step whose preceding step cites none and by every
  extension) over its edges (the targets of the screens it cites and of the panels their `Content` H2 cites).
- Unresolved IDs are `RULE-document-reference`'s and are skipped. Extension-to-state coverage is not checked. Not
  fixable.

### 3.16 `RULE-ux-coverage`

The gaps `RULE-ux-links` does not refuse: not every step happens on a screen, and a screen may carry global controls.
devkit gives each rule one severity, so the hint is a rule of its own, as `RULE-spec-progress` is.

- SHOULD report (severity `warning`): for every use case a current UX document lists, each main-scenario step and
  extension that cites no UX ID, once, on the first listing UX document the run targets (path order, at its
  `usecases` entry), else on the use case at the step's line; each Interactions row whose Step cell is empty, on its
  UX document. A use case no UX document lists is never reported. Not fixable.

### 3.17 `RULE-decision-supersession`

1. **Whole replacement**: IF an ADR has `superseded_by` without `status: superseded`, or is superseded without one
   resolving ADR in `superseded_by`, THEN the rule MUST report a non-fixable error at that field.
2. **Reciprocity**: WHEN an ADR names a whole successor or a visible partial replacement pointer, the rule MUST
   require that successor's scalar or list `supersedes` to name the earlier ADR.
3. **Replacement targets**: WHEN an ADR declares `supersedes`, the rule MUST require each value to resolve uniquely
   to an ADR whose status is superseded or whose visible partial pointer names the superseder.
4. **Canonical identity**: The rule MUST compare these relationships through unique canonical alias resolution.
5. **Evaluation boundaries**: The rule MUST check targeted ADRs including superseded records, exclude root and
   nested materials and PADRs, and read through the snapshot cache. It MUST NOT rewrite files or add graph edges.
6. **Partial history**: The rule MUST allow a wholly superseded ADR to retain earlier reciprocal partial pointers.
   Otherwise a partial-pointer owner MUST stay accepted. Pointer scanning masks code fences, indented code,
   comments, escapes and struck-out text, using the shared visible-prose scanner.

The rule is deployed with `docs:core`, phase linter and severity error. It has no rule-specific settings.
Review determines whether the replacement actually covers all or part of an ADR; the rule checks recorded
relationships. Tests: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/tests/`.

## 4. Interfaces & Data Contracts

### 4.1 Commands (devkit's)

| Command | Effect on the spec rules |
| --- | --- |
| `devkit rules check [FILES]...` | Runs every rule; without targets the whole workspace. `--phase linter` or `--phase hygiene` selects a phase. |
| `devkit rules check --staged` | The commit gate: evaluates the staged Git tree (snapshot run). |
| `devkit rules check --ci --base <ref>` | Evaluates `HEAD` against its merge base with `<ref>` (snapshot run; default `origin/main`). |
| `devkit rules fix [FILES]... [--dry-run]` | Applies the fixes above. |
| `devkit rules explain <RULE-id>` | Prints the rule's phase, severity, effective settings and its guide. |

Violations use devkit's `[VIOLATION: <RULE-id> severity= file= line= status= message= remediation= guide=]` sentinel, where `status` is
`open` or `fixable` and `guide` is the deployed guide path.

### 4.2 Configuration

```toml
[rules.phase_overrides]
RULE-document-summary = "hygiene"   # while a repository's documents get summaries

[rules.settings.RULE-document-summary]
max_length = 300
```

### 4.3 Packaging

Each rule is a class in a package (`ADR-spec-package-on-devkit`). The document rules (`RULE-code-entrypoints`,
`RULE-document-reference`, `RULE-decision-supersession`, `RULE-document-summary`, `RULE-id-convention`, `RULE-spec-format`,
`RULE-steering-documents`, `RULE-traceability-link`, `RULE-ux-coverage`, `RULE-ux-links`) live in
`devkit_docs.features.governance.usecases.<name>`, beside the document model they check (`ADR-document-package`);
the lifecycle rules (`RULE-spec-lifecycle`, `RULE-spec-progress`, `RULE-task-coverage`, `RULE-reconcile-contract`,
`RULE-proposal-boundaries`) and the rejected-proposal hygiene live in `devkit_spec.features.governance.usecases.<name>`.
Document rule assets ship in the `docs` bundle; lifecycle rule assets ship in `spec`. Each owner deploys
`rules/<name>/rule.py`, a thin subclass (devkit instantiates only classes a rule file defines), and the guide
`rules/<name>/guide.md`, to `.devkit/managed/<owner>/rules/<name>/`. Keeping the logic in the package means one tested
implementation and a deployed file that never changes when the rule does. A rule whose judgment lives in a bundle
instruction names it in `related` (`docs:living-spec-writing` for the reference, traceability, summary, steering,
identifier and lifecycle rules, `docs:decision-writing` for `RULE-decision-supersession`, `docs:contract-authoring` for `RULE-task-coverage`, `docs:ux-writing` and
`docs:usecase-writing` for `RULE-ux-links` and `RULE-ux-coverage`), and `devkit rules explain` prints its deployed
path. `devkit_docs.features.governance` exposes `document_index(ctx)`, `namespaces(ctx)` and the targeting helpers the rules share.

A rule's tests live in its folder, `rules/<name>/tests/test_rule.py`, and deploy with it. They load the rule with
`devkit_agt.features.rules.services.testing.load_rule(__file__)`, which loads the folder as devkit loads the deployed copy (the `rule.py`
subclass, so the deployed file and the package implementation are tested together), and evaluate
it with `check(RULE, tmp_path, files, ...)`; they use nothing from the repository's `tests/`. `devkit rules test
RULE-<id>` runs the deployed copy's tests in an isolated pytest run (no project configuration or `conftest.py`), and
without IDs every rule's tests. The repository's own `pytest` collects the same files under
both packages' `bundles/<owner>/bundle/rules/`.

### 4.4 Error Codes

| Code | Level | Condition |
| --- | --- | --- |
| `RULES_EXECUTION_FAILED` | `ERROR` (devkit's) | A rule raised an exception that is not an advisory; exit `2`. An advisory a rule raises keeps its own code: a malformed `[tool.docs]` table is `DOCS_CONFIG_INVALID` with the rule's ID. |

### Milestone hygiene advisories

The existing spec hygiene extension also checks repository milestone membership on the base. It reads direct proposal anchors only; rejected proposals are excluded and SPEC milestone metadata is ignored. It never claims to inspect unmerged branches.

| Code | Level | Condition and resolution |
| --- | --- | --- |
| `SPEC_MILESTONE_DONE_UNSETTLED` | WARNING | A done milestone still has unsettled members; review and reassign/clear those members, reject a proposal or finish the work before closing the milestone. |
| `SPEC_MILESTONE_DROPPED_UNSETTLED` | WARNING | A dropped milestone still has unsettled members; review and reassign/clear or reject those members. |

Warnings carry the milestone and member paths, deterministic remediation and the usual success exit code unless strict mode is requested. No out-of-order activation or close-candidate warning is emitted (`ADR-roadmap-and-milestones`).

### Milestone validation contract

Milestones use global docs/roadmap/MS-<slug>.md for planned/active and docs/roadmap/_archive/MS-<slug>.md for done/dropped, with word-led kebab-case slugs and matching ID/H1. Other nesting and namespace roadmap locations are invalid. Placement checks never move files or change lifecycle status; invalid archived live documents remain indexed and reportable. Duplicate milestone identities across locations remain errors. Format requires id, title, status and created_at; summary follows the English summary rule. Status is planned/active/done/dropped. Safe fixes fill missing metadata with planned status and created_at; existing invalid statuses need correction by hand.

Milestone membership is a scalar existing MS ID on proposal anchors only; legacy SPEC metadata yields no membership edge. Depends_on is an MS-ID list on milestones and a PROP/SPEC-anchor-ID list on proposal/spec anchors. Wrong field locations/shapes/kinds, auxiliary targets, unresolved or duplicate targets and cycles (including self-cycles) are errors. A targeted run checks each typed graph through the complete index and reports participating targeted anchors even when other cycle members are untargeted. Completed SPEC anchors resolve as terminal targets and do not contribute outgoing cycle edges. Exact same-slug handoff fixes also rewrite live incoming depends_on references; they do not infer completion or successors. Decomposed_from/supersedes on anchors are scalar PROP provenance; deleted sources are valid. Done/dropped milestone history follows explicit targeting and is never rewritten automatically.


## Lifecycle applicability during adaptive development

The ten docs rules keep their existing judgments under both approaches. In adaptive development, the five spec lifecycle
rules (`task-coverage`, `spec-lifecycle`, `spec-progress`, `reconcile-contract`, `proposal-boundaries`) apply to explicitly
SDD workflow-bound ownership, including prior snapshot anchors for changed/deleted bindings and companions.
Unbound current adaptive-development documents acquire no SDD lifecycle obligation. A rule with no applicable retained Unit
reports `SDD_LIFECYCLE_INACTIVE` omission evidence rather than a successful check.

WHEN a targeted retained SDD anchor or its binding is removed in adaptive development, `RULE-spec-lifecycle` MUST report that
its existing lifecycle ownership was not preserved. Root-level Units own their companions; valid quoted YAML binding
keys have the same meaning as plain keys. Current rules use run-scoped cached ownership; committed snapshots read
prior ownership through the generic rule repository, without requiring installed workflow definitions.
`packages/devkit-spec/tests/integration/features/policy/test_adaptive_dev.py` and
`packages/devkit/tests/integration/features/rules/test_ownership.py` cover applicability and normal binding spellings.
