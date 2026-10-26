---
sources:
  CAP-DLV-weekly-report: 0499a11d003f2b19a0ead794315b96ab8a09c22f
  UC-inspect-weekly-repository-progress: 4678537a309b3defe8a1a7c2e41d5842b3ac03af
  UC-publish-a-weekly-report: 9e5de0abff784fa43c00851d8b03cf8b59d60129
title: Inspect weekly repository progress
---

# Inspect weekly repository progress

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
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

At the end of a week you want to know what was actually delivered, what is still unverified, where the repository's
health has gaps and what to do next. The `weekly-report` playbook has your agent write that report from the evidence
already in the repository. It reads only: it fetches nothing, switches no branch, runs no maintenance or checks, and
creates no follow-up work. Publishing the finished report is a separate step with its own authority.

The use case is
[`UC-inspect-weekly-repository-progress`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-inspect-weekly-repository-progress.md),
built on
[`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-weekly-report.md).
Playbooks are explained in [Concepts](../concepts.md).

## Before you start

The playbook ships in the opt-in `maintenance` bundle of devkit-catalog; the project selects it before it is
deployed. Generation needs no external destination.

## 1. Invoke the playbook

Ask your agent for the weekly report through `devkit-playbook`, or confirm the offer the `spec` skill makes. The
agent retrieves it with:

```bash
uv run devkit playbook get maintenance/weekly-report
```

Tell it the scope. You may also give your timezone or an exact interval, where to write the report, and a prior
report to compare with.

## 2. The agent pins what it inspects

With local Git only, the agent records the repository identity, the inspected and integration revisions, the
generation time and whether the checkout is dirty. By default the interval is the previous complete Monday-to-Monday
week in your timezone, start inclusive, end exclusive, with each endpoint's UTC offset.

## 3. It gathers evidence

The agent reads committed content at the captured revision: completed specs included, every intended namespace, every
page of each listing. Each factual claim cites its evidence: a commit and path, a document ID, an envelope or a check
artifact.

## 4. It separates delivered from unverified

Work counts as delivered only with completion, verification and reachability evidence. A completed spec needs its
status, checked tasks, verification and reconcile evidence, and commits reachable from the integration revision.
Proposals, checkboxes or commits alone prove nothing; such work is reported as unverified.

## 5. Health, comparison and actions

The agent inventories health sources, compares findings with the prior report you named, and ranks next actions by
impact and urgency. It links existing open follow-ups and never creates new ones.

## 6. It rechecks before writing

Just before writing, the agent rechecks the inspected revision, the integration ref and relevant dirty content. What
changed is collected again or marked unverified, never silently mixed.

## 7. You get the report

The agent writes the report to a new local file, reads it back, verifies its identity and evidence links, and records
its SHA-256. A companion record holds the generation outcome with publication `pending`. You receive the artifact,
both outcomes, the limitations and the next steps.

## When it goes wrong

| Situation | What happens |
| --- | --- |
| Your timezone is unknown | The agent asks before resolving the interval or writing anything. |
| The interval is reversed, ambiguous or unresolved, or the repository identity is missing | Generation fails; no report is written. |
| There is no owning unit's materials and no repository materials location | The agent asks where to write. It never silently creates a tracked report on the default branch. |
| A source is missing, stale, failed or not comparable | It appears as a limitation with its reason. An optional source failing does not stop generation, and nothing missing counts as clean. |
| Work has no integration time or verification evidence | Reachable changes are reported as snapshot evidence, not as delivery within the week. |
| No prior report, or one with a different scope | The report says no comparison was made; a missing finding is never read as resolved. |
| A report for the same repository, scope and interval exists | A new run with its own ID names the run it supersedes; the earlier file is unchanged. |
| The readback or identity check fails | Generation fails and nothing is published. An unavailable evidence link alone is marked unverified instead. |

## Next

Publishing the verified report to a destination you choose is
[`UC-publish-a-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-publish-a-weekly-report.md),
covered in [Publish a weekly report](publish-a-weekly-report.md). Areas: [Delivery](../areas/delivery.md) and
[Governance](../areas/governance.md).
