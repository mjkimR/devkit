---
id: ADR-layered-writing-guidance
title: Layered writing guidance
summary: "For agent-read documents mixing writing rules with placement policy, we split writing guidance into a common instruction, one per document kind and a self-contained authoring one, to keep triggers precise, accepting five more headers per spec context."
proposal: SPEC-writing-guidance-layers
status: accepted
created_at: 2026-10-22
---

# [ADR-layered-writing-guidance] Layered writing guidance

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Skills, playbooks and instructions stack a condition, an action, an exception and a cross-reference in one sentence.
The `skill-authoring` playbook covers structure and size but not sentence-level writing. Living Spec documents have
templates but no type-specific patterns. `contract-authoring` and `living-spec-writing` mix general writing rules
with placement policy. Anthropic's skill authoring and prompting guidance is the agreed baseline.

## 2. Decision Drivers

- Context budget: `devkit get-context spec` returns every instruction header to every development session
  (`ADR-terminology-guidance-lives-in-living-spec-writing`).
- Trigger precision: an agent writing an ADR should not read the story or architecture patterns.
- Asset boundaries: criteria are instructions, procedures are playbooks (`ARCH-08-2-resource-taxonomy`); `authoring`
  is opt-in and never depends on `spec`.

## 3. Considered Options

- **One common instruction with per-type sections**: one header; every document write reads all type sections.
- **Common instruction plus one instruction per kind**: five headers (about 250 tokens per spec context); each type
  section is read only for its kind.
- **Per-type rules in templates only**: no header; templates are read only when a document is created, not edited,
  and `docs/architecture/` has no template.

## 4. Decision Outcome

Common instruction plus one instruction per kind:

- `spec` bundle, preset `core`: `document-writing` (sentence-level rules for every document), `decision-writing`,
  `capability-writing`, `story-writing`, `architecture-writing`. `contract-authoring` and `living-spec-writing` keep
  their own topics; a rule lives in one of them only. The Glossary stays in `living-spec-writing`.
- `authoring` bundle, presets `skill-authoring` and `all`: `agent-asset-writing`, self-contained; the
  `skill-authoring` playbook keeps procedures only.
- Each description starts with `Read before` and stays at most 300 characters.

## 5. Consequences

- **Positive**: the agent reads only the guidance for the document at hand; writing rules have one owner.
- **Negative / Risks**: five more headers in every spec context; `agent-asset-writing` restates a few common rules.
- **Follow-ups**: rewrite other skills after the `spec-plan` pilot; add mechanical style rules once the pilot gives
  evidence.

## 6. Confirmation

`packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py` checks the instruction set, the
description prefix and length; `packages/devkit/tests/integration/bundles/authoring/test_bundle.py` checks the
authoring preset and that `agent-asset-writing` names no `spec` instruction.
