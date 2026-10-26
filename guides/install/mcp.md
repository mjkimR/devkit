# MCP runtime and shared services

Neither `devkit-agt` nor `devkit-spec` installs `devkit-mcp`. For the MCP services, including devkit-spec's
source-bound proposal report publication (`spec_proposal_report`), add `devkit-agt[mcp]` or install `devkit-mcp`
directly in the retained base environment. Release-wheel installs name the matching `devkit-dist`, `devkit-core`,
`devkit-cli`, `devkit-advisory` and `devkit-mcp` wheels; see the release notes. Runtime installation alone can
discover an empty service set, because the services come from the installed packages; domain services use SDK-free
contracts. Proposal acceptance, handoff and integration are CLI commands, never MCP tools.

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
trust and execution permissions are separate facts. Complete the host's own trust flow and verify tool discovery.
MCP retains shared artifact services and `spec_proposal_report`; lifecycle acceptance, handoff and integration run
through CLI commands after Host-carried conversational approval. Protocol tests do not establish actual terminal UI
support. Desktop/VS Code adapters are outside this scope.

The Host reviews committed scope and required checks, presents the exact report, target and effects, obtains the
user's conversational decision under `ask`, then invokes the corresponding CLI command. The CLI revalidates scope
and policy but does not authenticate the conversation. Workers return verified scope to the Host and never request
business approval. Trust, tool and sandbox prompts may still appear.

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

For cloud execution, run `uv run devkit sync --cloud` and use CLI inspection and artifact commands. This saves the checkout-local execution setting and records the actual render environment in the receipt. MCP service onboarding supports shared resources and report publication; lifecycle mutation still requires Host-carried authority and CLI execution.

`sync --no-save --cloud` renders cloud guidance and records its provenance without changing persisted runtime authorization. The next ordinary sync uses the saved/default environment; status/check reports the pending difference. `sync --local` restores local guidance. Locked sync refuses canonical environment changes; use ordinary sync and commit the resulting tracked output.
