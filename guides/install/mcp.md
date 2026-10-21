# Optional MCP runtime and native approval

Install `devkit-mcp` intentionally in the retained base environment, or select `devkit-agt[mcp]` on an existing
harness requirement. Source installations must name the source for the optional wheel too; release-wheel installs
use the matching dist/advisory/runtime release assets. Runtime installation alone can discover an empty service
set. Install agt for integration and spec for handoff; domain packages do not need the SDK to import.

Run `devkit sync` in the owning checkout. Selected Codex CLI, Claude Code and Antigravity project entries are reconciled under
`.codex/config.toml`, `.mcp.json` and `.agents/mcp_config.json`; `[mcp] register = false` opts out. `devkit mcp status --descriptor --format json` inspects
the retained launch descriptor, and `devkit mcp setup --executable /retained/bin/python` explicitly selects a
verified runtime. It must remain installed after task cleanup, including any editable source locations.

Tracked host settings and visible foreign untracked files are never changed. Generated paths use existing ignores
or narrowly scoped clone-local Git exclusions after checking all worktrees. Edited, unowned identical and conflicting
entries are not adopted. Resolve reported same-name user/ancestor/local/managed registrations with host tools;
devkit never mutates global settings, trust or permission policy. `devkit mcp remove` retires exact owned project
entries; exclusions remain until manually reviewed across every linked worktree.

Reconnect the terminal host and inspect `devkit mcp status --format json`. Registration, connection, discovery,
native form support, trust and execution permissions are separate facts. Complete the host's own trust flow and
verify tool discovery, decline/cancel and approved effects separately; record host versions with UI evidence.
Protocol tests do not establish actual terminal UI support. Desktop/VS Code adapters are outside this scope.

The Host reviews committed scope and required checks, then calls `integration_integrate` or `spec_handoff` for
one native business approval. It needs no extra chat approval or integration prepare call. Workers return verified
scope to the Host and never request business approval. Trust, tool and sandbox prompts may still appear.

Cloud exposes only declared read-only tools and refuses interactive/preflight/resume execution even through stale
registrations. Its transport connectivity is separately host-dependent. Missing runtime, disconnected server,
unavailable forms or unsupported cloud transport requires intentional installation/connection or an independently
authorized CLI/PR route. Missing UI never supplies authority; existing authorization applies only to its exact scope.

## Supplied approval language

Set `[presentation] language = "ko"` in shared `.devkit/config.toml` or ignored `.devkit/config.local.toml` for Korean
devkit-owned integration and handoff copy. `en` selects English; `auto` uses English in forms and follows the request
in response-style. Unsupported strings fall back to English with provenance in `devkit config show --effective`.
Run sync to update inherited response-style assets; explicit bundle variables continue to win. Native forms reread
the preference per request from the owning checkout. Host buttons, validation/trust/permission prompts and omitted
metadata remain client-owned. Visible localized forms on both terminal hosts remain unverified; see
`CAP-INT-mcp-services` and `MAT-language-development-evidence`.

## Cloud setup

For cloud execution, run `uv run devkit sync --cloud` and use CLI inspection and artifact commands. This saves the checkout-local execution setting and records the actual render environment in the receipt. Optional native-service onboarding is for local execution only; skip it in cloud setup. Cloud mutation still requires a separately authorized CLI/PR route.

`sync --no-save --cloud` renders cloud guidance and records its provenance without changing persisted runtime authorization. The next ordinary sync uses the saved/default environment; status/check reports the pending difference. `sync --local` restores local guidance. Locked sync refuses canonical environment changes; use ordinary sync and commit the resulting tracked output.
