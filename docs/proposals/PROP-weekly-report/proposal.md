---
id: PROP-weekly-report
title: Evidence-based weekly maintenance reporting
summary: Define a manually invoked weekly-report playbook that turns revision-bound repository evidence into a report and prioritized follow-ups while separating generation from authorized publication.
status: accepted                         # draft | reviewing | accepted | rejected
created_at: 2026-10-21
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-reporting-and-actionable-insights
boundaries:
  owns:
    - packages/devkit-catalog/
    - guides/
    - docs/capabilities/delivery/
    - docs/capabilities/distribution/
    - docs/stories/governance/
  excludes:
    - packages/devkit/src/devkit/integration/
    - packages/devkit-dist/src/devkit/shared/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-weekly-report] Evidence-based weekly maintenance reporting

## 1. Background & Hypothesis

`MS-reporting-and-actionable-insights` calls for a manually invoked report that makes completed work, decisions,
repository health and next actions inspectable. The maintenance bundle introduced by `PROP-periodic-drift-reconciliation`
is the delivery home. A reporting procedure can consume available evidence without running drift or refactoring
first, and without a scheduler or history backend.

## 2. Planning Outcome

Deliver a manually invoked, content-only `maintenance/weekly-report` playbook. It collects available evidence,
writes a local Markdown report and separately publishes only when destination and authority are explicit.
The recommended Development effort remains medium. No runtime, scheduler, detector, or history backend is needed.

## 3. Proposed Design & Impact

### 3.1 Intake and observation boundaries

Record repository identity (a local canonical path or configured remote, without credentials), scope, inspected
commit SHA, selected integration branch/ref and its resolved SHA, generation timestamp, and dirty state before
collection. Never fetch, switch branches or change source files implicitly. The default observation interval is
the previous complete Monday-to-Monday calendar week in the user's configured timezone; if no timezone is known,
require it at invocation. Accept explicit start/end timestamps instead. Record inclusive start, exclusive end,
timezone name and UTC offsets at both boundaries; daylight-saving weeks need not contain 168 hours.

Separate events during the interval from the current snapshot at the inspected revision. Git commit timestamps
are discovery hints, not proof of integration date. Record the event timestamp basis for each dated claim. When
integration time cannot be established, state that limitation and report reachable changes without claiming they
were integrated during the interval. A selected ref is a local snapshot, not proof of remote freshness.

Default evidence is committed state at the captured SHA. Mark checkout-only lookup output as working-tree
observation and reconcile it against that SHA; do not attribute dirty documents to committed history. Include
uncommitted changes only when expressly selected, preserving an evidence diff/artifact reference and labeling
it separately. If the inspected state changes during collection, mark affected evidence unverified or restart
collection against a newly captured revision; do not silently mix snapshots.

### 3.2 Evidence and report structure

Use existing Git inspection, `CAP-DOCS-document-lookup` (including completed specs through `--history`, all intended
namespaces and complete pagination), workflow records and existing check artifacts. Inspect changed decisions,
capabilities and stories for behavior changes. No new command API is assumed. Reports contain:

1. Identity, interval, timezone, scope, revision, dirty state and evidence inventory.
2. Completed work and integration evidence; implementation complete but not verified integrated is separate.
3. Added or changed ADRs and significant behavior changes with document IDs and commit evidence.
4. Repository health: available hygiene, drift and review/refactoring results with source revision, scope,
   observed time and result; missing, stale, failed and not-comparable are explicit states, never a clean result.
5. Unresolved problems and prioritized next actions, including links to existing feedback/proposals.
6. Comparison to a named prior report when available, limitations, and generation/publication outcomes.

A proposal acceptance, task checkbox or commit alone never proves delivered work. For spec work, corroborate
completed status with tasks, verification/reconcile evidence and reachability of the delivered commits from the
selected integration SHA. For session work, cite the change, verification report and reachability evidence.
Missing evidence lowers the claim to unverified, not completed. Do not infer remote release or deployment.

Each factual claim cites a commit plus path/document ID, work-unit envelope, or check artifact; assessments are
labeled separately. Check outcomes apply only to their recorded revision and scope. Reuse available results;
generation does not automatically run maintenance sweeps or full checks. A missing or failed optional source
permits a generated report with explicit limitations; inability to capture repository/interval identity or write
and verify the report makes generation failed.

Compare findings only when prior/current scope, finding identity and supporting evidence are compatible.
Match by existing feedback/proposal ID first, otherwise by source, affected target and substantive discrepancy.
An item is resolved only with direct resolution evidence covering it; absence from this week's report is unknown.
Mark first observations new and evidenced continuing items recurring; record non-comparability instead of guessing.
Rank actions by demonstrated impact and urgency, state the reason and next step, and link matching open feedback
or proposals. Terminal feedback remains traceability and is not reopened merely because it appears in history.
The report recommends follow-ups; generation creates no feedback, proposals or fixes automatically.

### 3.3 Artifact identity, reruns and publication

Write to an explicitly selected local artifact location, defaulting to the owning work unit's materials directory
or the repository's existing materials location. If neither exists, resolve the output location at invocation;
do not silently create a tracked report on the default branch. Reuse existing material conventions when applicable.
No seven-day TTL applies to this report; retention policy and a history backend remain separate work.

The logical report key comprises repository identity, scope and exact interval/timezone. Each generation has a
unique run ID and captured source SHA; a rerun creates a new artifact and names any superseded run, preserving
previous evidence. Never silently overwrite a different artifact. Retrying publication reuses the same run ID
and exact artifact; changed content is a new run. A prior artifact is optional input, with no automatic history
service discovery assumed.

Generation outcome and publication outcome are independent. Generation is completed only after the local report
exists and its identity and evidence links have been checked. Publication states are pending (no destination or
permission), published (verified destination receipt/link), failed (confirmed failure), and unknown (lost response
or unverifiable destination). Store the artifact reference and content digest, destination, authority basis and
receipt separately from the report's immutable content, using a local companion outcome record. This avoids
changing the report bytes after a successful publication. No destination means a useful generated report with
pending publication; no upload, message, commit, push or external mutation follows implicitly.

Publication uses only an existing authorized connector/command for a user-selected destination; the playbook adds
no connector or platform-specific storage protocol. Before retrying an unknown result, inspect destination state
for that run and digest; if it cannot be verified, leave unknown and request a disposition rather than duplicate
publication. Destination replacement requires explicit authority and collision checks. No publisher or unavailable
permissions leave publication pending; publication failure never erases successful generation.

### 3.4 Distribution, dependencies and verification

Build on the accepted content layout of `PROP-periodic-drift-reconciliation`: the opt-in content-only maintenance
bundle in `packages/devkit-catalog/`, `default_preset = "all"`, no `auto_select` and no reserved `[presets.all]`.
Add the weekly-report asset and `reporting` preset, extend implicit all and preserve all delivered upkeep assets.
Selection never executes a playbook. Follow `CAP-DIST-context-and-playbooks` for explicit invocation and on-demand
body loading. Update catalog package tests, README and bundle recommendations under `guides/`.

The maintenance implementation is absent from this Planning base. Weekly-report can initialize the accepted
content-only bundle layout when absent, delivering reporting and implicit all with only weekly-report; do not
advertise upkeep until its assets exist. When maintenance is present, extend its manifest and preserve every
existing asset and preset. This contribution does not wait for companion playbooks. The Host serializes actual
catalog writes with overlapping Development and incorporates committed work before the next writer starts;
validate the manifest, asset layout and tests in that refreshed worktree. Planning relies on accepted content
design, not an invented sibling-worktree API.

Development reconciles the reporting procedure into delivery capabilities and a governance story, with
bidirectional traceability, and updates distribution contracts only where the asset changes documented behavior.
Existing parent directories in frontmatter are the allowed creation boundaries. A new reporting capability/story
will be named during specification; no runtime source or scheduling/history contract changes are required.

Acceptance evidence covers:

- A manual report for a bounded interval with completed and unintegrated work, changed decisions, and linked actions.
- Missing/stale/failed maintenance evidence, absent prior report and non-comparable scopes without false clean or
  resolved claims; existing follow-ups reused without creating duplicate work.
- Dirty checkout and changing revision, half-open interval boundaries and a daylight-saving interval; evidence
  that predates the interval is labeled as a snapshot rather than an event.
- Same-period rerun preserves the first artifact; publication retry retains identity and content digest.
- No destination/authorization, verified authorized publication using a controlled fixture, failure and lost
  response; generation stays distinct and no unapproved external writes occur.
- Catalog discovery, reporting/upkeep/all selection, explicit invocation, header validation and consumer smoke.

Use relevant catalog tests and package smoke, governance rules and the affected-test selector; verify the prose
procedure with recorded manual scenarios. Fixture publication needs no real external destination. No generic
publisher runtime or automation test harness is introduced solely to test prose.

## 4. Lifecycle & Retirement Criteria

Feature / proposal depth. Planning and recommended Development effort are medium. This proposal is ready for the
user's direction gate once its independent challenger findings are settled; acceptance is not Development start.
Companion playbooks are not prerequisites; overlapping catalog changes are coordinated by the Host. No milestone
transition belongs to this proposal.

**Scope excluded:** scheduler implementation, external analytics, automatic source fixes or maintenance sweeps,
new detection commands, standalone skills, a report database, GitHub orphan-branch history storage
(`MS-maintenance-history`), automatic follow-up creation, and publication without authorization. The future history
milestone remains the tracked destination for durable history integration and does not block manual reporting.
