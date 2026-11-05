---
id: PROP-gitignore-drift-detection-target
title: Target Living Spec Structure for PROP-gitignore-drift-detection
status: draft
proposal: PROP-gitignore-drift-detection
created_at: 2026-11-04
targets:
  - file: docs/architecture/ARCH-05-4-distribution-components.md
---

# [Blueprint] PROP-gitignore-drift-detection: Target Living Spec Structure for Automatic .gitignore Configuration and Drift Detection for Projected Assets

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-gitignore-drift-detection is accepted.

---

## 1. System Capabilities Plan (docs/capabilities/)

- **CAP-GOV-gitignore-integrity (proposed)**:
  - Defines the contract for automated `.gitignore` boundary management during projection sync.
  - Specifies sentinel markers (`# BEGIN devkit managed ignore` ... `# END devkit managed ignore`).
  - Defines the non-tracking rule RULE-git-projected-untracked and its remediation requirements.

---

## 2. Use Cases Plan (docs/usecases/)

- **UC-sync-gitignore-drift (proposed)**:
  - **Goal**: Maintain repository hygiene by ensuring projected agent assets remain ignored by Git.
  - **Scenario 1**: `devkit sync` runs on a fresh repository lacking `.gitignore` patterns; inserts managed block.
  - **Scenario 2**: Pre-commit gate detects staged projected assets; fails with actionable remediation message.
  - **Scenario 3**: `devkit rules fix` unstages tracked projected files via safe `git rm --cached`.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-4-distribution-components`:
  - Adds `.gitignore` sync handler to the distribution/projection pipeline.
- **Candidate ADR**:
  - PADR-managed-gitignore-sentinels: Choice of delimiter block comments vs separate global ignore files.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- Introduces RULE-git-projected-untracked to default governance rule set.
- Adds `[git.ignore]` table to `.devkit/config.toml` schema.

---

## 5. System Before & After Comparison (Before & After)

### As-Is
```
User runs devkit sync
  ↳ Generates .agents/, .claude/, .codex/ (100+ files)
User runs git status
  ↳ 100+ untracked files appear
User accidentally commits them
  ↳ Git history polluted, future branch merges collide
```

### To-Be
```
User runs devkit sync
  ↳ Checks .gitignore
  ↳ Writes/updates `# BEGIN devkit managed ignore` block
User runs git status
  ↳ Clean working tree; only project source files appear
Pre-commit gate (rules check --staged)
  ↳ Validates that no projected files are tracked in git index
```
