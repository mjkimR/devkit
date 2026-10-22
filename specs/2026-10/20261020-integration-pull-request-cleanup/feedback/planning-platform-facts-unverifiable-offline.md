---
id: FB-planning-platform-facts-unverifiable-offline
title: Planning of a platform integration cannot verify platform behaviour when network is denied
scope: repo
kind: friction
category: missing-capability
target: .devkit/managed/spec/skills/spec/references/planning.md (scout step under a network-denied worker payload)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-planning-platform-facts-unverifiable-offline] Planning of a platform integration cannot verify platform behaviour when network is denied

## 1. Friction / Question (friction, question)

- **Context**: A medium Planning run of PROP-integration-pull-request-cleanup designed a GitHub pull request merge
  route. The worker payload denied network operations, so the scout and the challenger could not read GitHub's
  official documentation.
- **Expectation**: Planning's scout answers with evidence from "internal code, documents and constraints or external
  official sources" (scout role description), and the design rests on verified platform facts.
- **Actual**: Only local `gh --help` output was verifiable. Every behaviour the design depends on (merge commit parent
  order, absence of a base pin, required-check timing after a push, self-approval, rule readability, branch deletion
  effects on dependent PRs) is recorded as unverified in both support envelopes.
- **Workaround (or Interpretation Chosen)**: Recorded each external claim as unverified and moved its verification to
  Development, named in the proposal.
- **Suggestion**: Let the payload grant read-only fetches of named official documentation hosts to the scout, or
  state in planning.md that a network-denied Planning lists external facts as Development verification items, so the
  acceptance request shows the gap explicitly.

## Diagnostic Details

- **Reproduction**: run a Planning worker whose payload denies network operations on a proposal that integrates an
  external platform.
- **Expected / Actual**: external facts verified / external facts marked unverified.
- **Versions**: unknown.
- **Conditions**: local-orchestrated Planning with network denied in `allowed_boundaries`.
- **Workarounds Attempted**: local `gh` help output as the only verified platform evidence.
- **Related Assets**: envelopes/scout-01.yaml, envelopes/challenger-01.yaml.

## Evidence

```text
scout-01 unverified: All GitHub REST/GraphQL, protection, ruleset, merge queue and bypass behaviour (no network; only local gh help verified)
challenger-01 unverified: All GitHub behaviour (required-check timing, async mergeability, self-approval, merge parents and tree, ...)
```

## Development observation

Official documentation verification found two concrete CLI premise errors before implementation: `gh repo view`
and `gh api` do not accept universal `-R` binding, and `gh pr merge --merge` can enqueue implicitly even without
`--auto`. The Host approved corrected mechanics recorded in `ADR-local-and-pull-request-integration` while
preserving the agreed explicit-repository and no-queue guarantees. This reinforces the existing recommendation
to permit official documentation reads during Planning. No live remote mutation was used for verification.

## Resolution

Directly resolved by `SPEC-worker-guidance-and-fixtures`: the delegation payload distinguishes named official-document reads from service mutations and requires Host-supplied verified evidence when reads are unavailable.

Verification: Independent medium code review confirmed AC-02; no live network grant or external mutation was introduced.
