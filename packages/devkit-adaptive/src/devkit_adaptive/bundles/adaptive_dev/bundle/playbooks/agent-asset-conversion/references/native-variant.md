# Native variant

A native variant is the source file copied unchanged for the one host it was written for.

## State the limits before copying

Read the file whole, tell the user each limit below and wait for the user's decision; the copy puts third-party instructions into the host as written.

- Hosts without a variant receive no file, and every `uv run devkit sync` reports the asset with an `ASSET_UNPROJECTED` notice. Read that notice as this limit, not as a failure to fix by narrowing the project's agents.
- A model or effort value pinned in the file stays in force; the project's model level policy does not reach a native variant.
- The file carries none of the swarm assignment and return contract: no absolute boundaries, no return fields, no rule against widening authority.
- Auto-invocation wording and each authority the source grants (commit, push, pull request, package install, deployment) stay active on that host. Quote each such line to the user.
- The source's license governs the copy. Keep its license notice and copyright line with the file; if the license is unknown or does not permit redistribution, stop.

## Copy and declare it

1. Copy the file byte for byte to `native/<host>/<prefix>-<role><suffix>` in the project bundle: `.toml` for `codex`, `.md` for `claude-code` and `antigravity`.
2. Save the source's license text beside it as `native/<host>/<prefix>-<role>.LICENSE`; it is undeclared, so it stays with the bundle source and is not deployed.
3. Declare the asset with `variants` and no `source`:

```toml
[[assets]]
id = "<prefix>-<role>"
kind = "subagent"
[assets.variants]
claude-code = "native/claude-code/<prefix>-<role>.md"
```

4. Record the provenance (source URL, commit, path) in the bundle's constitution entry; the copied file stays unchanged.

## What sync does

- The file lands unchanged, with no key added, removed or converted, at the host's agent path: `.claude/agents/<id>.md`, `.codex/agents/<id>.toml` or `.agents/agents/<id>.md`. No other host receives a file.
- The agent name inside the copied file is the source's own; the asset ID names the projected file.

## When the user wants the role on every host

Convert it to a role contract instead, and keep the native variant out; one asset declares `source` or `variants`, never both.
