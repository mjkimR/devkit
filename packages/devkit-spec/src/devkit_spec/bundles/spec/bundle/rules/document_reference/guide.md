# [RULE-document-reference] Exact Document References

## 1. Overview

Documents refer to each other by full ID, never by Markdown path: `` `ADR-example` `` in prose, the bare ID in a
relation field. An ID survives moves and renames and resolves with one lookup; a path breaks silently and a partial or
ambiguous ID sends an agent to the wrong document. `usecases` and `related_usecases` take `UC` IDs, `capabilities` and
`related_capabilities` `CAP` IDs, `spec` a `SPEC` ID, `plan` a `PLAN` ID, `milestone` (proposal and spec anchors
only) one `MS` ID and `depends_on` (milestones only) a list of `MS` IDs, without cycles.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: the targeted documents (Markdown files under `docs/` and `specs/` whose frontmatter declares a
  well-formed ID): their relation fields, the `` `ID` `` and `[ID]` references in their prose, and their relative
  Markdown links. Provenance fields need no existing target: a spec's `proposal:` is not checked, and an anchor's
  `decomposed_from` and `supersedes` must only be `PROP-` IDs.
- **Root glossary Owners**: additionally, `docs/steering/glossary.md` is checked without adding an ID or indexing it.
  In five-column tables headed `Term | Definition | Owner | Avoid | Code identifiers`, followed by a Markdown
  separator row, full IDs in backticks or brackets in the `Owner` cell must resolve uniquely. Empty owners and
  non-reference text are allowed. Only resolution is checked, with no glossary autofix or reference-graph edges;
  legacy tables are outside this extension. The header fixes the Owner column even when rows omit trailing cells or
  add surplus cells. The same prose masking, targeting, exclusions and snapshot cache apply.
- **Steering files**: every backtick-quoted full ID in the visible text of the Markdown files directly in
  `docs/steering/` (other than `README.md`), the glossary included, must resolve uniquely and must not be an alias.
  These files have no ID and stay out of the index: no autofix and no reference-graph edges. An ID already checked
  as a glossary Owner on the same line is reported once. Other ID-free files are outside this extension.
- **What is not**: reference extraction skips code fences, indented code, inline code other than a single ID, HTML
  comments, escapes, link labels, `~~strikethrough~~` (a historical mention of a removed document stays allowed
  there) and a heading's own ID. External URLs, images, code files, documents without IDs, links with a fragment or
  query and root-relative links keep Markdown links. Materials (`docs/materials/`, any `/materials/` directory) are
  free-form and not checked.
- **Completed specs**: files of a spec bundle whose `spec.md` is `completed` (and `done` or `dropped` milestones) are
  history: checked only when named as explicit targets, without the `[ID]`, handoff and alias findings, and never
  rewritten.
- **Aliases**: a document may declare previous or alternate IDs in `aliases`. A
  reference resolves through one canonical mapping: a declared ID always wins, and an alias resolves only when exactly
  one document declares it and no document has it as its ID. A reference written with another document's alias is
  reported in current documents, decision records (ADRs and PADRs) included. A document mentioning its own alias is not reported.
- **Declarations**: the duplicate-ID, shared-slug and alias checks (shape and collisions) cover every targeted
  document, materials and completed specs included.

## 2. Cause of Violation

- A relation field of the wrong shape: `<field> must be a list of IDs` (list fields), `<field> must be one ID`
  (`spec`, `plan`, `milestone` and the provenance fields `proposal`, `decomposed_from`, `supersedes`) or `<field>
  must contain string IDs`.
- A relation field on the wrong document: `milestone is valid only on proposal/spec anchors`, `depends_on is valid
  only on milestones`.
- A value that is not a full ID: `<field> must contain a full document ID, got '<value>'`.
- An ID of the wrong kind: `<field> takes <PREFIX>- IDs, got <ID>` (`decomposed_from` and `supersedes`: `<field>
  takes PROP- IDs, got '<value>'`).
- A `depends_on` chain that returns to a milestone, reported on each targeted milestone in the cycle: `milestone
  dependency cycle includes <ID>`.
- `[ID]` in prose (fixable): `` prose reference <ID> must be written `<ID>`, not [<ID>] ``.
- A `PROP-<slug>` reference that no longer resolves while exactly one `SPEC-<slug>` exists (fixable), typically added
  on another branch after the handoff: `` <ID> was handed off; reference `SPEC-<slug>` ``.
- A reference to an ID no document declares: `no document has the ID <ID>`; or that several declare: `<ID> is declared
  by <n> documents: <paths>`; or an alias that several documents declare: `<ID> is an alias declared by <n>
  documents: <paths>`.
- A reference written with an alias (fixable): `` <alias> is an alias of <ID>; reference `<ID>` ``. A root glossary
  Owner naming an alias (not fixed): `` Owner <alias> is an alias of <ID>; name `<ID>` ``; another ID cited in a
  steering file (not fixed): `` <alias> is an alias of <ID>; name `<ID>` ``.
- A malformed `aliases` field, reported at the item: `aliases must be a list of IDs`, `aliases must contain string
  IDs`, `aliases must contain full document IDs, got '<value>'`, `alias <ID> must have the document's own prefix
  <PREFIX>-`, `alias <ID> is the document's own ID`, `alias <ID> is repeated`, or `alias <ID> has a date- or
  number-based form; use a slug ID` (the forms `RULE-id-convention` reports).
- An alias another document declares as its ID, or that several documents declare, reported at line 1 of every
  document involved: `alias <ID> collides: it is declared by <paths>`. The declared ID keeps winning; a reference to
  the alias is left as it is.
- A relative Markdown link to a document that has an ID: `` internal document link <target> must be the ID `<ID>` ``.
- An ID declared by several documents, reported at line 1 of each: `<ID> is declared by <n> documents: <paths>`.
- A `PROP-<slug>` beside a `SPEC-<slug>` (declared or an alias), reported on the proposal: `PROP-<slug> shares its slug with SPEC-<slug>
  (<path>); a proposal and a spec cannot share a slug`. Handoff deletes the proposal, so the pair is an unfinished
  handoff or a reused slug.

## 3. Remediation

- **Autofix**: `devkit rules fix` converts `[ID]` to `` `ID` ``, replaces a handed-off `PROP-<slug>` with the
  canonical ID of `SPEC-<slug>` and an alias reference with the canonical ID, keeping a quoted frontmatter value's
  quote style. It never changes a spec's `proposal:` provenance field or an `aliases` entry, never rewrites an alias
  reference in an ADR or PADR, skips completed specs, materials and files that are not valid UTF-8, and writes only the
  targets when the run names any.
- **By hand**: a missing or duplicated ID is fixed by hand; the rule never guesses which document was meant. Find a
  document's path with `devkit docs resolve <ID>` and what references it with `devkit docs refs <ID> --direction in`.
  Create the intended document or correct the exact ID; give each document its own ID, then update the references to
  it; replace a document link with the target's ID; remove an already handed-off proposal or rename it to an unused
  slug; remove a `depends_on` edge to break a cycle; keep a colliding alias on one document only, and correct a
  malformed `aliases` item to a previous ID of the document with its own prefix.
- **Related**: before replacing a link or a reference by hand, read the `spec:living-spec-writing` instruction
  (References) for which documents take an ID and which keep an ordinary link.

## 4. Configuration

No settings.

## 5. Exceptions

No inline suppression. Mention a removed document in `~~strikethrough~~`, or keep free-form notes under a
`materials/` directory; `[rules] exclude` removes a file from every rule.

## 6. Example

```markdown
See `ADR-example`.
```

```yaml
capabilities:
  - CAP-AREA-example
```
