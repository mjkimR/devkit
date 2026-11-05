---
id: PROP-test-management
title: Evidence-based test management playbook
summary: "Evaluate a reusable test-management playbook for consumer repositories using findings from an unreviewed implementation draft. Establish evidence, scope and verification criteria before adopting runner, tiering or integration guidance."
status: accepted
created_at: 2026-11-05
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/
    - packages/devkit-catalog/tests/integration/bundles/test_bundles.py
    - packages/devkit-catalog/README.md
    - docs/capabilities/delivery/
    - docs/usecases/
  excludes:
    - packages/devkit/src/
    - .devkit/config.toml
    - .github/workflows/
    - justfile
    - scripts/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-test-management] Evidence-based test management playbook

## 1. Background & Hypothesis

Devkit, Auto Hub and Resource Indexer use different test ownership, resource boundaries and completion gates.
A reusable assessment procedure can find concrete coverage, isolation and runner-cost problems without imposing
one test layout or worker count. The implementation-shaped draft was removed; its review observations remain in
[review notes](materials/README.md). No source snapshots are retained.

The [repository assessment](materials/repository-assessment.md) records actual commands and constraints from all
three repositories. These were read-only inspections, not application test runs or performance measurements.

## 2. Planning Decisions and Alternatives

| Option | Benefit | Cost/risk | Recommendation |
| --- | --- | --- | --- |
| Existing performance-pass/review-refactor only | No additional asset | Neither inventories test coverage, resource isolation and completion gates as its primary operation | Reuse for applicable follow-ups |
| Bounded test-management assessment playbook | One entry point for test-specific diagnosis | One opt-in asset and its contract | Select |
| Uniform tier/worker/branch policy | Consistent configuration | Conflicts with consumer contracts; unsupported defaults | Reject |

Ship `maintenance/test-management` with a `testing` preset. Include it in the existing implicit `all` selection;
selection or an upgrade of `all` makes it available, never invoked. Existing individual presets retain their sets.
Use `SKILL.md` for trigger/constraints/procedure/completion, `references/assessment.md` for coverage/resource and
report details, and `references/pytest.md` only for pytest/xdist consumers. No fixed time thresholds, database
fixture templates, branch-promotion instructions, runtime command or new feature dependency edge is needed.
These bounded asset choices require no change to accepted architecture/integration policy and no separate PADR.

### Procedure

1. Record user-selected roots, HEAD/dirty paths, native commands, ownership and required gates. Inspect collection
   hooks, credentials, services and data boundaries before running tests; collection itself can execute code.
2. Inventory coverage and resources separately from directory/marker tiers. Preserve native labels and layouts;
   distinguish Python, frontend/browser, native/storage and provider coverage.
3. Run only bounded safe native commands within the assessment scope. Missing required prerequisites remain
   `not_run` with an unmet gate; preserve documented optional skips without treating them as executed coverage.
4. Report evidence, retained settings, proposed changes and limitations. Read pytest guidance only when applicable.
   Tuning is optional and needs current measurements before claiming a speedup or promoting a runner default.
5. Present one decision round. Invocation authorizes assessment, not edits. An unattended run applies nothing.
   Route approved changes through the consumer's development workflow, preserving its review and integration gates.
6. Report actual commands/outcomes, unresolved checks and decisions. Do not start another playbook automatically,
   require a history service, publish evidence or retain raw/source snapshots as part of routine assessment.

### Recommended repository settings

- **Devkit:** retain package tiers, affected selection/full fallback, capped worksteal runner and final landed-HEAD
  verification; preserve frontend instructions. Nightly checks are additional coverage.
- **Auto Hub:** retain serial unit/SDK/PostgreSQL and capped automatic SQLite worksteal execution. Preserve DB,
  migrations, frontend, SDK and isolated SDD gates; CI is manual. Shared DB safeguards are fixture-specific.
- **Resource Indexer:** retain source-owned marker tiers and serial `just check`. Eight-worker `test-parallel`
  remains optional; fast/tier recipes do not replace completion. Preserve native/storage, web and browser checks.

The sibling repositories are read-only references. Consumer configuration changes require separate work there.

## 3. Development Scope and Verification

Add the three-file playbook, manifest/preset registration and catalog README entry. Extend existing catalog
integration checks. Document one delivery capability and one reciprocal use case. Keep shipped text self-contained
and apply the authoring bundle's router guidance. No consumer-specific document IDs belong in shipped assets.

### Candidate acceptance criteria

- **AC-01:** `testing` and implicit `all` deploy the complete asset; individual presets keep their selections;
  unselected consumers receive nothing. Availability never invokes assessment.
- **AC-02:** a scenario with collection hooks, shared services or unavailable sockets determines prerequisites
  before execution. Missing required checks remain incomplete, independently of a test's tier label.
- **AC-03:** an unattended walkthrough reports findings and changes nothing; an approved change names exact scope
  and follows the consumer workflow without inferring authority for CI or integration-policy changes.
- **AC-04:** read-only walkthroughs for all three repositories preserve the gates/resource boundaries recorded in
  the assessment. A labelled non-pytest example uses native commands without installing pytest.
- **AC-05:** a tuning example compares collected identities, outcomes/skips, cleanup and elapsed time; unexecuted
  work is `not_run`. No universal worker/time default or application fixture is prescribed.
- **AC-06:** deployment/conditional-loading checks and author-led procedural walkthrough records support the
  contract. Phrase presence alone is insufficient. Relevant affected tests, lint, types and rules pass and the
  capability/use-case references resolve.

Walkthroughs record expected versus observed agent actions; they are not live application or performance evidence.
Consumer tuning uses one revision, lockfile and selected set; inspect prerequisites first, then compare serial and
existing parallel commands with one warmup and three interleaved timed repetitions each if a tuning change is
requested. Compare node-ID multisets, outcomes and cleanup. Keep raw logs outside versioned docs and retain a
short conclusion. Inconclusive evidence means retain current settings, not introduce a benchmark framework.
No performance claim or default promotion is made in this Planning.

### Non-goals

Consumer edits, test relayout, new affected selectors, application bug fixes, CI/branch policy redesign, benchmark
frameworks, raw evidence archives and mandatory history services. This unit ships assessment guidance only.

## 4. Lifecycle & Retirement Criteria

Keep `status: reviewing` on `plan-test-management` while presenting the committed direction and independent
Challenger evidence. Current policy requires user direction acceptance and separate Development handoff authority.
No consumer edits, source snapshots or automatic draft restoration are authorized. On acceptance, carry the
assessment and chosen design through the normal feature-spec handoff. Rejection follows normal retirement.
