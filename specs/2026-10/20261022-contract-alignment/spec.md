---
id: SPEC-contract-alignment
title: Align ADRs and alias wording with the shipped contracts
summary: Supersedes the package ownership and high-effort review loop ADRs with decisions that match the code and the bundled review loop, and states the document alias case in the contracts and mirrors that still describe exact IDs only.
status: completed
created: 2026-10-22
related_capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-DLV-spec-bundles
  - CAP-TRACE-code-entrypoints
  - CAP-DIST-manifest-spec
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-contract-alignment] Align ADRs and alias wording with the shipped contracts

## 1. Problem Statement & Motivation

Three Living Spec statements no longer describe what ships:

- `ADR-dist-foundation-ownership` says `devkit-dist` MUST own the shared foundation. The foundation is the
  `devkit-core` wheel (`devkit_core`, with `base` and `core`), and the `mcp` extra is declared by `devkit-agt`
  (`devkit-agt[mcp]` requires `devkit-mcp`), not by `devkit-dist`. No ADR records either change.
- `ADR-bounded-high-effort-review-loop` sends a contested P1 to the user as a `worker` question and closes a P1 the
  user rules invalid by a waiver citing the `answer` envelope. The shipped `spec` skill reference `review-loop.md`
  section 4 makes it a Host-owned `problem`, gives a Host-directed recovery the extra round and adds no user approval
  gate. `CAP-DLV-delivery-workflows` rule 7 still states the ADR's rule. The user decided that the shipped bundle rule
  holds.
- `CAP-DOCS-document-model` section 3.5 rule 6 makes an alias declaration count as a declaration and lets ID arguments
  resolve aliases, but `CAP-DLV-spec-bundles`, `CAP-TRACE-code-entrypoints`, `CAP-DIST-manifest-spec`, the bundled
  devkit `consumption` instruction and `docs/glossary.md` still describe exact IDs only.

An agent that reads these documents acts on rules the code does not apply.

### Source feedback

- `FB-package-ownership-adrs-lag-code`: record the foundation move to `devkit-core` and the `mcp` extra placement in
  an ADR that supersedes `ADR-dist-foundation-ownership`.
- `FB-review-loop-adr-disagrees-with-bundle`: record the shipped bounded-recovery rule in an ADR that supersedes
  `ADR-bounded-high-effort-review-loop`, and align `CAP-DLV-delivery-workflows`.
- `FB-alias-wording-outside-scope`: add explicit alias wording to `CAP-DLV-spec-bundles` (rule 3 and the
  `SPEC_EXISTS` row), `CAP-TRACE-code-entrypoints` (`--target`), `CAP-DIST-manifest-spec` (the playbook kind summary
  and alias uniqueness at bundle validation), the devkit bundle `consumption` instruction (playbook get by a declared
  alias) and `docs/glossary.md` (an alias term).

### Assumptions

1. The successor ADRs carry over every statement of the superseded ADRs that still holds, so a reader needs only the
   successor; the superseded files keep their text and gain the superseded status and pointer
   (`ADR-immutable-decisions-editable-records`).
2. References elsewhere that cite a superseded ADR for its current rule are repointed to the successor; references in
   completed spec bundles, materials and test docstrings stay as written (history, or outside the write scope).
3. The glossary gets one `Alias` row in its distribution section, owned by `CAP-DOCS-document-model`, with "search
   keyword" as the rejected synonym, because `ADR-playbook-aliases-as-identifiers` retired the keyword meaning.

## 2. User Stories

- **US-1**: As an agent reading the decision records, I want the in-effect ADRs on package ownership to name
  `devkit-core` as the foundation owner and `devkit-agt[mcp]` as the MCP extra, so that I do not place shared code or
  extras in the wrong wheel.
- **US-2**: As a worker or Host running a `high` review loop, I want the ADR, the capability and the bundled
  `review-loop.md` to state one hand-over rule, so that a contested P1 becomes a Host-owned `problem` without an
  extra user approval gate.
- **US-3**: As an agent calling `devkit spec new`, `devkit spec entrypoints --apply --target` or
  `devkit playbook get`, or validating a bundle, I want each contract to state how aliases behave, so that I do not
  have to infer it from `CAP-DOCS-document-model`.

## 3. Non-Goals

1. **Scope Excluded**: no production code, test, bundle behavior or `review-loop.md` change; only documents and the
   devkit bundle's `consumption` instruction text.
2. **Scope Excluded**: no edit to completed spec bundles, materials, `ADR-medium-review-delegation` or
   `ADR-package-split-and-namespaces` beyond the link repairs listed in `PLAN-contract-alignment`.
3. **Scope Excluded**: no new alias behavior; the documents state only what the code already does.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Foundation ownership successor ADR
- **Given** the `pyproject.toml` files of `devkit-core`, `devkit-dist`, `devkit-agt` and `devkit-mcp`
- **When** the accepted ADR that supersedes `ADR-dist-foundation-ownership` is read
- **Then** it states that `devkit-core` (`devkit_core`) owns the shared foundation, that `devkit-agt` declares the
  `mcp` extra requiring `devkit-mcp` and `devkit-dist` declares none, and it carries over the standalone scope, the
  sole `devkit` executable and the dependency direction; `ADR-dist-foundation-ownership` has `status: superseded` and
  `superseded_by` naming the successor.

### [AC-02] Review loop successor ADR
- **Given** section 4 of the `spec` bundle's `review-loop.md`
- **When** the accepted ADR that supersedes `ADR-bounded-high-effort-review-loop` is read
- **Then** it states that a contested P1 still asserted after one more round is a `problem` in the `worker` envelope,
  that the Host owns recovery within the authorized goal, scope and constraints and recovery adds no user approval
  gate, and that changing an acceptance criterion or waiving an agreed constraint needs the user's decision; it
  carries over the remaining rules of the superseded ADR, which has `status: superseded` and `superseded_by` naming
  the successor.

### [AC-03] Delivery workflows agree with the review loop
- **Given** `CAP-DLV-delivery-workflows`
- **When** rules 7 and 15 are read
- **Then** neither states a `worker` question for a contested P1 nor a waiver citing an `answer` envelope, rule 7
  states the Host-owned `problem` and the Host-directed recovery round, and rule 15 cites the successor ADR.

### [AC-04] Alias wording in the contracts and mirrors
- **Given** `index.declares` in `devkit spec new`, `index.resolve` in `devkit spec entrypoints --apply --target`,
  `_check_playbook_aliases` at bundle validation and alias selection in `devkit playbook get`
- **When** `CAP-DLV-spec-bundles` rule 3 and its `SPEC_EXISTS` row, `CAP-TRACE-code-entrypoints` `--target`,
  `CAP-DIST-manifest-spec` (the playbook kind and the validation rules), the devkit `consumption` instruction and
  `docs/glossary.md` are read
- **Then** each states the alias case its code implements, consistent with `CAP-DOCS-document-model` section 3.5
  rule 6, and the glossary defines `Alias` with "search keyword" under Avoid.

### [AC-05] References and checks hold
- **Given** the changed documents and the repointed references
- **When** `uv run devkit rules check`, `uv run devkit sync --check`, `just test-affected` and `git diff --check` run
- **Then** each exits `0`, and no current document outside history cites a superseded ADR of this change for its
  current rule.
