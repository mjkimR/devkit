---
id: PADR-rules-declare-their-input-files-undeclared-rules-always-run
title: Rules declare their input files; undeclared rules always run
summary: For targeted rules runs, we let a rule declare the workspace path patterns of the files it reads (BaseRule inputs) and run undeclared rules as today, to skip whole-workspace rules no target can affect without missing a finding, accepting that a too-narrow declaration hides findings.
proposal: PROP-lint-clean-target-scoped-rules
status: draft
created_at: 2026-10-22
---

# [PADR-rules-declare-their-input-files-undeclared-rules-always-run] Rules declare their input files; undeclared rules always run

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

A targeted run evaluates every active rule. Three rules need every Python file of the workspace whatever the targets:
`RULE-architecture` and `RULE-usecase-boundaries` ignore the targets and report the whole workspace, and
`RULE-advisory-unique-code` indexes every Python file but reports only targeted ones. On a documentation-only unit
they cost about 2.5 s of the 3.7 s `devkit workflow next` takes, and none of them reads a file such a unit holds
(`materials/spike-evidence.md`). The engine cannot tell this from the outside: the `Rule` protocol says nothing
about what a rule reads, and rules come from built-ins, bundles and plugin directories alike.

## 2. Decision Drivers

- No finding a target can introduce is ever lost.
- Existing and third-party rules keep working unchanged.
- One declaration is enough to express what the three rules read (extensions, but also `.devkit/architecture.toml`).
- The declaration follows the conventions rule authors already use (`BaseRule` fields, the `**` path grammar).

## 3. Considered Options

1. **Keep the current state**: every rule in every run. Correct, but the documentation units keep paying 2.5 s.
2. **File extensions** (`inputs_ext=(".py",)`): simple, but cannot name `.devkit/architecture.toml` or a single
   configuration file without over-matching every `.toml`.
3. **Path patterns on `BaseRule`** (`inputs=("**/*.py", ".devkit/architecture.toml")`) in the `**` grammar of
   `[rules] exclude`: expresses both; one more optional field for authors.
4. **A "workspace-wide" flag plus an input set**: the flag only says what the input set already implies; two fields
   where one suffices.
5. **Engine-inferred inputs** (from the `find_files` calls a rule makes): the rules that matter read outside the cache
   (`rglob`), and inference needs a run, which is the cost to avoid.

## 4. Decision Outcome

Option 3, because it is the only one that names both the extension and the exact configuration files (driver 3) in
the grammar authors already use (driver 4):

- `BaseRule` gains `inputs: tuple[str, ...] | None = None`: the workspace-relative patterns (`match_path` grammar,
  checked with `validate_pattern`) of every file whose content can change the rule's findings. It is not added to
  the `Rule` protocol; the engine reads it with `getattr`, as it reads `guide` and `promote_to`, so rules that do not
  subclass `BaseRule` keep satisfying the protocol.
- `None` (undeclared) means any file can affect the rule: it runs in every targeted run, exactly as today
  (drivers 1 and 2). An empty tuple or an invalid pattern raises `RuleDefinitionError` (`RULES_DEFINITION_INVALID`)
  at construction, so a rule cannot silence itself by accident.
- This proposal declares `inputs` on the three Python-source rules only: `RULE-architecture` (`**/*.py`,
  `**/pyproject.toml`, `**/bundle.toml`, `.devkit/architecture.toml`), `RULE-usecase-boundaries` (`**/*.py`,
  `.devkit/architecture.toml`) and `RULE-advisory-unique-code` (`**/*.py`). The Markdown rules stay undeclared.
- `devkit rules explain` prints the declaration (`inputs=` on the `[RULE: ...]` line, `inputs` in JSON, `-` or `null`
  when undeclared), so a skipped rule's reason is visible.

## 5. Consequences

- Positive: a documentation-only targeted run skips the three rules; the declaration is local to the rule that knows
  what it reads.
- Negative: a declaration that omits a file the rule reads makes a targeted run on that file miss the rule's findings
  until a full run, the commit gate or CI reports them. The rule's own tests guard it (Confirmation).
- Follow-up: declaring the Markdown rules (`RULE-document-reference` 0.78 s, the spec rules) would speed
  Python-only targeted runs such as `devkit rules check <file.py>`; triggered when such runs become a measured cost.

## 6. Confirmation

- Tests of `BaseRule` construction: an empty tuple and each invalid pattern form raise `RULES_DEFINITION_INVALID`.
- Each declared rule's `tests/test_rule.py`: a documentation-only target set does not evaluate it, and a seeded
  violation in a target matching each declared pattern is reported.
- `devkit rules explain RULE-architecture` shows the declaration.
