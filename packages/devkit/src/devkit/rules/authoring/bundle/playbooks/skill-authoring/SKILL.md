---
name: skill-authoring
description: Create an agent skill or playbook with a router structure, restructure one that grew too large (RULE-skill-document-size), and decide when it needs a helper script.
aliases:
  - restructure a large skill
  - split SKILL.md
  - skill document size
  - write a new skill
  - playbook authoring
---

# Skill authoring and restructuring

Use this playbook when you create or substantially edit a skill (`SKILL.md` with
optional `references/` and `scripts/`) or a playbook, and when
`RULE-skill-document-size` reports a file. Read
[script support](references/scripts.md) only when a step needs a helper script.

## Prerequisites

- The skill or playbook to create or restructure, and where its source lives:
  a project-native skill directory or a bundle source (`bundle/skills/`,
  `bundle/playbooks/`). Never edit agent projections or `.devkit/managed/`;
  change the source and run `devkit sync`.
- Restructure in a hygiene session or as the task itself, not as a side quest
  of unrelated feature work.

## Constraints

- Every instruction that applies on every run stays in `SKILL.md`. Never move
  safety, scope or boundary constraints into a rarely read file.
- Size is a review signal, not a goal. Do not shrink a file by joining lines,
  dropping verification criteria or deleting examples the procedure depends on.

## Step 1: Create new skills as a router

```text
<skill-name>/
├── SKILL.md          # always loaded when the skill triggers
├── references/       # read on a stated condition
└── scripts/          # executed, not read (see references/scripts.md)
```

- **Frontmatter**: `name` matches the directory. `description` says what the
  skill does and when to use it, with the words a user or agent would actually
  type; the description decides whether the skill triggers at all.
- **Body order**: purpose and trigger, required constraints, procedure or task
  branches, verification criteria (how the agent knows it is done), then
  situational reference paths.
- **References**: one file per situation or procedure, linked from `SKILL.md`
  with its read condition, for example "Read `references/review.md` when
  entering review." Keep references one level deep.
- **Examples**: one short example per pattern in `SKILL.md`; long or rare
  examples go to `references/`.
- **Normative words**: use MUST, SHOULD and MAY with explicit thresholds instead
  of vague qualifiers.

## Step 2: Restructure a large skill

Apply these in order and stop once the file is focused; a later step is not
required when an earlier one suffices.

1. **Compress.** Remove repeated explanation, long background and overlapping
   examples. Keep execution conditions, required constraints and verification
   criteria.
2. **Split conditional content first.** Move content that only some runs need:
   recovery procedures, tool- or host-specific instructions, the detailed schema
   of one stage, rare long examples. Name each file after its situation and
   state the read condition where `SKILL.md` links it.
3. **Thin router.** `SKILL.md` keeps purpose and trigger, shared constraints,
   task branches and the situational reference paths. Do not instruct the agent
   to read every reference at start; that loads the same context as before.
4. **Review supporting files.** Apply the same steps to a large reference. Split
   it by situation or procedure, not by arbitrary size. Avoid many tiny files
   and chains where one reference sends the agent to another.

## Step 3: Record a justified exception

When a file must stay large (a single procedure that is always read whole, or a
quoted external protocol), add an exact-path override with the reason as a
comment directly above it in `.devkit/config.toml`:

```toml
# Read as one procedure; split deferred.
[[rules.settings.RULE-skill-document-size.overrides]]
path = ".agents/skills/example/SKILL.md"
max_bytes = 12288
```

Update or remove the entry when the file moves or shrinks.

## Completion conditions

- Every link from `SKILL.md` resolves, and every reference is linked from
  somewhere.
- Every required constraint is still reachable on every path that needs it; a
  run that does not hit a stated condition does not need the moved file.
- `uv run devkit rules check --phase hygiene` reports no
  `RULE-skill-document-size` warning for the edited files, or the remaining
  file has a commented override.
