---
id: ADR-retire-native-approval-and-moved-ownership-clauses
title: Retire native-approval and moved-ownership clauses
summary: "For accepted ADRs that still state the removed native approval route or an ownership that later decisions moved, we retire those clauses only, to keep the ledger in step with Host-run CLI approval and the docs bundle, accepting that current rules live in the replacing ADRs."
status: accepted
created_at: 2026-11-02
supersedes: [ADR-proposal-acceptance, ADR-mcp-runtime-and-shared-artifacts, ADR-document-system, ADR-steering-documents]
---

# [ADR-retire-native-approval-and-moved-ownership-clauses] Retire native-approval and moved-ownership clauses

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: user, agent
- **Involved Components/Capabilities**: `CAP-DLV-proposal-planning`, `CAP-INT-mcp-services`, `CAP-VIEW-repository-viewer`,
  `CAP-DOCS-document-model`, `CAP-DIST-context-and-playbooks`

---

## 1. Context & Problem Statement

Later decisions replaced some clauses of four accepted ADRs without adding a "Superseded in part by" line, so those
ADRs still state them:

- `ADR-host-cli-lifecycle-authority` moved approval to the Host's conversation followed by a CLI call. Commits
  `2a491881` and `8f570521` then removed the native approval forms. `ADR-proposal-acceptance` still authorizes
  acceptance through a native `spec_plan_accept` form. `ADR-mcp-runtime-and-shared-artifacts` still makes native
  confirmation the normal route.
- `ADR-repository-viewer` reads the working tree. `ADR-proposal-acceptance` still carves a "narrowly scoped"
  exception out of a Git-only viewer.
- The document-and-SDD bundle split, now in `ADR-document-system`, gave the document rules, templates, docs skeleton
  and steering context to the docs bundle. `ADR-document-system` still says the spec bundle ships every rule asset and
  lists templates, without distinguishing document templates, and the docs skeleton as devkit-spec methodology. `ADR-steering-documents` still says
  `devkit get-context spec` lists the steering documents.

The ADR compaction found these clauses and kept them verbatim, because a compaction changes no decision
(`FB-native-approval-adrs-without-pointers`, `FB-adr-ownership-moves-without-pointers`).

---

## 2. Decision Drivers

- No accepted ADR states a route or an owner that the code no longer has.
- The decisions that replaced these clauses stay the source of the current rules.
- No behavior changes.

---

## 3. Considered Options

### Option 1: Retire the clauses with one ADR (Selected)
- **Overview**: One partial supersession of the four ADRs, naming each clause.
- **Pros**: One record of one cleanup; pointer lines make the retirement visible where the clause stood.
- **Cons**: One ADR touches four topics. Under `ADR-group-compaction-by-topic`, that does not bind them into one
  compaction group.

### Option 2: Add pointer lines only
- **Overview**: Point each clause at the ADR that replaced it, without a new record.
- **Pros**: No new ADR.
- **Cons**: A pointer line needs a reciprocal `supersedes`, and the replacing ADRs cannot gain one without changing
  their own records.

---

## 4. Decision Outcome

We adopt **Option 1**. It retires only the clauses below. Every other clause of the four ADRs stays in force, and all
four stay `accepted`.

- From `ADR-proposal-acceptance`, the native lifecycle approval clause is retired: a native `spec_plan_accept` form no
  longer authorizes acceptance, merge, cleanup or handoff. Acceptance follows `ADR-host-cli-lifecycle-authority`:
  the user's conversational decision, then `devkit spec proposal accept`.
- From `ADR-proposal-acceptance`, the consequence that native form rendering needs separate live evidence is retired
  with the native form.
- From `ADR-proposal-acceptance`, the viewer exception clause is retired. The viewer reads the working tree under
  `ADR-repository-viewer`, which also carries its loopback, Host-check, no-CORS, sanitization and read-only
  protections.
- From the Host-approval clause of `ADR-mcp-runtime-and-shared-artifacts`, three parts are retired: native
  confirmation as the normal route, CLI/PR authorization as mere recovery, and no extra approval after native
  confirmation. Approvals still belong to the Host, now through `ADR-host-cli-lifecycle-authority`, and no host
  permission prompt is suppressed.
- From `ADR-document-system`, the distribution clause that the spec bundle keeps shipping every rule asset is retired.
  So are the document templates and the docs skeleton in the devkit-spec methodology list; devkit-spec keeps its lifecycle
  templates. The document-and-SDD bundle clauses
  of the same ADR give them to the docs bundle.
- From `ADR-steering-documents`, the statements are retired that `devkit get-context spec` lists the steering
  documents, that role contracts receive the list through the spec context, and that a guidance test asserts this.
  Role contracts still load the spec context for their own work. The docs bundle declares
  `context_documents`, so `devkit get-context docs` lists them.

---

## 5. Consequences

- **Positive**: The four ADRs no longer contradict the route or the owner the code has.
- **Negative / Risks**: None beyond reading the current rules from the replacing ADRs.
- **Follow-ups**: None.

---

## 6. Confirmation

- `rg spec_plan_accept packages/ tools/` finds nothing.
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml` declares `context_documents`.
- `RULE-decision-supersession` checks the pointer lines.
