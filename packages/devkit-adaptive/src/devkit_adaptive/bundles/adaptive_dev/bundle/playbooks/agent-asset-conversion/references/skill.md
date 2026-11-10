# Skill

Choose a skill when the source is a procedure the Host itself runs. A source skill that holds domain checks for delegated work and no Host procedure becomes a role overlay.

## Write the directory

1. Create `skills/<prefix>-<name>/SKILL.md` in the project bundle; the directory name is the asset ID.
2. Keep two frontmatter keys, `name` and `description`. Drop host-specific keys such as `allowed-tools`, `model` and `license`; the source license stays in the conversion report.
3. Rewrite `description` for triggering in this project: what the skill does and the situation that calls for it, in the words this project's users type. Remove auto-invocation wording.
4. Rewrite the body with the rewrite rules, as numbered steps that end with completion criteria the agent can check.
5. Keep in `SKILL.md` what every run needs; move what some runs need to `references/<situation>.md`, each linked from `SKILL.md` with its read condition.
6. End `SKILL.md` with the provenance line: source URL, commit and path.

```markdown
---
name: <prefix>-<name>
description: <What it does and the situation in this project that calls for it.>
---

# <Skill title>

## Constraints

- <Boundary that holds on every run.>

## Procedure

1. <Step, with the exact command where the step is fragile.>

## Completion

- <A command and its expected result, or a file state.>

Source: <url> at <commit>, `<path>`; rewritten for this project.
```

## Decide the invocation

- Leave `invocation` out when the agent may start the skill from a matching task.
- Set `invocation = "user"` when the skill changes files beyond the task at hand, runs for a long time, spends an external quota, or the user asked that it start on request alone.
- Declare it in `bundle.toml` and nowhere else: a `disable-model-invocation` key in `SKILL.md` or a `policy.allow_implicit_invocation` key in `agents/openai.yaml` makes the bundle invalid.

```toml
[[assets]]
id = "<prefix>-<name>"
kind = "skill"
source = "skills/<prefix>-<name>"
invocation = "user"
```

## Import a script

1. Import a script when the user selected that script by path, and only after reading it whole.
2. Report what it reads, what it writes, each network address it contacts and each program it starts.
3. Never run it during conversion; its first run belongs to a task the user starts.
4. A copied script is verbatim text: keep the source's license notice beside it in the skill directory.
5. If a script installs packages, changes host settings or reaches outside the project, leave it out and list the step it served as an unmet prerequisite.

## Deploy it

- `uv run devkit sync` deploys the whole directory, executable bits included, to `.claude/skills/<id>/` and `.agents/skills/<id>/`, and writes each host's explicit-invocation setting when `invocation = "user"`.
- One skill ID has one owning bundle; a second bundle shipping the same ID stops the sync with `BUNDLE_CONFLICT`.
- When the project bundle has a constitution, each deployed copy gains a line telling the agent to read `uv run devkit get-context <bundle>` first.

## Trial

The user starts the skill on one small real task. Compare the outcome with the skill's completion criteria; report the trial as unverified when the user has not run it.
