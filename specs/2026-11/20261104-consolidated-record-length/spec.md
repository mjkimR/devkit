---
id: SPEC-consolidated-record-length
title: Line budgets for consolidated records
summary: Lets the hygiene file-length check budget consolidated ADRs and feedback records by what they are instead of by per-file overrides, so consolidation runs stop producing warnings while an over-broad group still gets one.
status: planned
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-consolidated-record-length] Line budgets for consolidated records

## 1. Problem Statement & Motivation

Handed off from proposal PROP-consolidated-record-length on 2026-11-04.
- **Preserved Materials**: `docs/materials/2026-11/20261104-consolidated-record-length`

### 1. Background & Hypothesis

`RULE-file-length` warns above 400 lines for Markdown by default. The repository raises capabilities to 600.
`ADR-decision-ledger` consolidates related ADRs so a reader finds a topic's decisions together; splitting a
replacement to satisfy the ordinary budget defeats that operation. `ADR-feedback-lifecycle-ledger` likewise
appends closed feedback entries to an area/status record.

The Planning baseline at source `2cf7879a74b50b687867e2184188dee6c29a2fbc` has eleven file-length warnings:
seven consolidated ADRs, three capabilities and one use case. Six ADRs fall between 401 and 600 lines;
`ADR-document-system` has 619. `docs/materials/2026-11/20261104-consolidated-record-length/planning-evidence.md` records the command, exact counts and reproduction.
The initial draft's roadmap-record line count and feedback alias count were approximate; the measured values are
407 lines and fifteen aliases for the longest 110-line feedback record.

A larger opt-in budget for alias-bearing ADRs and consolidated feedback removes repetitive exact-path exceptions.
It remains a bounded warning budget; records above it still need a topic review. Alias history is a heuristic for
ADRs, not proof of consolidation, and grants no authority to edit or consolidate records.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Line budgets for consolidated records so that system capabilities are extended.

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

- **Q1 — Where does selection live?** Rule-local `FileLengthSettings.consolidated_max_lines: int | None = None`.
  `SettingsResolver` already supports optional integers and validates rule-local constraints. The rule uses
  `ctx.cache.get_frontmatter` only for targeted Markdown above its ordinary limit when the option is set.
  Generic override conditions would add policy grammar, loader injection and file-content dependencies to the
  reusable settings model for one demonstrated consumer. That extension is outside this work.
- **Q2 — Which records qualify?** A Markdown header with a nonempty string `id` and a valid list of distinct,
  nonempty string aliases qualifies when either (a) `id` begins `ADR-` and at least two aliases remain, or
  (b) `id` follows `FB-consolidated-<area>-<status>` (including namespace-qualified areas) and at least one alias remains. The feedback playbook permits a one-item
  group, so two aliases is not its lower bound. PADRs and other document kinds do not qualify.
  An ADR renamed more than once can match; this accepted heuristic is documented rather than inferred as
  consolidation provenance. Duplicate aliases do not raise the count. Malformed or absent frontmatter, malformed
  aliases, or an unrelated ID keep the ordinary limit. Document validation remains with its owning rules.
- **Q3 — Which budget?** The repository opts into 600 lines for both qualifying kinds. It removes six current
  warnings while retaining the 619-line ADR signal. No evidence supports separate feedback tuning today.
  Consumers that omit the key retain exactly the current limits and remediation.
- **Q4 — What do playbooks do?** ADR grouping uses the configured budget as a topic-breadth heuristic, never as
  permission to drop drivers, decisions, alternatives or consequences. Feedback writing names an over-budget
  record as a signal for a separate grouping decision; this change does not split it or alter its identity scheme.
  Both playbooks retain their ordinary `devkit rules check` completion command; no hygiene stage is added.
- **Q5 — Compatibility and errors?** A configured value is a positive integer, validated by the existing typed
  settings machinery with `RULES_SETTINGS_INVALID`, the rule ID and exit 2. Booleans, strings, zero and negatives
  are rejected. Existing path override syntax, ordering, extensions, line counting, severity and phases are retained.
  The selected budget is `max(max_lines, consolidated_max_lines)`, so enabling it cannot reduce an existing
  higher path-specific limit. Omission disables the alternative budget; TOML has no null literal.

### 3. Proposed Design & Impact

`ADR-consolidated-record-budgets` records the alternatives and the chosen rule-local contract.

#### Rule and configuration

1. Add the optional positive integer to `FileLengthSettings` and its validation. No model or engine change and
   no feature dependency are needed.
2. Resolve settings per file as today and count lines from cached text. When enabled and the ordinary limit is
   exceeded, classify eligible Markdown using the existing frontmatter cache. Catch `FrontmatterError` and retain
   the ordinary budget; an invalid header never suppresses a length finding or crashes this hygiene rule.
3. For a qualifying record, select the larger of the ordinary and consolidated limits. Report at selected limit
   plus one, preserving the message's existing numeric format. A finding for an eligible record advises reviewing
   the consolidation group by topic while preserving every retained decision or outcome. A nonqualifying record
   keeps the existing remediation. The rule never rewrites any file.
4. Set this repository's optional budget without changing its capability override:

   ```toml
   [rules.settings.RULE-file-length]
   consolidated_max_lines = 600
   ```

A configured path override may replace `consolidated_max_lines` through the existing settings mechanism.
A 900-line path budget remains 900 even when the consolidated budget is 600.

#### Guides and contracts

- The built-in rule guide and `docs/development/reference/rules.md` describe the option, exact eligibility,
  ADR rename false positives, one-entry feedback, selected-limit precedence and remediation.
- `CAP-GOV-evaluation-lifecycle` section 5 records this rule-local option alongside existing typed settings.
  The rule base class and `CAP-GOV-rule-authoring` are unchanged.
- `adr-consolidation` grouping names the budget as a topic-review heuristic. `feedback-consolidation` names the
  over-budget signal and leaves splitting to a separately authorized decision. Content tests cover both texts.
- Development runs the synchronization implied by changed selected `spec` assets and records tracked sync
  outputs under the workflow's existing rules; no source asset is edited through its projection.

#### Verification contract

- **AC-01:** With the option omitted, default and path-specific checks produce the current findings, limits,
  line locations and ordinary remediation for the same files, including alias-bearing ADRs.
- **AC-02:** With ordinary 400 and consolidated 600, a qualifying 500-line ADR with two distinct aliases and
  a qualifying one-alias consolidated feedback record pass; an eligible 601-line record warns at line 601 and
  receives consolidation-specific remediation. Exact 600 and final-newline cases follow existing counting.
- **AC-03:** A PADR, a non-record document, a single-alias ADR, duplicate aliases leaving fewer than two,
  malformed alias values, absent frontmatter and malformed YAML all retain the ordinary limit. A twice-renamed
  ADR with two valid aliases qualifies by the documented heuristic.
- **AC-04:** Boolean, string, zero and negative configured budgets fail with `RULES_SETTINGS_INVALID`, rule ID
  and exit 2. Defaults and existing settings remain valid. A higher ordinary override remains authoritative.
- **AC-05:** Guidance and content tests retain fidelity and the existing ordinary completion commands.
  The docs option matches the rule and no generic frontmatter override grammar or new document field appears.
- **AC-06:** With the option disabled versus 600 on the same final head and same files, six known ADR findings
  disappear; `ADR-document-system` stays. The four pre-existing non-ADR findings stay unless changed by another
  task. Compare identities, not an invariant total; new history documents may add unrelated warnings.

Tests live with the built-in rule in `file_length/tests/`, with engine/CLI integration tests under
`packages/devkit/tests/{unit,integration}/features/rules/` only where the boundary needs coverage. Bundle-content
checks live under the existing `packages/devkit-spec/tests/integration/bundles/spec/` owner.
Development runs relevant lint, Pyright, tests, `just test-affected` with its full fallback, sync checks, and the
hygiene comparison. The comparison disables only this option in an in-memory rules configuration through the
existing testing/evaluation entrypoint; it never checks out an older commit or rewrites project policy for a probe.

### Planning decisions

- Recommend rule-local opt-in selection rather than adding generic file-content matching to every rule.
- Recommend 600 for both record kinds and preserve higher existing overrides with `max`.
- Treat alias-based ADR detection as an explicit heuristic; use the existing `FB-consolidated-<area>-<status>` marker for
  one-entry feedback. No provenance marker or document-model change is introduced.
- Keep the feedback split deferred; no follow-up implementation is being claimed or required here.
- Planning and Development effort are `medium`: the selector changes a shipped consumer contract and the
  two playbook texts; mandatory review and reconciliation cover those boundaries.

### 4. Lifecycle & Retirement Criteria

Planning returns this committed recommendation, its PADR, evidence and challenger record for `plan-accept`.
One feature spec implements AC-01 through AC-06 after acceptance and Development handoff.
Completion requires relevant tests, synchronized assets, final diff review, Living Spec reconciliation and the
same-head hygiene comparison; a warning-count claim alone does not prove completion.

Non-goals: changing the default 400-line consumer budget; generic override predicates; changing the document
model or adding frontmatter fields; splitting, regrouping or editing existing ADRs or feedback records; making
hygiene part of commits or CI; fixing the four existing non-ADR warnings; authoritative consolidation provenance.

