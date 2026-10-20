# Runtime and registration evidence

Research date: 2026-10-20. Planning evidence only; no host configuration or production runtime was changed.

## Repository observations

- `packages/devkit-dist/src/devkit/host/mcp/contracts.py`: dependency-free service dataclasses/callbacks.
- `packages/devkit-dist/src/devkit/host/mcp/server.py`: SDK and jsonschema imports, dist-owned reported version,
  form-capability check inside callback, structured JSON and stdout isolation.
- `packages/devkit-dist/src/devkit/host/mcp/services.py`: metadata entry-point discovery and duplicate rejection.
- `packages/devkit-dist/src/devkit/host/mcp/onboarding.py`: user-scoped Codex registration, explicit replace,
  shadow checks and linked-worktree runtime refusal; no project-sync reconciliation exists.
- `packages/devkit/src/devkit/integration/service.py`: integrate prepares then confirms, _run checks process-local
  authority and locks; resume does not call confirm, so a callback-only cloud guard is insufficient.
- `packages/devkit/src/devkit/integration/mcp.py`: prepare can fetch for PR route; MCP readOnlyHint alone cannot
  define the cloud read-only profile.
- `packages/devkit-spec/src/devkit_spec/handoff_mcp.py`: creates worktree after form, independently of final merge.
- `packages/devkit-dist/src/devkit/distribution/installation/extensions.py`: post-sync extensions run after successful
  asset sync and failures become notices. A runtime-only post-sync cleanup cannot run after runtime uninstall;
  plan/transaction ownership must remain in the lower installed layer.
- `scripts/dist_only.sh`, `scripts/smoke.sh`, `scripts/release.sh`, `scripts/affected_tests.py`, root/package
  pyprojects: current extras, package enumeration, imports and version expectations all need extraction coverage.

## Official platform findings

- [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli): project `.codex/config.toml`, stdio command/args/cwd,
  trusted-project loading and a separate warning that local transports may not be available in cloud.
- [Codex config precedence](https://learn.chatgpt.com/docs/config-file/config-basic): project/user/profile/CLI layers
  require effective-state inspection; a written project entry cannot prove the selected server.
- [Claude Code MCP](https://code.claude.com/docs/en/mcp): project `.mcp.json`, local > project > user same-name precedence,
  managed overrides, separate project-server/workspace trust, and interactive elicitation dialogs.
- [Codex App Server](https://learn.chatgpt.com/docs/app-server): form elicitation protocol and response actions;
  protocol documentation alone is not a live CLI UI test.
- [MCP elicitation 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation) and
  [2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation): version-specific capability
  negotiation differs. The installed supported SDK must normalize advertised form support correctly.
- [MCP roots](https://modelcontextprotocol.io/specification/2025-11-25/client/roots): roots do not replace server-side
  workspace validation. Claude's documented CLAUDE_PROJECT_DIR is also distinct from process cwd.

Inference from these sources: project configuration can be reconciled without granting trust, provided trust and
permission stores remain untouched and diagnostics do not claim connection/UI success. Neither cloud read-only
availability nor exact prompt count can be inferred universally. Codex per-field same-name merge behavior and
Claude default stdio cwd were not established; explicit roots and conflict refusal avoid depending on them.

## Verification matrix for Development

| Area | Required positive cases | Required negative/change cases |
| --- | --- | --- |
| Wheels | dist only, runtime only, agt extra, spec+runtime | absent SDK, missing service, duplicate module/file, release enumeration |
| Registration | both project formats, repeated no-op, selected agents | foreign/same-name overrides, uninstall, opt-out, modified/duplicated entries, malformed files |
| Transaction | journal recovery and exact removals | symlink, partial failure, concurrent devkit writer, changed external file |
| Runtime identity | retained venv/tool installation and explicit config checkout | editable import in deleted task, wrong clone, vanished workspace, restart authority |
| Environment | local form, cloud read-only status | stale local registration, direct launch, cloud before/after form or lock, resume after transition |
| Hosts | versioned Codex/Claude connect/discover/forms | cancellation/disconnect, missing form capability, trust/tool permission independence |

No live host trust, connection, approval UI, destructive cleanup, cloud provider or release operation was exercised
in Planning. Those remain named implementation checks, not assumptions supporting a completed implementation.
