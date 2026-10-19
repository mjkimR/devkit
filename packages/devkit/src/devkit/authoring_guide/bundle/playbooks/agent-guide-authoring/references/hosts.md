# How agent hosts load guides

Read this when you add a nested guide, move content between guides, or connect
`CLAUDE.md` to `AGENTS.md`. Host behavior changes between releases; confirm the
current rules in the host's documentation before relying on a detail.

## Codex

- Combines `AGENTS.md` files from the repository root down to the working
  directory, root first, so a nested guide adds to or narrows the root guide.
- Drops what exceeds a combined size limit, so a large root guide crowds out
  nested guides.

## Claude Code

- Reads `CLAUDE.md`, not `AGENTS.md`. Connect them with a `CLAUDE.md` that
  contains only `@AGENTS.md` (an import expanded into the context) or with a
  symlink; devkit never writes `CLAUDE.md`.
- Loads the guides of the working directory and its ancestors at session start;
  a guide in a subdirectory is loaded when the agent works with files there.
- Imported files count toward the context like the guide itself.

## Other hosts

Check whether the host reads `AGENTS.md`, how it treats nested files and whether
it supports imports. When it reads none of them, point its own guide file at
`AGENTS.md` the same way as for Claude Code.

## Nested guides

- Write a nested guide only for rules that hold in that subtree and not
  elsewhere; repeat nothing from the root guide.
- Keep nested guides smaller than the root guide; give them a lower `max_bytes`
  with a path override when they start to grow.
- A nested guide still loads on every turn in its subtree: the same "what stays"
  test applies.
