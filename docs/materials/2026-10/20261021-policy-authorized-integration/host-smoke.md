# Implemented auto integration host smoke

AC-06 was exercised on 2026-10-21 in two ignored disposable repositories, with the changed IntegrationService and real SDK stdio server. Both used a deterministic fixture readiness provider, not fabricated merge effects; source/readiness semantics are covered by package tests separately. No test changed real repository policy or global host settings.

| Host | Version | Permission configuration | Result |
| --- | --- | --- | --- |
| Codex CLI | 0.163.0 | Invocation-only MCP enabled_tools=[integration_integrate], tools.integration_integrate.approval_mode=approve; ephemeral session | completed, authority=policy; one integration tool call, no ui_action, no devkit elicitation |
| Claude Code | 2.1.305 | strict task MCP configuration and --allowedTools mcp__policy_smoke__integration_integrate; no-session-persistence | completed, authority=policy; reported one integration tool call, permission_denials=[], no confirmation prompt |

Codex structured tool output records merge, worktree_remove, branch_delete and post_finish completed, marker_clear skipped, errors/notices empty, network_operations=excluded. Claude's terminal result reports the same effects and no permission denial. Independent Git/filesystem inspection confirmed both effects below. The smoke repositories had no remotes; local execution made no remote effect. SDK regression additionally connects without elicitation capability and verifies actual merge/cleanup.

| Host | Result SHA | First parent | Source parent | Task worktree | Task branch | Remotes |
| --- | --- | --- | --- | --- | --- | --- |
| codex | eb9b1c591b45310998d2fdc8b824471f3052e97f | 05c48a1ae76201bc174eaad632741f2c2d17d041 | c571474ca14869ac9e7a95996fc5c38838b6ebbe | absent | absent | none |
| claude | 633627828e0aed172fd5b1043813121033cb7aae | 05c48a1ae76201bc174eaad632741f2c2d17d041 | c571474ca14869ac9e7a95996fc5c38838b6ebbe | absent | absent | none |

These results establish unattended execution for the explicitly granted invocation settings above, not all host installations or permission modes. Host tool authorization and server filesystem access remain prerequisites. Raw session logs are temporary and are not retained because they contain local paths and session metadata.

Configuration reference: [official Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) documents invocation configuration equivalents for tool allow lists and per-tool approval mode. Existing host protections were not disabled.
