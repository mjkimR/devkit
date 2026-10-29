---
name: spec-feedback
description: 'Record observations on repository-owned (optionally upstream) tools and assets: friction, inefficiency, guessed decisions, rule/playbook needs. Use for user feedback or a session sweep (/spec-feedback); requested sweeps write no envelope.'
---

# spec-feedback: Repository-First Feedback Capture

One observation, one file, committed with the work. Capture writes `status: open` and never changes a status.

## When to record

| kind | Record when |
| :--- | :--- |
| `friction` | An instruction, skill, CLI command, spec document or rule blocked the task or forced a workaround |
| `suggestion` | A more efficient procedure, structure or default is visible |
| `change-request` | A specific procedure or instruction should change in a specific way |
| `question` | An instruction was ambiguous and you decided by guess; a human should confirm |

- Fix an ordinary task defect instead of recording it. Never record rejected non-goals or ideas without a concrete
  target.
- `FEEDBACK_POLICY` in `devkit spec policy`: `capture=requested-only` records only on the user's request;
  `coverage=repo` excludes `upstream` observations. An explicit user request overrides both.
- Choose the scope yourself, without asking: `repo` when this repository owns the asset (in-repository bundles and
  project overrides included, even if other repositories install it); `upstream` when an installed or external tool
  or bundle owns it; `unknown` when ownership is uncertain or mixed.

## Recording procedure

1. Record a `question` (at least its one-line decision) right after deciding; anything else after the current step.
2. Write the file where the work is, `<name>` kebab-case and unused (`devkit docs resolve FB-<name>` finds nothing):
   - Proposal Planning: `docs/proposals/PROP-<slug>/feedback/<name>.md`.
   - Spec Unit work: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/feedback/<name>.md` in the current spec bundle.
   - Otherwise: `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<name>.md`, today's date.
3. Fill it from the [feedback template](references/template.md):
   - `target`: the asset path or command a maintainer should open.
   - `origin: user` when the user raised the point; if the user's word is the only support, record a `question`.
   - Assess the merits yourself, never "the user asked for it".
   - `severity: critical` only when the next task here will certainly block at the same point.
   - `recurring: true` when you have seen this before in this repository.
4. Return to the task; `devkit docs list feedback` discovers the file.

For a `collect-feedback` or `report-session` stage, a Planning run's return or an explicit user-requested session
sweep, read the [sweep procedure](references/sweep.md).

## Completion

- `uv run devkit rules check <file>` exits `0` for each recorded file (`devkit rules fix <file>` aligns the ID and H1
  with the path).
- One conversation line per observation: `> Feedback recorded: <path> (<scope>/<kind>, <severity>)`.
