# [RULE-id-convention] Slug Identifier Convention

## 1. Overview

A document's ID is a slug derived from its path. Dates order dated documents in their partitions; they are never part
of an ID, and neither are sequence numbers: they collide across parallel branches and make references ambiguous.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: the identifier targets below (path, frontmatter ID, `area`, heading token, uniqueness), and
  every Markdown file under `docs/` and `specs/` for date- or number-based references. `README.md` files are not
  identifier targets, but their references are checked.
- **What is not**: references in `docs/materials/` and a namespace's `docs/packages/<name>/materials/`; references
  inside code blocks, indented code, inline code, HTML comments and escapes. Markdown link labels and targets are
  checked.
- **Targeting**: violations are reported in the targeted files; duplicates are detected across the whole workspace,
  namespaces included. Files of completed spec bundles are checked only when named as explicit targets, and never
  rewritten.

### Dated Partitions: ADR, Change Spec, Feedback

| Document | Path | ID |
| :--- | :--- | :--- |
| ADR | `docs/decisions/{YYYY-MM}/{YYYYMMDD}-{slug}.md` | `ADR-{slug}` |
| Spec bundle | `specs/{YYYY-MM}/{YYYYMMDD}-{slug}/spec.md`, `plan.md`, `tasks.md`, `reconcile.md` | `SPEC-{slug}`, `PLAN-{slug}`, `TASKS-{slug}`, `reconcile_id: REC-{slug}` |
| Feedback in a bundle | `specs/{YYYY-MM}/{YYYYMMDD}-{slug}/feedback/{name}.md` | `FB-{name}` |
| Proposal feedback | `docs/proposals/PROP-{slug}/feedback/{name}.md` | `FB-{name}` |
| Month-level feedback | `specs/{YYYY-MM}/feedback/{YYYYMMDD}-{name}.md` | `FB-{name}` |

`{slug}` and `{name}` are kebab-case and their first segment must contain a letter (`20261014-2024-budget` would
give `ADR-2024-budget`, which reads as the number-based `ADR-2024`; write `20261014-budget-2024`). The `{YYYY-MM}`
partition must match the date prefix. A feedback file inside a bundle has no date prefix.

### Living Spec and Roadmap: Capability, Story, Architecture, Milestone

The ID is the file stem:

| Document | Path | Also required |
| :--- | :--- | :--- |
| Capability | `docs/capabilities/{area}/CAP-{AREA}-{slug}.md` | `{AREA}` upper-case letters and digits; `area: {area}` |
| Story | `docs/stories/{area}/US-{slug}.md` | `area: {area}`; only `README.md` directly under `docs/stories/` |
| Architecture | `docs/architecture/ARCH-{slug}.md` or `ARCH-{NN}[-{n}]-{slug}.md` | `{NN}` an arc42 chapter, `{n}` a sub-document (1-9) |
| Milestone | `docs/roadmap/MS-{slug}.md` | global only: no nested or namespaced roadmap location |

The first segment of `{slug}` must contain a letter: `CAP-HARN-001-foo` and `US-010-bar` are sequence numbers.
`{NN}` is an arc42 chapter `01`-`11` in arc42's order (`05-1` containers, `05-2` components), except `09` (decisions
live in `docs/decisions/`); `12` (the glossary) is `docs/glossary.md`. A deep-dive outside the chapters is
`ARCH-{slug}`. Chapters: 01 Introduction and Goals, 02 Architecture Constraints, 03 System Scope and Context (C4 L1),
04 Solution Strategy, 05 Building Block View, 06 Runtime View, 07 Deployment View, 08 Cross-cutting Concepts, 09
Architecture Decisions, 10 Quality Requirements, 11 Risks and Technical Debts, 12 Glossary.

In a monorepo, a package registered in `[[tool.spec.namespaces]]` of `.devkit/config.toml` keeps its Living Spec
under `docs/packages/<name>/` with the same layout (`capabilities/`, `stories/`, `architecture/`). IDs are
repository-wide, so a slug is unique across `docs/` and every package.

## 2. Cause of Violation

- A path off the convention above (wrong depth, an undated or misdated partition, a non-kebab-case name, a dated
  feedback name inside a bundle, a slug whose first segment is a date or sequence number, chapter 09 or 12, a
  capability or story outside an area directory, a milestone outside `docs/roadmap/`): `Invalid partition path:
  <what the path must be>`. Nothing else is reported for the file until it is moved.
- No frontmatter (or one never closed): `Missing YAML frontmatter; expected <field>: <ID>`.
- A frontmatter `id` (`reconcile_id` in `reconcile.md`) other than the path requires (fixable): `Frontmatter <field>
  is "<declared>" but the path requires "<ID>"`.
- A capability's or story's `area` other than its directory (fixable): `Frontmatter area is "<area>" but the
  directory requires "<directory>"`.
- A first `# ` heading opened by an `[ID]` or `` `ID` `` token that is not the ID (fixable; in a spec bundle file
  the token may follow a leading label, `` # Technical Plan: `SPEC-{slug}` ``, and a plan, tasks or reconcile heading
  may name `SPEC-{slug}`): `Heading token [<token>] does not match identifier <ID>[ or <ID>]`. An ID later in the
  heading is a reference and is never rewritten.
- Outside spec bundle files (`spec.md`, `plan.md`, `tasks.md`, `reconcile.md`), a first `# ` heading that does not
  open with an ID token but names an ID of the document's own kind (`# Capability [CAP-X-old] Title`):
  `Heading does not open with the document's own ID <ID> but names [<token>]`. Reported, not fixed: rewrite the
  heading as `# [<ID>] <title>`.
- An ADR, spec or Living Spec ID that another file's path also derives: `Identifier <ID> is duplicated across
  <paths>`. Slugs are unique per document type across partitions and areas. Duplicate `FB-` IDs are reported by
  `RULE-document-reference`.
- A date- or number-based reference in the frontmatter or prose: `Date- or number-based identifier reference
  "<reference>"`, for `SPEC-20261006`, `FB-20261006`, `ADR-0006`, `PADR-0001`, `US-010`, `CAP-HARN-007`, or `ARCH-06`
  (also `ARCH-05-2`) without a slug.

## 3. Remediation

1. Move the file to the required path (for a Living Spec document or milestone, the ID is the file stem; for a dated
   document, use the decision or start date). `devkit rules fix` never moves files; `devkit spec resolve <ID>` finds
   a document by ID.
2. **Autofix**: `devkit rules fix` sets the `id` / `reconcile_id` and `area` lines (inserting a missing one: the ID as
   the first header line, `area` after the `id` line) and rewrites the heading token (in a spec bundle file, to
   `SPEC-{slug}`). It never moves a file, never renames a duplicate slug, never rewrites a reference, needs the
   frontmatter to exist for the field fixes, and skips completed spec bundles and files that are not valid UTF-8.
   It writes only the targets when the run names any.
3. Add missing frontmatter with the ID, `title` and `status`; rename one of two duplicate slugs.
4. Replace date- or number-based references with the slug ID by hand, written as `` `ADR-{slug}` ``,
   `` `SPEC-{slug}` ``, `` `CAP-{AREA}-{slug}` ``, `` `US-{slug}` `` or `` `ARCH-{NN}-{slug}` `` in prose.

Read the `spec:living-spec-writing` instruction (References) when rewriting a reference: it says where a full ID, an
exact field ID or an ordinary link belongs.

## 4. Configuration

No settings. Namespaces come from `[[tool.spec.namespaces]]` in `.devkit/config.toml`.

## 5. Exceptions

No inline suppression. Quote an old date- or number-based identifier inside inline code or a code block, or keep it
in a `materials/` directory; `[rules] exclude` removes a file from every rule.
