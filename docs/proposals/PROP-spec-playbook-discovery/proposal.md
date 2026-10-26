---
id: PROP-spec-playbook-discovery
title: Task-aware playbook discovery through spec
summary: "Moves the agent playbook entry point toward spec-playbook and lets spec discover procedures for new tasks, with explicit skip cases for established Planning and Development work."
status: reviewing                      # draft | reviewing | accepted | rejected
created_at: 2026-10-23
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/tests/
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/
    - packages/devkit-dist/tests/
    - packages/devkit-catalog/README.md
    - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/
    - guides/install/
    - docs/capabilities/distribution/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/
    - docs/usecases/governance/
    - docs/architecture/
    - docs/decisions/
  excludes:
    - Search ranking algorithm changes
    - Scheduling and execution history
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-spec-playbook-discovery] Task-aware playbook discovery through spec

## 1. Background & Hypothesis

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

## 2. Technical Spike Questions

- **Q1**: Which concrete examples distinguish new task intake from continuation, clarification, review fixes or
  retries? Define representative skip cases for clearly established Planning and Development work without using
  task kind or workflow membership as a universal exclusion.
- **Q2**: How much belongs in `spec`, and should `spec-playbook` own the full search-and-use procedure or only
  candidate application? Avoid repeated search and skill-body loading on the ordinary intake path.
- **Q3**: How is the generated `devkit-playbook` entry point removed or reduced in favor of `spec-playbook`, and
  what remains available to consumers that install playbooks without the `spec` bundle?
- **Q4**: What candidate count, output byte budget and repeat-search conditions provide useful discovery at a
  bounded cost? Compare missed candidates and unnecessary searches using representative task requests.

## 3. Proposed Design & Impact

- Prefer `spec-playbook` as the agent-facing skill name. Reduce reliance on the generated `devkit-playbook`
  entry point. Settle skill ownership and whether a separate skill remains during Planning.
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
  selected-body loading and consumers without the `spec` bundle.
- Non-goals: search ranking changes, alias keyword indexing, scheduling, execution history, bulk context loading,
  and automatic execution beyond the user's authorized task.

## 3a. Planning direction

Evidence: [discovery evidence](materials/discovery-evidence.md). Open user decisions are listed as pending; the rest
is the working direction this Planning turn settled.

### Discovery trigger and skip cases (Q1, settled)

`spec` runs discovery once at **new task intake**: a `/spec <intent>`, or a request within an ongoing conversation that
falls outside the agreed scope of the current task. Task kind (`feature`, `bugfix`, `overall-refactor`) and
planning depth never exempt a task. Discovery is skipped, with these representative cases:

| Skip case | Example |
| --- | --- |
| Continuation of an existing proposal or Unit: `/spec-next`, a `planning-worker` or `development-worker` turn, a Host resuming a handoff or the stage `devkit workflow next` names | "Continue Planning for PROP-x"; a worker payload naming its unit |
| A follow-up within the same task: answers, clarifications, review fixes, retries, corrections of the delivered change | "Use option b"; "fix the lint error"; "rerun the tests" |
| The entry is already explicit: the user names a playbook ID (`devkit playbook get` directly), or a failing rule's remediation names one | "Run spec/adr-compaction" |
| Execution inside a selected playbook | A step of `brownfield-adoption` asks for a change; no nested search |
| An information-only question that requests no change and no operation | "What does `devkit sync` write?" |

Not skipped: a new request after earlier work finished, even inside a Planning or Development conversation ("now clean
up open feedback"), and a question that asks how to perform an operation ("how do I adopt devkit here?").

### Bounded retrieval (Q4, settled)

- One `devkit playbook search "<English query>" --limit 3` per intake; the default `--max-bytes` stays. The probe
  measured 564 to 1810 bytes at `limit=5`, about 360 bytes per candidate, with every relevant playbook ranked first.
- No automatic query refinement. A search runs again only at the next new task intake; unchanged bundle context is
  not reloaded.
- A candidate is selected only when its `description` names the requested operation. Scores never decide: `hybrid`
  and `lexical` return candidates for unrelated tasks. When no description fits, `spec` continues the ordinary path
  without mentioning the search.
- Only a selected playbook's body is read (search path or `devkit playbook get`), after its bundle's context when
  that is not already loaded.

### Decisions pending the user

- **Q2 ownership** between `spec` and `spec-playbook` (worker question `ownership`).
- **Q3 the generated `devkit-playbook` skill** and consumers without `spec` (worker question `entry-skill`).
- **Application authority** after a match, which decides how the playbooks' explicit-invocation prerequisites are
  rewritten (worker question `apply-authority`).

### Decision record

Discovery from ordinary task intake reverses `ADR-external-playbook-execution` §4 ("Ordinary requests do not
authorize discovery"). Development writes a new ADR that supersedes it and restates its retained decision: exact
receipt-backed retrieval without execution authority, external scheduling and execution. A PADR records the
direction once the pending decisions are answered.

### Interaction with PROP-review-refactor

`PROP-review-refactor` adds a `maintenance` playbook and owns `packages/devkit-catalog/src/devkit_catalog/maintenance/`
and `docs/capabilities/delivery/`. This proposal edits the entry-condition wording of the existing maintenance
playbooks there. The new playbook states its entry condition in the form settled here and a `description` that names
its operation; whichever proposal lands second reconciles the other's wording.

## 4. Lifecycle & Retirement Criteria

Keep this proposal in draft until Planning is requested. Planning settles the discovery boundary, skip examples,
skill ownership and the division of responsibility between `spec` and `spec-playbook`. Development starts only
through the proposal handoff after direction acceptance. Existing runtime and invocation contracts remain in force
until implementation is delivered.
