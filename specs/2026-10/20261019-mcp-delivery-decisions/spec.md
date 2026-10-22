---
id: SPEC-mcp-delivery-decisions
title: MCP delivery decisions
summary: "User-facing Planning to Development handoff with effort selection and understandable local integration confirmation."
status: completed
created: 2026-10-19
related_capabilities: [CAP-INT-mcp-services]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-mcp-delivery-decisions] MCP delivery decisions

## Problem and intent

People starting Development need the accepted plan's summary, the next action and an editable effort recommendation. People approving local integration need a readable explanation of completed work before exact Git and cleanup scope.

The user authorized implementing the discussed handoff and inspecting/improving main-branch merge approval. Work is feature, spec depth, direct mode, medium effort. AutoHub and native MCP are alternative hosts of the same user intervention. This change implements only the local devkit MCP path.

## Non-Goals

No change to required gates, provider verification, local integration authority, remote merge policy, model reasoning settings or the read-only viewer. No production deployment or main-branch merge is authorized by implementation approval.

## Acceptance Criteria

### [AC-01] Review an activity before starting
- **Given** a proposal on a selected base branch
- **When** the user reviews the Planning-to-Development handoff through devkit MCP
- **Then** the review presents its title, summary, plan details, next action, immutable base SHA and activity-specific effort hint, falling back to medium.

### [AC-02] Confirm effort and prevent stale starts
- **Given** an activity review
- **When** the user starts with a chosen effort
- **Then** the choice is returned as Development run input, a changed base refuses the handoff before creating a worktree, and an existing Development branch is refused rather than started twice.

### [AC-03] Native MCP handoff confirmation
- **Given** an accepted proposal and an MCP client supporting form elicitation
- **When** the handoff tool is invoked
- **Then** the native form displays the review and an editable effort defaulted to its hint; only affirmative approval starts Development, and decline, cancel, unavailable confirmation or invalid input starts nothing.

### [AC-04] Understand local merge approval
- **Given** a prepared local integration request
- **When** confirmation is displayed
- **Then** task title and summary from committed provider evidence precede source/target branches and exact cleanup scope; full SHAs remain visible, untrusted text is escaped, and existing authority/stale-scope checks remain enforced.
