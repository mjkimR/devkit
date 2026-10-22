---
id: SPEC-guidance-followups
title: Align milestone tone, role shell notes and traceability follow-ups
summary: States the capability's milestone granularity guidance as a recommendation, drops the stale challenger no-shell note, links the integration use case with the runtime registration capability on both sides, and names the reconcile-check envelope command in spec-sync.
status: planned
created: 2026-10-22
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-MCP-runtime-registration
related_usecases:
  - UC-drive-development-to-integration
workflow: sdd-spec-feature
---

# [SPEC-guidance-followups] Align milestone tone, role shell notes and traceability follow-ups

## 1. Problem Statement & Motivation

Four small follow-ups from `SPEC-milestone-guidance-tone` and `SPEC-superseded-reference-cleanup` stayed open because
they fell outside those units' write scopes:

- The milestone paragraph of `CAP-HARN-agent-guidance` still states granularity as "Authors SHOULD describe ..." and
  "it SHOULD NOT exist solely as a sequencing gate", while `ADR-milestone-merging` and the roadmap README state it as a
  recommendation ("Milestones are loosely managed themes. Prefer ..."). The user decided to align the capability.
- The `challenger` row of the `spec-delegate` payload reference says the role "has no shell", but the `challenger`
  contract grants a read-only shell on every host.
- Extension 7g of `UC-drive-development-to-integration` cites `CAP-MCP-runtime-registration`, but neither side lists
  the other, so `devkit spec refs` and the viewer miss the pair.
- `spec-sync` step 5 asks for a `reconcile-check` envelope without naming its command, so a low-effort implementer
  guesses a nonexistent `devkit workflow envelope reconcile-check` command.

## 2. User Stories

- **US-1**: As a user reviewing milestones, I want the capability to phrase granularity as a recommendation, so that
  it reads like the roadmap guidance and the ADR it implements.
- **US-2**: As a Host building a `challenger` payload, I want the payload reference to match the role's tool set, so
  that I do not over-supply inputs the role can read itself.
- **US-3**: As an agent changing the stale-runtime contract, I want `devkit spec refs CAP-MCP-runtime-registration` to
  list `UC-drive-development-to-integration`, so that I find the use case that restates its recovery.
- **US-4**: As an implementer at `activity-effort` low, I want `spec-sync` to point at the `reconcile-check` envelope
  command, so that I record the check without a failed guess.

## 3. Non-Goals

1. **Scope Excluded**: Any behavior, CLI, rule or role-contract change; this unit changes wording and traceability
   links only.
2. **Scope Excluded**: Other sentences of the `CAP-HARN-agent-guidance` milestone paragraph, including the `MAY`
   merge clause and the closure rules, which state requirements rather than granularity guidance.
3. **Scope Excluded**: The use case's extension text and the capability's body; only their traceability frontmatter
   changes.
4. **Scope Excluded**: Restating every `reconcile-check` flag in `spec-sync`; the `spec` skill's
   `references/envelope.md` stays the place that explains them.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The capability states milestone granularity as a recommendation
- **Given** the milestone paragraph of `CAP-HARN-agent-guidance`
- **When** `rg -n "SHOULD" docs/capabilities | rg -i milestone` runs
- **Then** no line contains `Authors SHOULD describe` or `SHOULD NOT exist solely`
- **And** the paragraph prefers a multi-unit phase, release or architectural theme advancing
  `ARCH-01-introduction-and-goals` over a milestone that only sequences one proposal, as `docs/roadmap/README.md` does

### [AC-02] The payload reference makes no stale shell claim
- **Given** the `spec-delegate` skill's `references/payload.md`
- **When** an agent reads the `challenger` and `reconcile-reviewer` rows
- **Then** neither row contains `no shell`
- **And** a bundle guidance test asserts that the reference contains no `no shell` text

### [AC-03] The integration use case and the runtime registration capability link each other
- **Given** `UC-drive-development-to-integration` and `CAP-MCP-runtime-registration`
- **When** `uv run devkit rules check` runs
- **Then** the use case lists `CAP-MCP-runtime-registration` in `capabilities`, the capability lists
  `UC-drive-development-to-integration` in `usecases`, and no `RULE-traceability-link` violation is reported

### [AC-04] spec-sync names the reconcile-check envelope command
- **Given** the `spec-sync` skill
- **When** an agent reaches step 5 (Verify)
- **Then** the step names `devkit workflow envelope new --kind reconcile-check --stage living-spec-draft` and links the
  `spec` skill's `references/envelope.md` for the remaining flags
- **And** a bundle guidance test asserts the command and the link, and the bundle budget tests pass

## 5. Assumptions

- The recommendation wording reuses the roadmap README sentence, so the capability and the guidance it governs read
  the same; the obligation is unchanged, because RFC 2119 SHOULD already meant "recommended".
- No other capability holds a SHOULD-worded milestone granularity sentence (`rg -n "SHOULD" docs | rg -i milestone`
  finds only `CAP-HARN-agent-guidance`).
- The `reconcile-reviewer` row of the payload reference makes no shell claim; it is checked and left unchanged.

## Source feedback

- `FB-capability-milestone-granularity-tone`: rewrite the capability's milestone granularity sentence as a
  recommendation (AC-01).
- `FB-payload-challenger-no-shell-note`: remove the stale no-shell note from the payload reference (AC-02).
- `FB-runtime-registration-usecase-link`: link the use case and the capability on both sides (AC-03).
- `FB-spec-sync-reconcile-check-command`: name the `reconcile-check` envelope command in `spec-sync` (AC-04).
