# Manual intake run: offer frequency and skip behavior

**Manual evidence, not test coverage.** The agent applied the `spec` skill's intake step (routing step 1) as written
in this Unit to each row below; the search outputs are recorded command results, the offer decisions are the
agent's application of the selection rule. The text contract of the step is tested separately
(`test_playbook_discovery_guidance.py`).

## 1. Setup

- Base: worktree head `c4c4e8d7` plus this Unit's uncommitted bundle changes, branch `dev-spec-playbook-discovery`.
- Scratch consumer `tmp/probe/` (ignored) with `[presets] spec = ["core"]`, `authoring = "skill-authoring"`,
  `maintenance = "all"`, synchronized with `uv run devkit sync -w tmp/probe`. Synchronized playbooks (6):
  `spec/brownfield-adoption`, `spec/feedback-hygiene`, `spec/adr-compaction`, `authoring/skill-authoring`,
  `maintenance/drift-reconciliation`, `maintenance/weekly-report`. The `maintenance` catalog is included, which the
  Planning probe could not synchronize.
- Each search: `uv run devkit playbook search "<query>" -w tmp/probe --limit 3 --max-bytes 4096 --mode <m>` for
  `hybrid` (what `auto` resolves to here) and `lexical` (a consumer without the search extra). Search errors: 0.
- Raw output per row: [manual-run-probe.tsv](manual-run-probe.tsv); an operation-first row repeats its id.

## 2. Ordinary intents (intake-frequency §6): 0 offers required

Query: the spec title, then the operation-first form the step prescribes. Candidates are listed in rank order.

| # | Spec | Title query: hybrid / lexical | Operation-first query: hybrid / lexical | Offer | Why rejected |
| --- | --- | --- | --- | --- | --- |
| 1 | 20261013-feedback-list-filters | "Feedback list filters": feedback-hygiene / feedback-hygiene | "add filters to the feedback list command": feedback-hygiene, weekly-report, adr-compaction / feedback-hygiene, weekly-report, adr-compaction | none | builds the feedback list command (topic) |
| 2 | 20261013-open-feedback-and-progress | "Open feedback outside history and in-progress specs": feedback-hygiene, brownfield-adoption, drift-reconciliation / feedback-hygiene, brownfield-adoption, weekly-report | "list open feedback outside history and in-progress specs": feedback-hygiene, brownfield-adoption, drift-reconciliation / feedback-hygiene, brownfield-adoption, weekly-report | none | changes which feedback the listing shows (topic) |
| 3 | 20261014-feedback-config | "Repository-first feedback configuration": weekly-report, feedback-hygiene, brownfield-adoption / feedback-hygiene, weekly-report, brownfield-adoption | "read feedback configuration from the repository first": feedback-hygiene, weekly-report, brownfield-adoption / feedback-hygiene, brownfield-adoption, weekly-report | none | changes feedback configuration code (topic) |
| 4 | 20261016-planning-feedback-capture | "Feedback capture in Planning": feedback-hygiene, brownfield-adoption / feedback-hygiene, brownfield-adoption | "capture feedback during Planning": feedback-hygiene / feedback-hygiene | none | adds feedback capture to Planning (topic) |
| 5 | 20261020-feedback-terminal-status | "Treat feedback promotion and direct resolution as terminal outcomes": feedback-hygiene, adr-compaction, drift-reconciliation / feedback-hygiene, adr-compaction, drift-reconciliation | "treat feedback promotion and direct resolution as terminal statuses": feedback-hygiene, adr-compaction, drift-reconciliation / feedback-hygiene, adr-compaction, drift-reconciliation | none | changes feedback status semantics (topic) |
| 6 | 20261022-feedback-quick-fixes | "Feedback Quick Fixes": feedback-hygiene / feedback-hygiene | "fix feedback quick-fix defects": feedback-hygiene / feedback-hygiene | none | fixes feedback items, does not triage them (topic) |
| 7 | 20261022-feedback-guidance-fixes | "Feedback Guidance Fixes": feedback-hygiene, drift-reconciliation / feedback-hygiene, drift-reconciliation | "fix feedback guidance defects": feedback-hygiene, drift-reconciliation / feedback-hygiene, drift-reconciliation | none | fixes guidance defects (topic) |
| 8 | 20261021-proposal-review-and-approval | "Proposal review reports and unified plan-accept MCP approval": feedback-hygiene, weekly-report, drift-reconciliation / drift-reconciliation, feedback-hygiene, brownfield-adoption | "add proposal review reports and plan-accept MCP approval": feedback-hygiene, weekly-report, brownfield-adoption / drift-reconciliation, feedback-hygiene, brownfield-adoption | none | builds review reports and MCP approval (topic) |
| 9 | 20261022-document-id-aliases-and-compaction | "Document and Playbook ID Aliases": adr-compaction, skill-authoring, drift-reconciliation / skill-authoring, adr-compaction, drift-reconciliation | "add ID aliases for documents and playbooks": adr-compaction, drift-reconciliation, feedback-hygiene / drift-reconciliation, adr-compaction, feedback-hygiene | none | adds an ID alias feature; compaction is not the operation (topic) |
| 10 | 20261022-contract-alignment | "Align ADRs and alias wording with the shipped contracts": adr-compaction, feedback-hygiene, brownfield-adoption / adr-compaction, feedback-hygiene, brownfield-adoption | "align ADR and alias wording with the shipped contracts": adr-compaction, feedback-hygiene, brownfield-adoption / adr-compaction, feedback-hygiene, brownfield-adoption | none | aligns wording; no ADR is consolidated (topic) |
| 11 | 20261019-response-style-skill | "Templated response-style skill deployment": skill-authoring / skill-authoring | "deploy the response-style skill from a template": skill-authoring, adr-compaction, brownfield-adoption / skill-authoring, adr-compaction, brownfield-adoption | none | builds templated skill deployment, not authoring one skill (topic) |
| 12 | 20261022-writing-guidance-layers | "Layered writing guidance for documents and agent assets": skill-authoring, drift-reconciliation, brownfield-adoption / drift-reconciliation, skill-authoring, brownfield-adoption | "layer the writing guidance for documents and agent assets": skill-authoring, drift-reconciliation, brownfield-adoption / drift-reconciliation, brownfield-adoption, skill-authoring | none | restructures writing guidance, not one skill or playbook (topic) |
| 13 | 20261017-hygiene-reliability | "Repair hygiene reliability and rule reference size": feedback-hygiene, skill-authoring, brownfield-adoption / skill-authoring, feedback-hygiene, brownfield-adoption | "repair hygiene rule reliability and rule reference size": skill-authoring, feedback-hygiene, brownfield-adoption / skill-authoring, feedback-hygiene, brownfield-adoption | none | repairs rule reliability; a size fix is one step (primary operation fails) |
| 14 | 20261019-repository-viewer | "Local multi-repository SDD viewer owned by devkit": brownfield-adoption, feedback-hygiene, weekly-report / brownfield-adoption, feedback-hygiene, weekly-report | "build a local multi-repository viewer": weekly-report, skill-authoring, brownfield-adoption / weekly-report, skill-authoring, brownfield-adoption | none | builds a viewer (topic) |
| 15 | 20261019-devkit-dist-package-separation | "Separate asset distribution into independent devkit-dist package": brownfield-adoption, adr-compaction / brownfield-adoption, adr-compaction | "separate asset distribution into a devkit-dist package": brownfield-adoption, adr-compaction, skill-authoring / brownfield-adoption, adr-compaction, skill-authoring | none | splits a package (topic) |
| 16 | 20261021-deterministic-milestone-completion | "Simple milestone completion from direct proposal checks": brownfield-adoption, weekly-report / brownfield-adoption | "complete milestones from direct proposal checks": brownfield-adoption, weekly-report / brownfield-adoption | none | changes milestone completion (topic) |

Result: **0 offers in 16 intents** in both query forms and both modes, although every intent returned at least one
candidate.

## 3. Positive controls: exactly the named offer required

| Request | Query | hybrid | lexical | Offer |
| --- | --- | --- | --- | --- |
| compact the ADR ledger | "compact the ADR ledger" | adr-compaction, brownfield-adoption, feedback-hygiene | adr-compaction, brownfield-adoption, feedback-hygiene | `adr-compaction` (consolidate ADRs is the operation; the others are topic) |
| tidy up old ADRs | "tidy up old ADRs" | adr-compaction | adr-compaction | `adr-compaction` |
| triage open feedback files | "triage open feedback files" | feedback-hygiene, adr-compaction | feedback-hygiene, adr-compaction | `feedback-hygiene` (`adr-compaction` is topic) |
| write a maintenance playbook for spec-code drift reconciliation | "write a playbook for drift reconciliation" | drift-reconciliation, skill-authoring, weekly-report | drift-reconciliation, skill-authoring, weekly-report | `skill-authoring` (`drift-reconciliation` reviews drift, the request writes a playbook: topic) |

The literal query "write a maintenance playbook for spec-code drift reconciliation" returns drift-reconciliation, brownfield-adoption, feedback-hygiene in `hybrid` and drift-reconciliation, skill-authoring, brownfield-adoption in `lexical`: with the
`maintenance` catalog synchronized, `--limit 3` cuts `skill-authoring` in `hybrid`, so that query would offer
nothing (a silent miss, never a wrong offer). The step therefore writes the query as the requested operation on its
artifact without subject-only qualifiers ("write a playbook for drift reconciliation"), which keeps
`skill-authoring` second in both modes. Result: **each positive control produces exactly its named offer, one line**.

## 4. Paraphrase probe, maintenance intents and out-of-sample authoring requests

| Request | Query | hybrid | lexical | Offer |
| --- | --- | --- | --- | --- |
| clean up old decisions | "clean up old decisions" | feedback-hygiene, drift-reconciliation | drift-reconciliation, feedback-hygiene | none: the paraphrase misses; the canonical query is "tidy up old ADRs" (row above) |
| consolidate ADR documents | "consolidate ADR documents" | adr-compaction, brownfield-adoption | adr-compaction, brownfield-adoption | `adr-compaction` |
| adopt spec-driven development in an existing repository | "adopt spec-driven development in an existing repository" | brownfield-adoption, weekly-report, drift-reconciliation | brownfield-adoption, weekly-report, feedback-hygiene | `brownfield-adoption` |
| reconcile Living Spec drift with code | "reconcile Living Spec drift with code" | drift-reconciliation, brownfield-adoption, feedback-hygiene | drift-reconciliation, brownfield-adoption, feedback-hygiene | `drift-reconciliation` |
| write a weekly repository progress report | "write a weekly repository progress report" | weekly-report, skill-authoring, feedback-hygiene | weekly-report, skill-authoring, brownfield-adoption | `weekly-report` |
| refactor the sync module | "refactor the sync module" | weekly-report, adr-compaction, brownfield-adoption | adr-compaction, brownfield-adoption, feedback-hygiene | none: no description names refactoring a module, and a repository-wide procedure exceeds the scope |

Operation-first rule outside the acceptance sample (finding 3 of `review-01`):

| Request | Query | hybrid | lexical | Offer |
| --- | --- | --- | --- | --- |
| write a release playbook for changelog checks | "write a release playbook for changelog checks" | skill-authoring, brownfield-adoption, weekly-report | skill-authoring, drift-reconciliation, brownfield-adoption | `skill-authoring` (the other candidates are topic) |
| write a release playbook for changelog checks | "write a playbook for changelog checks" | skill-authoring, drift-reconciliation, feedback-hygiene | skill-authoring, drift-reconciliation, brownfield-adoption | `skill-authoring` (the other candidates are topic) |
| create a weekly maintenance report playbook for repository health | "create a weekly maintenance report playbook for repository health" | weekly-report, brownfield-adoption, skill-authoring | weekly-report, skill-authoring, drift-reconciliation | `skill-authoring` (the other candidates are topic) |
| create a weekly maintenance report playbook for repository health | "create a playbook for repository health reports" | weekly-report, brownfield-adoption, skill-authoring | skill-authoring, weekly-report, drift-reconciliation | `skill-authoring` (the other candidates are topic) |
| write a skill for ADR review | "write a skill for ADR review" | skill-authoring, drift-reconciliation, adr-compaction | drift-reconciliation, skill-authoring, adr-compaction | `skill-authoring` (the other candidates are topic) |

Each keeps `skill-authoring` in the first three in both query forms and both modes, so the rule is not only tuned
on P04; the skill's example is this sample's first row, not an acceptance control.

## 5. Skip and no-skip scenarios

| Scenario | Row | Search | Offer |
| --- | --- | --- | --- |
| "Continue Planning for PROP-x" (Host payload to a `planning-worker`) | skip: continuation | none | none |
| `/spec-next` in a repository with an in-progress Unit | skip: continuation | none | none |
| A `development-worker` turn naming its unit (this run) | skip: continuation; not a user's own message | none | none |
| "Use option b" after a question | skip: same-task follow-up | none | none |
| "fix the lint error" on the delivered change | skip: same-task follow-up | none | none |
| "rerun the tests" | skip: same-task follow-up | none | none |
| "Run spec/adr-compaction" | skip: explicit entry (`devkit playbook get spec/adr-compaction`) | none | none |
| A failing `RULE-skill-document-size` names `skill-authoring` | skip: explicit entry | none | none |
| A `brownfield-adoption` step asks to move legacy files | skip: inside a selected playbook | none | none |
| "What does `devkit sync` write?" | skip: information-only question | none | none |
| "Don't use playbooks in this conversation", then "tidy up old ADRs" | conversation stop | none | none |
| `adr-compaction` declined, then "consolidate ADR documents" | declined candidate | one (row R02) | none: the only passing candidate was declined |
| "now clean up open feedback" after a finished Development task | not skipped: new request | one | `feedback-hygiene` (hybrid and lexical first) |
| "how do I adopt devkit here?" | not skipped: how-to question for an operation | one ("adopt devkit in this repository") | `brownfield-adoption` |

## 6. Measured numbers

| Measure | Result |
| --- | --- |
| Offers on the 16 ordinary intents | 0 of 16 (title and operation-first queries, `hybrid` and `lexical`) |
| Positive controls with exactly the named offer | 4 of 4 (operation-first query for the playbook-authoring control) |
| Out-of-sample authoring requests with the `skill-authoring` offer | 3 of 3 (literal and operation-first) |
| Offer lines per intake | at most 1 in every row |
| Skip and conversation-stop rows that searched | 0 of 11 |
| Declined-candidate row | searched once, offered nothing |
| No-skip rows that searched once | 2 of 2 |
| Search output bytes at `--limit 3` | 572 to 1877 (budget 4096; never truncated) |
| Search time | 0.12 to 0.28 s per call |
| Search errors | 0 |

Without the selection rule 16 of 16 ordinary intents would surface a candidate; with it none does.
