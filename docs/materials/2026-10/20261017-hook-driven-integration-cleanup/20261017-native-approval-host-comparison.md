---
id: MAT-native-approval-host-comparison
title: Native integration approval through CLI hooks and MCP
summary: "Research comparing Claude Code and Codex hook-driven confirmation, MCP elicitation, related upstream issues, and the current devkit integration boundary."
created_at: 2026-10-17
---

# [MAT-native-approval-host-comparison] Native integration approval through CLI hooks and MCP

Research snapshot checked on 2026-10-17. This material preserves source evidence and implementation observations;
it does not introduce a new approval policy or claim that every host has been tested interactively.

Related contracts: `CAP-INT-mcp-services`, `CAP-GATE-commit-gates`, `CAP-DLV-delivery-workflows`.
Follow-up: `FB-multi-host-integration-ergonomics`.

## 1. Findings

MCP is not required to execute a local merge. The current devkit CLI supports integration after conversational
approval with `devkit worktree finish <branch> --merge --local-only`. Its built-in native confirmation path uses
an MCP tool and form elicitation. This is an implementation choice for the supported path, not a universal rule
that native approval interfaces require MCP.

| Surface | Native confirmation mechanism | Scope and limits |
| --- | --- | --- |
| Claude Code interactive hook | `PreToolUse` can return `permissionDecision: "ask"` | Requests confirmation of a tool call without an MCP server. This capability alone does not implement devkit's exact-request approval binding. |
| Codex `PreToolUse` hook | `permissionDecision: "ask"` is documented as unsupported | A hook cannot use this value to force native confirmation of an otherwise permitted call. |
| Codex `PermissionRequest` hook | Handles an approval request already raised by Codex | Can allow, deny, or leave the existing approval flow to the host; it does not independently create a business approval request. |
| MCP form elicitation | A server requests input; the host renders a form and returns the response | Available only through a connected MCP server and a client that implements the requested interaction. UI behavior depends on the client surface and version. |
| Plain devkit CLI | Executes the guarded local integration command | Current fallback obtains conversational approval first; it does not request a Codex-native form itself. |

The Claude hook behavior is specified in the [Claude Code hooks reference](https://code.claude.com/docs/en/hooks#pretooluse-decision-control).
The Codex distinction is specified in the [Codex hooks reference](https://developers.openai.com/codex/hooks/).
Claude Code also documents [interactive MCP elicitation](https://code.claude.com/docs/en/mcp#respond-to-mcp-elicitation-requests).
These documented capabilities are separate from an end-to-end devkit adapter validation.

## 2. Current devkit implementation

The retained devkit MCP server exposes four integration tools:

- `integration_prepare`: inspect readiness and the proposed integration scope.
- `integration_integrate`: prepare, request native approval, then execute the approved scope in the same call.
- `integration_status`: inspect retained request state.
- `integration_resume`: resume eligible work from a retained request.

The transport sends a form elicitation request through the MCP SDK. The client renders the interface; the MCP
server does not draw it. Native `action=accept` together with `approve=true` grants authority for the prepared
request, including source and target commit IDs and cleanup scope. A caller-supplied approval argument cannot
replace that response. Request validation and execution are owned by integration, while the host layer owns
transport and confirmation adaptation.

Implementation entry points:

- `packages/devkit/src/devkit/host/mcp/server.py`: client form-capability check and `elicit_form` call.
- `packages/devkit/src/devkit/host/mcp/services.py`: installed service discovery.
- `packages/devkit/src/devkit/integration/`: request preparation, confirmation binding and execution.
- `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-integrate/SKILL.md`: MCP-first routing and CLI fallback.

Git commit hooks (`pre-commit`, `commit-msg`) run commit checks. They are distinct from host lifecycle hooks and
MCP business confirmation. A successful commit-hook status does not establish an active approval UI connection.

The current supported interactive path targets Codex. The protocol adapter checks client capabilities rather
than establishing general Claude Code support. A Claude-specific hook route remains a candidate for
`FB-multi-host-integration-ergonomics`; no adapter or policy change is adopted by this research.

## 3. Upstream issue and patch status

Statuses below were checked on 2026-10-17 and are historical observations, not continuing status guarantees.

| Project | Issue or patch | Checked state | Relevance |
| --- | --- | --- | --- |
| Codex | [#28437: Support PreToolUse permissionDecision: ask for native approval prompts](https://github.com/openai/codex/issues/28437) | Open | Direct feature request for a hook to route a specific call into native human approval. |
| Codex | [PR #20702: Support PreToolUse permissionDecision ask](https://github.com/openai/codex/pull/20702) | Closed, not merged; closed 2026-05-20 | Implementation attempt for that feature. The issue describes inactivity as the closure reason, rather than feature rejection. |
| Codex | [#15311: Add blocking PermissionRequest hook for external approval UIs](https://github.com/openai/codex/issues/15311) | Closed as completed | Implemented through PR #17563. It handles existing permission requests and does not supply the missing PreToolUse ask behavior. |
| Codex | [#23465: Expose effective approval reviewer to PermissionRequest hooks or support explicit defer](https://github.com/openai/codex/issues/23465) | Open in the inspected issue page | Related routing request: distinguish direct user approval from auto-review and avoid duplicate approval interfaces. |
| Claude Code | [#89858: MCP elicitation declined without drawing a prompt](https://github.com/anthropics/claude-code/issues/89858) | Open | Reports Desktop/SDK-controlled sessions returning decline without a visible form; the same server works in the terminal in reported reproductions. |
| Claude Code | [#41292: VS Code extension silently declines MCP elicitation](https://github.com/anthropics/claude-code/issues/41292) | Bug report inspected; closure status not independently checked | Related extension-specific report of a missing elicitation UI handler. |

The Claude issues are reported failure cases, not proof that all versions or all clients fail. They also do not
invalidate the separate documented interactive hook `ask` capability. Neither a closed patch nor a capability
advertisement demonstrates a working approval interface in the installed host.

## 4. Observed local connection state

The inspection after `SPEC-hygiene-reliability` integration established:

| Check | Observation | What it establishes |
| --- | --- | --- |
| `codex mcp get devkit --json` | No MCP server named devkit | No devkit registration was found in the effective CLI configuration. |
| Current agent tool catalog | No `integration_*` tools | This session had no callable devkit integration MCP tools. |
| `devkit.host.mcp.services.load_tools` in the retained runtime | All four integration tools loaded | Local service definitions were available; this is not a transport handshake or UI test. |
| Installed MCP SDK | Version 1.30.0 | The dependency was installed in the inspected runtime. |
| `devkit host status --format json` | Empty host hook list, no inspection errors | No devkit host-hook registrations were reported; an empty list is not proof of active hooks. |
| `devkit gate status --format json` | Managed pre-commit and commit-msg hooks with valid interpreters | Git commit hooks were present independently of MCP registration. |

That integration used conversational approval followed by the local-only CLI fallback. No native MCP approval
form was requested in that execution. The missing registration explains the absence of that path; it does not
establish whether the current UI would support elicitation after connection.

The earlier [Codex native integration confirmation spike](codex-spike-evidence.md) records a different interactive
session with an explicitly connected prototype server. Its UI observations do not establish this session's
connection state or full production integration behavior.

## 5. Connection and validation sequence for follow-up work

Codex [MCP configuration documentation](https://developers.openai.com/codex/mcp/) describes server registration
through `codex mcp add` or configuration. devkit can print the retained-runtime command with
`devkit host mcp config --format json`. Registration and inspection alone do not prove connection or visible UI.

A host-adapter investigation should establish these facts separately:

1. The retained runtime loads the installed integration services.
2. The host registers and connects to the server, and exposes the expected tools in the active session.
3. The client advertises form elicitation and actually displays the requested form.
4. Accept-with-approval, accept-without-approval, decline and cancellation produce distinct observed outcomes.
5. Approval binds the source and target commits and cleanup scope; changed input invalidates the request.
6. The verified scope executes once, and cleanup/resume preserves partial progress.

For a Claude hook alternative, separately verify how the user decision reaches the executor and remains bound to
one prepared integration request. A native tool permission dialog is not automatically an implementation of that
contract. The remaining evaluation is tracked by `FB-multi-host-integration-ergonomics`.

No server registration, host configuration change, Git mutation or upstream issue submission was performed
as part of this research capture.
