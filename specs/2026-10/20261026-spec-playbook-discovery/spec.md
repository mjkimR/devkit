---
id: SPEC-spec-playbook-discovery
title: Task-aware playbook discovery through spec
summary: Lets spec run one bounded playbook search at new task intake and offer a matching playbook in one line that the user confirms, with explicit skip cases; the generated devkit-playbook skill stays the generic explicit entry.
status: planned
created: 2026-10-26
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-spec-playbook-discovery] Task-aware playbook discovery through spec

## 1. Problem Statement & Motivation

Handed off from proposal PROP-spec-playbook-discovery on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-spec-playbook-discovery`

### 1. Background & Hypothesis

The explicit `devkit-playbook` entry point is rarely used in practice. Procedures remain undiscovered unless
users already know to request a playbook or a failing rule names one. `spec` is the normal work entry point and
can provide a discovery opportunity without a separate user invocation.

Task kinds are broad categories: a feature or bugfix can still benefit from a specialized procedure. Workflow
routing alone therefore does not identify whether a playbook applies. Asking the agent to search only when a
reusable procedure would help also requires a relevance judgment before candidates are visible.

The proposed default is discovery when `spec` takes in a new task, with representative, explicit skip cases.
Established Planning and Development work already has a procedure and is a candidate for skipping discovery.
Candidate metadata stays bounded; only a selected procedure body is loaded. Adding a query to `get-context`
alone does not solve repeated discovery across tasks, because bundle context is loaded once per agent context
while task-specific candidates can change during the conversation.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Task-aware playbook discovery through spec so that system capabilities are extended.

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

- **Q1**: Which concrete examples distinguish new task intake from continuation, clarification, review fixes or
  retries? Define representative skip cases for clearly established Planning and Development work without using
  task kind or workflow membership as a universal exclusion.
- **Q2**: How much belongs in `spec`, and should `spec-playbook` own the full search-and-use procedure or only
  candidate application? Avoid repeated search and skill-body loading on the ordinary intake path.
- **Q3**: How is the generated `devkit-playbook` entry point removed or reduced in favor of `spec-playbook`, and
  what remains available to consumers that install playbooks without the `spec` bundle?
- **Q4**: What candidate count, output byte budget and repeat-search conditions provide useful discovery at a
  bounded cost? Compare missed candidates and unnecessary searches using representative task requests.

### 3. Proposed Design & Impact

- `spec` owns discovery at intake; no separate `spec-playbook` skill is created (§3a Q2). The generated
  `devkit-playbook` skill stays the spec-neutral explicit entry (§3a Q3).
- Let `spec` initiate discovery for new tasks by default, subject to explicit skip examples. Do not require an
  explicit playbook invocation or a pre-search judgment that a reusable procedure exists.
- Representative proposed skip cases are continuing an established proposal's Planning run, executing an agreed
  Development task, and answering questions or making corrections within that same ongoing work. Planning must
  distinguish these from a new request that starts a specialized adoption, review or maintenance procedure.
- Keep discovery independent of the broad feature/bugfix classification. A workflow can govern delivery while a
  playbook supplies a specialized procedure within the authorized task.
- Reuse `devkit playbook search/get` as retrieval primitives. Expose bounded candidate metadata from frontmatter
  before loading a selected body. Do not load the complete catalog or repeat unchanged bundle context.
- When no candidate applies, continue the ordinary work path. A search result grants no additional authority and
  does not expand the requested scope or bypass workflow gates.
- Reconcile the explicit-only restrictions in `spec`, the generated playbook skill, distribution guidance and
  `CAP-DIST-context-and-playbooks`, `CAP-HARN-agent-guidance` and `ARCH-08-2-resource-taxonomy`. Revisit
  `ADR-external-playbook-execution` where discovery entry conditions change; preserve exact retrieval and external
  execution boundaries.
- Verify new task discovery, each agreed skip case, same-task continuation, bounded metadata, no-match fallback,
  selected-body loading and consumers without the `spec` bundle, split into mechanical tests and recorded manual
  scenarios (§3a Verification split).
- Non-goals: search ranking changes, alias keyword indexing, scheduling, execution history, bulk context loading,
  and automatic execution beyond the user's authorized task.

### 3a. Planning direction

Evidence: [discovery evidence](../../../docs/materials/2026-10/20261026-spec-playbook-discovery/discovery-evidence.md), [intake frequency](../../../docs/materials/2026-10/20261026-spec-playbook-discovery/intake-frequency.md), the
challenger round historical Git `a3b0318924be4a9ee081cf3ae99bae1b8aa17058:docs/proposals/PROP-spec-playbook-discovery/envelopes/challenger-01.yaml` and the user's answers historical Git `a3b0318924be4a9ee081cf3ae99bae1b8aa17058:docs/proposals/PROP-spec-playbook-discovery/envelopes/answer-01.yaml`. Decision:
`ADR-spec-intake-playbook-discovery`.

#### Discovery trigger and skip cases (Q1, settled)

`spec` runs discovery once at **new task intake**: a `/spec <intent>`, or a request within an ongoing conversation that
falls outside the agreed scope of the current task. Only a user's own message is intake: no message from another agent
(Host payload, worker turn, nested role), no hook and no stage `devkit workflow next` names. Discovery runs as the
first step of intake, **before classification and before any Unit is created**, so a selected playbook's stated depth and scope inform the
classification (`adr-compaction` runs at `session` depth, and a `spec` Unit or a proposal under review can never be
lowered). Task kind (`feature`, `bugfix`, `overall-refactor`) and planning depth never exempt a task. Discovery is
skipped in these representative cases:

| Skip case | Example |
| --- | --- |
| Continuation of an existing proposal or Unit: `/spec-next`, a `planning-worker` or `development-worker` turn, a Host resuming a handoff or the stage `devkit workflow next` names | "Continue Planning for PROP-x"; a worker payload naming its unit |
| A follow-up within the same task: answers, clarifications, review fixes, retries, corrections of the delivered change | "Use option b"; "fix the lint error"; "rerun the tests" |
| The entry is already explicit: the user names a playbook ID (`devkit playbook get` directly), or a failing rule's remediation names one | "Run spec/adr-compaction" |
| Execution inside a selected playbook | A step of `brownfield-adoption` asks for a change; no nested search |
| An information-only question that requests no change and no operation | "What does `devkit sync` write?" |

Two conversation-level stops also skip discovery: the user said not to use playbooks in this conversation, and a
candidate the user declined is never offered again in the same conversation, even for a reworded request.

Not skipped: a new request after earlier work finished, even inside a Planning or Development conversation ("now clean
up open feedback"), and a question that asks how to perform an operation ("how do I adopt devkit here?").

- **Selection survives isolation**: when a task with a selected playbook continues to a Unit or proposal, the
  playbook ID is recorded in the `plan-intent` note (and the Unit's or proposal's records), so a worker that skips
  discovery still follows it.
- **Compaction**: one clause in the `spec` guidance fragment of the root guidance block states that a new task intake
  runs the `spec` intake step, so the rule survives a lost skill body.

#### Bounded retrieval (Q4, settled)

- One `devkit playbook search "<English query>" --limit 3 --max-bytes 4096` per intake. Intake overrides the project's
  `[playbooks] limit` and `max_bytes` on purpose; explicit discovery keeps the configured values. A header may reach
  4096 bytes, so the byte budget, not the current description lengths, is the bound. The probe measured 564 to 1810
  bytes at `limit=5`, about 0.2 to 0.3 s per search.
- The query is written with the repository's canonical artifact nouns (ADR, feedback, Living Spec, proposal,
  playbook, rule, release) in place of the user's paraphrase. The paraphrase probe shows this closes the misses:
  "clean up old decisions" omits `adr-compaction`, while "tidy up old ADRs" ranks it first in `hybrid` and `lexical`.
  No automatic refinement follows; a search runs again only at the next new task intake, and unchanged bundle context
  is not reloaded.
- **Selection rule** (tightened for offer frequency, [intake frequency](../../../docs/materials/2026-10/20261026-spec-playbook-discovery/intake-frequency.md) §5). Scores never
  decide: `hybrid` and `lexical` return candidates for unrelated tasks. A candidate is offered only when all hold:
  - **operation, not topic**: its `description` names the operation the request asks the agent to perform on the
    artifact; a request to build, fix or change the tool, code or documents about that artifact is a topic match and
    is never offered ("Feedback Quick Fixes" never offers `feedback-hygiene`);
  - **primary operation**: it covers the request's main operation, not one step of a larger change;
  - **scope fits**: its scope does not exceed the requested scope ("refactor the sync module" never offers a
    repository-wide review playbook);
  - **one line**: at most one offer line per intake.
- **No match** continues the ordinary path silently. The offer to draft a reusable playbook stays with explicit
  discovery only; `CAP-DIST-context-and-playbooks` §3 and `ARCH-08-2-resource-taxonomy` are reconciled to say so.
- **Search errors** at intake (`NOT_SYNCHRONIZED`, `CONFIG_LOCAL_RENDER_STALE`, `ARGUMENT_INVALID`,
  `SEARCH_EXTRA_MISSING`, a lock timeout) count as no match: intake never runs an error's remediation (such as
  `devkit sync`) for discovery's sake, and reports the error in one line only when it also blocks the task.
- Only a selected playbook's body is read (search path or `devkit playbook get`), after its bundle's context when that
  is not already loaded.

#### Ownership, entry skill and authority (Q2, Q3, settled by the user)

- **Ownership (Q2)**: `spec` owns the trigger, the skip table and the single search. The post-selection procedure (load
  the bundle's context, read the body, check prerequisites, follow it) is a `spec` reference file (for example
  `references/playbooks.md`) read only on a match. No `spec-playbook` skill exists: a model-invocable one would fire
  outside intake and bypass the skip table, and a user-only one cannot be routed from `spec`.
- **Generic entry (Q3)**: the generated `devkit-playbook` skill stays the explicit entry for every consumer, `spec` or
  not. Its body, the root guidance line and the `devkit playbook` CLI help are reworded spec-neutrally: the clause
  that references from other skills do not authorize discovery is dropped, and the draft offer stays with explicit
  discovery. `devkit-dist` gains no dependency on `spec` semantics; `spec` adds its intake step on top.
- **Confirm first**: every discovered candidate is named in one line together with the classification statement of
  intake step 1, and nothing of it runs before the user confirms. The confirmation is the explicit invocation, so each
  playbook's "the user asked for it" prerequisite reads "the user invoked or confirmed it". No match asks nothing.
- **`adr-compaction`**: confirming a discovered `adr-compaction` candidate is its explicit invocation and authorizes its
  deletions, at `session` depth.

#### Offer frequency (user concern)

[Intake frequency](../../../docs/materials/2026-10/20261026-spec-playbook-discovery/intake-frequency.md) measures it over the 105 spec titles in `specs/`: the search returns
a candidate for 84% of them, the selection rule offers one for 1 of 105 (a true positive), and 16 topical matches it
must reject form the false-positive sample. A false positive costs one line and a "no", never an action.

- **Acceptance criterion**: in Development's recorded manual run, the 16 ordinary intents of intake-frequency §6
  produce 0 offers, each positive control produces exactly its named offer, each skip and no-skip scenario behaves as
  its row states, and no intake produces more than one offer line.

#### Decision record

`ADR-spec-intake-playbook-discovery` records the direction; handoff promotes it to the new ADR. It partially replaces
two accepted ADRs, as `ADR-immutable-decisions-editable-records` §4 allows: the §4 statement "Ordinary requests do not
authorize discovery" and the matching §5 consequence of `ADR-external-playbook-execution`, and the compaction-invocation
statement of `ADR-immutable-decisions-editable-records` §4 (a confirmed discovered candidate is explicit invocation).
Each affected statement gets a one-line pointer. Exact receipt-backed retrieval without execution authority and
external scheduling and execution stay in force. `ADR-playbook-aliases-as-identifiers` is unaffected: discovery
searches name and description only and never aliases.

#### Verification split

- Mechanical: `devkit-spec` text-contract tests for the intake step (trigger, order before classification, skip
  table and conversation-level stops, `--limit 3 --max-bytes 4096`, canonical-noun query, the four selection
  conditions, confirm-first wording, silent no-match, error-as-no-match, recorded selection); `devkit-dist` tests for
  the reworded generated entry skill, guidance line and CLI help, which name no `spec` bundle asset.
- Manual evidence: one recorded scenario run per skip case and per no-skip case, kept in the Unit's materials and
  named as manual evidence, never reported as test coverage. The run includes the offer-frequency sample of the
  acceptance criterion and the paraphrase probe, with the `maintenance` catalog selected, which this Planning worktree
  could not synchronize.

#### Interactions

- `PROP-review-refactor` adds a `maintenance` playbook and owns `packages/devkit-catalog/src/devkit_catalog/maintenance/`
  and `docs/capabilities/delivery/`. This proposal edits the entry-condition wording of the existing maintenance
  playbooks there. The new playbook states its entry condition in the form settled here and a `description` that
  names its operation and scope; whichever proposal lands second reconciles the other's wording. Its proposal has no
  pointer back yet: the Host records the dependency there.
- `PROP-release-handbook` (draft) adds another explicitly invoked playbook and needs the same entry wording.

### 4. Lifecycle & Retirement Criteria

Planning settles the discovery boundary, skip examples, selection rule, offer-frequency bound, skill ownership and
application authority. Development starts only
through the proposal handoff after direction acceptance. Existing runtime and invocation contracts remain in force
until implementation is delivered.

