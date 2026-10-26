---
sources:
  CAP-DOCS-document-model: 65a68b9b0c43ddbcd7817e14d278f31c640a221a
  CAP-GATE-commit-gates: 83c1bd822d3330dab5eed84e7b8f13a552e5f638
  CAP-GOV-spec-rules: d995eca73f4dea46ac7a5836f25cdfa4bf158b6e
  CAP-TRACE-code-entrypoints: 3b8cb1476d9102bf09e6ffc6a469c3e00e58da97
  UC-keep-the-living-spec-consistent: 7ebdf1e2f7ae6581fa9140d1898d755de57b5667
title: Keep the Living Spec consistent
---

# Keep the Living Spec consistent

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `ae01161143be`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
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

Source: [`UC-keep-the-living-spec-consistent`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-keep-the-living-spec-consistent.md).

## Before you start

- The project selects the `spec` bundle, and `devkit sync` has deployed its rules (they come with its `core` preset).
- The rules are ordinary devkit rules, so everything about phases, severities and tuning in `[rules]` of
  `.devkit/config.toml` applies; see the [governance area](../areas/governance.md).

## Step by step

1. **Check what you changed.** Run the spec rules over the whole workspace or over the files you touched:

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

The eleven rules are catalogued in
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md).
The ones you meet most often:

| Rule | You see it when | Fix |
| --- | --- | --- |
| `RULE-document-reference` | an ID does not resolve, or a reference uses bracket form or an alias | partly fixable |
| `RULE-id-convention` | a file's path, `id`, `area` or heading token disagree | fixable once the path is right |
| `RULE-traceability-link` | a use case lists a capability that does not list it back | appends the reverse ID |
| `RULE-spec-lifecycle` | `spec.md`, `tasks.md` and `reconcile.md` disagree on status | sets `status: completed` |
| `RULE-reconcile-contract` | a `resolved` record claims a `modified` target the diff did not change | by hand |
| `RULE-code-entrypoints` | an `entrypoints` path no longer exists | by hand |

How documents get their IDs and how references resolve is the document model,
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md)
(see the [documents area](../areas/documents.md)).

## When it goes wrong

- **The run fails with `SPEC_CONFIG_INVALID` (exit `2`).** The `[tool.spec]` table in `.devkit/config.toml` is
  malformed, for example it has an unknown key. This is not a violation: the rules cannot tell which documents follow
  which conventions, so nothing is judged. Correct the table and run again.
- **A violation stays `open` after `fix`.** There is no deterministic repair: a reference to an ID no document
  declares, a dead entrypoint, missing reconcile evidence. The fix leaves it unchanged on purpose. Follow its
  remediation by hand, then recheck.
- **The commit is refused for a capability you did not touch.** You deleted or moved code that a capability declares
  in `entrypoints`, and `RULE-code-entrypoints` reports every document that declares a deleted path. Restore the code,
  point the declaration at the moved code, or remove it, then commit again. The path contract is
  [`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md)
  (see the [traceability area](../areas/traceability.md)).
- **The commit is refused on a `reconcile.md`.** You marked it `resolved` with a `modified` target that this commit
  does not change. Stage the Living Spec edit together with the record.
- **The gate refuses with `GATE_RULES_FAILED`.** Each `[DETAIL]` line names the rule, file and line, with a `fix:` hint
  when the rule has one. A `RULES_RUN_FAILED` instead means the run could not judge the commit at all (for example
  managed rule files are missing in a fresh worktree: run `devkit sync`). Gate behavior is
  [`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/gate/CAP-GATE-commit-gates.md)
  (see the [gate area](../areas/gate.md)).

## What you end up with

The targeted files and the committed tree pass every spec rule, links and statuses are written in the files' own
style, and completed bundles are untouched. A refused commit creates no commit, so nothing half-checked lands.
