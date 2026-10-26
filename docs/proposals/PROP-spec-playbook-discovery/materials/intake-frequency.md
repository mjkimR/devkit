# Intake frequency: when discovery runs and how often it speaks

Planning evidence for `PROP-spec-playbook-discovery`, answering the concern that discovery at intake must not fire
too often. Probe data: [intake-probe.tsv](intake-probe.tsv) (every row below is reproducible from it); earlier probes:
[discovery evidence](discovery-evidence.md) §1.

## 1. Two different frequencies

- **Search frequency**: how often intake runs `devkit playbook search`. It is invisible to the user: one call of
  about 0.2 to 0.3 s and at most 4096 bytes of candidate metadata (measured: mean 1252, maximum 1849 bytes at
  `--limit 3`), read by the agent and never shown.
- **Offer frequency**: how often the user sees a one-line candidate. This is the frequency the concern is about. It is
  set by the selection rule, not by the search: the search returns something for almost every request.

## 2. When discovery runs

Only at **new task intake**, at most once per intake:

- `/spec <intent>`, or
- a user's own message in an ongoing conversation that requests a change or an operation outside the agreed scope of
  the current task, after that task finished or alongside it.

Nothing else is intake: no message from another agent (a Host payload, a worker turn, a nested role), no hook, no
`/spec-next`, no stage that `devkit workflow next` names.

## 3. When it does not run

The skip table of proposal §3a (continuation, same-task follow-up, an already explicit entry, a step inside a
selected playbook, an information-only question), plus two conversation-level stops added for this concern:

- the user said not to use playbooks in this conversation: no later intake searches;
- a candidate the user declined is never offered again in the same conversation, even for a reworded request.

## 4. What the measurement shows

Corpus: the titles of all 105 feature specs in `specs/` (2026-10-13 to 2026-10-24), each an ordinary development
intent that once went through `/spec`. Synchronized playbooks: `spec/brownfield-adoption`, `spec/feedback-hygiene`,
`spec/adr-compaction`, `authoring/skill-authoring`. Search: `--limit 3 --max-bytes 4096`, `hybrid` and `lexical`.

| Measure | Result |
| --- | --- |
| Intents with at least one search candidate (`hybrid` / `lexical`) | 88 / 85 of 105 (84% / 81%) |
| First candidate among them (`hybrid`) | feedback-hygiene 41, brownfield-adoption 23, skill-authoring 18, adr-compaction 6 |
| Intents whose candidate passes the selection rule of §5 | 1 of 105 (about 1%) |
| Topic-only matches the rule must reject (§6 sample) | 16, including all 41 feedback-hygiene first hits |
| Search errors | 0 |

The single pass is `20261021-periodic-drift-reconciliation` ("Spec-code drift reconciliation maintenance playbook"):
`skill-authoring` ("Create an agent skill or playbook ...") names that operation, so the offer is a true positive.
`20261021-weekly-report` also authored a playbook but its title does not say so; the search returned nothing (a
silent miss, which costs what today's state costs).

Without the selection rule, 84% of intakes would surface a candidate. With it, about 1 in 100. The rule, not the
search, carries the frequency bound, so the rule is tightened and tested in §5 and §6.

## 5. The selection rule, tightened

A candidate is offered only when all of these hold; scores never decide:

1. **Operation, not topic**: its `description` names the operation the request asks the agent to perform on the
   artifact (triage open feedback, consolidate ADRs, adopt spec-driven development, create or restructure a skill or
   playbook). A request to build, fix or change the tool, code or documents *about* that artifact is a topic match and
   is never offered: "Feedback list filters", "Feedback Quick Fixes" (fixing feedback items, not triaging them),
   "Document and Playbook ID Aliases".
2. **Primary operation**: the playbook covers the request's main operation, not one step of a larger change
   ("Repair hygiene reliability and rule reference size" does not offer `skill-authoring`).
3. **Scope fits**: its scope does not exceed the requested scope ("refactor the sync module" never offers a
   repository-wide review playbook).
4. **One line**: at most one offer line per intake, naming the passing candidates (normally one) together with the
   classification statement of intake step 1.

## 6. False-positive sample for acceptance

Ordinary intents from the corpus whose search ranks a playbook first by topic; each must produce **no offer**:

| Spec | Title | Topical candidate |
| --- | --- | --- |
| 20261013-feedback-list-filters | Feedback list filters | feedback-hygiene |
| 20261013-open-feedback-and-progress | Open feedback outside history and in-progress specs | feedback-hygiene |
| 20261014-feedback-config | Repository-first feedback configuration | feedback-hygiene |
| 20261016-planning-feedback-capture | Feedback capture in Planning | feedback-hygiene |
| 20261020-feedback-terminal-status | Treat feedback promotion and direct resolution as terminal outcomes | feedback-hygiene |
| 20261022-feedback-quick-fixes | Feedback Quick Fixes | feedback-hygiene |
| 20261022-feedback-guidance-fixes | Feedback Guidance Fixes | feedback-hygiene |
| 20261021-proposal-review-and-approval | Proposal review reports and unified plan-accept MCP approval | feedback-hygiene |
| 20261022-document-id-aliases-and-compaction | Document and Playbook ID Aliases | adr-compaction |
| 20261022-contract-alignment | Align ADRs and alias wording with the shipped contracts | adr-compaction |
| 20261019-response-style-skill | Templated response-style skill deployment | skill-authoring |
| 20261022-writing-guidance-layers | Layered writing guidance for documents and agent assets | skill-authoring |
| 20261017-hygiene-reliability | Repair hygiene reliability and rule reference size | feedback-hygiene, skill-authoring |
| 20261019-repository-viewer | Local multi-repository SDD viewer owned by devkit | brownfield-adoption |
| 20261019-devkit-dist-package-separation | Separate asset distribution into independent devkit-dist package | brownfield-adoption |
| 20261021-deterministic-milestone-completion | Simple milestone completion from direct proposal checks | brownfield-adoption |

Positive controls; each must produce exactly the named offer: "compact the ADR ledger" and "tidy up old ADRs"
(`adr-compaction`), "triage open feedback files" (`feedback-hygiene`), "write a maintenance playbook for spec-code
drift reconciliation" (`skill-authoring`). Probed at `--limit 3`, each expected playbook is among the candidates in
both `hybrid` and `lexical` (`skill-authoring` third in `hybrid` for the last one), so the limit does not cut a
positive.

Acceptance criterion (proposal §3a): in Development's recorded manual run, the 16 intents above produce 0 offers,
each skip and no-skip scenario behaves as its row states, and each positive control produces its one offer.

## 7. Why a false positive stays cheap

- It is one line in the intake reply, next to the classification statement the user reads anyway.
- Nothing runs until the user confirms: confirm-first means the confirmation is the invocation, so a wrong candidate
  costs a "no", never a file move, deletion or status update.
- A declined candidate is not offered again in the conversation.
- No match and search errors are silent: the ordinary path continues with no question.

## 8. Residual risks

- **Agent judgment**: the rule is applied by the agent, so mechanical tests can check only its wording; the bound is
  shown by the recorded manual run, not by test coverage.
- **Corpus bias**: spec titles are concise English; live requests are longer, paraphrased or Korean. The query is
  rewritten in English with canonical artifact nouns (proposal §3a), which narrows but does not remove this gap.
- **Catalog growth**: every new playbook adds topical candidates. The bound holds only while each `description` names
  one operation and its scope; `PROP-review-refactor` and `PROP-release-handbook` must follow that form.
- **Silent misses**: a request that never names the artifact (the weekly-report case) finds nothing; this equals
  today's behavior.
- **Not measured**: the `maintenance` catalog (`drift-reconciliation`, `weekly-report`) was not synchronized in this
  worktree; Development's manual run repeats the sample with it selected.
