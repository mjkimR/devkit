---
id: PROP-consolidated-record-length
title: Line budgets for consolidated records
summary: Lets the hygiene file-length check budget consolidated ADRs and feedback records by what they are instead of by per-file overrides, so consolidation runs stop producing warnings while an over-broad group still gets one.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/models/settings.py
    - packages/devkit/src/devkit_agt/features/rules/services/builtins/file_length/
    - packages/devkit/tests/unit/features/rules/
    - packages/devkit/tests/integration/features/rules/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-consolidation/
    - docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    - docs/capabilities/governance/CAP-GOV-rule-authoring.md
    - docs/development/reference/rules.md
    - .devkit/config.toml
  excludes:
    - docs/decisions/
    - .devkit/managed/
    - docs/capabilities/documents/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-consolidated-record-length] Line budgets for consolidated records

## 1. Background & Hypothesis

`RULE-file-length` (hygiene phase, warning, default 400 lines for `.md`) exists so that a reader or an agent who needs
one section does not pay for a whole file; its remediation is "split the file at a meaningful boundary". Its only
targeting mechanism is a path pattern: `[[rules.settings.RULE-file-length.overrides]]` with `path` and `max_lines`,
resolved per file by `SettingsResolver.for_file`. The repository has one such override, `docs/capabilities/**` at 600.

`ADR-decision-ledger` points the other way for decision records: the `adr-consolidation` playbook replaces a group of
related ADRs with one record that carries every member's drivers, considered options, in-effect clauses with their
source IDs, consequences and aliases, because "the current decision on a topic is readable in one record". Length is
the designed outcome, not an accident, and the rule's remedy, splitting the file, is the state consolidation removed.
The 2026-11-02 consolidation shows the scale (`uv run devkit rules check --phase hygiene`, 2026-11-04):

| Record | Lines | Aliases |
| --- | --- | --- |
| `ADR-document-system` | 619 | 13 |
| `ADR-local-and-pull-request-integration` | 536 | 11 |
| `ADR-orchestration-workers` | 529 | 10 |
| `ADR-adaptive-development-and-research` | 471 | 8 |
| `ADR-package-ownership-and-release-version` | 455 | 9 |
| `ADR-rules-run-workspace-cache` | 425 | 7 |
| `ADR-roadmap-and-milestones-ledger` | 401 | 8 |

Seven of the eleven hygiene warnings are consolidated ADRs. Every ADR with seven or more aliases exceeds 400 lines, every
ADR without aliases is 107 lines or shorter, and a replacement runs at roughly 45 to 55 lines per member. The next
consolidation run adds members to these records, so the warnings return after every run, and the guide's advice (an
exact-path override with a comment per exception) means one more config entry per replacement per run.

Feedback consolidation has the same shape on a slower clock. `FB-consolidated-<area>-<status>` records grow by one
H2 and three lines per retired item and never shrink; the largest after the first run is
`FB-consolidated-delivery-promoted` at 110 lines (about 21 entries). The default budget holds about 75 entries, so a
busy area reaches it after a few more runs. `ADR-feedback-lifecycle-ledger` already defers this ("if one area's
record becomes too long to read, a later decision may split it"), and unlike ADRs these files carry a marker in their
name (`*-consolidated-*.md`), so a path override can reach them today.

The two consolidated kinds share one property the rule cannot see: both carry `aliases` with two or more members by
contract (a consolidation group has two or more members; a feedback record lists every retired ID). A single ADR
carries none, or one when it inherited its PADR's ID at handoff.

Hypothesis: the budget should follow what the record is, read from its own frontmatter, not from where it sits or
from a hand-kept override list. A consolidated record gets a larger fixed budget; a record that still exceeds it is
the signal the topic-grouping clause of `ADR-decision-ledger` wanted, a group that spans more than one topic, and the playbook turns
that into a regrouping heuristic instead of a split.

## 2. Technical Spike Questions

- **Q1**: Where does the selector live? Candidates: (a) a generic condition on every rule's override,
  `[[rules.settings.<RULE>.overrides]] path = "docs/decisions/**", frontmatter = { aliases = { min_items = 2 } }`,
  evaluated by `SettingsResolver.for_file` with a frontmatter loader the engine supplies from the run cache; (b) a
  rule-local setting of `RULE-file-length`, such as `consolidated_max_lines`, applied when the file's `aliases` has two
  or more items. (a) is reusable (`RULE-cli-contract` excludes whole directories today for the same reason) but puts
  file reading behind the settings model; (b) is smaller and keeps the model pure. Planning decides, and names the
  layering consequence for `devkit_agt.features.rules.models`.
- **Q2**: What marks a consolidated record? Candidate: `aliases` with two or more items, derived from the consolidation
  contracts and needing no new field. Alternatives: an explicit frontmatter field (`consolidated: true`, a kind-table
  change in `devkit-docs`, out of this proposal's scope) or a file-name marker (works for feedback, and would change
  ADR file names and therefore the file-name-derived identity). Planning confirms the alias condition does not catch a
  record it should not (an ADR that inherited one PADR alias and later gained another).
- **Q3**: What are the budgets? Proposed: consolidated records 600 lines, the same as capabilities. Six of the seven
  ADRs above pass; `ADR-document-system` (13 members across packaging, command mount, policy table, rules, skill names,
  docs skeleton, parse memo and kind table) stays reported, which is the intended group-breadth signal. Planning
  checks whether 600 is a reasonable per-topic ceiling at about 50 lines per member (roughly twelve members) and
  whether feedback records take the same number or their own.
- **Q4**: How do the playbooks use the budget? Candidate: `adr-consolidation` Step 1 names the consolidated budget as
  a grouping heuristic (a group whose replacement would exceed it probably spans two topics; split it before writing),
  and its completion conditions keep `uv run devkit rules check` exit `0` without adding the hygiene phase.
  `feedback-consolidation` Step 3 names the budget as the trigger for the split `ADR-feedback-lifecycle-ledger`
  deferred, or leaves the split to that later decision. Planning decides whether any playbook runs the hygiene phase.
- **Q5**: Consumer impact. `RULE-file-length` is a `devkit-agt` builtin shipped to every consumer; the default budget
  and the existing override keys must not change. Planning confirms the new key or condition is optional, is rejected
  with the rule ID when malformed (as every settings error is), and is documented in the rule guide and
  `CAP-GOV-evaluation-lifecycle` section 5.

## 3. Proposed Design & Impact

- **Selector**: an override condition that reads the targeted file's frontmatter (Q1). With (a), `SettingsResolver`
  gains an optional `frontmatter` matcher per override and `evaluate_rules` passes a loader built on the run cache and
  `devkit_core.core.frontmatter.parse`; files without frontmatter never match a frontmatter condition. With (b),
  `FileLengthSettings` gains `consolidated_max_lines` (default `None`, meaning no separate budget) and the rule parses
  frontmatter only for files whose size is over `max_lines`, so the common path stays as cheap as today.
- **Configuration** (repository, under either design): one entry for consolidated records at the chosen budget,
  replacing the prospect of one exact-path override per replacement. The `docs/capabilities/**` override stays.
- **Rule guide and capability**: the guide's section 4 and 5 document the condition and name consolidated records as
  the case it is for; `CAP-GOV-evaluation-lifecycle` section 5 states the condition's syntax and validation;
  `CAP-GOV-rule-authoring` is touched only if the rule base class changes.
- **Playbooks**: `adr-consolidation` Step 1 gains the group-breadth heuristic and the fidelity review keeps its
  wording; `feedback-consolidation` names the budget where its records are extended (Q4).
- **Remediation text**: the violation's remediation distinguishes a consolidated record ("the group spans more than
  one topic; regroup by topic") from an ordinary file ("split at a meaningful boundary"), so an agent reading the
  hygiene report does not split a replacement.
- **Expected effect**: the hygiene report drops from eleven warnings to five (`ADR-document-system`, three
  capabilities and one use case); the four non-ADR warnings are pre-existing and out of scope.

Expected affected contracts: `CAP-GOV-evaluation-lifecycle` (typed settings and overrides). The hygiene phase, the
rule's default budget, its severity, `RULE-decision-supersession` and the document model are unchanged.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1 to Q5 and records the selector and budget as a PADR; acceptance and handoff create one feature
spec. Completion requires: the selector implemented with unit tests for a matching, a non-matching and a
frontmatter-less file and for a malformed condition; the repository configuration carrying the consolidated budget;
the rule guide, capability section and reference updated; the two playbooks updated and the `spec` bundle tests
passing; and `uv run devkit rules check --phase hygiene` on `main` reporting no consolidated ADR under the chosen
budget except those the group-breadth signal is meant to catch.

Non-goals: changing the default 400-line budget for consumers; splitting or regrouping any existing ADR (a separate
`adr-consolidation` run, which the heuristic then guides); splitting any feedback record; running the hygiene phase
in the commit gate or CI; a new frontmatter field or kind-table change in `devkit-docs`; the three capabilities and
one use case over budget today.

<!--
- Preliminary decisions: devkit spec proposal padr consolidated-record-length "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept consolidated-record-length --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff consolidated-record-length.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
