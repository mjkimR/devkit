---
id: SPEC-feedback-guidance-fixes
title: Feedback Guidance Fixes
summary: 'Resolves five open feedback items: a discoverable proposal report template, a reverify fix that names the reconcile-check path, PADR withdrawal and answer-correction procedures in the Planning guides, and handoff placement of carried validation scenarios.'
status: in-progress
created: 2026-10-22
namespace: global
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-workflow-envelopes
  - CAP-DLV-spec-bundles
  - CAP-HARN-agent-guidance
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-guidance-fixes] Feedback Guidance Fixes

## 1. Problem Statement & Motivation

Five open feedback items report friction an agent hit while following the delivery workflow:

- A caller of `spec_proposal_report` cannot discover the required report structure: the domain-owned
  `template(root, slug, sha)` has no CLI or MCP route, and `PROPOSAL_REVIEW_INVALID` names neither the failed field
  class nor a retrieval route.
- `devkit workflow envelope reverify --from envelopes/reconcile-check-NN.yaml` is refused with a `[FIX]` that names
  only review and challenger rounds, not the reconcile-check route that closes a reconcile finding.
- The Planning reference says how a PADR is recorded but not how one withdrawn before `plan-accept` is handled,
  although handoff promotes every PADR left in `decisions/`.
- The worker-records reference gives no record for the user's correction of an already-recorded answer.
- Proposal handoff classifies a heading that names both acceptance evidence and non-goals as Non-Goals, so carried
  positive validation scenarios land under `## 3. Non-Goals`.

## 2. User Stories

- **US-1**: As an agent publishing a proposal review report, I want a supported route to the report template and a
  refusal that names what failed, so that I can build a valid briefing without reading the implementation.
- **US-2**: As an agent closing a reconcile finding, I want the reverify refusal to name the reconcile-check route.
- **US-3**: As a Planning worker, I want the Planning guides to say how to withdraw a PADR and how to record an answer
  correction, so that the records stay truthful without improvised procedures.
- **US-4**: As an agent normalizing a handed-off spec, I want carried validation scenarios kept apart from exclusions.

## 3. Non-Goals

1. **Scope Excluded**: Weakening any source, language, identity or coverage check of report publication.
2. **Scope Excluded**: New envelope kinds, statuses or fields; a withdrawn-PADR status; CLI changes for answer
   corrections (the existing `answer` command already accepts a later answer to an answered question).
3. **Scope Excluded**: Changing the `spec-delegate` skill text (outside this unit's write scope); the reconcile route
   is already stated in the `spec` skill's `references/effort.md`.
4. **Scope Excluded**: Splitting a mixed carried section into acceptance criteria and non-goals automatically.

## 4. Assumptions

- **A1 (template route)**: the CLI route is a `--template` flag on `devkit spec proposal report`, mutually exclusive
  with `--body-file`; the MCP route is a separate `read_only` tool `spec_proposal_report_template(slug, source_sha)`
  that resolves the source like `spec_proposal_report`. A separate read-only tool keeps publication's
  `bounded_write` contract unchanged and is available under the read-only MCP profile.
- **A2 (field classes)**: the refusal message prefixes the failed class (`identity`, `title`, `sections`,
  `decisions`, `decision fields`, `coverage`, `dev_effort`, `size`, `source`) and names the mismatched keys,
  headings, PADR IDs or tokens; the `[FIX]` names both template routes.
- **A3 (mixed sections)**: an H2 heading is a carried contract when it names a non-goal keyword together with
  `acceptance`, `validation` or `verification`. A heading naming validation or verification alone (such as
  `Lifecycle & Verification`) stays a carried note, which is already neutral. A carried contract keeps its heading
  as H3 with inner headings demoted under a neutral `Carried Proposal Contract` section placed after the acceptance
  criteria; Non-Goals keep their placeholder and leftover notes follow it with the next section number.
- **A4 (scope of item 2)**: the Host's payload scopes the reverify feedback to the `[FIX]` text; the `spec-delegate`
  sentence its suggestion also names stays as it is and is reported as a follow-up observation.

## 5. Acceptance Criteria & Behavioral Contracts

### [AC-01] CLI prints the report template without publishing
- **Given** a clean committed Planning branch `plan-example` with the example proposal, one PADR and one envelope
- **When** `devkit spec proposal report example --source-sha <HEAD> --template` runs
- **Then** it exits `0`, stdout is the template Markdown whose frontmatter binds `proposal`, `source_sha`,
  `language` and `repository_namespace` and which names the PADR and the envelope file, no artifact is published,
  and `--format json` returns one object with `proposal`, `source_sha` and `template`

### [AC-02] Template and body options are exclusive
- **Given** the same repository
- **When** `devkit spec proposal report example --source-sha <HEAD>` runs with both `--template` and `--body-file`,
  or with neither
- **Then** it exits `2` with `ARGUMENT_INVALID` and publishes nothing

### [AC-03] Read-only MCP template route
- **Given** the MCP tools of the proposal report module
- **When** `spec_proposal_report_template` is invoked with `slug` and `source_sha`
- **Then** it is declared `execution=read_only` with `read_only=True`, returns `{"template": ...}` equal to the CLI
  template, requests no confirmation, and the `spec_proposal_report` description names
  `spec_proposal_report_template`

### [AC-04] Refusal names the failed field class and the route
- **Given** a briefing that fails one check (wrong `source_sha`, a missing PADR, a missing decision field, a missing
  envelope token)
- **When** it is published
- **Then** `PROPOSAL_REVIEW_INVALID` is raised, its message starts with the failed class (`identity`, `decisions`,
  `decision fields`, `coverage`) and names the mismatched key, PADR ID or token, and its `[FIX]` names
  `--template` and `spec_proposal_report_template`; every briefing refused before the change is still refused

### [AC-05] Review skill names the template route
- **Given** the synced `spec-review-proposal` skill (local and cloud renderings)
- **When** an agent reads its publication step
- **Then** it names `--template` (both renderings) and `spec_proposal_report_template` (local rendering)

### [AC-06] Reverify refusal names the reconcile-check route
- **Given** a unit with `envelopes/reconcile-check-01.yaml`
- **When** `devkit workflow envelope reverify --from envelopes/reconcile-check-01.yaml` runs
- **Then** it exits `2` with `ENVELOPE_FROM_INVALID`, its `[FIX]` names `--kind reconcile-check` (a new
  reconcile-check envelope) and the reconcile-reviewer, and a `scout` source keeps the existing challenger `[FIX]`

### [AC-07] Planning reference states PADR withdrawal
- **Given** the `spec` skill's `references/planning.md`
- **When** a Planning turn withdraws a PADR before `plan-accept`
- **Then** the reference says to delete the PADR file in the fold commit and to name the withdrawn PADR ID and the
  reason in the proposal's Planning decisions

### [AC-08] Worker records state answer corrections
- **Given** the `spec` skill's `references/worker-records.md`
- **When** the user corrects an already-recorded answer
- **Then** the reference says to record a later `answer` envelope naming the same `worker` envelope, re-answering
  that question with the corrected decision and naming the corrected `answer-NN.yaml` in its summary, leaving the
  earlier envelope unchanged, and the existing `envelope answer` command accepts that envelope (exit `0`)

### [AC-09] Handoff keeps carried validation scenarios out of Non-Goals
- **Given** a proposal with a `## 4. Acceptance Evidence and Non-Goals` section holding AC1 and AC2 items
- **When** the proposal is handed off
- **Then** the generated `spec.md` has the AC items under `## 5. Carried Proposal Contract`, `## 3. Non-Goals` holds
  only the `Scope Excluded` placeholder, and a leftover notes section follows as `## 6. Carried Proposal Notes`

### [AC-10] Living Spec and checks
- **Given** the change complete
- **When** `uv run devkit sync`, `uv run devkit rules check` and `just test-affected` run
- **Then** all exit `0`, and `CAP-DLV-proposal-incubation`, `CAP-DLV-spec-bundles`, `CAP-DLV-workflow-envelopes`
  and `CAP-HARN-agent-guidance` describe the changed behavior

## 6. Source feedback

Each open source is resolved directly by this spec:

- `FB-proposal-report-template-discovery`: AC-01 to AC-05.
- `FB-reverify-fix-omits-reconcile-check`: AC-06.
- `FB-padr-withdrawal-unspecified`: AC-07.
- `FB-answer-correction-unrecorded`: AC-08.
- `FB-handoff-skeleton-scenario-placement`: AC-09.
