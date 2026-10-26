---
sources:
  CAP-DLV-weekly-report: 0499a11d003f2b19a0ead794315b96ab8a09c22f
  UC-inspect-weekly-repository-progress: 4678537a309b3defe8a1a7c2e41d5842b3ac03af
  UC-publish-a-weekly-report: 9e5de0abff784fa43c00851d8b03cf8b59d60129
title: Publish a weekly report
---

# Publish a weekly report

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
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
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

You already have a verified weekly report and want it to reach a place where others read it: a wiki page, a channel,
a document store. This journey shows how your agent publishes it so that you know whether it arrived intact, without
overwriting someone else's content and without sending it twice.

Generating the report is a separate step (`UC-inspect-weekly-repository-progress`). Both live in the `weekly-report`
playbook of the opt-in `maintenance` catalog bundle; see the [delivery area](../areas/delivery.md) and, for playbooks
in general, [Concepts](../concepts.md).

Source: [`UC-publish-a-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-publish-a-weekly-report.md),
contract [`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-weekly-report.md).

## Before you start

- The `maintenance` bundle is selected (`uv run devkit add maintenance`, or `maintenance:reporting` for this playbook
  alone) and synchronized.
- The report was generated and verified: it has a SHA-256 digest and a companion outcome record next to it. The
  report itself is immutable; everything about publication is written to the companion record.
- You have an existing, authorized way to reach the destination: a connector or command your agent already has.
  devkit ships no publisher of its own.

Running the playbook does not authorize publication, and neither does any integration policy. Publication needs your
explicit authority for a destination you chose.

## Step by step

1. **Choose the destination and grant authority.** Invoke the playbook explicitly (`/devkit-playbook` or
   `uv run devkit playbook get maintenance/weekly-report`) and tell the agent where to publish, saying that it may.
2. **The agent prepares.** It reads the companion record and finds the connector or command that reaches your
   destination.
3. **Collision check.** It looks at the destination for existing content at the target.
4. **Digest check.** It recomputes the local report's SHA-256 and compares it with the recorded one.
5. **Send.** It sends the report's exact bytes under its run ID and records the attempt, destination and authority in
   the companion record.
6. **Verify.** It reads back the destination's receipt or link and confirms that content, run ID and digest match.
7. **Report back.** The companion record now says `published` with the receipt evidence, and the agent gives you the
   destination and the outcome. The report file is unchanged.

## The publication states

| State | Meaning |
| --- | --- |
| `pending` | no destination, authority, publisher or permission yet |
| `published` | a verified receipt matches content, run and digest |
| `failed` | the connector or command confirmed a failure |
| `unknown` | the response was lost, or the destination cannot be verified |

## When it goes wrong

- **No companion record, or it records no completed generation.** Publication is blocked and nothing is sent. The
  verified report stays as it is; regenerate if you need a fresh record.
- **No authorized connector, or permission missing.** Publication stays `pending`. The agent keeps the local artifact
  and tells you what is missing.
- **The destination already holds content there.** The agent replaces it only if your authority names that target.
  Otherwise nothing is sent.
- **The local digest no longer matches.** Nothing is sent. Changed content is a new run, which generation has to
  produce.
- **The connector reports a failure.** The companion records `failed` with the error. A later retry resends the same
  run ID and the same bytes.
- **The response was lost.** The companion records `unknown`, and the agent inspects the destination before any
  retry. A matching receipt resolves it to `published` without resending; confirmed absence permits a retry within
  your authority; a destination it cannot verify stays `unknown`, and the agent asks you what to do.
- **The destination holds different content (other run or digest).** That is treated as a collision, as above.
- **It is only a rehearsal.** In a controlled exercise the agent labels authority and receipts as simulated and
  claims no external publication.

## What you end up with

Either a `published` record whose receipt you can check, or a clear `pending`, `failed` or `unknown` state with every
attempt preserved. The report bytes and its generation outcome never change, nothing is replaced without authority
naming it, and an `unknown` publication is never retried blindly.
