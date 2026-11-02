---
id: FB-contract-docs-without-rfc-keywords
title: Capability and architecture documents state rules without RFC 2119 keywords
scope: repo
kind: change-request
category: docs-mismatch
target: docs/capabilities/, docs/architecture/
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-02
---

# [FB-contract-docs-without-rfc-keywords] Capability and architecture documents state rules without RFC 2119 keywords

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `capability-writing` and `architecture-writing` require one RFC 2119 keyword per rule. Many
  capability and architecture documents still state their rules in prose ("never", plain present tense). A reviewer
  therefore cannot compare an ADR clause's intended strength with its restatement.
- **Proposed Procedure**: Run an `overall-refactor` pass, after `SPEC-adr-normative-outcomes` lands, that rewrites the
  prose rules of these documents as EARS rules with RFC 2119 keywords. Each rule keeps its current meaning. The strength
  follows `contract-authoring`, and each choice of MUST or SHOULD is justified by the check, review or consequence
  behind it.
- **Expected Benefit**: The capability and architecture documents become the single normative source, with explicit
  strength, and clause-level review of ADR restatements becomes possible.
- **Cost & Risk**: Choosing MUST or SHOULD for a prose rule fixes its strength, so an unsupported choice strengthens or
  weakens a contract. This touches many files; several capabilities already exceed `RULE-file-length`.
- **Attempted**: Hypothesis. `SPEC-adr-normative-outcomes` deferred this pass as Non-Goal 2.

## Diagnostic Details

- **Reproduction**: Count `\b(MUST|SHOULD|MAY)\b` per file under `docs/capabilities/*/` and `docs/architecture/`.
- **Expected / Actual**: Expected keywords in every rule; observed 28 of 63 files with none.
- **Versions**: base `fceda9d2`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: none; the ADR-only clauses of 13 ADRs were restated with keywords in this spec.
- **Related Assets**: `capability-writing`, `architecture-writing`, `contract-authoring` instructions;
  `SPEC-adr-normative-outcomes`.

## Evidence

```text
28 of 63 files under docs/capabilities/*/ and docs/architecture/ contain no MUST, SHOULD or MAY (2026-11-02), for
example ARCH-04-delivery-strategy, ARCH-05-1-containers (before this spec), CAP-WT-task-worktrees and
CAP-DIST-workspace-ownership.
```
