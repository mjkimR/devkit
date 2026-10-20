---
id: MAT-language-development-evidence
title: Language content Development evidence
summary: "Separates tested bilingual domain/SDK content from unobserved Codex and Claude terminal form rendering."
created_at: 2026-10-20
---

# [MAT-language-development-evidence] Language content Development evidence

## Runtime versions

The assigned worktree reports devkit-dist 0.1.1, devkit-agt 0.1.1, devkit-spec 0.1.0 and devkit-mcp 0.1.1.
Python MCP SDK is 1.30.0 and its latest protocol constant is 2025-11-25. The fixture uses the SDK's normal
initialize exchange, not a host-specific protocol adapter. Installed version commands report Codex CLI 0.163.0
and Claude Code 2.1.304. Codex's version command warned that PATH aliases could not be created in the sandbox;
the version still returned exit 0. No alias, trust or user configuration was changed by this worker.

## Evidence boundary

Domain fixtures cover local merge, fast-forward, already-merged cleanup, pull-request creation/reuse/cleanup,
optional removal/branch deletion, absent markers, summary escaping/truncation and handoff setup/effort semantics.
SDK stdio fixtures request English and Korean messages with identical canonical properties, boolean defaults and
effort enums. They observe received UTF-8 messages/schema and returned replies; they do not observe a host screen.
The domain tests use disposable pytest repositories, and synthetic handoff outcome fixtures execute no business
operation. Real SDK integration fixtures operate only on their disposable repositories.

| Host | Installed version | Localized visible form | Message/title/description/enum display | Buttons, validation, permission prompts |
| --- | --- | --- | --- | --- |
| Codex terminal CLI | 0.163.0 | Unverified | Unverified | Client-owned; unverified |
| Claude Code terminal CLI | 2.1.304 | Unverified | Unverified | Client-owned; unverified |

No live native fixture was launched: this worker has no observed native form surface for either terminal host.
It did not connect a fixture through real host configuration, request trust changes, or run actual handoff/merge
operations for UI evidence. Therefore no assertion is made about omitted/transformed metadata, boolean widgets,
buttons, host headings, validation text or permission prompts. Existing English Claude approval evidence does not
establish Korean rendering. A future harmless data-returning native fixture may close this explicit evidence gap;
that gap does not weaken tested supplied-content or authorization contracts.
