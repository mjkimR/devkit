---
sources:
  CAP-DOCS-document-model: f8721682fd5a48b32c20f3417977802ddb61b571
  CAP-DOCS-namespaces: f6a06f2fb6a7564ed6ede84c6375c1e401dedb91
  CAP-GATE-commit-gates: d29338c7967d0820ca4b68b7061c99f0cf5a9cf0
  CAP-GOV-spec-rules: 903255aa74c723fbf1e382808a1b7bfbcd9c68b2
  CAP-TRACE-code-entrypoints: f85e685d002096791b5d75d3954edc3782f59f9b
  UC-keep-the-living-spec-consistent: 6aa78b77ed1eb5a1f7f8b59742048c01319abccc
title: Keep the Living Spec consistent
---

# Keep the Living Spec consistent

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `a6e769c5721d`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Assess a selected test suite](assess-test-management.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Discover and refine an idea](discover-and-refine-an-idea.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Execute an isolated command](execute-an-isolated-command.md)
- [Explore a design problem](explore-a-design-problem.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](import-third-party-agent-assets.md)
- [Improve an interface and user flow](improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Plan and hand off a proposal](plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Read decision supersession](read-decision-supersession.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Record a maintenance run](record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
- [Adopt and refresh bundle sources locally](snapshot-bundle-sources.md)
- [Speed up selected slow operations](speed-up-selected-slow-operations.md)
- [Advisories](../areas/advisory.md)
- [Agent-first CLI toolkit](../areas/cli.md)
- [Collaboration](../areas/collaboration.md)
- [Compact command output](../areas/compact.md)
- [Delivery](../areas/delivery.md)
- [Distribution](../areas/distribution.md)
- [Documents](../areas/documents.md)
- [Commit gates](../areas/gate.md)
- [Generated Files](../areas/generated.md)
- [Governance rules](../areas/governance.md)
- [Harness](../areas/harness.md)
- [Host](../areas/host.md)
- [Integration](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [Search](../areas/search.md)
- [Traceability](../areas/traceability.md)
- [Viewer](../areas/viewer.md)
- [Worktree](../areas/worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The Living Spec under `docs/` is only useful if later agents can trust it without re-reading everything. This
journey shows how devkit keeps it structurally sound while you (or your agent) change documents and code: broken
references, one-sided links, misplaced files, stale spec statuses, unreconciled changes and dead code entrypoints are
each reported with a stable rule ID and, where the repair is unambiguous, fixed for you.

Whether the documents say the *right* thing is a different question; that is
[Reconcile Living Spec drift](reconcile-living-spec-drift.md). For the vocabulary used here (Living Spec, rules,
commit gate), see [Concepts](../concepts.md).

Source: [`UC-keep-the-living-spec-consistent`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-keep-the-living-spec-consistent.md).

## Before you start

- The project selects the `docs` bundle, and `devkit sync` has deployed its document rules (they come with its
  `core` preset). With spec-driven delivery the `spec` bundle adds the lifecycle rules of feature specs and proposals.
- The rules are ordinary devkit rules, so everything about phases, severities and tuning in `[rules]` of
  `.devkit/config.toml` applies; see the [governance area](../areas/governance.md).

## Step by step

1. **Check what you changed.** Run the rules over the whole workspace or over the files you touched:

   ```sh
   uv run devkit rules check                      # whole workspace
   uv run devkit rules check docs/usecases/x.md   # only these targets
   ```

   Each violation names its rule (for example `RULE-traceability-link`), whether it is `fixable` or `open`, and what
   to do about it. A violation is reported only in the files the run targets, and completed spec bundles are treated
   as history: they are checked only when you name them.

2. **Apply the deterministic fixes.**

   ```sh
   uv run devkit rules fix --dry-run   # preview
   uv run devkit rules fix
   ```

   A fix rewrites only targeted current files and only the bytes it owns, in the file's own style. It never moves or
   renames a file, never guesses a missing ID and never rewrites a completed bundle.

3. **Recheck.** `devkit rules check` again should report nothing.

4. **Commit.** The built-in `rules-check` gate evaluates the exact staged tree (what `devkit rules check --staged`
   does) and accepts the commit. Unstaged edits cannot change its verdict.

5. **Open a pull request.** CI runs `devkit rules check --ci --base <ref>`, judging the whole branch against its merge
   base the same way.

To learn what a rule checks and how to repair it by hand, run `uv run devkit rules explain <RULE-id>`.

## What the rules look for

The fifteen rules, ten document rules shipped by `docs` and five lifecycle rules shipped by `spec`, are
catalogued in
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/governance/CAP-GOV-spec-rules.md).
The ones you meet most often:

| Rule | You see it when | Fix |
| --- | --- | --- |
| `RULE-document-reference` | an ID does not resolve, or a reference uses bracket form or an alias | partly fixable |
| `RULE-id-convention` | a file's path, `id`, `area` or heading token disagree | fixable once the path is right |
| `RULE-traceability-link` | a use case lists a capability that does not list it back | appends the reverse ID |
| `RULE-spec-lifecycle` | `spec.md`, `tasks.md` and `reconcile.md` disagree on status | sets `status: completed` |
| `RULE-reconcile-contract` | a `resolved` record claims a `modified` target the diff did not change | by hand |
| `RULE-code-entrypoints` | an `entrypoints` path no longer exists | by hand |
| `RULE-steering-documents` | a file in `docs/steering/` carries an `id`, lacks `title` or `summary`, or the directory grows past its caps | by hand |
| `RULE-ux-links` | a UX document and the use case steps that cite it disagree | by hand |

While the project's development approach is adaptive development, the document rules judge as always, but the lifecycle rules
apply only to Units explicitly bound to an SDD workflow. Where none applies, a run reports `SDD_LIFECYCLE_INACTIVE` as
omission evidence rather than a successful check.

How documents get their IDs and how references resolve is the document model,
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/documents/CAP-DOCS-document-model.md)
(see the [documents area](../areas/documents.md)).

## When it goes wrong

- **The run fails with `DOCS_CONFIG_INVALID` (exit `2`).** The `[tool.docs]` table in `.devkit/config.toml`, which
  registers document namespaces, is malformed, for example it has an unknown key. This is not a violation: the rules cannot tell which documents follow
  which conventions, so nothing is judged. Correct the table and run again.
- **A violation stays `open` after `fix`.** There is no deterministic repair: a reference to an ID no document
  declares, a dead entrypoint, missing reconcile evidence. The fix leaves it unchanged on purpose. Follow its
  remediation by hand, then recheck.
- **The commit is refused for a capability you did not touch.** You deleted or moved code that a capability declares
  in `entrypoints`, and `RULE-code-entrypoints` reports every document that declares a deleted path. Restore the code,
  point the declaration at the moved code, or remove it, then commit again. The path contract is
  [`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md)
  (see the [traceability area](../areas/traceability.md)).
- **The commit is refused on a `reconcile.md`.** You marked it `resolved` with a `modified` target that this commit
  does not change. Stage the Living Spec edit together with the record.
- **The gate refuses with `GATE_RULES_FAILED`.** Each `[DETAIL]` line names the rule, file and line, with a `fix:` hint
  when the rule has one. A `RULES_RUN_FAILED` instead means the run could not judge the commit at all (for example
  managed rule files are missing in a fresh worktree: run `devkit sync`). Gate behavior is
  [`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/gate/CAP-GATE-commit-gates.md)
  (see the [gate area](../areas/gate.md)).

## What you end up with

The targeted files and the committed tree pass every document and lifecycle rule, links and statuses are written in the files' own
style, and completed bundles are untouched. A refused commit creates no commit, so nothing half-checked lands.

## Namespace registers and replacement records

Registered namespaces can keep steering glossaries, synonym files, UX object registers and roadmap milestones under
`docs/packages/<name>/`. The root and selected namespace registers are read together.
`RULE-decision-supersession` checks reciprocal whole/partial ADR replacement metadata; review decides whether its
scope is accurate. Alias fixes also cover visible steering references, glossary Owner cells and configured quick references.
Entrypoint derivation excludes receipt-owned generated outputs while scope observation retains their write paths.

## Working with this release

Rule findings at `notice` severity are nonblocking considerations, including under strict mode and commit gates. `uv run devkit rules context FILE` returns bounded working-versus-HEAD change evidence and applicable change-scoped notices; native file reads do not call it automatically. Missing evidence is disclosed rather than replaced with whole-file history.
