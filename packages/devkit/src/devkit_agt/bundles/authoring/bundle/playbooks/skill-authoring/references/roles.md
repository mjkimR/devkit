# Role authoring

## Choose the role's placement

- For a role used only within one skill, keep its instructions in the skill's `roles/<role>.md` by default, so its
  metadata stays out of the global subagent list.
- Register a subagent when it needs independent selection outside that skill or role-specific host settings that
  a general subagent invocation cannot supply, such as model, tool or sandbox settings.
- Keep role procedures and return requirements separate from host execution settings; Markdown instructions do
  not enforce tool permissions or sandbox boundaries.

## Write the delegation instructions

- For a skill-local role, route the task to one role file and tell a `role-worker` subagent to read that file first;
  pass its absolute installed path without loading every role body into the coordinator.
- Name the subagent type per role or assignment in the delegation instructions, `role-worker` by default. If a role
  or assignment needs a capability outside the `role-worker` tool list, such as interacting with a running UI, name
  the host's general subagent (`general-purpose` on Claude Code) for it instead.
- If `role-worker` is unavailable, tell the coordinator to stop that delegation and report the missing subagent and
  its cause; never write a runtime fallback to another subagent type.
- If the child holds commit authority or worktree ownership, such as adaptive-dev's builder role, keep the
  delegation the skill defines instead of `role-worker`.
- For a registered role, use the host's registered-role invocation so its execution settings apply.
- Supply the child with its goal, relevant sources, read/write boundaries, permitted actions, stop condition and
  expected return; make its assigned role file readable within those boundaries.
- Where the host supports it, spawn with a fresh context without parent conversation inheritance; otherwise
  report that limitation and pass only the task's required information.
- When required delegation or permissions are unavailable, report missing coverage; never describe a prompt as
  native enforcement.

## Write the path-resolution instructions

- Resolve `roles/<role>.md` from the directory containing the invoked `SKILL.md`, not the working directory or
  the directory of a reference file; use the loaded skill's location rather than a hardcoded host directory.
- If that location is unavailable, locate and verify the invoked skill before delegation; verify the selected
  role file exists and pass its resolved absolute path to the child.

Example: if the invoked skill is `/workspace/project/.agents/skills/review/SKILL.md`, the assignment starts with
`Read /workspace/project/.agents/skills/review/roles/critic.md first, then review the supplied draft within the
assigned read boundaries and return the findings in that role's format.` Derive the path from the invoked skill;
the example directory is not a required installation location.

## Check the authored guidance

- Verify that each role's invocation matches its placement and required host settings.
- Verify that role paths resolve from the invoked skill when the working directory or a loaded reference's
  directory differs from the skill root.
- Verify that the assignment carries the required boundaries and return format without claiming native controls
  that the host does not provide.
