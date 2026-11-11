---
name: command-design
description: Read before creating, configuring or extending justfile recipes, CLI commands or MCP tools. Selects necessary operations and callers before adding entry points, keeping setup and discovery concise.
---

# Design command entry points

1. Before adding an entry point, identify the requested operation, its caller and the existing way to run it.
   Add one only when it serves that operation, not a hypothetical future task.
2. Reuse an existing command when it meets the caller's needs. Add a wrapper or alias when it provides useful
   task composition, required execution context or a distinct caller contract; name that purpose.
3. Apply the relevant interface guidance below. Use the project's framework and output conventions.
4. Verify the resulting entry points from their documented working directory with their required tools.
   Keep setup guidance to the commands the project uses; place specialized options in the relevant help.

## Justfile

- Add recipes for actual project tasks; preserve established names instead of imposing a standard set.
- Keep recipes thin by calling existing scripts or package commands; group commands only when the caller needs the
  combined task. Create no placeholder recipes for tools the project does not use.
- Choose fast commit checks explicitly and keep slower suites in full verification or CI. Check existing hooks
  before connecting a recipe so the same check does not run twice. Example: when `npm run lint` already covers the
  commit check, configure that command directly; add a `verify` recipe only if the project needs a combined task.

## CLI

- Expose operations the caller needs, with a clear result and actionable failure. Keep internal helper steps
  behind the operation unless callers need to invoke them independently.
- Give common tasks short help and examples; put specialized flags in subcommand help instead of loading the
  entire command inventory into agent instructions.
- Preserve existing public commands and callers when extending a tool; removal is a separate compatibility
  decision, not a consequence of low usage in the current task.

## MCP

- Register only operations needed by MCP callers; do not generate a tool for every CLI command or helper.
- Share the operation implementation with other transports. Keep separate tools when their purposes,
  permissions or input contracts differ; do not hide unrelated actions behind one opaque generic tool.
- State each tool's purpose and input constraints concisely; use the host's discovery mechanism for specialized
  operations instead of duplicating their full schemas in setup instructions.

Done when every added entry point has an identified operation and caller, works from the documented context and
adds no redundant check or unsupported placeholder. Review accumulated interfaces separately when cleanup is requested.
