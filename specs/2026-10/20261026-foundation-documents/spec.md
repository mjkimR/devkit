---
id: SPEC-foundation-documents
title: Steering documents for project-wide background
summary: Adds a flat docs/steering/ directory of project-wide background documents such as the glossary, product vision and style guides, whose frontmatter devkit get-context lists in every agent context so agents read a body when a decision concerns it, and moves the glossary into it.
status: planned
created: 2026-10-26
depends_on:
  - SPEC-table-driven-document-kinds
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-foundation-documents] Steering documents for project-wide background

## 1. Problem Statement & Motivation

Handed off from proposal PROP-foundation-documents on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-foundation-documents`

### 1. Background & Hypothesis

The Living Spec has kinds for behavior and structure (capabilities, use cases, architecture, decisions) and a free
form for evidence (materials). It has no place for project-wide background that applies to every piece of work but
is neither behavior nor evidence: the product's purpose and principles, a brand or tone guide, a visual style
direction, a domain or setting overview. The glossary is the only document of this nature today, and it sits alone
at `docs/glossary.md` (with `docs/glossary.yaml` for search synonyms).

Without a place, such background is written into capabilities, where it bends the contract shape and invites
entrypoints and reconciliation that do not apply, or into materials, where it loses its standing as current and
binding. Either way agents do not know to read it, so work that depends on it (wording, naming, interface and
content decisions) drifts from it.

Hypothesis: one flat `docs/steering/` directory of ID-free steering documents, one file per topic, fixes both
problems when every agent context sees what each file covers. `devkit get-context spec` prints each steering file's
frontmatter (title and a one-line scope) at run time, so the list is always current and always loaded, and an agent
reads a body only when its decision concerns that scope. A rule bounds the number of files and each body's size, so
the always-loaded cost stays small. The glossary moves into the directory.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Steering documents for project-wide background so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

Answered in `docs/materials/2026-10/20261026-foundation-documents/spike-findings.md` (F1-F6, round 1) and `docs/materials/2026-10/20261026-foundation-documents/steering-design.md` (round 2).

- **Q1**: Name and layout. Settled by the `user`: `docs/steering/`, flat, one Markdown file per topic.
- **Q2**: What the spec rules check in steering files: `RULE-steering-documents` (shape, frontmatter, caps) and the
  cited-ID check of `RULE-document-reference` (`user`, answer-02).
- **Q3**: How agents read the group. Settled by the `user`: progressive loading through `devkit get-context`
  (`ADR-background-pointer-in-constitution`).
- **Q4**: What moves with the glossary: every consumer of spike F3.

### 3. Proposed Design & Impact

- **Directory** (`ADR-steering-documents-directory`): `docs/steering/` (created under `docs/`) holds one Markdown
  file per topic (for example `glossary.md`, `product.md`, `style.md`) and the glossary's `glossary.yaml`; no
  subdirectories and no namespace copy. Files carry frontmatter `title` and `summary` (the one-line English scope) and
  no `id`, so they stay outside the document index (`CAP-DOCS-document-model` rule 3.2). Documented in
  `CAP-DOCS-document-model`; the glossary gains the row **Steering document** (Avoid: foundation, background).
- **Loading** (`ADR-background-pointer-in-constitution`): every steering file's `title` and `summary` are always
  loaded; bodies are read only when a decision concerns that scope. One constitution line names `docs/steering/` and
  states that trigger. The `scout`, `challenger` and `reconcile-reviewer` contracts (`bundle/subagents/`) run
  `devkit get-context spec` instead of reading the managed `AGENTS.md`, as `code-reviewer` already does, and a guidance
  test asserts that every role contract loads the spec context.
- **Bundle context** (`ADR-bundle-context-lists-project-documents`): the `spec` bundle's manifest declares
  `docs/steering` as a context document directory, and `devkit get-context <bundle>` adds `documents` (`path`,
  `title`, `summary` per Markdown file, read from the workspace at run time, not rendered by sync) to its result.
  `devkit-dist` reads only the directory the manifest names and knows nothing of steering
  (`CAP-DIST-context-and-playbooks`, `CAP-DIST-manifest-spec`). The field follows the seeded `target` grammar; the
  declaration is read from the receipt-verified managed `bundle.toml`; only regular, non-symlink `*.md` files other
  than `README.md` directly inside a non-symlinked directory are listed, from a header prefix of at most 4096 bytes;
  unreadable, non-UTF-8 or non-string values become `null`, never an error. `documents` is always present (`[]` when
  undeclared or absent), with absolute `path`, sorted by path. `CAP-DIST-workspace-ownership` is amended: seeded
  files are never receipt-verified context files, but a declared context directory may list project files, seeded
  ones included. One test per case, plus a test of the output size at the default caps.
- **Bounds** (`user`, answer-03): a new spec rule `RULE-steering-documents` (under
  `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/`), error severity, reports in `docs/steering/` a
  subdirectory, a file other than `*.md` and `glossary.yaml`, an `id`, a missing `title`, a missing or non-English
  `summary` longer than its own `max_summary_length` (default 300), each Markdown file beyond `max_files` in sorted
  order (so a commit adding the overflowing file is refused at the gate), and a body (the text after the frontmatter)
  over `max_body_bytes`. `README.md` is neither counted nor listed. Settings `max_files` (default 10), `max_body_bytes` (default
  24576, for every file, the glossary included) and `max_summary_length` (default 300); a project raises a setting
  when it needs more; one test per case, including a staged commit for the count. Documented in
  `CAP-GOV-spec-rules`.
- **Cited IDs** (`user`, answer-02): `RULE-document-reference` resolves backtick-quoted IDs in steering files the way
  it resolves root glossary Owners: they must resolve, aliases are reported, no autofix and no graph edges; a test
  covers an unresolved ID, an alias and a resolved ID. Documented in `CAP-GOV-spec-rules`.
- **Glossary move** (`user`): `glossary.md` and `glossary.yaml` move to `docs/steering/`, the glossary gaining the
  steering frontmatter; the repository's own glossary moves in the same change; no migration and no notice for
  existing consumers (`AGENTS.md` Compatibility). Each literal path of spike F3 is one acceptance item with a test
  that the old path is no longer read: the `RULE-document-reference` Owner check, search `GLOSSARY_PATH` and
  `SPEC_GLOSSARY_INVALID` (`base/errors.py`), the `docs-skeleton` seed and its README tables, `living-spec-writing`,
  `architecture-writing`, `spec-sync`, `adr-compaction`, the brownfield `migration.md`, rule guides, viewer
  `bookGroup` (see Viewer), `docs/README.md`,
  `docs/architecture/README.md` and the capabilities naming the path (`CAP-DOCS-document-model`,
  `CAP-DOCS-document-search`, `CAP-GOV-spec-rules`, `CAP-HARN-agent-guidance`, `CAP-DLV-release-handbook`,
  `CAP-DLV-delivery-workflows`). Package glossaries stay at `docs/packages/<name>/glossary.md`, read together with
  the root glossary. The receipt `.devkit/installation.json` follows `devkit sync`. The handoff ADR declares that it
  amends the glossary paths that `ADR-spec-package-on-devkit` and `ADR-writing-and-terminology-guidance` fix.
- **Release handbook**: `scripts/handbook.py` reads the glossary at the pinned commit from `docs/steering/`, falls
  back to `docs/glossary.md` for a commit before the move, and fails with a code when neither exists; its tests cover
  both layouts. The handbook pages are not refreshed.
- **Viewer** (`policy`, Host addition): `bookGroup` in `packages/devkit-viewer/frontend/src/lib/api/documents.ts`
  replaces its literal `docs/glossary.md` with one `Steering` book group for every file under `docs/steering/`, in
  place of the `Glossary` group in `bookGroups`, defined as a viewer literal because steering is not a kind; a
  package glossary `docs/packages/<name>/glossary.md` also lands in `Steering`; a front-end test next to it asserts
  that `docs/steering/glossary.md`, another steering file and a package glossary land in `Steering` and that
  `docs/glossary.md` is no longer special. The committed build
  under `packages/devkit-viewer/src/devkit_viewer/static/` is rebuilt (`just viewer build`). This proposal owns the
  fix because `SPEC-table-driven-document-kinds` excludes the viewer.
- **Search** (`user`): unchanged. Steering files are not search candidates; glossary synonym expansion reads the
  moved `glossary.yaml`.
- Non-goals: no new ID-bearing kind, no relation fields to or from steering documents, no change to the glossary
  table columns, the Owner check's semantics, document search or the ranker, and no namespace steering directory.

#### Order with parallel proposals

- `SPEC-table-driven-document-kinds` lands first (`depends_on`); it is accepted and handed off, its spec now in
  Development. At this proposal's handoff the dependency names that spec, whose ID this branch cannot resolve yet. Steering is not a kind and adds no row; where this
  proposal touches the rules, it builds on the table's definitions instead of adding constants beside them. That
  proposal excludes the viewer, so the viewer grouping is this proposal's alone.
- `PROP-ux-documentation` follows this proposal (`user`, answer-02; the Host adds this proposal to its `depends_on`),
  so its guidance names the glossary at
  `docs/steering/glossary.md` and points to steering style documents instead of restating them; its option 6b (an
  object table in the glossary) would change the glossary table format, which this proposal excludes.

#### Planning decisions

- `policy`: search citation corrected to `CAP-DOCS-document-search`; owns extended to every path spike F3 names;
  `depends_on` on `SPEC-table-driven-document-kinds` per the user's ordering decision.
- `user` (answer-01): name `steering`; one flat directory; progressive loading through `devkit get-context spec` at
  run time; a rule caps file count and body size so the glossary fits; the glossary moves; search unchanged.
- `policy`: no namespace steering directory: no registered namespace exists here, package glossaries already have
  their place (`living-spec-writing`), and get-context lists one directory per bundle declaration.
- `user` (answer-02, answer-03): cited IDs in steering files are checked like glossary Owners; UX follows this
  proposal; caps `max_files` 10 and `max_body_bytes` 24576 for every file.
- `policy` (challenger-02): every spec role loads the context through get-context; read and path-safety rules,
  output shape and the workspace-ownership amendment specified; rule scope defined; package glossaries keep a viewer
  group.
- `policy`: the get-context change is a manifest-declared directory, not a steering path in `devkit-dist`, because the
  base harness stays SDD-agnostic (`ARCH-05-1-containers` section 2.4).

### 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-foundation-documents`; the proposal is deleted there and its decisions become ADRs.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

