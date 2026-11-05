---
id: PROP-gitignore-drift-detection
title: Git Tracking Diagnostics for Projected Assets
summary: "Detects missing ignore coverage and tracked devkit projections during sync without modifying project ignore rules or the Git index."
status: accepted                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high
dev_effort: medium                    # low | medium | high
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - docs/capabilities/distribution/
    - docs/usecases/
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-gitignore-drift-detection] Git Tracking Diagnostics for Projected Assets

## 1. Background & Hypothesis

Pilot adoption exposed generated native agent files in Git status and accidental tracking. Native projection
roots also contain project-owned settings and instructions. CAP-DIST-workspace-ownership leaves root ignore
rules and the Git index under project ownership; sync already seeds ignores for managed and transient content
inside `.devkit/.gitignore`.

The retained scope is a read-only diagnostic during sync. It should identify the actual devkit-deployed native
paths that lack effective ignore coverage or are already tracked, then give precise remediation.

## 2. Technical Spike Questions

- Which receipt and planned projection records identify the deployed paths without including neighboring
  project-owned files, including removed or changed projections?
- How should Git ignore checks distinguish missing coverage from already tracked files, including negations,
  nested ignore files and a workspace without Git?
- How can sync return bounded notices with stable codes and actionable paths without repeating every generated
  file in the output? Planning must settle dry-run, check and locked-mode behavior.

## 3. Proposed Design & Impact

- Check only actual devkit-owned native projection paths, using installation records and the sync plan.
- Distinguish missing effective ignore coverage from files already in the Git index.
- Return notices with the relevant paths and precise ignore or untracking instructions. Preserve the standard
  notice and `--strict` behavior defined by ARCH-08-1-agent-output.
- Keep the implementation in distribution so distribution-only installations receive the diagnostic.
- Preserve the existing `.devkit/.gitignore` behavior.

### Non-Goals

- No automatic root `.gitignore` edits, managed ignore block or new opt-out setting.
- No Git index writes or automatic `git rm --cached` fixer.
- No blanket ignore of `.agents/`, `.claude/` or `.codex/`.
- No default commit-blocking rule or parallel governance implementation.

## 4. Validation & Priority

Implement this diagnostic before broader onboarding conveniences. Verify an ignored untracked projection,
a projection without ignore coverage, an already tracked projection and a neighboring project-owned file.
Include nested/negated ignore cases and a workspace without Git. Assert that root ignore files and the Git
index remain unchanged, and that notice output stays bounded.
