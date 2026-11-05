---
name: test-management
description: Assess user-selected test suites for coverage gaps, resource isolation and runner configuration, preserve native verification gates, and route only agreed changes through the consumer workflow.
---

# Test management

Run only when the user invoked or confirmed this playbook (`devkit-playbook`,
`devkit playbook get maintenance/test-management` or a confirmed intake offer). Selection and retrieval never
invoke assessment. Invocation authorizes assessment, not configuration changes. An unattended run stops at the
one decision round with nothing applied.

## Constraints for every run

- Keep the consumer's test ownership, tier names, required checks and integration approvals.
- Inspect executable collection hooks and resource prerequisites before running tests, including collection.
- Use disposable test data and documented test services; never contact paid providers, use real credentials or
  modify product data implicitly. Clarify an unknown resource boundary before executing the affected command.
- Treat directory/marker tiers and resource isolation as separate facts; async unit tests can need local sockets.
- Report a missing required check as `not_run` and an unmet gate; preserve documented optional skips and name the
  coverage they do not establish. Never weaken tests to accommodate the execution environment.
- Keep repository identities credential-free and logs free of secrets. Keep raw output outside versioned reports;
  retain concise findings and evidence locations, without source snapshots or a required history service.
- Read managed agent assets as evidence; route their changes to source or the consumer's override mechanism.
- Record application defects as follow-up work instead of repairing them inside this assessment.

## 1. Scope and prerequisites

1. Identify the user-selected suite roots and goal; clarify missing scope before test execution.
2. Record repository identity, HEAD, dirty paths, native commands, runner versions, ownership and required gates.
3. Read `references/assessment.md` before inspecting suite coverage, resource requirements or completion gates.
4. Inspect collection hooks, fixtures, service URLs, file/port ownership and runtime prerequisites by reading their
   source. Record which commands are safe, unavailable or require clarification before running them.
5. Execute only bounded safe native commands relevant to the agreed scope; report each command, result and limit.

## 2. Assess and propose

1. Inventory exercised boundaries and missing coverage independently of tier labels. Preserve package, feature,
   marker and language-specific ownership unless a concrete problem justifies a proposed change.
2. Separate iteration commands from completion checks, including frontend/browser, database/migration, native
   storage and provider coverage when applicable. Read CI triggers; do not infer execution from a workflow file.
3. Read `references/pytest.md` when the consumer uses pytest and runner configuration or concurrency is in scope.
   Other runners keep their native commands; do not install pytest to assess them.
4. For each finding, record source evidence, consequence, proposed disposition, exact edited paths and validation.
   Keep existing settings when evidence is inconclusive. Do not infer branch/CI redesign from test duration.
5. When proposing a tuning change, measure the current command and candidate before claiming a speedup. Without
   executable prerequisites or comparable results, report `not_run` and recommend no default promotion.

## 3. One decision round

1. Present findings together as keep, defer, or proposed change; include unresolved prerequisites and coverage.
2. Record the user's decision and reason per candidate. Leave unanswered candidates pending with nothing applied.
3. Route approved changes through the consumer's normal development workflow with exact scope and checks.
   A decision supplies that work's intent, not its integration approval. Revalidate findings if HEAD or relevant
   dirty content changed before application; return changed intent to the decision round.
4. Treat CI/branch policy redesign as separately scoped work. Never invoke another playbook automatically;
   performance-only follow-ups can use an explicitly selected performance pass.

## 4. Report and completion

Write an ordinary local report at the owning unit's evidence location or the consumer's report destination.
Record inspected state, coverage/resources, native commands and actual outcomes, findings, retained settings,
user decisions, routed work and verification gaps. Label examples and walkthroughs separately from executed tests
or performance evidence. State `stopped at decision round`, `routed`, `partially routed` or `kept` as the outcome.
An unattended assessment is complete with its decision-round report and no edits; unanswered candidates stay
pending. For a decided run, completion requires every approved candidate to have a routed destination and every
required unexecuted check to remain visible. Publication requires separate authority.
