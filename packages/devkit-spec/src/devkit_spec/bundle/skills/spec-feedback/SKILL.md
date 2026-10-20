---
name: spec-feedback
description: 'Record observations on repository-owned (optionally upstream) tools and assets: friction, inefficiency, guessed decisions, rule/playbook needs. Use for user feedback or a session sweep (/spec-feedback); requested sweeps write no envelope.'
---

# spec-feedback: Repository-First Feedback Capture

One observation, one file, committed with the work. This skill only records: new observations stay `status: open`.
Hygiene promotes, dismisses or forwards selected items. An authorized direct-fix task resolves only its explicitly linked open source
feedback after implementation and verification, following the `spec` skill's [completion procedure](../spec/references/completion.md#source-feedback-resolution).
`promoted` closes feedback by handing it to follow-up work; `resolved` closes a directly addressed and verified
observation without promotion. Both are terminal; only open feedback needs action. Follow-up completion does not
change promoted sources to resolved.

---

## 1. When to record

Record when one of these is true; the cost is one small file.

| kind | Record when | Later destination (hygiene) |
| :--- | :--- | :--- |
| `friction` | An instruction, skill, CLI command, spec document or rule blocked the task or forced a workaround | rule / playbook / bundle fix |
| `suggestion` | A more efficient procedure, structure or default is visible | bundle fix / proposal |
| `change-request` | A specific procedure or instruction should be changed in a specific way | bundle fix |
| `question` | An instruction was ambiguous and you decided by guess; a human should confirm | guide or skill wording |

Read `devkit spec policy` before recording. Its `FEEDBACK_POLICY` line (JSON `feedback`) controls autonomous capture:

- `capture=observed`: record concrete observations as they arise and during enabled stage sweeps.
- `capture=requested-only`: record only when the user explicitly requests feedback; stage sweeps write policy-skip evidence ([sweep](references/sweep.md)).
- `coverage=repo`: repository-owned assets only. `coverage=repo-and-upstream`: also upstream tools used in the work (devkit, devkit-spec and others).
- `detail=brief|standard|detailed`: the detail contract in the [template](references/template.md).
- `reminder=contextual|off`: optional reminders from the router, not mandatory stage execution.

An explicit request to record an observation or sweep the session overrides capture, coverage and stage restrictions, never the evidence, detail, privacy and hygiene rules. Never ask the user to classify a tool, choose its maintainer or supply frontmatter.

Ownership scopes (`scope`):

- `repo`: this repository owns the affected asset: rules, skills, instructions, playbooks, workflows, role contracts, script/CLI tools, templates, Living Spec documents and in-repository bundles, project overrides included. A spec skill developed in devkit-spec is `repo`; its installed copy in another repository is `upstream`.
- `upstream`: an installed or external tool or bundle owns it.
- `unknown`: ownership is uncertain or spans repository and upstream assets; record the observed target and leave ownership to hygiene.

`target` identifies the observed command or asset, not the presumed resolution owner.

Do not record: ordinary task defects (fix them), rejected non-goals, or ideas with no concrete target.

---

## 2. Procedure

1. **Finish the current step first.** Exception: for `question`, write at least the one-line decision right after you make it so the chosen interpretation is not lost.
2. **Locate the destination** (paths and IDs are checked by `RULE-id-convention`):
   - Proposal Planning: `docs/proposals/PROP-<slug>/feedback/<name>.md`, inside this proposal's write boundary.
   - Spec Unit work (`spec` depth or Development after proposal handoff): `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/feedback/<name>.md`, in the spec bundle you are working in (no date prefix on the file).
   - Work without a spec bundle (`session` depth, investigation or review): `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<name>.md`, current month, today's date.
   - Create the `feedback/` directory if needed. Never write under `.devkit/` or elsewhere under `docs/`.
   - `<name>` is kebab-case and not used by another feedback file (`devkit spec resolve FB-<name>` finds none).
3. **Write one file from the [feedback template](references/template.md)**, following its evidence, privacy and detail rules. Fill the frontmatter completely; set `id: FB-<name>` (no date) and the H1 `# [FB-<name>] <title>` (`devkit rules fix <file>` aligns both with the path).
   - `target` is the most important field: the asset path or command a maintainer should open.
   - `origin: user` when the user raised the point; otherwise `agent`. If the only support is "the user said so", the item is a `question`, not a `change-request`.
   - **The assessment is yours**: why you agree or disagree on the merits, never "the user asked for it".
   - `severity: critical` only when the next task in this repository will certainly block at the same point. Simple inconvenience is `blocked` or below.
   - `recurring: true` when you have seen this before in this repository.
4. **Return to the task.** Do not mention the file as a completion item; `devkit spec list feedback` discovers it. Capture never changes `status`; source-feedback resolution belongs to task completion.

Before each Planning or Development run's last work commit, capture observed feedback in its proposal or spec, including questions or problems. Handoff carries open files to the spec; deletion without handoff follows the `spec` skill's `references/feedback-retirement.md`.

---

## 3. Category reference

Use the [category table](references/categories.md) when assigning the observation category.

---

## 4. Output in the conversation

For a single observation, one line:

```markdown
> Feedback recorded: `specs/<...>/feedback/<name>.md` (<scope>/<kind>, <severity>)
```

---

## 5. Sweep (stage or user request)

For a workflow stage sweep (`collect-feedback`, or the `report-session` stage of a `session` task), a Planning run's return ([run coverage](references/sweep.md#planning-run-coverage)) or an explicit user-requested session sweep, read the [sweep procedure](references/sweep.md).
