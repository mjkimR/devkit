# Native variant

A native variant is the source file copied unchanged for the one host it was written for. Choose it only on the user's request for the unmodified original.

## State the limits before copying

Read the file whole, then tell the user each limit below and wait for the user's decision. The copy puts third-party instructions into the host as written, so the decision is the user's.

- Hosts without a variant receive no file, and every `uv run devkit sync` reports the asset with an `ASSET_UNPROJECTED` notice.
- A model or effort value pinned in the file stays in force; the project's model level policy does not reach a native variant.
- The file carries none of the swarm assignment and return contract: no absolute boundaries, no return fields, no rule against widening authority.
- Auto-invocation wording and each authority the source grants (commit, push, pull request, package install, deployment) stay active on that host. Quote each such line to the user.
- The source's license governs the copy. Keep its license notice and copyright line with the file; if the license is unknown or does not permit redistribution, stop.

## Copy and declare it

1. Copy the file byte for byte to `native/<host>/<prefix>-<role><suffix>` in the project bundle: `.toml` for `codex`, `.md` for `claude-code` and `antigravity`.
2. Save the source's license text beside it as `native/<host>/<prefix>-<role>.LICENSE`; sync deploys declared assets alone, so this file stays with the bundle source in the repository.
3. Declare the asset with `variants` and no `source`:

```toml
[[assets]]
id = "<prefix>-<role>"
kind = "subagent"
[assets.variants]
claude-code = "native/claude-code/<prefix>-<role>.md"
```

4. Record the provenance (source URL, commit, path) in the bundle's constitution entry, because the copied file itself stays unchanged.

## What sync does

- The file lands unchanged at the host's agent path: `.claude/agents/<id>.md`, `.codex/agents/<id>.toml` or `.agents/agents/<id>.md`.
- No key is added, removed or converted, and no other host receives a file.
- The agent name inside the copied file is the source's own; the asset ID names the projected file.

## When the user wants the role on every host

Convert it to a role contract instead, and keep the native variant out; one asset declares `source` or `variants`, never both.
