---
id: FB-proposal-boundaries-unchecked
title: Proposal boundaries may name Living Spec areas that do not exist
scope: repo
kind: suggestion
category: missing-capability
target: devkit-spec proposal frontmatter (boundaries.owns), devkit spec proposal handoff
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-proposal-boundaries-unchecked] Proposal boundaries may name Living Spec areas that do not exist

## 2. Suggestion / Change Request

- **Current Procedure**: `boundaries.owns` in `proposal.md` is free text. Nothing checks it when the proposal is
  created, at plan-intent or at handoff, which copies it into the spec's carried notes
  (`devkit_spec/proposals/handoff.py`, `specs.py`). This proposal declared `capabilities/core/`, an area that does
  not exist under `docs/capabilities/` (the core contracts live in `capabilities/harness/` and the architecture
  documents), while areas the change does touch were missing.
- **Proposed Procedure**: A hygiene or linter rule over proposal frontmatter that reports a `boundaries.owns` or
  `target_area` entry naming no existing directory under `docs/` (a new area must then be stated explicitly, for
  example with a trailing comment or a `new:` marker).
- **Expected Benefit**: The Development boundary carried into the spec starts from real paths; Planning reviews do
  not need to rediscover the area list.
- **Cost & Risk**: A proposal that creates a new area would need the explicit marker; low otherwise.
- **Attempted**: Hypothesis. This run corrected the list by hand from the docs tree.

## Diagnostic Details

- **Reproduction**: `ls docs/capabilities` in the Planning worktree against the proposal frontmatter.
- **Expected / Actual**: Expected every owned area to exist or be marked new; actual `capabilities/core/` absent.
- **Versions**: devkit-spec 0.1.0 (workspace source at the plan-intent commit).
- **Conditions**: Proposal created in Backlog and confirmed at plan-intent without a frontmatter check.
- **Workarounds Attempted**: Manual correction during Planning.
- **Related Assets**: `.devkit/managed/spec/templates/proposal.md`, `devkit spec proposal handoff`.

## Evidence

```text
proposal.md frontmatter: boundaries.owns: [capabilities/distribution/, capabilities/core/, capabilities/host/,
  capabilities/search/, architecture/]
ls docs/capabilities: README.md advisory collaboration compact delivery distribution documents gate generated
  governance harness host integration search traceability worktree   (no core)
devkit rules check <proposal dir> -> no finding
```

- **Disposition**: PROP-envelope-record-gaps: a rule for proposal boundaries and target_area (Q3)
- **Disposition (resolved)**: `SPEC-envelope-record-gaps` adds the warning rule `RULE-proposal-boundaries`
  (`ADR-proposal-acceptance`). Verified by
  `packages/devkit-spec/src/devkit_spec/bundle/rules/proposal_boundaries/tests/test_rule.py` (AC-08 to AC-10).
