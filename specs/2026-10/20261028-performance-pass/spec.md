---
id: SPEC-performance-pass
title: Performance pass maintenance playbook
summary: Add a maintenance playbook that measures, profiles and applies behavior-preserving performance changes to user-selected commands with differential preservation evidence, separate from review-refactor.
status: in-progress
created: 2026-10-28
related_capabilities:
  - CAP-DLV-review-refactor
  - CAP-DIST-context-and-playbooks
  - CAP-DIST-content-packages
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-performance-pass] Performance pass maintenance playbook

## 1. Problem Statement & Motivation

The design was settled in Planning and accepted; its evidence is preserved in
`docs/materials/2026-10/20261028-performance-pass` (`pass-evidence.md`, `design-options.md`), and its lasting
decisions are `ADR-keep-performance-passes-in-a-separate-maintenance-playbook`,
`ADR-reuse-review-refactor-application-through-exact-playbook-retrieval`,
`ADR-measure-performance-unprofiled-and-interleaved-in-one-session` and
`ADR-classify-performance-changes-by-observable-behavior`.

A performance pass over this repository on 2026-10-27 (per commit, warm and unprofiled: file listing in a full rules
check 0.30 s to 0.05 s, a one-file rules check 0.44 s to 0.33 s, `sync --dry-run` 1.25 s to about 0.92 s with
subprocesses 29 to 14; `pass-evidence.md` §1) borrowed the `maintenance/review-refactor` procedure, but its goal is
latency, not a smaller surface, and it needed steps that playbook does not have: a measured baseline, profiling
without being misled by profiler inflation or child processes, per-component timing, and differential old/new
comparisons as preservation evidence. A fresh review still found a regression (a symlink loop breaking every file
listing) that tests missed (`pass-evidence.md` §2). Session totals taken in another measuring session differed from
the per-commit figures; that cross-session noise is what the measurement protocol addresses.

Hypothesis: a separate, router-structured maintenance playbook that turns a user-selected set of slow operations into
measured, behavior-preserving changes with differential evidence makes such passes repeatable in any repository and
keeps `review-refactor` focused on maintenance cost.

## 2. User Stories

- **US-1**: As a developer whose agent runs a performance pass, I want each reported saving measured unprofiled and
  interleaved against the previous revision in one session, so that the numbers survive repetition.
- **US-2**: As a developer deciding candidates, I want each candidate's measured share, expected saving, risk and
  classification in one decision round, so that I approve only behavior-preserving speedups as such and see contract
  changes separately.
- **US-3**: As a maintainer of the `maintenance` bundle, I want the performance pass to reuse `review-refactor`'s
  application and evidence procedure by reference, with a test that fails when a cited section disappears, so that
  the two playbooks do not drift.

## 3. Non-Goals

1. **Scope Excluded**: a regression-investigation mode or bisection; it is added when a real regression run shows the
   need (`design-options.md` O1).
2. **Scope Excluded**: a bundled timing script, an executable-bit contract for playbook directories, a deploy test for
   one or script unit tests (`user`, O4 B).
3. **Scope Excluded**: extending the direct-mode overall-refactor route to performance passes; `review-refactor`'s
   "Work items and route" stays its own (`user`, O7 A).
4. **Scope Excluded**: adding `performance-pass` to `upkeep` or changing `refactoring` or `reporting` (O5 A).
5. **Scope Excluded**: a milestone (`user`); handbook entries, which follow at the next release; any change to
   `review-refactor`'s text.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The bundle declares the playbook and the `performance` preset
- **Given** the `maintenance` bundle manifest
- **When** it is loaded and a project selects each preset in turn
- **Then** `performance-pass` is a `playbook` asset with source `playbooks/performance-pass`; the declared presets are
  exactly `upkeep`, `reporting`, `refactoring` and `performance`, with `performance` = {`performance-pass`,
  `review-refactor`} and the other three unchanged; implicit `all` deploys the four playbooks
- **And** after sync, the managed files are exactly the selected playbooks' files, and lexical search and exact
  `devkit playbook get maintenance/performance-pass` return the playbook with a non-empty body

### [AC-02] Every preset that deploys `performance-pass` deploys `review-refactor`
- **Given** the presets of the `maintenance` bundle, implicit `all` included
- **When** the bundle test checks membership
- **Then** each preset containing `performance-pass` also contains `review-refactor`

### [AC-03] Every citation of `review-refactor` names an existing heading
- **Given** the playbook files of `performance-pass`
- **When** the bundle test parses every citation of the form `review-refactor references/<file>.md "<heading>"`
- **Then** it finds at least the sections `references/applying.md` "Work items and route", "Branch and edit tasks",
  "Subagent edits", "Commits and verification", "Review", "Report", "Integration", "Contract removals" and
  `references/criteria.md` "Preservation evidence"
- **And** each parsed heading, with its leading number removed, is a heading of the named `review-refactor` file

### [AC-04] The entry condition authorizes no change before the decision round
- **Given** `performance-pass`'s `SKILL.md`
- **When** an agent loads it by invocation, a confirmed intake offer or an external runner
- **Then** the body states that it runs only when the user invoked or confirmed it, that invocation, an external
  runner and a clean measurement authorize no change, and that an unattended run stops at the decision round with
  nothing applied
- **And** the `description` names a performance pass over user-selected slow operations with measured and
  differential evidence, so that intake discovery offers it only for a performance request

### [AC-05] The playbook is a self-contained router within budget
- **Given** the `performance-pass` directory
- **When** the bundle test and `uv run devkit rules check --phase hygiene` inspect it
- **Then** it holds exactly `SKILL.md` and `references/{measurement,profiling,candidates,changes}.md`; `SKILL.md`
  links each reference with a read condition; no reference links another of the playbook's references; each file is
  at most 12288 bytes; no file names a repository document ID; the hygiene check reports no
  `RULE-skill-document-size` or `RULE-agent-asset-wording` violation for them

### [AC-06] `review-refactor` is resolved by exact retrieval and read, never run
- **Given** a run that reaches the decision round
- **When** the agent follows `SKILL.md`
- **Then** it runs `devkit playbook get maintenance/review-refactor`, reads each cited file under `references/` next
  to the returned `source.path`, reads the managed copy when an override directory lacks the file, starts none of
  `review-refactor`'s intake, batches or decision round, and stops with a report when a cited heading is missing

### [AC-07] Measurement follows the unprofiled, interleaved protocol with no bundled script
- **Given** `references/measurement.md`
- **When** an agent times a target
- **Then** it times the real process from outside with an exact argument list, working directory and environment;
  uses an installed benchmark tool (for example `hyperfine`) or its own short loop, either meeting the same
  requirements: a discarded warm-up per variant, at least five interleaved repetitions per variant, each run's exit
  code checked and its output compared, failed runs dropped, median, minimum and range reported
- **And** it defines the noise floor, the quiet-machine rule with load recorded before and after, cold and warm
  labels, old and new against the same input without stashing or switching the working checkout, per-component
  timing for composite operations and the baseline record, and every comparison re-runs the older revision in the
  same session

### [AC-08] Candidates are classified by observable behavior and routed through the feature workflow
- **Given** `references/candidates.md`
- **When** the agent prepares the decision round
- **Then** each candidate records location, cost mechanism, unprofiled measured share, proposed change, expected
  saving, risk, classification, planned differential inputs, route and write scope; candidates below the noise floor
  are dropped and counted; behavior-preserving and contract-change criteria match
  `ADR-classify-performance-changes-by-observable-behavior`
- **And** the agreed behavior-preserving changes form one work item following the repository's feature workflow at
  its own depth, for one module or several, and `review-refactor`'s "Work items and route" is stated as not followed

### [AC-09] Application reuses `review-refactor` with the performance overrides and additions
- **Given** `references/changes.md`
- **When** the round approved changes
- **Then** it cites the shared sections, states that every difference found by the differential comparison or review
  is fixed or returned as its own contract-change work item, that timing waits until no edit task or verification
  runs, that each change is measured old against new and recorded in its commit body, that differential inputs
  include error cases and unusual states, the reviewer brief additions, and the final interleaved measurement of every
  target against the intake revision

### [AC-10] Modes, report and completion
- **Given** `SKILL.md`
- **When** a run selects a mode and ends
- **Then** `survey` loads measurement, profiling and candidates and stops at the decision round with nothing applied
  (an approved change turns it `targeted`, recorded in the report); `targeted` loads every reference in phase order
- **And** the report holds intake and environment, mode, targets and baselines, coverage, candidates and changes as
  separate records, decisions with provenance, follow-ups, counts, the final measurement and the outcome
  (`stopped at decision round`, `applied`, `partially applied`); a run is complete with no pending decision, every
  agreed change committed or routed and the final measurement recorded

### [AC-11] Catalog documentation names the preset
- **Given** `packages/devkit-catalog/README.md` and `guides/install/bundle-recommendations.md`
- **When** a reader looks up the `maintenance` bundle
- **Then** both list the `performance` preset with `performance-pass` and `review-refactor`, and default `all` as the
  four playbooks

## 5. Design Contract

The playbook's content follows the accepted design; the plan maps it to files.

- **Router layout**: `SKILL.md` (header; entry condition; constraints for every run: no change without the decision
  round, behavior preservation, measurement honesty, receipt-owned files read-only, a correctness defect found on the
  way is a follow-up, never stash; intake; mode table; resolving `review-refactor`; decision round dispositions and
  route; report fields; completion), `references/measurement.md` (every mode, before the first timed run),
  `references/profiling.md` (when measurement does not already name the cost), `references/candidates.md` (before the
  decision round), `references/changes.md` (after the round approved changes). The application reference is named
  `changes.md` so it is never confused with `review-refactor`'s `references/applying.md`. Each file aims at about
  9.5 KB.
- **Intake**: run ID, credential-free repository identity, HEAD, dirty paths, prior reports, report destination,
  plus machine, operating system, runtime versions and the load at intake. The user selects each target as an exact
  argument list with working directory and environment, the metric (wall time, subprocess count, peak memory) and an
  optional goal; missing scope is clarified before any timed run.
- **Citation form**: `review-refactor references/<file>.md "<heading text without its number>"`.
- **Attribution** (`profiling.md`): profile only to attribute cost; deterministic profilers inflate wall time two to
  three times and call-heavy code more than I/O, so confirm a share unprofiled; sampling profilers only when
  installed; count and time subprocesses separately; measure collector time and object counts for large object
  graphs; profile cold and warm separately; measure startup and import time on their own; tools named only as
  examples, installed only with the user's consent.
- **Dispositions**: apply with behavior preserved, contract change, defer (destination and restart condition), keep
  (reason); all candidates of the run decided in one round; unanswered ones stay pending. A measured cost no change
  can remove is reported as kept with its reason. Removing repeated work is preferred over micro-optimization.

## 6. Living Spec Impact

- New capability CAP-DLV-performance-pass under `docs/capabilities/delivery/`, entrypoint the playbook's `SKILL.md`.
- New use case UC-speed-up-selected-slow-operations under `docs/usecases/governance/`.
- `CAP-DIST-context-and-playbooks` §5: a playbook may read a co-deployed playbook's body resources as reference text;
  that is no invocation and starts none of its intake or decision rounds.
- `CAP-DIST-content-packages` §6: the `performance` preset, the co-deployment constraint, reference reading without
  running, and four playbooks under `all`.
- `CAP-DLV-review-refactor`: its application and evidence section headings are cited by `performance-pass`, so a
  rename needs a matching edit there.

## 7. Assumptions

1. The new capability and use case slugs are CAP-DLV-performance-pass and UC-speed-up-selected-slow-operations; the
   proposal named no slugs.
2. The `maintenance` bundle version stays as is: catalog bundle versions follow the package version, which a release
   bumps (`test_registered_bundle_loads_under_its_entry_point_name`).
3. The base contains merge `dc3e07a2` (checked with `git merge-base --is-ancestor`), so every cited `review-refactor`
   section exists; no premise of the accepted design differs on the current base.
4. "No reference sends the agent to another of its own references" is tested by the absence of a
   `references/<name>.md` link inside each reference; citations of `review-refactor`'s files use the citation form,
   not a link.

## 8. Planning Decisions

- Settled by `user` at intent: a separate maintenance playbook, router-structured, in the `maintenance` bundle beside
  `review-refactor`, reusing its parallel application and differential evidence by reference.
- Settled in Planning: two modes, no regression mode (O1); exact retrieval with co-deployment, override fallback and a
  parseable citation form (O2); report in `SKILL.md` (O3); preset `performance`, `upkeep` unchanged (O5); the
  measurement protocol and change classification decisions; for performance changes every found difference is a
  contract change.
- Decided by `user`: `q1` the behavior-preserving work item follows the repository's feature workflow at its own
  depth, for one module or several (O7 A); `q2` no milestone (`MS-maintenance-operations` stays `done`); `q3`
  procedure only, no bundled timing script, with tool-neutral timing-loop requirements in `references/measurement.md`
  (O4 B).

## 9. Lifecycle & Retirement Criteria

Retire or merge into `review-refactor` if a later run shows the two playbooks share most of their procedure.
