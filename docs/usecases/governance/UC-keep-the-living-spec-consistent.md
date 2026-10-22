---
id: UC-keep-the-living-spec-consistent
title: Keep the Living Spec Consistent
summary: "An AI coding agent keeps the Living Spec structurally consistent with deterministic spec rules, fixes, the commit gate and CI, so that each inconsistency is reported with a stable rule ID and repaired automatically where the repair is unambiguous."
area: governance
primary_actor: AI coding agent
supporting_actors:
  - Commit gate (checks the staged tree)
  - CI (checks a pull request branch)
status: active
capabilities:
  - CAP-DOCS-document-model
  - CAP-GOV-spec-rules
  - CAP-TRACE-code-entrypoints
  - CAP-GATE-commit-gates
created_at: 2026-10-13
---

# [UC-keep-the-living-spec-consistent] Keep the Living Spec Consistent

## 1. Goal

- **Goal**: have every structural inconsistency the agent introduces (a broken reference, a one-sided link, a
  misplaced file, a stale spec status, an unreconciled change, a dead code entrypoint) reported with a stable rule ID
  and a deterministic remediation, and repaired automatically where the repair is unambiguous, so that the Living Spec
  stays a trustworthy current-state contract that later agents navigate by ID without re-validating it
- **Scope**: the `spec` bundle's rules run by devkit's rule engine (`devkit rules check`, `fix`, the commit gate and
  CI); semantic drift that structure cannot show is reconciled under `UC-reconcile-living-spec-drift`
- **Trigger**: the agent has changed documents or code in a project that uses the `spec` bundle
- **Preconditions**: `devkit sync` has deployed the `spec` bundle's rules; agents may lose context, work on parallel
  branches and delete or move code

---

## 2. Main Success Scenario

1. The agent runs the spec rules over the workspace or the files it changed (`CAP-GOV-spec-rules`).
2. The system reads the document index and reports each inconsistency in the targeted files with its rule ID, its
   status (`open` or `fixable`) and its remediation, leaving completed spec bundles alone unless they are named
   (`CAP-GOV-spec-rules`, `CAP-DOCS-document-model`).
3. The agent applies the fixes; the system rewrites only targeted current files and only the bytes each fix owns
   (`CAP-GOV-spec-rules`).
4. The agent rechecks; the system reports no violation (`CAP-GOV-spec-rules`).
5. The agent commits; the commit gate evaluates the exact staged tree as a snapshot run and accepts the commit
   (`CAP-GATE-commit-gates`, `CAP-GOV-spec-rules`).
6. On a pull request, CI evaluates the branch against its merge base the same way and passes (`CAP-GOV-spec-rules`).

---

## 3. Extensions

- **2a.** The `[tool.spec]` table is malformed: the run fails with `SPEC_CONFIG_INVALID` attributed to the rule,
  because the rules cannot tell which documents follow which conventions; the agent corrects the table; resumes at
  step 1.
- **3a.** A violation is `open` (no deterministic repair: a reference to an ID no document declares, a dead
  entrypoint, missing reconcile evidence): the fix leaves it unchanged and never guesses; the agent repairs it by hand
  following its remediation; resumes at step 4.
- **5a.** The commit deletes code that a capability declares in `entrypoints` without updating the capability:
  `RULE-code-entrypoints` reports the capability although the commit does not touch it, and the gate refuses the
  commit; the agent restores the code, points the declaration at the moved code or removes it; resumes at step 5
  (`CAP-TRACE-code-entrypoints`).
- **5b.** The commit marks a `reconcile.md` `resolved` with a `modified` target the commit does not change:
  `RULE-reconcile-contract` reports the target, and the gate refuses the commit; the agent stages the Living Spec edit
  with the record; resumes at step 5.

---

## 4. Postconditions

- **Success guarantee**: the targeted files and the committed tree pass every spec rule; fixed links, IDs and statuses
  are written in the files' own style; completed spec bundles are unchanged.
- **Minimal guarantee**: no fix moves or renames a file, guesses a missing ID or rewrites a historical file; a refused
  commit creates no commit.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Fixes a one-sided link deterministically
- **Covers**: main success scenario
- **Given**: a use case lists a capability in `capabilities`, and the capability does not list the use case
- **When**: the agent runs `devkit rules check` and then `devkit rules fix`
- **Then**: the check reports `RULE-traceability-link` on the capability with `status=fixable`, the fix appends the
  use case ID to the capability's `usecases` in the list's existing style, and a recheck reports no violation

### Scenario 2: Fails the run on a malformed policy table
- **Covers**: 2a
- **Given**: `.devkit/config.toml` has a `[tool.spec]` table with an unknown key
- **When**: the agent runs `devkit rules check`
- **Then**: the run fails with `SPEC_CONFIG_INVALID` naming the table and exits `2`

### Scenario 3: Reports a reference to a missing document, never guessing
- **Covers**: 3a
- **Given**: a decision cites a capability ID that no document declares
- **When**: the agent runs `devkit rules check` and then `devkit rules fix`
- **Then**: `RULE-document-reference` reports the unresolved ID with `status=open`, and the fix leaves the reference
  unchanged

### Scenario 4: Fails the commit gate when code is deleted without its document
- **Covers**: 5a
- **Given**: a capability declares `src/<package>/engine.py` in `entrypoints`
- **When**: a commit stages only the deletion of that file and the commit gate runs `devkit rules check --staged`
- **Then**: `RULE-code-entrypoints` reports the capability, although the commit does not touch it, and the commit is
  refused until the declaration is updated or removed

### Scenario 5: Requires the evidence of a resolved reconcile record
- **Covers**: 5b
- **Given**: a commit marks a spec's `reconcile.md` `resolved` with a `modified` target that the commit does not change
- **When**: the commit gate runs `devkit rules check --staged`
- **Then**: `RULE-reconcile-contract` reports the target, and committing the Living Spec edit with the record clears it
