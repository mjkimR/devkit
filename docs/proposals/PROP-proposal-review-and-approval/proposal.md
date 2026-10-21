---
id: PROP-proposal-review-and-approval
title: Proposal review reports and unified plan-accept MCP approval
summary: "Generate PADR-focused proposal review reports in the shared workspace and provide a native MCP plan-accept confirmation that links the report and selects accept-only or combined handoff."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-20
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-autonomous-backlog-and-orchestration
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/
    - packages/devkit-viewer/src/devkit_viewer/
    - docs/capabilities/delivery/
    - docs/capabilities/viewer/
    - docs/development/reference/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-proposal-review-and-approval] Proposal review reports and unified plan-accept MCP approval

## 1. Background & Hypothesis

Reviewing full English `proposal.md` documents and `PADR-*.md` records in detail before `plan-accept` carries high
cognitive load. In `local-orchestrated` runs where several workers finish Planning in parallel, printing long review
summaries directly in the Host chat causes earlier briefings to scroll off-screen while other units report progress.
At the same time, the current transition from Planning completion to Development can trigger up to three separate
confirmations: conversational `plan-accept`, `integration_integrate` to merge `plan-<slug>`, and `spec_handoff` to
start `dev-<slug>` (which currently embeds the entire raw `proposal.md` text inside the native confirmation message).

The hypothesis is that separating **where the human reads the design briefing** from **how the Host obtains native
approval** solves these problems together:

1. **Shared-workspace review report**: when Planning reaches `plan-accept`, the executor or Host writes a concise
   review report—focused on newly added PADRs (decision, rejected alternatives, trade-offs), surface/boundary
   impacts, and waived Challenger risks—into the shared workspace (`PROP-worker-shared-state-mcp`, local default
   `<base-checkout>/.devkit/.shared/` or configured server adapter, accessed via MCP when connected locally or via the
   equivalent CLI command in Cloud Agent / non-MCP sessions) in the configured `[presentation] language`
   (`SPEC-language-setting-coverage`, e.g., Korean) with a 7-day TTL and `source_sha` binding, keeping tracked
   repository files in English.
2. **Minimal `plan-accept` approval screen and optional MCP sandbox delegation**: the Host presents only minimal
   metadata (title, one-line summary, PADR list, recommended `dev_effort`) and a clickable link (or local
   `devkit-viewer` route) to the shared review report. When devkit MCP is connected locally, executing `plan-accept`
   merge and handoff through MCP delegates sibling worktree (`../<repo>-wt-*`) and `.git/` mutations outside the
   per-command shell sandbox (`MAT-codex-native-worker-evidence`) while using the native MCP form UI
   (`CAP-MCP-runtime-registration`); when MCP is not used, the same concise report link and approval choices work
   through the Host's native question UI and CLI fallback.
3. **Hold/defer for interactive Q&A**: if the user wants to inspect later or ask questions and request edits, choosing
   decline/cancel holds the proposal so the user can review and refine it conversationally (or in an isolated review
   session via a dedicated review skill) and regenerate the report when ready.
4. **Unified vs. split approval (`accept_and_handoff` vs. `accept_only`)**: Proposal acceptance (`accepted`) and
   Development start (`handoff`) are distinct lifecycle decisions, even though they are usually approved together.
   The native `plan-accept` confirmation form offers both choices in one screen—approving acceptance, `plan-<slug>`
   base merge, and immediate `dev-<slug>` handoff in a single step by default (`accept_and_handoff`), or recording
   `accepted` and merging `plan-<slug>` without starting Development (`accept_only`)—while retaining the standalone
   `spec_handoff` approval screen for accepted proposals started later.

## 2. Technical Spike Questions

- **Q1 — Review report schema, language and revision binding:** What exact structure should the proposal review report
  follow so that PADR decisions, considered options, consequences, boundary impacts and open/waived Challenger findings
  are immediately scannable? How does the report bind the `plan-<slug>` `source_sha` and `[presentation] language`,
  and how is regeneration triggered when the commit changes or after the 7-day TTL expires?
- **Q2 — Link presentation and `devkit-viewer` read-only viewing:** How should the Host and native MCP confirmation
  surface the shared review report link (both as a local `.devkit/.shared/` file link and through `devkit-viewer` under
  `CAP-VIEW-repository-viewer`), while preserving `ADR-read-only-local-server-over-git-refs` so the viewer remains
  strictly read-only and never inverts the client-host relationship?
- **Q3 — Native `plan-accept` MCP tool and relation to `spec_handoff`:** How should the new or extended MCP tool
  coordinate `devkit spec proposal accept <slug> --by user`, committing the decision record on `plan-<slug>`,
  integrating `plan-<slug>` into the base checkout (`devkit.integration` / `devkit.worktree`), and—when
  `accept_and_handoff` is selected—starting `dev-<slug>` and running `handoff_proposal` in one atomic user-approved
  flow? How should partial failures (e.g., base moved after acceptance, or setup failure during handoff) report
  recoverable state?
- **Q4 — Standalone `spec_handoff` message diet and interactive review skill:** When a proposal was accepted earlier
  (`accept_only` or `--direct` in Backlog) and `spec_handoff` runs later, how should `spec_handoff` replace its raw
  `proposal.md` dump with the shared review report link and concise PADR summary? How should a dedicated proposal
  review skill guide Q&A and design edits in a separate session before re-triggering approval?

## 3. Proposed Design & Impact

Planning should specify four connected deliverables across `CAP-DLV-proposal-incubation`, `CAP-HARN-agent-guidance`
and `CAP-VIEW-repository-viewer`:

1. **Proposal review report generator and MCP shared-workspace storage**:
   - Written via the shared workspace MCP interface (`PROP-worker-shared-state-mcp`) under a deterministic key per
     proposal slug, with metadata (`slug`, `source_sha`, `language`, `created_at`, `expires_at` = 7 days).
   - Summarizes each `PADR-*.md` (problem, chosen outcome, rejected options, lasting constraints), key contract or
     boundary changes, Planning effort/envelope coverage, and waived Challenger items in the user's configured
     presentation language (`ko` or `en`), without committing localized scratch files into `docs/` or `specs/`.
2. **Native MCP `plan-accept` confirmation (`spec_plan_accept` / extended handoff service)**:
   - Displays concise metadata plus the shared review report link (and optional `devkit-viewer` URL) instead of
     inlining the full `proposal.md` body.
   - Schema fields:
     - `mode`: `"accept_and_handoff"` (default: records `plan-accept`, merges `plan-<slug>` into base, cleans up the
       Planning worktree, creates `dev-<slug>` and runs handoff) or `"accept_only"` (records `plan-accept`, merges
       `plan-<slug>` into base and cleans up the Planning worktree, leaving `PROP-<slug>` accepted on the base).
     - `activity_effort`: `"low" | "medium" | "high"` (defaulted from `dev_effort`; used when `mode` is
       `"accept_and_handoff"`).
   - Declining or cancelling the form leaves `plan-<slug>` unaccepted (hold/defer) so the user can inspect the report
     later or open an interactive review turn.
3. **Refined standalone Development approval (`spec_handoff`)**:
   - Retained for proposals that are already `accepted` on the base branch (via `accept_only` or Backlog `--direct`).
   - Uses the same concise summary + shared review report link format (generating or refreshing the shared report on
     demand if its 7-day TTL expired) rather than dumping the raw `proposal.md` text.
4. **Interactive proposal review guidance / skill**:
   - Enables reviewing a proposal in a dedicated agent session (or after holding the MCP dialog), answering user
     questions against `proposal.md` and `PADR-*.md`, folding requested changes into the Planning branch, refreshing
     the shared review report for the new `HEAD`, and re-invoking the native approval screen.

Acceptance evidence for the selected design should include:

- Completing a Planning turn writes the PADR-focused review report to the shared workspace (`.devkit/.shared/` locally)
  bound to `plan-<slug>`'s `HEAD` SHA and the configured presentation language, leaving `git status --porcelain` clean.
- The native `plan-accept` MCP confirmation presents the concise summary and report link; selecting `accept_only`
  records `gate:plan-accept`, merges `plan-<slug>` into the base checkout and stops without creating `dev-<slug>`.
- Selecting `accept_and_handoff` completes acceptance, `plan-<slug>` merge, `dev-<slug>` worktree creation and
  proposal handoff in a single confirmation without prompting a second MCP dialog.
- Declining or cancelling the confirmation makes no acceptance, merge or handoff mutations.
- Running `spec_handoff` on a previously `accepted` proposal whose shared report expired regenerates or links the
  concise report and requires explicit Development approval.

Non-goals: adding write, chat or LLM API endpoints to `devkit-viewer`, committing translated review reports into
tracked repository paths, or removing the separate Development approval screen (`spec_handoff`) for proposals accepted
with `accept_only` or `--direct`.

## 4. Lifecycle & Retirement Criteria

Depends on `SPEC-standalone-devkit-mcp` (MCP runtime), `PROP-worker-shared-state-mcp` (shared workspace adapter and
7-day TTL storage) and `SPEC-language-setting-coverage` (presentation language resolution). Medium Planning should
settle the exact MCP tool names, form schema, report template and partial-failure recovery semantics before handoff.
