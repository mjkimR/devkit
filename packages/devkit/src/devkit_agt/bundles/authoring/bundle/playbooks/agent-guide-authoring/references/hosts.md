# How agent hosts load guides

Confirm a detail in the host's documentation before relying on it; host behavior changes between releases.

- Codex combines `AGENTS.md` files from the repository root down to the working directory, root first, and drops
  what exceeds a combined size limit, so a large root guide crowds out nested guides.
- Claude Code reads `CLAUDE.md`, not `AGENTS.md`. Connect them with a `CLAUDE.md` that contains only `@AGENTS.md`,
  or with a symlink, never with a copy; devkit never writes `CLAUDE.md`. It loads the guides of the working
  directory and its ancestors at session start and a subdirectory's guide when the agent works there; imported
  files count toward the context.
- If another host does not read `AGENTS.md`, point its own guide file at `AGENTS.md` the same way.

A nested guide holds only rules for its subtree, repeats nothing from the root guide, passes the playbook's Step 1
test and stays smaller than the root guide; give it a lower `max_bytes` override when it grows.
