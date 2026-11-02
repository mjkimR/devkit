---
id: SPEC-adr-normative-outcomes
title: ADR normative outcomes and Living Spec restatement
summary: Decision Outcomes list clauses with RFC 2119 keywords and the target document ID; restate the ADR-only clauses of 13 accepted ADRs in capability/architecture documents and fix the snapshot-gate contradiction in CAP-GOV-rule-authoring.
status: planned
created: 2026-11-02
related_capabilities: [CAP-HARN-agent-guidance, CAP-GOV-rule-authoring]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adr-normative-outcomes] ADR normative outcomes and Living Spec restatement

## 1. Problem Statement & Motivation

Capabilities and architecture documents are the normative source of truth, and their writing instructions require
RFC 2119 keywords. Spec planning and review also check designs against accepted ADRs. The ADRs, however, do not say
which of their clauses are normative or where each clause is restated.

An audit of the 97 accepted ADRs in `docs/decisions/2026-10/` (2026-11-02) found three problems:

- **Clauses left only in ADRs.** 83 ADRs are fully restated in a contract location and 1 sets no lasting policy. The
  other 13 keep at least one lasting clause only in the ADR (§5).
- **Unmarked strength.** 91 of the ADRs use no RFC 2119 keyword, so a reviewer cannot tell whether a restatement kept
  the intended strength.
- **One contradiction.** `CAP-GOV-rule-authoring` §Optional `inputs` says the Git snapshot gates always evaluate a
  rule that declares `inputs`. `CAP-GOV-evaluation-lifecycle` (run step 3) and
  `ADR-scope-snapshot-runs-to-diff-paths-including-deletions` say instead that snapshot runs are scoped to the diff
  candidate paths.

The completion guidance adds to the first problem. It classifies "decisions and lasting policy → ADRs", so new lasting
policy keeps landing only in ADRs.

## 2. User Stories

- **US-1**: As an agent planning or reviewing a change, I want every lasting rule stated with its strength in a
  capability or architecture document, so that I check one normative source instead of interpreting ADR prose.
- **US-2**: As a reviewer of a new ADR, I want each normative clause in its Decision Outcome to carry its RFC 2119
  keyword and the ID of the document that restates it, so that I can verify the restatement and its strength clause by
  clause.

## 3. Non-Goals

1. **Scope Excluded**: Applying the new Decision Outcome format to accepted ADRs other than the 13 listed in §5.
2. **Scope Excluded**: Adding RFC 2119 keywords to existing prose rules in the 28 capability and architecture documents
   that use none. This is separate follow-up work.
3. **Scope Excluded**: A governance rule that checks Decision Outcome clauses mechanically.
   - **When to Reconsider**: when reviews keep finding normative ADR clauses that have no restating document, or
     restatements whose strength differs from the ADR.
4. **Scope Excluded**: Changing any decision. A restatement keeps the clause's existing meaning and strength. A
   clause that the current implementation contradicts is reported, not restated.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Decision-writing instruction defines clause-level normative outcomes
- **Given** the docs bundle's `decision-writing` instruction
- **When** an author reads its Decision Outcome guidance
- **Then** it directs the author to write the Decision Outcome as one list item per clause
- **And** it directs that a normative clause carries one RFC 2119 keyword and the backticked ID of the capability or
  architecture document that restates it
- **And** it directs that a clause with no restating document carries no keyword and serves only as rationale or
  context
- **And** it states that the restating document is authoritative and that the ADR keyword records the strength
  intended at decision time
- **And** it lets `Confirmation` cite those restating IDs

### [AC-02] Decision template shows the clause format
- **Given** the docs bundle's `decision` template
- **When** an author scaffolds an ADR from it
- **Then** its Decision Outcome section shows one example normative clause in the
  `<clause with MUST|SHOULD|MAY> → <target ID>` form and one example rationale clause with no keyword
- **And** the bundle text names only placeholder IDs (`CAP-<AREA>-<slug>`, `ARCH-<id>`), never a real document of
  this repository

### [AC-03] Completion classification routes lasting rules to contract documents
- **Given** the spec bundle's completion guidance
- **When** an agent classifies the Living Spec impact of a completed change
- **Then** the guidance routes lasting rules to capabilities or architecture, written with RFC 2119 keywords
- **And** it routes the reasons for those rules to an ADR whose Decision Outcome cites the restating ID
- **And** it no longer routes "lasting policy" to ADRs alone

### [AC-04] ADR-only clauses of the 13 ADRs are restated
- **Given** an ADR listed in §5 and its clause listed there
- **When** the clause still holds against the current implementation and guidance
- **Then** a capability or architecture document restates it as a rule with an RFC 2119 keyword of the strength the
  ADR intends
- **And** the ADR's Decision Outcome marks that clause with the keyword and the restating ID, as a format edit that
  does not change the decision
- **When** the clause is stale, superseded or one-off
- **Then** `reconcile.md` records that classification with its evidence (file and line)
- **And** no document restates the clause

### [AC-05] Snapshot-gate contradiction is resolved
- **Given** `CAP-GOV-rule-authoring` §Optional `inputs`
- **When** a reader looks up how the Git snapshot gates treat a rule that declares `inputs`
- **Then** the text agrees with `CAP-GOV-evaluation-lifecycle` and the implementation: a snapshot run skips the rule
  when no diff candidate path matches its `inputs`, counting deleted paths as candidates
- **And** the text names the exceptions that the lifecycle capability defines

### [AC-06] Checks pass
- **Given** the finished change
- **When** `uv run devkit rules check` and `just test-affected` run in the worktree
- **Then** both exit `0`
- **And** `uv run devkit rules check --phase hygiene` reports no `RULE-agent-asset-wording` warning for the edited
  bundle assets

## 5. ADR-only clauses (audit input)

The last column is the initial owner document. The implementer may choose a better-fitting owner and records the
choice in `plan.md`.

| ADR | Clause only in the ADR | Initial owner |
| --- | --- | --- |
| `ADR-adaptive-dev-approach-name` | Documents say "adaptive development" and identifiers say `adaptive-dev`; there is no `incubation` alias and no `.devkit/incubation.md` fallback read | `CAP-DLV-adaptive-development` |
| `ADR-kind-definition-table-keyed-on-the-declared-kind-enum` | Consumers read kind rows through the accessor at check time, not through constants bound at import; templates get no table field | `CAP-DOCS-document-model` |
| `ADR-response-style` | No presets, new variables, per-host variants, manifest exceptions or fragment splitting; raising the size limit needs observed host behavior and a new accepted decision; borrowed ideas are rewritten in original wording | `CAP-DIST-content-packages` |
| `ADR-roadmap-and-milestones` | A scheduled roadmap review (at three `done` milestones or on 2027-01-31) that Backlog records and `spec-next` reports | `CAP-HARN-agent-guidance` |
| `ADR-share-document-index-and-defer-catalog-build-in-rules-run` | Rules that receive the shared `DocumentIndex` treat it and its parsed documents as read-only | `CAP-GOV-rule-authoring` |
| `ADR-spec-package-on-devkit` | Generic first: a generic capability that `devkit-spec` needs is added to `devkit` first | `ARCH-05-1-containers` |
| `ADR-test-selection-and-ci` | Test selection graph: resolve conservatively or fall back to the full suite; no implicit package edge; opaque consumers keep a broad dependency; no deferred imports that hide dependencies; reductions are validated with before/after matrices | `ARCH-07-deployment` |
| `ADR-writing-and-terminology-guidance` | A writing instruction's `description` starts with "Read before" and stays within 300 characters; each rule lives in one instruction only | `CAP-HARN-agent-guidance` |
| `ADR-configuration-language-and-rendering` | Approval-form text: domains own reviewed English and Korean templates, every choice is explained, keys, values and evidence are kept, provider text is shown verbatim. Cloud text gives only supported CLI paths and Host boundaries; local text is MCP-first | `CAP-DIST-sync-and-transactions` |
| `ADR-delivery-decision-boundaries` | Helpers add no human approval or acknowledgment for routine findings, and they report codes and next actions; the list of escalation triggers | `CAP-DLV-project-policy` |
| `ADR-immutable-decisions-editable-records` | The in-place edits allowed on an accepted ADR without a new ADR; the definition of a decision change that needs a new ADR | `CAP-DOCS-document-model` |
| `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` | Every documented or suggested agent-facing command is `uv run devkit`; hooks keep their own forms | `CAP-DIST-context-and-playbooks` |
| `ADR-local-and-pull-request-integration` | GitHub adapter limits: `gh` only and no stored token; fork PRs, merge queues, `--auto` and `--admin` refused before confirmation; synchronous merge with a pinned SHA; no `--delete-branch`. Also the `INTEGRATION_CHECKS_PENDING` publish-then-resume flow | `CAP-INT-mcp-services` |

## 6. Assumptions

- The user chose clause-level keywords with target IDs and no retroactive rewrite beyond the 13 ADRs (conversation,
  2026-11-02).
- Adding the keyword and the restating ID to existing clauses of the 13 ADRs is a format edit, which
  `ADR-immutable-decisions-editable-records` allows without a new ADR.
- `docs/development/` is a quick reference, not a contract location. A clause found only there still needs a
  restatement in a capability or architecture document.
