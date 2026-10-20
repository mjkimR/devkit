---
id: PROP-integration-host-confirmation
title: Integration onboarding and diagnostics for Codex CLI and Claude Code
summary: "Evaluate remaining integration onboarding and registration-diagnostic gaps for Codex CLI and the Claude Code terminal CLI, whose native form approval paths are already supported. Keep other host surfaces outside scope."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-multi-host-native-integration
boundaries:
  owns:
    - packages/devkit-dist/src/devkit/host/
    - docs/capabilities/host/
    - docs/capabilities/integration/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---


# [PROP-integration-host-confirmation] Integration onboarding and diagnostics for Codex CLI and Claude Code

- **Source feedback**: `FB-multi-host-integration-ergonomics`.
- **Related**: `CAP-INT-mcp-services`, `CAP-HOST-lifecycle-observation`, `ADR-integration-approval-asserted`,
  `SPEC-claude-terminal-mcp-approval`.

## 1. Background & Hypothesis

The supported interactive native form-approval paths already include Codex CLI and the Claude Code terminal CLI.
`SPEC-claude-terminal-mcp-approval` verified and documented the Claude terminal path without changing the server.
The server checks advertised form capability rather than a host-name allowlist. This proposal does not need to add
another approval surface for either CLI.

Codex registration and inspection are available through `devkit host mcp setup/status --host codex`. Claude Code
uses its own `claude mcp add/get/remove` commands with the retained runtime/base printed by devkit configuration;
there is no devkit Claude setup/status adapter. Registration diagnostics do not prove discovery, visible approval
or permission-prompt behavior. A missing projected server is different from a client lacking form capability.

Only Codex CLI and the Claude Code terminal CLI are relevant to this personal repository. The hypothesis to test
is whether their actual setup and diagnostic differences justify a small adapter or clearer guidance. Keeping the
existing manual Claude route is a valid outcome if it meets the observed need.

## 2. Technical Spike Questions

- **Q1 — Actual friction:** Which concrete registration, stale-runtime, reconnect or tool-discovery problems remain
  in the two CLI workflows? Compare current documented commands with an actual local setup before proposing code.
- **Q2 — Minimal solution:** Do existing Claude commands and onboarding guidance suffice, or would a bounded
  `devkit host mcp setup/status --host claude` adapter remove repeated work? Define idempotence, explicit replacement,
  retained-runtime checks and failure behavior without treating registration as successful native confirmation.
- **Q3 — Evidence and routing:** Which CLI versions and interactive permission modes have verified visible form
  acceptance, rejection and cancellation? Record unknowns explicitly and retain conversational CLI fallback when
  the running client cannot show the form. Add mode-specific experiments only for actual usage, not a host matrix.

## 3. Proposed Design & Impact

No adapter or new command is selected. Planning first compares no change, concise onboarding corrections and a
Claude registration/inspection adapter. Keep the existing server, request binding, user-only affirmative approval
and authorization boundary. Configuration changes remain explicit; no automatic host settings or blanket grants.

Expected impact is limited to host onboarding/diagnostics and their documentation. Identify concrete tests and
additional paths before Development. Any needed integration routing change must be justified by an observed
failure in one of the two supported CLIs, not by hypothetical support for another surface.

Verification should show matching registration is unchanged, replacement requires explicit intent, worktree or
stale runtime references are reported accurately, and registration success is distinguished from tool discovery
and visible user approval. A native decline/cancel must perform no integration mutation. Reuse existing evidence
where applicable and state what has not been exercised.

Non-goals: Claude Desktop, VS Code extensions, Agent SDK, Antigravity, OpenCode or other hosts; a new approval
protocol; agent self-approval; new integration execution behavior; and automatic configuration changes.

## 4. Lifecycle & Retirement Criteria

This remains a draft. Review concrete CLI friction before deciding whether implementation is needed. Close with
rationale if existing commands and guidance suffice; otherwise settle the minimum scope and verification at
Planning before acceptance. Historical research materials remain unchanged and do not expand this proposal's scope.
