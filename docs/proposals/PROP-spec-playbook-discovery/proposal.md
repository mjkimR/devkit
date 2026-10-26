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
    - packages/devkit-dist/tests/
    - docs/capabilities/distribution/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/
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

## 4. Lifecycle & Retirement Criteria

Keep this proposal in draft until Planning is requested. Planning settles the discovery boundary, skip examples,
skill ownership and the division of responsibility between `spec` and `spec-playbook`. Development starts only
through the proposal handoff after direction acceptance. Existing runtime and invocation contracts remain in force
until implementation is delivered.
