---
sources:
  CAP-DLV-incubation-sdd-baseline: 8899fda9b8975eb5cf9848c226df2ee8f43abc14
  CAP-HARN-agent-guidance: 3e6c66d7ea068a580cc1ee82308708d407dab6bd
  UC-adopt-sdd-from-incubation: 84cab126d6e7b0c498c33f38a07531ed16c0c6d3
title: Adopt SDD from incubation
---

# Adopt SDD from incubation

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](incubate-an-idea.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
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

An incubated product can stay in incubation for as long as it is useful. When you decide the part you want to keep
should change under spec-driven development (SDD) from now on, the `sdd-baseline` playbook gets it there honestly:
your agent checks the retained product against its implementation, current documents and checks that really ran,
fixes the documents, and switches the approach only after you approve the exact effects. No retrospective proposals,
spec Units or decisions are invented for past experiments.

Source: [`UC-adopt-sdd-from-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-adopt-sdd-from-incubation.md),
contract [`CAP-DLV-incubation-sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md),
playbook [`sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/SKILL.md).
For a repository that never used incubation, see [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md).

## Before you start

- The repository's approach is `incubation` ([Incubate an idea](incubate-an-idea.md)). If it is already `sdd`, there is
  nothing to graduate: drift goes through [Reconcile Living Spec drift](reconcile-living-spec-drift.md).
- You can say which behavior, flows, structure and choices you want to keep, and what to leave out.
- The agent can run the repository's build, lint, test and usage checks.
- Nothing starts on its own: product size, elapsed time or the number of experiments never trigger adoption. You
  invoke the playbook or confirm it when offered.

## Step by step

1. **Start without switching.** The agent loads the procedure (`uv run devkit playbook get spec/sdd-baseline`, or
   through `/devkit-playbook`). The approach stays `incubation` throughout preparation. If `devkit-spec` or its assets
   are missing, it presents the installation and `uv run devkit add spec` effects; installing them prepares adoption
   but neither activates nor proves anything.
2. **Fix the scope.** It records the repository, exact `HEAD`, relevant dirty paths and the effective approach from
   `uv run devkit config show`, reads `.devkit/incubation.md` and current documents as input, and agrees with you on
   the retained items and the exclusions.
3. **Compare.** For each retained item it links the implementation, the current document (or where one is missing)
   and the evidence, and marks it `verified`, `gap` or `excluded`. Excluded items never count as verified. It writes
   or corrects only the capabilities, use cases, architecture, decision documents and run instructions that coverage
   needs, stating current choices and known reasons without inventing past alternatives.
4. **Run the checks.** It runs the applicable project commands and exercises representative user flows, recording
   each command, source identity, environment and outcome. A passing document-format check proves only what it
   checks, not that the product is ready.
5. **Present readiness.** With no gap left, it presents the report, the retained scope, the check outcomes and the
   exact activation effects: `[development] approach = "sdd"` in `.devkit/config.toml` and, when the integration
   provider is missing or `project`, setting it to `spec`. Other settings stay unless you authorize a change.
6. **You decide.** You authorize those same effects for that same source and scope, or the agent reuses an explicit
   decision you already gave for exactly them.
7. **Activate and confirm.** The agent edits the shared configuration, then runs `uv run devkit sync`,
   `uv run devkit config show`, `uv run devkit spec policy` and `uv run devkit sync --check`, and records the observed
   final state. Your next requested change goes through [Route a development request](route-development-intent.md);
   the baseline itself leaves no Unit or envelope.

The report defaults to `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md` (or the repository's usual
evidence location). It is an ordinary material with no workflow binding or status.

## When it goes wrong

- **You never asked.** Ordinary incubation continues; this journey does not start.
- **A check is missing, failed or skipped, or a document disagrees with the code.** The gap is recorded and you
  choose: correct the document, authorize a behavior fix separately, narrow the retained scope, or defer adoption and
  stay in incubation. A required item is never waived into readiness.
- **The source changes before activation.** The affected observations are invalidated and rechecked; stale evidence
  never activates SDD.
- **You do not authorize an effect**, such as the needed provider change. Adoption stays unactivated and the mismatch
  is reported.
- **Installation, the policy edit or sync fails part way.** The agent reports the actual partial state and the
  supported recovery, and claims neither success nor a rollback; completion waits for revalidation.

## What you end up with

The retained product has truthful current documents and observed evidence, and the approach, the selected guidance
and the routing of the next change all agree on SDD. Unrelated edits and existing SDD history stay, and any unresolved
gap stays visible. Area: [Delivery](../areas/delivery.md).
