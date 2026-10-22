---
name: spec-feedback
description: 'Record observations on repository-owned (optionally upstream) tools and assets: friction, inefficiency, guessed decisions, rule/playbook needs. Use for user feedback or a session sweep (/spec-feedback); requested sweeps write no envelope.'
---

# spec-feedback: Repository-First Feedback Capture

One observation, one file, committed with the work. Capture writes `status: open` and never changes a status:

- The `feedback-hygiene` playbook promotes, dismisses or forwards selected items.
- An authorized direct-fix task resolves only its explicitly linked open feedback, after implementation and
  verification, by the `spec` skill's [source feedback resolution](../spec/references/completion.md#source-feedback-resolution).

## When to record

Record when one of these is true:

| kind | Record when |
| :--- | :--- |
| `friction` | An instruction, skill, CLI command, spec document or rule blocked the task or forced a workaround |
| `suggestion` | A more efficient procedure, structure or default is visible |
| `change-request` | A specific procedure or instruction should be changed in a specific way |
| `question` | An instruction was ambiguous and you decided by guess; a human should confirm |

- Fix an ordinary task defect instead of recording it.
- Do not record rejected non-goals or ideas with no concrete target.

Read `devkit spec policy` before recording. Its `FEEDBACK_POLICY` line (JSON `feedback`) controls autonomous capture:

- `capture=observed`: record concrete observations as they arise and during enabled stage sweeps.
- `capture=requested-only`: record only when the user explicitly requests feedback; stage sweeps write policy-skip
  evidence ([sweep](references/sweep.md)).
- `coverage=repo`: repository-owned assets only. `coverage=repo-and-upstream`: also upstream tools used in the work.
- `detail=brief|standard|detailed`: the detail contract in the [template](references/template.md).
- `reminder=contextual|off`: optional reminders from the router, not a mandatory stage.

If the user explicitly requests an observation record or a session sweep, ignore the capture, coverage and stage
restrictions; the evidence, detail and privacy rules still apply.

Classify the tool, choose its owner and fill the frontmatter yourself; do not ask the user for them. Ownership scopes
(`scope`):

- `repo`: this repository owns the affected asset: rules, skills, instructions, playbooks, workflows, role contracts,
  script/CLI tools, templates, Living Spec documents and in-repository bundles, project overrides included. An asset
  developed here stays `repo` even when other repositories install it.
- `upstream`: an installed or external tool or bundle owns it.
- `unknown`: ownership is uncertain or spans repository and upstream assets; record the observed target and leave
  ownership to hygiene.

## Recording procedure

1. **Finish the current step first.** For a `question`, write at least the one-line decision right after you make it,
   so the chosen interpretation is not lost.
2. **Locate the destination** (`RULE-id-convention` checks paths and IDs):
   - Proposal Planning: `docs/proposals/PROP-<slug>/feedback/<name>.md`, inside this proposal's write boundary.
   - Spec Unit work (`spec` depth, or Development after proposal handoff):
     `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/feedback/<name>.md` in the current spec bundle, no date prefix on the file.
   - Work without a spec bundle (`session` depth, investigation or review):
     `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<name>.md`, current month, today's date.
   - Create the `feedback/` directory if it is missing. Write nothing under `.devkit/` and nothing elsewhere under
     `docs/`.
   - `<name>` is kebab-case and unused: `devkit spec resolve FB-<name>` finds nothing.
3. **Write one file from the [feedback template](references/template.md)**, following its evidence, privacy and detail
   rules. Set `id: FB-<name>` (no date) and the H1 `# [FB-<name>] <title>`; `devkit rules fix <file>` aligns both with
   the path.
   - `target` names the asset path or command a maintainer should open, not the presumed resolution owner.
   - Set `category` from the [category table](references/categories.md).
   - Set `origin: user` when the user raised the point; otherwise `agent`.
   - If the only support is "the user said so", record a `question`, not a `change-request`.
   - Write your own assessment of the merits, never "the user asked for it".
   - Set `severity: critical` only when the next task in this repository will certainly block at the same point; set
     a simple inconvenience to `blocked` or below.
   - Set `recurring: true` when you have seen this before in this repository.
4. **Return to the task.** Do not list the file as a completion item; `devkit spec list feedback` discovers it.

Before each Planning or Development run's last work commit, capture observed feedback, questions and problems
included, in its proposal or spec. Handoff carries open files to the spec. If a proposal is deleted without handoff,
follow the `spec` skill's [feedback retirement](../spec/references/feedback-retirement.md).

## Sweep (stage or user request)

Read the [sweep procedure](references/sweep.md) for a workflow stage sweep (`collect-feedback`, or the
`report-session` stage of a `session` task), a Planning run's return or an explicit user-requested session sweep.

## Completion

- `uv run devkit rules check <file>` exits `0` for each recorded file.
- The conversation gets one line per recorded observation:

  ```markdown
  > Feedback recorded: `specs/<...>/feedback/<name>.md` (<scope>/<kind>, <severity>)
  ```
