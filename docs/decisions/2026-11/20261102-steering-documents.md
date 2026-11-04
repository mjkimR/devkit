---
id: ADR-steering-documents
title: Steering documents in one directory, listed in every context
summary: "For background without a Living Spec place, we keep ID-free steering files in one flat docs/steering/ directory and list their titles and summaries in every context through a bundle-declared directory, reading bodies on demand, to keep it visible at bounded cost, accepting agent judgment on reading."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-steering-documents-directory
  - ADR-background-pointer-in-constitution
  - ADR-bundle-context-lists-project-documents
---

# [ADR-steering-documents] Steering documents in one directory, listed in every context

Superseded in part by `ADR-namespace-steering-directories`: For a registered namespace that needs package background, we check docs/packages/<name>/steering/ under the root steering contract and list it in a context through a devkit-docs provider selected by the working directory, to keep background visible at bounded cost, accepting one more entry point.

Superseded in part by `ADR-retire-native-approval-and-moved-ownership-clauses`: the listing of steering documents through `devkit get-context spec` and its reach through the spec context.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `docs/steering/`, `CAP-DIST-manifest-spec`, `CAP-DIST-context-and-playbooks`,
  `CAP-DIST-workspace-ownership`

---

## 1. Context & Problem Statement

Project-wide background (product purpose, tone, style direction, a domain overview) has no place in the Living Spec:
written into capabilities it bends the contract shape, written into materials it loses its standing as current. The
glossary was the only such document and sat alone at `docs/glossary.md`. "Foundation" was the draft's name, but it
already names devkit's lowest code layer (`devkit-core`, `ARCH-05-1-containers`).

Steering documents apply to wording, naming, interface and content decisions in every activity, Development workers
and nested roles included. Agents read background only when they know what exists and when it applies. Loading every
body into every context has no bound; the `spec` skill's intake never reaches workers (`spec` skill, Route step 1);
`living-spec-writing` is read only before writing documents. Every role loads `devkit get-context spec` once per agent
context.

The list must be current at run time (`user`). `devkit get-context <bundle>` already runs once per agent context and
returns the constitution and instruction headers, but it is part of `devkit-dist`, which stays SDD-agnostic
(`ARCH-05-1-containers` section 2.4). Options and costs are compared in
`docs/materials/2026-10/20261026-foundation-documents/steering-design.md` D1.

---

## 2. Decision Drivers

- One known place per repository that agents and people find without search. (ADR-steering-documents-directory)
- No new document kind, ID or relation fields. (ADR-steering-documents-directory)
- A name free of existing repository vocabulary. (ADR-steering-documents-directory)
- Every role sees what steering covers, workers and nested roles included. (ADR-background-pointer-in-constitution)
- A bounded, small always-loaded cost. (ADR-background-pointer-in-constitution)
- A mechanical check that the trigger and the bounds exist. (ADR-background-pointer-in-constitution)
- The list is current at run time, without a sync. (ADR-bundle-context-lists-project-documents)
- `devkit-dist` holds no SDD concept or path. (ADR-bundle-context-lists-project-documents)
- Loading a context never fails because of a project document. (ADR-bundle-context-lists-project-documents)

---

## 3. Considered Options

### Directory
- **One flat `docs/steering/` directory, glossary inside** (selected in `ADR-steering-documents-directory`): one
  Markdown file per topic, ID-free, with `title` and `summary` frontmatter; `glossary.md` and `glossary.yaml` move in;
  no subdirectories and no namespace copy. Pros: one place; the glossary is its first member; nothing enters the
  document index. Cons: about twenty literal glossary paths change
  (`docs/materials/2026-10/20261026-foundation-documents/spike-findings.md` F3); existing consumers of the seed receive
  a new glossary path.
- **ID-free background files at the existing docs root** (rejected in `ADR-steering-documents-directory`): no new
  directory; a pointer names each file. Smallest change and the glossary stays, but background mixes with
  `docs/README.md` and other root files; no directory to list.
- **A per-namespace copy as well** (rejected in `ADR-steering-documents-directory`): `docs/packages/<name>/steering/`
  beside the root directory gives package-specific background, but no registered namespace needs it today and it
  multiplies the always-loaded list.

### Loading
- **Progressive loading: frontmatter always, bodies on demand** (selected in
  `ADR-background-pointer-in-constitution`): every role knows what exists at the cost of a short list; bodies cost
  nothing until needed. Cons: whether an agent applies the trigger is judgment.
- **A constitution pointer to the directory only** (rejected in `ADR-background-pointer-in-constitution`): one line
  names `docs/steering/`; no get-context change, but the agent does not know which files exist or what they cover
  without listing the directory.
- **Load every body** (rejected in `ADR-background-pointer-in-constitution`): no judgment, but unbounded cost in every
  context, reviewers included.
- **Search only** (rejected in `ADR-background-pointer-in-constitution`): an agent does not search for what it does not
  know exists; steering files are not search candidates.

### Listing mechanism
- **A manifest-declared context document directory** (selected in `ADR-bundle-context-lists-project-documents`): data,
  not code; any bundle can use it; the list is read at run time. Cons: a new manifest field and result key.
- **An entry-point context provider** (rejected in `ADR-bundle-context-lists-project-documents`): `devkit-spec`
  registers a provider that `get-context` calls; arbitrary content, but a plugin contract and package code running
  inside every context load, beyond the need.
- **A literal `docs/steering` in `devkit-dist`** (rejected in `ADR-bundle-context-lists-project-documents`): smallest
  change, but puts an SDD path into the SDD-agnostic package.
- **Sync renders the list into the constitution** (rejected in `ADR-bundle-context-lists-project-documents`): no
  get-context change, but stale between syncs; the `user` chose run-time reading.

---

## 4. Decision Outcome

Steering documents live in one flat `docs/steering/` directory; their frontmatter is listed in every context through a
bundle-declared context document directory and their bodies are read on demand.

### Directory

- Project background lives in one flat `docs/steering/` directory: one Markdown file per topic, ID-free, with `title`
  and `summary` frontmatter; `glossary.md` and `glossary.yaml` move in; no subdirectories and no namespace copy
  (`user`). The directory gives background one known place as ID-free files, and "steering" collides with no existing
  term. (ADR-steering-documents-directory)
- Package glossaries stay at `docs/packages/<name>/glossary.md`. (ADR-steering-documents-directory)

### Loading

- Superseded in part by `ADR-retire-native-approval-and-moved-ownership-clauses`: the `get-context spec` listing and the steering list
  reaching role contracts through the spec context, in the next two items and in the matching Confirmation item.
- `devkit get-context spec` lists each steering file's `title` and `summary` (its one-line scope) in every context; one
  constitution line names `docs/steering/` and tells the agent to read a body before a decision that concerns its
  scope; every spec role contract loads the context through `devkit get-context spec`; `RULE-steering-documents` caps
  the number of files (default 10) and each body's size (default 24576 bytes), both settings a project can raise
  (`user`). (ADR-background-pointer-in-constitution)
- The list reaches every role that loads the spec context, its size is bounded by the caps and the summary length, and
  a guidance test plus the rule check both. (ADR-background-pointer-in-constitution)

### Listing mechanism

- A bundle's `bundle.toml` names one workspace directory; `get-context` adds `documents` (`path`, `title`, `summary` of
  each Markdown file directly in it) to its result, read under the shared project lock. It reads at run time from a
  directory the bundle names, so `devkit-dist` knows no steering path. (ADR-bundle-context-lists-project-documents)
- A file with malformed frontmatter or a missing `title` or `summary` is listed with `null` for the missing value,
  never an error; `RULE-steering-documents` reports it. (ADR-bundle-context-lists-project-documents)
- The `docs` bundle declares `docs/steering`. (ADR-bundle-context-lists-project-documents)
- Read rules: the field follows the seeded `target` grammar; get-context reads the declaration from the
  receipt-verified managed `bundle.toml`; it lists only regular, non-symlink `*.md` files other than `README.md`
  directly inside a non-symlinked directory, reading at most a 4096-byte header prefix; `documents` is always present
  (`[]` when undeclared or absent), with absolute `path`, sorted. `CAP-DIST-workspace-ownership` is amended so a
  declared context directory may list seeded files. (ADR-bundle-context-lists-project-documents)

---

## 5. Consequences

- **Positive**:
  - Background has a place; the glossary gains the row **Steering document** (Avoid: foundation, background).
    (ADR-steering-documents-directory)
  - Steering is visible everywhere at a cost of about 400 bytes per file
    (`docs/materials/2026-10/20261026-foundation-documents/steering-design.md` D2).
    (ADR-background-pointer-in-constitution)
  - One mechanism for any bundle that needs project documents in context.
    (ADR-bundle-context-lists-project-documents)
- **Amends**: the root glossary paths `docs/glossary.md` and `docs/glossary.yaml` that `ADR-document-system` and
  `ADR-writing-and-terminology-guidance` name are now `docs/steering/glossary.md` and `docs/steering/glossary.yaml`;
  their decisions otherwise stand. (ADR-steering-documents-directory)
- **Negative / Risks**:
  - A missed glossary path fails silently; each is an acceptance item with a test. Existing consumers move their
    glossary by hand (no migration, `AGENTS.md` Compatibility). (ADR-steering-documents-directory)
  - An agent may skip a relevant body; the scope summary makes the relevance visible but does not prove it was read.
    (ADR-background-pointer-in-constitution)
  - A large directory raises every context's cost; the spec rule caps it, but `devkit-dist` itself enforces no cap.
    (ADR-bundle-context-lists-project-documents)
- **Follow-ups**:
  - A namespace copy when a registered namespace needs package background that its package glossary cannot hold.
    (ADR-steering-documents-directory)
  - If reviews show drift from steering despite the list, consider a review step that names the steering files a
    change's wording depends on. (ADR-background-pointer-in-constitution)
  - None for the listing mechanism. (ADR-bundle-context-lists-project-documents)

---

## 6. Confirmation

- `RULE-steering-documents` (shape, frontmatter, caps `max_files` 10 and `max_body_bytes` 24576);
  `RULE-document-reference` for IDs cited in steering files; tests under `packages/devkit-spec/tests/` that the Owner
  check and synonym expansion read `docs/steering/` and no longer `docs/glossary.md`; the handbook script tests in
  `tools/devkit-dev/tests/integration/test_handbook_script.py` for both layouts. (ADR-steering-documents-directory)
- Superseded in part by `ADR-retire-native-approval-and-moved-ownership-clauses`: the role-contract part of the next item.
- A guidance test under `packages/devkit-spec/tests/integration/bundles/spec/` asserts the constitution line, its
  trigger and that every role contract under `subagents/` loads the spec context; `RULE-steering-documents` checks the
  caps and frontmatter; a test under `packages/devkit-dist/tests/` asserts the size of the `documents` output at the
  default caps and the maximum summary length. (ADR-background-pointer-in-constitution)
- Tests under `packages/devkit-dist/tests/` for the manifest field's validation and for `documents` in the
  `get-context` result (present, undeclared, absent directory, symlinked directory or file, non-regular entry,
  non-UTF-8, oversized file, malformed frontmatter, non-string values, order); `CAP-DIST-manifest-spec` and
  `CAP-DIST-context-and-playbooks` document both. (ADR-bundle-context-lists-project-documents)
