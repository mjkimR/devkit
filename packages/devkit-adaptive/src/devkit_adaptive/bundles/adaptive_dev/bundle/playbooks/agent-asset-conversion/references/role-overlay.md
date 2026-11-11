# Role overlay

A role overlay is a plain Markdown file an archetype reads first. It adds domain checks to an assignment; the archetype supplies the tools, sandbox, delegation limits and return contract.

## Write the file

1. Create `roles/<prefix>-<role>.md` in the project bundle from the skeleton below; the file has no frontmatter.
2. Name the one mapped archetype in the second line.
3. Keep the skeleton's first directive (reading the assignment), its no-added-permission line and its return line; put the domain checks between them, one directive per line, and add the role-specific evidence to the return line.
4. End the file with the provenance line: source URL, commit and path.
5. Keep the file to about 40 lines. If the kept material needs more, stop and choose a skill or a project document for it; splitting one role across overlays is no remedy.

```markdown
# <Role title>

Use with `swarm-<archetype>` or a compatible caller-owned execution contract.

1. Read the assignment's goal, absolute paths, source/base identity, permitted actions, checks and stop condition.
2. <Domain check: what to inspect and the condition that makes it a defect.>
3. <Decision criterion or failure mode, with the evidence that shows it.>
4. Keep the execution contract and caller's workflow authoritative; this overlay grants no added tool, Git or write permission.
5. Return status, source/base and final SHA when committed, actual changed paths, commands/outcomes, defects and unverified areas, plus <role-specific evidence>; report unavailable capabilities and preserve partial results.

Source: <url> at <commit>, `<path>`; rewritten for this project.
```

Example directives for a migration reviewer converted from a database-specialist persona:

```markdown
2. Check each migration for a lock that blocks writes on a table the service writes during deployment.
3. Check that each schema change has a tested reverse step, and report a change without one as a defect.
4. If a migration needs a production operation, name the operation in the return instead of running it.
```

## Declare and deploy it

Add the overlay to the project bundle's `bundle.toml` as a `document` asset:

```toml
[[assets]]
id = "<prefix>-<role>"
kind = "document"
source = "roles/<prefix>-<role>.md"
```

- `uv run devkit bundle plan <bundle source> --agent <agent>` lists the asset with the one path `.devkit/managed/<bundle>/roles/<prefix>-<role>.md`, for every agent.
- `uv run devkit sync` writes that managed copy byte for byte and registers no agent or skill for the overlay in any host directory; a host learns of the role through an assignment.
- After the source file changes, run `uv run devkit sync` again.

## Use it in an assignment

1. Resolve `<project root>/.devkit/managed/<bundle>/roles/<prefix>-<role>.md` to an absolute path and verify the file exists; if it is missing, run `uv run devkit sync`.
2. Invoke the archetype through the host's registered-role mechanism and name that absolute path as the role file in the assignment, inside its read boundary.
3. Supply the rest of the assignment as for any archetype: one goal, source/base identity, absolute read and write ownership, permitted actions and Git operations, checks, stop condition and expected return fields.

Constitution entry for the overlay:

```markdown
- `<prefix>-<role>`: <use> with `swarm-<archetype>`; role path `.devkit/managed/<bundle>/roles/<prefix>-<role>.md`. Unmet prerequisites: <list or none>.
```

## Limits

- An overlay sets no tool list, sandbox mode or model; a role that needs one is a role contract.
- An archetype rejects an overlay that asks for more than the assignment permits; never write one that does.
