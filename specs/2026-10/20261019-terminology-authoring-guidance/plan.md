---
id: PLAN-terminology-authoring-guidance
spec: SPEC-terminology-authoring-guidance
---

# Technical Plan: `SPEC-terminology-authoring-guidance` Terminology authoring guidance and a glossary that agents read

## 1. Constitution & Invariant Review

None. The change edits existing bundle assets only: no new asset in `bundle.toml`, no rule, workflow or command, and
no constitution line (`ADR-terminology-guidance-lives-in-living-spec-writing`). The seeded glossary stays write-once
and project-owned (`ADR-docs-skeleton-is-opt-in`); the columns follow `ADR-seeded-glossary-columns`. Both ADRs are
accepted and are not edited.

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md`: the `description` names
    terminology and the glossary; the `## Glossary` section keeps its package-glossary bullet and gains a short lead,
    the eight rules of the proposal's guidance draft and the older-glossary fallback (AC-01, AC-02, AC-03). Lines are
    wrapped at 120 characters.
  - `packages/devkit-spec/src/devkit_spec/bundle/seed/docs/glossary.md`: five-column table with placeholder comments
    that say what each column holds, a pointer to the instruction, an "Avoided Generic Nouns" section for project
    additions and accepted exceptions; the two authoring guidelines removed (AC-04).
  - `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-sync/SKILL.md`: one Step 1 bullet (AC-06).
  - `docs/glossary.md`: `Defined in` becomes `Owner`, `Avoid` (empty) and `Code identifiers` added, lead paragraph
    rewritten in place (AC-07).
  - `packages/devkit-spec/tests/test_terminology_guidance.py` (new: AC-01, AC-02, AC-04, AC-06) and
    `packages/devkit-spec/tests/test_package.py` (the docs-skeleton test asserts the seeded header, AC-05).
  - Living Spec (reconcile, not tasks): `CAP-HARN-agent-guidance` sections 4.3 and 4.7, `CAP-DLV-delivery-workflows`
    business rule 9.
- **New Dependencies**: None.

### Design choices

- The three lines beside the rules are folded into rule 1 (project list), rule 3 (Avoid as `glossary.yaml` synonym)
  and a closing paragraph (fallback), keeping each next to the rule it qualifies and the section short.
- The content test checks stable anchors (the boundary sentence, the eight rules, the seeded header, the removed
  guideline, the `spec-sync` question) rather than the whole text, so a later wording edit does not break it. The
  30-line bound (AC-03) is an acceptance check of this change, not a lasting invariant: it is verified with
  `git diff --numstat` against the handoff base and recorded in the final report, not in a test. devkit's own
  `docs/glossary.md` is repository content, not package content, so AC-07 is verified by reading it, not by a package
  test.

## 3. Error Handling & Edge Cases

- **A project without `docs/glossary.md`**: the rules still apply; the lead states that registration steps apply only
  where a glossary exists.
- **An existing seeded glossary**: not rewritten by `devkit sync` (write-once seed); the fallback paragraph covers
  older columns.

## 4. Verification & Test Plan

- `just test devkit-spec tests/test_terminology_guidance.py tests/test_bundle_budgets.py tests/test_package.py`
  during development; `just test-affected` on the reviewed head.
- `just lint devkit-spec`, `just check devkit-spec`, `just rules-check`.
- `just smoke` only if smoke asserts seeded glossary content (it does not today: it checks `docs/` seeding and
  discovery), so it is run once as a regression check of the seeded skeleton.
- `devkit sync` after the bundle change refreshes `.devkit/managed/spec/` and the receipt.
