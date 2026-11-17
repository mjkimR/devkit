---
id: SPEC-adr-body-metadata-removal
title: Remove the ADR body metadata block and trim the ADR template
summary: Drop the Status/Date/Deciders/Involved block from the ADR template, the proposal scaffold and the handoff acceptance rewrite, since the frontmatter already owns status, date and supersession, and shorten the option and separator scaffolding to what decision-writing asks for.
status: completed
created: 2026-11-17
related_capabilities: [CAP-DLV-proposal-planning, CAP-DLV-proposal-lifecycle]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adr-body-metadata-removal] Remove the ADR body metadata block and trim the ADR template

## 1. Problem Statement & Motivation

Handed off from proposal PROP-adr-body-metadata-removal on 2026-11-17.
- **Preserved Materials**: `docs/materials/2026-11/20261117-adr-body-metadata-removal`

### 1. Background & Hypothesis

The ADR template (`templates/decision.md`) puts a metadata list under the H1: `- **Status**`, `- **Date**`,
`- **Deciders**` and `- **Involved Components/Capabilities**`.

- Status and Date repeat the frontmatter `status` and `created_at`; the superseded form ("Superseded by" plus an ADR ID)
  repeats `superseded_by`. In the 71 of 94 ADRs that carry the block at the proposal's base, both values agree with
  the frontmatter.
- Deciders appears in 27 of 94 ADRs and Involved Components in 45; nothing parses either line, but backticked IDs in
  Involved Components lines count as body references for `devkit docs refs` and the viewer's reference panel.
- No rule enforces the block, but code keeps the copy alive: the proposal scaffold (`scaffold.py`) writes it for PADRs,
  and handoff acceptance (`_accept_status` in `handoff.py`) rewrites the body Status line in step with the frontmatter.
  Tests pin both (`test_proposal_handoff.py`, `test_proposal_scaffold.py`).

The same template scaffolds per-option Overview/Pros/Cons although `decision-writing.md` asks for one or two lines per
option with its main trade-off, and separates every section with `---`.

Hypothesis: the frontmatter is the single owner of status, date and supersession; removing the body copy removes a
synchronization path in code and a field authors fill by rote. `ADR-frontmatter-only-decision-status` records the
decision.

Kept: the "Superseded in part by" body lines (they name replaced clauses, which the frontmatter cannot), Decision
Drivers, Confirmation and the outcome-trace comments (test-enforced).

## 2. User Stories

- **US-1**: As an agent writing an ADR or PADR, I want a template without a body status, date, deciders or components
  block and with one line per option, so that I fill only fields a reader or tool uses.
- **US-2**: As an agent handing off a proposal, I want promotion to change only the frontmatter status and to drop the
  block a pre-upgrade scaffold wrote, so that no ADR reaches the ledger with a stale body status.
- **US-3**: As a reader of `docs/decisions/`, I want every ADR to state its status only in the frontmatter, so that no
  body copy disagrees with it after a later supersession.

## 3. Non-Goals

1. **Scope Excluded**: the option layout and `---` separators of existing ADRs; rewriting them is a per-ADR edit, not
   a mechanical one.
2. **Scope Excluded**: any rule or check that forbids the block; no reader parses it, and the template, scaffold and
   handoff stop producing it.
3. **Scope Excluded**: "Superseded in part by" lines, Decision Drivers, Confirmation and the outcome-trace comments;
   they stay as they are.
4. **Scope Excluded**: other formal templates and documents, which `SPEC-formal-doc-padding-trim` already changed.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The decision template has no metadata block, separators or per-option scaffolding
- **Given** the docs bundle template `templates/decision.md`
- **When** `uv run pytest packages/devkit-docs/tests/integration/bundles/docs/test_decision_template.py` runs
- **Then** it exits `0`, asserting that the template body has no `- **Status**`, `- **Date**`, `- **Deciders**` or
  `- **Involved Components/Capabilities**` line, no `---` line after the frontmatter and no `**Overview**`,
  `**Pros**` or `**Cons**` text, and that Considered Options carries one `- **<Option>** (selected): ` line and one
  `- **<Option>**: ` line.

### [AC-02] decision-writing names the frontmatter as the only status owner and asks to mark the selected option
- **Given** `instructions/decision-writing.md`
- **When** the same test runs
- **Then** it asserts that the instruction states that status, date and whole supersession live only in the
  frontmatter, with no body metadata line, and that Considered Options marks the selected option; its "one or two
  lines per option" rule stays and the existing decision guidance tests pass.

### [AC-03] The PADR scaffold writes no body metadata
- **Given** an empty workspace with a proposal
- **When** `devkit spec proposal padr` scaffolds a PADR
- **Then** the PADR has no `- **Status**` or `- **Date**` line and no `---` after the frontmatter, and its H1 is
  followed by one blank line and `## 1. Context & Problem Statement`
  (`test_proposal_scaffold.py`).

### [AC-04] Promotion accepts only the frontmatter and deletes the legacy scaffold block
- **Given** an accepted proposal whose PADR carries, in the first list after its H1, the legacy block
  `- **Status**: Draft` (or `Proposed`), `- **Date**: <date>` and a following `---`
- **When** `devkit spec proposal handoff` promotes it
- **Then** the ADR has `status: accepted`, no `- **Status**` or `- **Date**` line below its H1 and no `---` left from
  the block, and its H1 is followed by one blank line and the first section heading.
- **And** a `- **Status**: Draft` line in a fenced example or an HTML comment stays byte-identical, a PADR without the
  block is promoted with its body unchanged apart from the ID rename, and no body line `- **Status**: Accepted` is
  written (`test_proposal_handoff.py`).

### [AC-05] Existing ADRs carry no body metadata block and keep their reference edges
- **Given** every ADR under `docs/decisions/` at the Development head
- **When** `rg -n '^- \*\*(Status|Date|Deciders|Involved Components/Capabilities)\*\*' docs/decisions` runs
- **Then** it reports only the milestone lifecycle item of `ADR-roadmap-and-milestones-ledger`; every
  "Superseded in part by" line stays; each backticked ID that only an Involved Components line named appears in one
  Context sentence "This decision involves `<ID>`, …."; `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` ends
  its Context with its provenance sentence; and `uv run devkit rules check docs/decisions` reports no violation.

### [AC-06] The Living Spec states the frontmatter-only status
- **Given** `CAP-DLV-proposal-planning` §4.4, `CAP-DLV-proposal-lifecycle` §4.1 step 4 and `DESIGN-proposal-handoff`
- **When** `rg -n 'Status\*\*' docs/capabilities/delivery/CAP-DLV-proposal-planning.md docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md docs/designs/delivery/DESIGN-proposal-handoff/design.md` runs
- **Then** it reports only the legacy-block sentences: §4.4 states that the PADR body carries no Status, Date, Deciders
  or Involved Components line (MUST), step 4 states that promotion changes only the frontmatter status and deletes
  the legacy scaffold block (MUST), and the design's ADR-promotion observed-run row no longer cites a body status.

### [AC-07] Verification passes
- **Given** the final Development head
- **When** `just lint-check`, `uv run devkit generated check`, `uv run devkit rules check --ci --base main` and
  `just test-affected --base main` run
- **Then** each exits `0`, and `uv run devkit sync --check` exits `0` after the committed sync output.

## 5. Planning decisions

Each answer is a Planning decision and binds Development; `ADR-frontmatter-only-decision-status` records Q1-Q3.

- **Q1**: Existing ADRs: remove the block from all of them in one mechanical pass, or leave them and only stop writing
  it?
  - **Answer**: remove it, in one mechanical pass that Development runs at its own HEAD (after
    `SPEC-formal-doc-padding-trim` integrates, so any ADR promoted in between is covered). A wording and metadata
    repair the `docs/decisions/` ledger allows without a superseding ADR.
- **Q2**: Does any reader parse the body Status line?
  - **Answer**: no reader parses the Status, Date or Deciders lines; backticked IDs in Involved Components lines are
    body references, so the Q1 pass keeps those edges
    (`docs/materials/2026-11/20261117-adr-body-metadata-removal/body-status-readers.md`).
- **Q3**: Where do "Superseded in part by" lines sit once the block is gone?
  - **Answer**: directly under the H1, each a paragraph of its own, as the handoff already writes them; the template
    comment under the H1 stays as the authoring cue.
- **Q4**: Option scaffolding.
  - **Answer**: one list item per option, `- **<Option>** (selected): <main trade-off against the drivers>.` for the
    chosen one and `- **<Option>**: <main trade-off against the drivers>.` for the others, under a comment pointing to
    `decision-writing`; every `---` separator in the template body goes. Existing ADRs keep their option layout and
    separators.
- **Reference edges** (user at `plan-accept`): when an Involved Components line names a backticked ID that the rest of
  the body does not mention, one sentence at the end of Context & Problem Statement keeps it: "This decision involves
  `<ID>`, …." Plain path or skill names in those lines are dropped.
- **Handoff compatibility** (user at `plan-accept`): promotion keeps a deletion-only pass for the legacy scaffold
  block. It deletes only the first visible `- **Status**: Draft` or `Proposed` line in the first list after the H1, a
  `- **Date**:` line directly after it, and a `---` that is the next non-blank line when that list is left empty;
  fenced, indented and commented lines stay. `ADR-frontmatter-only-decision-status` names its removal condition.

### Mechanical pass over existing ADRs

In the first list after the H1 (before `## 1.`), the pass removes each item starting with `- **Status**:`,
`- **Date**:`, `- **Deciders**:` or `- **Involved Components/Capabilities**:`, together with that item's indented
continuation lines. Every other line stays where it is. When the list is left empty, its surrounding blank lines
collapse to one, and a `---` that is the next non-blank line goes with it. When items remain, the list and its `---`
stay. Handled by name:

- `ADR-ux-screens`: its three "Superseded in part by" list items stay as the list.
- `ADR-dual-source-of-truth-and-periodic-reconciliation`: its `- **Follow-up**` item stays as the list.
- `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation`: its Deciders provenance becomes one sentence at the end of
  Context & Problem Statement: "Decided by the user on the rejection of ~~`PROP-direct-devkit-invocation`~~ (Git
  `4672a101eec0`)."
- `ADR-orchestration-workers`: prose follows the block before its `---`, so the `---` stays.
- A `- **Status**:` item elsewhere in a body (the milestone lifecycle item of `ADR-roadmap-and-milestones-ledger`) is
  not in the first list and stays.

### Design, domain and operations assessment

- Design: `DESIGN-proposal-handoff` is affected. Its observed ADR-promotion row claims the promoted ADR has
  `- **Status**: Accepted`. Source identity: `handoff.py` `_accept_status`. Statement owner:
  `CAP-DLV-proposal-lifecycle` handoff step 4; the design only illustrates it. Maintenance action: edit that row only.
- Domain: unaffected. No document under `docs/domain/` names the body block.
- Operations: unaffected. No document under `docs/operations/` reads or repairs the block.
