# Language coverage evidence

Research date: 2026-10-20. This material distinguishes payload contracts, current source inspection and visible UI
observations. The Scout returned completed with gaps, without changing files/index/HEAD or running native sessions.
No live approval fixture was launched. All proposed behavior is pending Development.

## Internal ownership evidence

| Location | Observed behavior | Design consequence |
| --- | --- | --- |
| `packages/devkit-dist/src/devkit/host/mcp/server.py:42-53` | Checks form capability, forwards message/schema to elicit_form | Transport need not translate domain strings. |
| `packages/devkit-dist/src/devkit/host/mcp/contracts.py:20-33` | SDK-free confirmation callback and service invocation | Keep preference resolution SDK-free and domain rendering separate. |
| `packages/devkit/src/devkit/integration/models.py:168-255` | Local/PR/cleanup conditional English messages, exact quoted scope | Translate all owned branches; preserve interpolation, escape and evidence limits. |
| `packages/devkit/src/devkit/integration/service.py:196-231` | Boolean approve false; only accept plus true proceeds | Schema/authorization values must stay exact. |
| `packages/devkit-spec/src/devkit_spec/handoff_mcp.py:36-60` | Full plan, setup and effort disclosures | Embedded plan remains verbatim; owned explanation gets static translation. |
| `packages/devkit-spec/src/devkit_spec/handoff_mcp.py:128-157` | Boolean approval and canonical effort enum | Localized message legend works without new enum metadata. |
| `packages/devkit-catalog/src/devkit_catalog/response_style/bundle/bundle.toml:6-8` | String language defaults auto | Preserve explicit override; inherit shared preference only when absent. |
| `packages/devkit-dist/src/devkit/distribution/bundles/templates.py:16-86` | Explicit type/default declarations, vars-only sandbox | Add one whitelisted default source; do not expose raw config/context. |

The accepted proposal now carried by `SPEC-local-config-execution-environment` defines shared/effective readers,
local allowlist, canonical receipts and eligible local rendering. `PROP-standalone-devkit-mcp` is accepted and
selects separate owning config workspace and retained executor. Neither implementation is assumed present here.
No active spec appeared in this worktree's spec listing (its recorded specs have completed status); concurrently
running sibling Development was deliberately not inspected.

## Official external evidence

| Surface | Evidence level and result | Limitation |
| --- | --- | --- |
| MCP message and schema | [Elicitation specification, revision 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation), User Interaction Model, Elicitation Requests, Requested Schema: server message, string/boolean title and description; titled enum const/title data | Protocol does not prescribe the UI or prove field display. This is the newest revision encountered, not an exhaustive release audit or the negotiated devkit runtime revision. |
| Codex message/field metadata | [Codex raw source](https://raw.githubusercontent.com/openai/codex/refs/heads/main/codex-rs/tui/src/bottom_pane/mcp_server_elicitation.rs), parse_field lines 529-608, parse_single_select_field 611-673, current_prompt_text 912 onward: message becomes prompt, field title label, description prompt, enumNames and const/title map labels separately from values | Moving main, not a pinned release. Raw and GitHub HTML crawled snapshots differed; line numbers refer to the raw view fetched by Scout. |
| Codex host-owned strings | Same source: boolean labels around 553, footer_tips 941-968 and submit_answers 1104 | Boolean True/False, footer instructions and required-field errors belong to Codex, not the supplied title/message. |
| Claude Code form dialogs | [Official MCP documentation](https://code.claude.com/docs/en/mcp#respond-to-mcp-elicitation-requests), Respond to MCP elicitation requests: native server-defined forms and form/url modes | No documented field-by-field display guarantee or Korean rendering observation. |
| Response instructions | [Official agent instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and [Claude settings](https://code.claude.com/docs/en/settings) | Assistant instruction/setting mechanisms do not establish native form language. Claude settings-reference page exceeded fetch size; no language-propagation contract was confirmed. |

The source findings justify a bounded supplied-content design; they do not justify promising translated host
widgets, native validation, permission prompts, or identical metadata rendering across versions. The recommendation
therefore keeps an explanatory message and existing simple schemas, without adopting newer titled-enum features.

## Local and prior native evidence

Read-only symlink inspection identified Codex `0.163.0` at
`~/.codex/packages/standalone/releases/0.163.0-aarch64-apple-darwin` and Claude `2.1.304` at
`~/.local/share/claude/versions/2.1.304`. These identify installed release paths, not executed-version output.
No interactive CLI, trust/config writer or business tool was run.

`MAT-claude-terminal-mcp-approval-evidence` records English native approval outcomes on Claude Code 2.1.303:
false submission, decline, cancel and true approval. It did not inspect translated titles/descriptions, Korean
messages or host-native language controls. It therefore proves none of this proposal's localized visible coverage.

| Claim | Current status | Development evidence |
| --- | --- | --- |
| Static en/ko copy and canonical values | Proposed, not implemented | Domain parity/escaping/schema tests and bilingual semantic review. |
| UTF-8 through SDK/stdio | Existing forwarding code; localized fixture not run | Pinned installed SDK/protocol fixture. |
| Codex localized message and metadata display | Unverified for installed 0.163.0 | Harmless terminal fixture with captured visible fields and exact versions. |
| Claude localized message and metadata display | Unverified for installed 2.1.304 | Same fixture and explicit omitted/transformed field record. |
| Fully localized host screen | Out of scope; not established | No promise; host owns its controls. |

A harmless fixture must have only a response-recording handler, with no domain integration/handoff callbacks.
Use disposable eligible configuration only under granted boundaries; otherwise report the gap. Do not edit actual
host trust/config or run a business mutation to establish presentation. Record SDK/protocol and client versions
separately. Source inspection and mocks cannot be promoted to live UI evidence.

## Alternatives and recommendation

A conversation-specific response-style variable is a poor owner for runtime approvals. A shared presentation
preference with one opt-in manifest default source is the narrow extension: core owns values/provenance, catalog
opts in, and domains own static copy. A general template config namespace or arbitrary registry is unnecessary.
The default_from whitelist preserves the existing vars-only template contract; the explicit consumer value still
wins after shared/local per-key merge. More language packs, aliases, automatic detection and host-level UI language
control have no evidence-backed need in this proposal.

## Verification gaps

No immutable Codex source commit was obtained: Scout's shell GitHub API lookup encountered DNS failure; web
retrieval returned moving source. Claude exact per-field behavior and native language preferences remain
unverified. These gaps do not alter the conservative supplied-content boundary. Development must retain per-host
unverified status until actual harmless rendering evidence is collected; unavailable evidence does not silently
waive a support claim. No native UI was observed in this Planning run.
