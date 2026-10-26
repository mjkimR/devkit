---
id: FB-boundaries-cannot-name-prerequisite-paths
title: Proposal boundaries cannot name a path a prerequisite creates
scope: repo
kind: friction
category: missing-capability
target: RULE-proposal-boundaries
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-boundaries-cannot-name-prerequisite-paths] Proposal boundaries cannot name a path a prerequisite creates

## 1. Friction / Question (friction, question)

- **Context**: Planning `PROP-ux-documentation`, whose Development follows `SPEC-foundation-documents`, which moves
  the glossary from `docs/glossary.md` to `docs/steering/glossary.md`.
- **Expectation**: `boundaries.owns` names the paths Development will change, so the carried `_Boundary:` lets a
  worker write the moved glossary.
- **Actual**: `RULE-proposal-boundaries` warns on a directory that does not exist yet, and its remediation names the
  nearest existing parent, `docs/`, which would own the whole Living Spec. The current path `docs/glossary.md` will
  not exist when this proposal's Development starts.
- **Workaround (or Interpretation Chosen)**: Kept `docs/glossary.md` and wrote in the proposal that the Host swaps in
  the moved path before `plan-accept`, or records it as a `_Boundary:` extension at handoff.
- **Suggestion**: Let a proposal name a path that one of its `depends_on` prerequisites creates (for example accept it
  when a prerequisite's `owns` or target docs name it), or document the swap as the standard procedure.

## Diagnostic Details

- **Reproduction**: Add a not-yet-existing directory such as `docs/foundation/` to `boundaries.owns` of a proposal and
  run `uv run devkit rules check` on it.
- **Expected / Actual**: Expected no report for a path a prerequisite creates; actual warning "names no existing
  directory".
- **Versions**: plan branch based on `main` at `96df5d86`.
- **Conditions**: A proposal whose prerequisite moves or creates a file it must change.
- **Workarounds Attempted**: The Host-swap note above; naming `docs/` was rejected as too broad.
- **Related Assets**: `RULE-proposal-boundaries`, `CAP-DLV-proposal-incubation`, `SPEC-foundation-documents`.

## Evidence

```text
[VIOLATION: RULE-proposal-boundaries severity=warning ... message="boundaries.owns entry 'docs/foundation/' names no
existing directory (repository path, docs-root path or capability area)" remediation="... name its nearest existing
parent directory and the new path in the proposal text"]
```

## Disposition

Resolved as the documented procedure in `RULE-proposal-boundaries` (guide) and `CAP-DLV-proposal-incubation`: while
a `depends_on` prerequisite that creates or moves a path has not landed, the proposal keeps the current path and
names the expected one in its text; Development writes the expected path into its `_Boundary:` entries after the
prerequisite lands. No rule change.
