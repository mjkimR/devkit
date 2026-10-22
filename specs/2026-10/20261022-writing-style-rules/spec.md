---
id: SPEC-writing-style-rules
title: Writing style rules and layout-free guidance tests
summary: Adds a hygiene rule that flags hedges, emphatic capitals and time-relative words in agent assets, and makes bundle guidance tests match wording regardless of line wrapping.
status: planned
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-writing-style-rules] Writing style rules and layout-free guidance tests

## 1. Problem Statement & Motivation

The `agent-asset-writing` and `document-writing` instructions forbid hedged directives, emphatic capitals and
time-relative words, but only a reviewer reading every line enforces them. The rollout of that guidance
(`SPEC-writing-guidance-rollout`) removed the existing cases, so a check now guards a clean baseline instead of
reporting a backlog.

The same rollout showed that several spec bundle guidance tests search raw file text: a pinned phrase split across
two lines by rewrapping fails the test although its wording is unchanged. Each test file also carries its own copy of
the bundle path, the Jinja rendering reader and the whitespace normalization.

## 2. User Stories

- **US-1**: As an agent editing a skill, playbook, instruction or role contract, I want a hygiene warning on a hedge,
  an emphatic capital or a time-relative word, so that the writing rules hold without a line-by-line review.
- **US-2**: As an agent rewriting bundle prose, I want guidance tests to pin wording, not line layout, so that
  rewrapping text never breaks a test.

## 3. Non-Goals

1. **Scope Excluded**: Detecting bare prohibitions (a prohibition without its alternative).
   - **Rationale**: Whether an alternative exists is a judgment; detection has false positives. It stays a review item.
2. **Scope Excluded**: Flagging bold text or procedural relative words ("the new branch", "still", "now").
   - **Rationale**: The scan of the bundle sources found these only in legitimate uses (list labels, procedure
     steps relative to an earlier step), never as a time reference to the writing date.
3. **Scope Excluded**: Checking `docs/`, specs, READMEs or rule guides by default.
   - **When to Reconsider**: a project adds those paths through the rule's `paths` setting; the default covers
     agent-executed assets only.
4. **Scope Excluded**: Rewriting guidance tests of packages other than `devkit-spec`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A hedge, an emphatic capital or a time-relative word is reported per occurrence
- **Given** an agent asset under a default path containing the hedge `might`, the capitalized `ALWAYS` and the word
  `recently` on separate lines
- **When** `devkit rules check --phase hygiene` runs
- **Then** `RULE-agent-asset-wording` reports three `warning` violations at those files and lines, each naming the
  category and the word, and exits with code 0 unless `--strict` is given

### [AC-02] Quoted, code and template text is ignored
- **Given** the same words only inside a fenced code block, an inline code span, double quotes (straight or curly),
  an HTML comment or a Jinja tag
- **When** the rule runs
- **Then** it reports no violation

### [AC-03] Defined keywords and ordinary casing pass
- **Given** the RFC 2119 keywords `MUST`, `MUST NOT`, `SHOULD`, `MAY`, the lowercase words `always`, `never` and
  `only`, and the word `considered`
- **When** the rule runs
- **Then** it reports no violation

### [AC-04] Scope follows the paths, the receipt and the targets
- **Given** matching words in a bundle skill, a bundle subagent contract, a project skill under `.agents/skills/`,
  a receipt-owned projection under `.claude/skills/`, and a file under `docs/`
- **When** the rule runs with default settings, then with `paths` set and with a changed-file target
- **Then** the default run reports the bundle skill, the subagent contract and the project skill only; `paths` and
  targets narrow or extend the set accordingly

### [AC-05] Word lists are configurable and validated
- **Given** settings that replace `hedges`, set `emphatic` to an empty list, or give an empty or multi-line word
- **When** the rule runs
- **Then** replaced lists take effect, an empty list disables its category, and an invalid word is reported as
  `RULES_SETTINGS_INVALID`

### [AC-06] The rule ships in the skill-authoring preset and passes on this repository
- **Given** the `authoring` bundle selected with preset `skill-authoring`
- **When** `devkit sync` runs and then `devkit rules check --phase hygiene`
- **Then** the rule is deployed with its guide and tests (`devkit rules test RULE-agent-asset-wording` exits 0), and
  this repository's bundle sources produce no `RULE-agent-asset-wording` violation

### [AC-07] Guidance tests pin wording, not layout
- **Given** the spec bundle guidance tests under `packages/devkit-spec/tests/integration/bundles/spec/`
- **When** a pinned phrase (for example "only when the prerequisite is explicitly waived" in
  `skills/spec/references/backlog.md.jinja`) is rewrapped across two lines without changing its words
- **Then** the tests still pass; they read bundle text through one shared helper in `tests/support/spec_support/`,
  and no test file there defines its own bundle reader or whitespace normalization

## 5. Source feedback

- `FB-writing-style-rules`: the hygiene rule (AC-01 to AC-06); bare prohibitions stay a review item (Non-Goal 1).
- `FB-guidance-tests-pin-line-layout`: the shared normalizing reader (AC-07).

## 6. Assumptions

- One rule with three word-list categories, not three rules: the categories share scanning, ignored spans, paths and
  remediation, and an empty list turns a category off.
- Default word lists: hedges `likely`, `might`, `probably`, `perhaps`, `maybe`, `possibly`, `consider`
  (case-insensitive, whole word); emphatic `CRITICAL`, `IMPORTANT`, `ALWAYS`, `NEVER`, `ONLY`, `NOTE`, `WARNING`,
  `DO NOT` (exact case); time-relative `recently`, `currently`, `nowadays`, `as of now`, `at the moment`, `for now`
  (case-insensitive). The scan of the 83 bundle agent assets found none of them outside quotes and code.
- `FB-parallel-pruning-cuts-both-owners` is dismissed on this branch by the user's decision (too narrow a case for
  standing guidance); it is not a source of this spec.
