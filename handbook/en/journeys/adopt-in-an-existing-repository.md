---
sources:
  CAP-GOV-spec-rules: 903255aa74c723fbf1e382808a1b7bfbcd9c68b2
  CAP-HARN-agent-guidance: dff559b3349a28515857465630025e54b334b414
  CAP-HARN-command-mount: 9963e0253b7b23f53d30d2185998241d83cecd95
  UC-adopt-in-an-existing-repository: 018001c6e9a67168a045c00dd6d3938b05cbecad
  UC-adopt-sdd-from-adaptive-development: 1eb8461c21c7c3e6fa131c4efb88d7f7e07095f6
title: Adopt devkit in an existing repository
---

# Adopt devkit in an existing repository

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `93e3808721b4`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
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
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
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

You have a repository with code, some Markdown under `docs/` and perhaps your own agent instructions. You want new
work to follow spec-driven delivery from today, without first rewriting every legacy document. This journey takes you
from installation to a passing `devkit rules check`, then leaves the legacy content to migrate as work touches it.

The use case behind this page is
[`UC-adopt-in-an-existing-repository`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/harness/UC-adopt-in-an-existing-repository.md).
For the terms bundle, sync and Living Spec, see [Concepts](../concepts.md).

This path contains legacy rule debt and lets it migrate gradually. If you have been developing an idea adaptively and want to
adopt spec-driven delivery from that retained product instead, ask for the adaptive development baseline: it follows
[`UC-adopt-sdd-from-adaptive-development`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md),
which verifies the product before activating SDD and moves no legacy documents.

## Before you start

- The repository is managed with `uv`.
- Its current state is committed. The containment step moves files, and a clean commit is your rollback point.

## 1. Install the package and synchronize

```bash
uv add --dev devkit devkit-spec
uv run devkit sync
```

devkit-spec brings devkit-docs with it. Neither has an executable of its own: they register the `spec` and `docs`
bundles and the `devkit spec` and `devkit docs` command groups through entry points, so everything runs through the
one `devkit` executable of your project environment
([`CAP-HARN-command-mount`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-command-mount.md)).

`devkit sync` then does three things
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-agent-guidance.md)):

- copies the `core` presets of both bundles to `.devkit/managed/spec/` and `.devkit/managed/docs/`: `docs` holds the
  shared document guidance, templates and document rules, `spec` the delivery lifecycle;
- projects the skills and role contracts into each agent host's own directories;
- adds the guidance pointer line to the managed block of your root `AGENTS.md`.

It writes nothing under `docs/` or `specs/`. Your existing documents stay exactly as they are.

## 2. Confirm the commands answer

```bash
uv run devkit spec --version
uv run devkit docs --version
```

You see `[VERSION: devkit-spec <version>]` and `[VERSION: devkit-docs <version>]`. Note that `devkit --version`
reports devkit itself, not these packages.

## 3. Take the baseline

```bash
uv run devkit rules check
```

The document and spec rules now read the Markdown already under `docs/` and `specs/`. In a brownfield repository
they usually report violations: number-based IDs such as ADR-0001, missing frontmatter, paths that do not match the Living Spec
layout. Each finding is a `[VIOLATION: ...]` line naming the rule, the file and a remediation. The catalog of the
fifteen rules (ten document rules shipped by `docs`, five lifecycle rules shipped by `spec`) is in
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/governance/CAP-GOV-spec-rules.md);
`uv run devkit rules explain <RULE-id>` prints one rule's guide.

## 4. Let the agent contain the legacy documents

Ask your agent for the `brownfield-adoption` playbook, or confirm the one-line offer the `spec` skill makes when you
ask it to adopt devkit here. Your request or confirmation is what authorizes the agent to move files.

The agent follows the playbook:

1. It lists the legacy Markdown and reviews a long or mixed set with you.
2. It moves the legacy files under `docs/materials/_legacy/<original path>`. Material directories are free-form, and
   no document or spec rule checks them.
3. It updates references to the moved paths elsewhere in the repository.
4. It proposes the containment as one commit, before any migration, so you review moves and content edits apart.

No rule is edited to make the check pass.

## 5. Rerun the rules

```bash
uv run devkit rules check
uv run devkit gate status
```

Both exit `0`. From here, new work goes through the `spec` skill (see
[Route development intent](route-development-intent.md)), and legacy content moves into the Living Spec as work
touches it.

## Options along the way

- **Seed a docs skeleton.** `uv run devkit add docs:docs-skeleton` writes only the skeleton files that do not exist
  yet. An existing `docs/README.md`, for example, stays unchanged.
- **Keep the commands, skip the bundle.** Set `[presets] spec = false` in `.devkit/config.toml` and run
  `uv run devkit sync`. No managed files or projections of the `spec` bundle are deployed, while `devkit spec` stays
  available. Removing `docs` as well leaves SDD unsupported; `uv run devkit add docs` restores it.
- **Review your policy.** `uv run devkit spec policy` shows which approval gates wait for you; record your decisions
  in `.devkit/config.toml`. See [Delivery](../areas/delivery.md).

## When it goes wrong

| What you see | What to do |
| --- | --- |
| A file has to stay at its path, because a tool reads it there | Decide to keep it. The agent records the deferral as a `.devkit/config.toml` entry, such as `[rules] exclude`, with your reason in a comment directly above it. |
| You prefer to fix one rule's debt in place, area by area | Decide to move that rule to the `hygiene` phase through `[rules.phase_overrides]`; the agent records it with its reason. |
| A moved file's relative link now fails | Prefix the link so it still resolves from `_legacy/`, or decide to exclude `docs/materials/_legacy/**`. |
| The commit gate refuses a commit that touches a file with an error finding | Fix the finding, contain the file, or decide to lower or disable the rule; every such entry carries its reason. |

The guarantee throughout: `devkit sync` changes no existing file under `docs/` or `specs/`, no rule is edited to pass,
and a deferral exists only where you decided it.

## Related

- [Harness](../areas/harness.md) and [Governance](../areas/governance.md) areas.
- [Find the right documents](find-the-right-documents.md), once your Living Spec starts to grow.
