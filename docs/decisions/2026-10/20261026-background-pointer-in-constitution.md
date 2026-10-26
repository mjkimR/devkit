---
id: ADR-background-pointer-in-constitution
title: Load steering frontmatter always and bodies on demand
summary: "For steering documents that every role needs only when a decision concerns them, we list each file's title and one-line scope in every context and read bodies on demand, capping file count and body size, to keep background visible at a bounded cost, accepting that reading stays the agent's judgment."
proposal: SPEC-foundation-documents
status: accepted
created_at: 2026-10-26
---

# [ADR-background-pointer-in-constitution] Load steering frontmatter always and bodies on demand

- **Status**: Accepted
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Steering documents apply to wording, naming, interface and content decisions in every activity, Development workers
and nested roles included. Agents read background only when they know what exists and when it applies. Loading every
body into every context has no bound; the `spec` skill's intake never reaches workers (`spec` skill, Route step 1);
`living-spec-writing` is read only before writing documents. Every role loads `devkit get-context spec` once per agent
context.

## 2. Decision Drivers

- Every role sees what steering covers, workers and nested roles included.
- A bounded, small always-loaded cost.
- A mechanical check that the trigger and the bounds exist.

## 3. Considered Options

### Option 1: Progressive loading: frontmatter always, bodies on demand (Selected)
- **Overview**: `devkit get-context spec` lists each steering file's `title` and `summary` (its one-line scope) in
  every context (`ADR-bundle-context-lists-project-documents`); one constitution line names `docs/steering/` and
  tells the agent to read a body before a decision that concerns its scope; every spec role contract loads the context
  through `devkit get-context spec`; `RULE-steering-documents` caps the number of files (default 10) and each body's size (default 24576 bytes), both
  settings a project can raise.
- **Pros**: every role knows what exists at the cost of a short list; bodies cost nothing until needed.
- **Cons**: whether an agent applies the trigger is judgment.

### Option 2: A constitution pointer to the directory only
- **Overview**: one line names `docs/steering/`.
- **Pros**: no get-context change.
- **Cons**: the agent does not know which files exist or what they cover without listing the directory.

### Option 3: Load every body
- **Pros**: no judgment.
- **Cons**: unbounded cost in every context, reviewers included.

### Option 4: Search only
- **Cons**: an agent does not search for what it does not know exists; steering files are not search candidates.

## 4. Decision Outcome

We decided to adopt **Option 1** (`user`): the list reaches every role that loads the spec context (driver 1), its
size is bounded by the caps and the summary length (driver 2), and a guidance test plus the rule check both (driver
3).

## 5. Consequences

- **Positive**: steering is visible everywhere at a cost of about 400 bytes per file (`docs/materials/2026-10/20261026-foundation-documents/steering-design.md`
  D2).
- **Negative / Risks**: an agent may skip a relevant body; the scope summary makes the relevance visible but does not
  prove it was read.
- **Follow-ups**: if reviews show drift from steering despite the list, consider a review step that names the
  steering files a change's wording depends on.

## 6. Confirmation

A guidance test under `packages/devkit-spec/tests/integration/bundles/spec/` asserts the constitution line, its
trigger and that every role contract under `subagents/` loads the spec context; `RULE-steering-documents` checks the
caps and frontmatter; a test under `packages/devkit-dist/tests/` asserts the size of the `documents` output at the
default caps and the maximum summary length.
