---
id: PROP-gitignore-drift-detection
title: Automatic .gitignore Configuration and Drift Detection for Projected Assets
summary: Ensures projected agent assets (.agents/, .claude/, .codex/) are properly excluded from Git tracking during devkit sync.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high
dev_effort: medium                    # low | medium | high
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit-docs/src/devkit_docs/features/governance/
    - docs/capabilities/governance/
    - docs/capabilities/distribution/
    - docs/usecases/
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-gitignore-drift-detection] Automatic .gitignore Configuration and Drift Detection for Projected Assets

## 1. Background & Hypothesis

`devkit sync` projects agent configurations, subagent instructions, skills, and runtime manifests into `.agents/`, `.claude/`, `.codex/`, `.devkit/managed/`, and `.devkit/transient/`. These projected assets total dozens to hundreds of generated files.

When establishing devkit in brownfield repositories or updating agent configurations, repositories frequently lack exclusion patterns for `.agents/`, `.claude/`, and `.codex/` in the root `.gitignore`. Consequently:
1. Git index and status are polluted with hundreds of generated markdown and TOML files.
2. Developers unintentionally stage and commit generated assets, resulting in merge conflicts and noisy commit histories.
3. Untracking these files after the fact requires error-prone manual `git rm --cached` operations.

**Hypothesis**:
`devkit sync` should inspect the repository's `.gitignore` and automatically manage a delimited block (e.g., `# BEGIN devkit managed ignore` ... `# END devkit managed ignore`) ensuring all projected agent asset roots are ignored by Git. Additionally, `devkit rules check` and pre-commit gates should detect if projected paths are currently tracked by Git (`git ls-files`), raising an immediate actionable violation with an automated fixer.

## 2. Technical Spike Questions

- **Q1 — Managed Block Format**: How should `.gitignore` modifications be scoped to avoid overwriting user patterns?
  - *Approach*: Use explicit boundary comments:
    ```gitignore
    # BEGIN devkit managed ignore
    .agents/
    .claude/
    .codex/
    .devkit/transient/
    # END devkit managed ignore
    ```
  - `devkit sync` treats only lines between these sentinels as managed. User-defined patterns before or after remain untouched.
- **Q2 — Detection of Tracked Generated Assets**: How should Git tracking drift be detected?
  - *Approach*: A new hygiene/linter rule RULE-git-projected-untracked executes `git ls-files -- .agents .claude .codex .devkit/transient`. Any matches produce an error violation with remediation instructions (`git rm -r --cached <paths>`).
- **Q3 — Configuration & Opt-out**: What if a repository explicitly wishes to version-control agent projections?
  - *Approach*: Provide `[git.ignore] auto_manage = false` in `.devkit/config.toml` to disable automatic `.gitignore` synchronization.

## 3. Proposed Design & Impact

1. **`devkit sync` Enhancement**:
   - During projection deployment, compute the list of target projection roots (`.agents/`, `.claude/`, `.codex/`, `.devkit/transient/`).
   - Check the root `.gitignore`. If the managed block is absent or drifting, create/update the block idempotently.
2. **Hygiene Rule (RULE-git-projected-untracked)**:
   - Runs during `devkit rules check` and `--staged` pre-commit gate.
   - Ensures no projected or transient files are tracked in the Git index.
3. **CLI Diagnostic / Fixer**:
   - `devkit rules fix` applies `git rm -r --cached` to staged/tracked projected assets automatically.

## 4. Lifecycle & Retirement Criteria

- Acceptance: `devkit spec proposal accept gitignore-drift-detection --by user` transitions this proposal to planning upon consensus.
- Validation: End-to-end integration tests verifying that `devkit sync` creates/updates `.gitignore` cleanly without breaking existing user ignore rules.
