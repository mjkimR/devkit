---
id: ADR-terminal-statuses-are-historical
title: Terminal statuses are historical in document browsing
summary: "For browsing crowded by settled items, we treat terminal feedback, decision and proposal statuses as historical in list and search, shown with --history or a matching --status and counted as hidden=, to keep default pages current, accepting a status default the earlier non-goal refused."
status: accepted
created_at: 2026-10-26
---

# [ADR-terminal-statuses-are-historical] Terminal statuses are historical in document browsing

- **Status**: Accepted
- **Date**: 2026-10-26
- **Deciders**: user
- **Involved Components/Capabilities**: `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`,
  `CAP-DOCS-document-search`

---

## 1. Context & Problem Statement

`devkit spec list` and `devkit spec search` hide historical documents unless `--history` is passed: the files of
completed spec bundles and done or dropped milestones (`CAP-DOCS-document-model`). Feedback, decisions and proposals
have terminal statuses too (feedback `resolved`, `promoted`, `dismissed`, `forwarded`; decision `superseded`;
proposal `rejected`), but stayed current. In this repository the default `list feedback` page held 170 items of
which 10 were open, and `list decision` 53 ADRs of which 7 were superseded, so settled items crowd the current ones
out of the page and the agent's context.

Non-Goal 1 of `SPEC-feedback-list-filters`, mirrored in a scope note of `CAP-DOCS-document-lookup`, refused a
feedback status default: a default for one kind would make `list feedback` and `list feedback spec` select
differently, and items hidden without a trace would drop out of the delivery report and the hygiene pass.

## 2. Decision Drivers

- Default pages show what is current, at the smallest context cost.
- One selection rule whatever kinds are named.
- Nothing disappears without a trace in the output.
- Settled items stay one flag away; IDs stay resolvable.

## 3. Considered Options

### Option 1: Terminal statuses are historical, with a hidden count (Selected)
- **Overview**: a per-kind table of terminal statuses joins the historical rule for browsing and search; `--history`
  or a `--status` naming the status shows them; `list` prints `hidden=<n>` and a `[HISTORY_CMD: ...]` hint.
- **Pros**: the same rule for every kind selection, as completed bundles already follow; the count answers the
  trace concern; explicit `--status` filters keep working.
- **Cons**: a default selection exists that the earlier non-goal refused; callers that need settled items must pass
  `--history`.

### Option 2: Keep explicit filters only (current state)
- **Overview**: callers pass `--status open` where they want current feedback.
- **Pros**: no hidden selection.
- **Cons**: every default page carries settled history; decisions and proposals have no equivalent one-value filter.

### Option 3: A feedback-only default status
- **Overview**: `list feedback` shows `open` unless asked.
- **Pros**: smallest change for feedback.
- **Cons**: the inconsistency the earlier non-goal named: `list feedback` and `list feedback spec` select
  differently.

## 4. Decision Outcome

We decided to adopt **Option 1**.

- Feedback `resolved`, `promoted`, `dismissed` and `forwarded`, decision `superseded` and proposal `rejected`
  (case-insensitive) are historical for browsing and search, whatever bundle holds them.
- A given `--status` replaces the default hiding, so a named status is never empty only through history.
- `list` reports `hidden=<n>` on its page line and in JSON, and `[HISTORY_CMD: ...]` when n is above zero.
- The rules keep checking terminal-status documents on every run; only browsing and search hide them.

**Rationale**: the uniform rule answers the selection-consistency driver, the hidden count the trace driver, and the
`--status` override keeps settled items one flag away. This reverses Non-Goal 1 of `SPEC-feedback-list-filters`.

---

## 5. Consequences

- **Positive**: default `list feedback` shows the open items only; `list decision` the ADRs in effect.
- **Negative / Risks**: a caller that needs settled items and omits `--history` sees fewer documents; the hidden
  count and hint make this visible.
- **Follow-ups**: a kind whose settled items crowd its listing joins the table through a new decision.

---

## 6. Confirmation

`packages/devkit-spec/tests/integration/features/documents/test_terminal_history.py`.
