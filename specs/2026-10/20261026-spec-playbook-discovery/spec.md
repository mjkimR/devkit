---
id: SPEC-spec-playbook-discovery
title: Task-aware playbook discovery through spec
summary: Lets spec run one bounded playbook search at new task intake and offer a matching playbook in one line that the user confirms, with explicit skip cases; the generated devkit-playbook skill stays the generic explicit entry.
status: in-progress
created: 2026-10-26
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-DIST-context-and-playbooks
  - CAP-DLV-drift-reconciliation
  - CAP-DLV-weekly-report
related_usecases:
  - UC-reconcile-living-spec-drift
  - UC-inspect-weekly-repository-progress
workflow: sdd-spec-feature
---

# [SPEC-spec-playbook-discovery] Task-aware playbook discovery through spec

## 1. Problem Statement & Motivation

Handed off from proposal PROP-spec-playbook-discovery on 2026-10-26.

- **Preserved Materials**: `docs/materials/2026-10/20261026-spec-playbook-discovery` (discovery evidence, intake
  frequency, intake probe data).
- **Decision**: `ADR-spec-intake-playbook-discovery`.

Playbooks run only on explicit invocation (`devkit-playbook`, an exact ID or a failing rule's remediation), so they
stay unused unless the user already knows them. `spec` is the normal work entry point and can offer a fitting
procedure at new task intake without a separate invocation. The search returns a topical candidate for 84% of
ordinary intents, so the selection rule, not the search, must keep the user-visible offer rare: the user's highest
priority is that discovery does not fire too often.

The `spec` skill today forbids searching or routing to playbooks; the generated `devkit-playbook` skill, the root
guidance line, the `devkit playbook` CLI help, the `devkit` bundle constitution and five playbook prerequisites assume
that only an explicit request starts a playbook. `ADR-spec-intake-playbook-discovery` partially replaces
`ADR-external-playbook-execution` §4/§5 and `ADR-immutable-decisions-editable-records` §4.

## 2. User Stories

- **US-1**: As a developer starting a new task with `/spec`, I want the agent to name a playbook whose operation is
  exactly what I asked for, in one line I can confirm or decline, so that I find procedures I did not know existed.
- **US-2**: As a developer, I want discovery to stay silent on ordinary development intents, follow-ups,
  continuations and questions, so that the offer is rare and never interrupts established work.
- **US-3**: As a consumer without the `spec` bundle, I want the generated `devkit-playbook` skill to stay a generic
  explicit entry that names no `spec` asset.

## 3. Non-Goals

1. **Scope Excluded**: search ranking changes, alias keyword indexing, new search options or a changed
   `[playbooks]` default.
2. **Scope Excluded**: scheduling, execution history, bulk context loading and automatic playbook execution; a
   discovered candidate never runs before the user confirms it.
3. **Scope Excluded**: a `spec-playbook` skill, and removal or renaming of the generated `devkit-playbook` skill.
4. **Scope Excluded**: discovery in any entry other than `spec` intake (`/spec-next`, workers, hooks, stages).
5. **Scope Excluded**: a mechanical test of the agent's selection judgment; the offer-frequency bound is shown by the
   recorded manual run, not by test coverage.

## 4. Acceptance Criteria & Behavioral Contracts

`<skill>` is the `spec` skill source `skills/spec/SKILL.md.jinja` of the `spec` bundle; `<ref>` is its
`references/playbooks.md`. Text criteria are checked against the rendered text with whitespace collapsed.

### [AC-01] Intake runs one bounded search before classification

- **Given** the rendered `<skill>`
- **When** a test reads its routing steps
- **Then** the first routing step is playbook discovery at new task intake, ordered before the classification step
  and before any Unit is created; it defines intake as `/spec <intent>` or a user's own message outside the agreed
  scope of the current task and excludes messages from another agent, hooks and stages `devkit workflow next` names;
  it runs exactly `devkit playbook search "<English query>" --limit 3 --max-bytes 4096` once per intake with the
  query written as the requested operation on its artifact, in canonical artifact nouns (ADR, feedback, Living Spec,
  proposal, playbook, rule, release), without qualifiers that only name the subject and with no automatic refinement, and the old sentence "Do not search or route to playbooks from `spec`" is absent.

### [AC-02] Skip cases and conversation-level stops

- **Given** the rendered `<skill>`
- **When** a test reads the skip table
- **Then** it holds the five skip rows (continuation of an existing proposal or Unit, a follow-up within the same
  task, an already explicit entry, execution inside a selected playbook, an information-only question), the two
  conversation-level stops (the user declined playbooks for the conversation; a declined candidate is never offered
  again, even reworded), the two not-skipped cases (a new request after earlier work finished; a question that asks how
  to perform an operation), and the statement that task kind and planning depth never exempt a task.

### [AC-03] Selection rule offers operations, never topics

- **Given** the rendered `<skill>`
- **When** a test reads the selection rule
- **Then** it states that scores never decide and names the four conditions (operation, not topic; primary operation;
  scope fits; one line), including the topic example that "Feedback Quick Fixes" never offers `feedback-hygiene`.

### [AC-04] Confirm-first offer, silent no-match and recorded selection

- **Given** the rendered `<skill>` and `<ref>`
- **When** a test reads the offer and fallback wording
- **Then** a candidate is named in at most one line together with the classification statement and nothing of it
  runs before the user confirms; the confirmation is the explicit invocation; no match and the search errors
  `NOT_SYNCHRONIZED`, `CONFIG_LOCAL_RENDER_STALE`, `ARGUMENT_INVALID`, `SEARCH_EXTRA_MISSING` and a lock timeout
  continue the ordinary path without a question and without running the error's remediation; a selected playbook ID
  is recorded in the `plan-intent` note; the draft offer is absent from intake.

### [AC-05] Post-selection procedure lives in a reference read only on a match

- **Given** the `spec` bundle source tree
- **When** a test lists its skills and reads `<skill>`
- **Then** `<ref>` exists and is linked from `<skill>` with "only on a match" wording, it lists loading the bundle's
  context, reading the selected body, checking prerequisites and following the procedure, and no skill directory
  named `spec-playbook` exists.

### [AC-06] The generated entry skill, guidance line and CLI help stay spec-neutral

- **Given** `devkit_dist`'s generated `devkit-playbook` skill files, the root guidance line for playbooks and the
  `devkit playbook --help` output
- **When** a test reads them
- **Then** none contains "do not authorize playbook discovery", "references from other skills", `spec-playbook`,
  `/spec` or `references/playbooks.md`; the skill keeps `disable-model-invocation: true` and Codex
  `allow_implicit_invocation: false`; its draft offer applies to explicitly requested discovery only; it states that
  a user's confirmation of a candidate another entry skill offered is explicit invocation; the guidance line no
  longer says "explicit user invocation only"; and `devkit playbook --help` exits `0` without the phrase "after
  explicit devkit-playbook invocation".

### [AC-07] Playbook prerequisites read "invoked or confirmed"

- **Given** the playbooks `spec/brownfield-adoption`, `spec/feedback-hygiene`, `spec/adr-compaction`,
  `maintenance/drift-reconciliation` and `maintenance/weekly-report`
- **When** a test reads each body
- **Then** each entry condition says the user invoked or confirmed the playbook, `adr-compaction` keeps that this
  authorizes its deletions at `session` depth, and no body says "only on explicit invocation through
  `devkit-playbook`".

### [AC-08] The spec guidance pointer keeps the intake rule

- **Given** the `spec` bundle guidance fragment `guidance/spec-pointer.md`
- **When** a test reads it
- **Then** it holds one clause stating that a new task intake runs the `spec` skill's intake step, and the fragment
  stays one line.

### [AC-09] Recorded manual run bounds the offer frequency

- **Given** a scratch consumer with `spec`, `authoring:skill-authoring` and `maintenance` synchronized from this
  change
- **When** the agent applies the intake step to the 16 ordinary intents of the intake-frequency sample, the four
  positive controls, the paraphrase probe and one scenario per skip and no-skip row
- **Then** the run recorded in `materials/manual-run.md` shows 0 offers for the 16 ordinary intents, exactly the named
  offer for each positive control ("compact the ADR ledger" and "tidy up old ADRs": `adr-compaction`; "triage open
  feedback files": `feedback-hygiene`; "write a maintenance playbook for spec-code drift reconciliation":
  `skill-authoring`), no search for each skip row, one search for each no-skip row, and at most one offer line per
  intake; it is labeled manual evidence, not test coverage.

## 5. Assumptions

- The manual run uses a scratch consumer under the worktree's ignored `tmp/` path, because this repository's
  `.devkit/config.toml` does not select `maintenance` and is outside this Unit's write scope.
- "Lock timeout" is the advisory a search reports when the shared project lock is not acquired in time; it is named in
  prose, as the search contract defines no separate code for it.
- The playbook prerequisite wording in the `maintenance` catalog is changed here; `PROP-review-refactor` and
  `PROP-release-handbook` adopt the same entry wording when they land (proposal §3a Interactions).
- The query is led by the requested operation and drops subject-only qualifiers. With the `maintenance` catalog
  synchronized, the literal positive control "write a maintenance playbook for spec-code drift reconciliation" ranks
  `drift-reconciliation`, `brownfield-adoption` and `feedback-hygiene` in `hybrid` at `--limit 3` and cuts
  `skill-authoring`; "write a playbook for drift reconciliation" keeps it second in both modes
  (`materials/manual-run.md`). This refines how the canonical-noun query is written; limit, budget and ranking stay.
- The skip table and selection rule stay in the `spec` skill body, not in the reference, so they hold on every intake
  without an extra read; the reference holds only what runs after a match.
