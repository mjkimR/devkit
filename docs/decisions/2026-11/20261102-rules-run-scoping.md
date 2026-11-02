---
id: ADR-rules-run-scoping
title: Skip declared rules no target or diff path can affect
summary: "For targeted and snapshot rules runs, we let rules declare input patterns and skip a declared rule in evaluate_rules when no target, or no diff path including deletions, matches, to speed lint-clean and the commit gate without missing a finding, accepting that too-narrow declarations hide findings."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-rules-declare-their-input-files-undeclared-rules-always-run
  - ADR-scope-only-explicit-working-tree-targets-in-the-evaluator
  - ADR-scope-snapshot-runs-to-diff-paths-including-deletions
---

# [ADR-rules-run-scoping] Skip declared rules no target or diff path can affect

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `BaseRule`, `evaluate_rules`, `scope_rules`, `RunProjectRulesUseCase`,
  `CAP-GOV-rules-engine`

---

## 1. Context & Problem Statement

A targeted run evaluates every active rule. Three rules need every Python file of the workspace whatever the targets:
`RULE-architecture` and `RULE-usecase-boundaries` ignore the targets and report the whole workspace, and
`RULE-advisory-unique-code` indexes every Python file but reports only targeted ones. On a documentation-only unit
they cost about 2.5 s of the 3.7 s `devkit workflow next` takes, and none of them reads a file such a unit holds
(`docs/materials/2026-10/20261022-lint-clean-target-scoped-rules/spike-evidence.md`). The engine cannot tell this from
the outside: the `Rule` protocol says nothing about what a rule reads, and rules come from built-ins, bundles and
plugin directories alike.

Once rules declare their inputs, the engine must decide in which runs, at which layer and against which target list
a declared rule is skipped. Targets reach the evaluator from four callers: `devkit rules check|fix FILES`,
`lint-clean` (`run_project_rules(root, targets=files)`), the Git snapshot gates (`check --staged` at commit time,
`check --ci`) and library callers of `evaluate_rules`, including `devkit_agt.features.rules.services.testing.check`.
A snapshot's targets are its changed files; its deleted files are not targets, yet a deletion can change a
whole-workspace rule's result (an import of a removed module).

An in-place staged snapshot run (`devkit rules check --staged`) on this repository takes 4.49 s on a documentation
edit, spending ~2.93 s on whole-workspace Python AST evaluation for files the commit cannot affect.

---

## 2. Decision Drivers

Drivers are listed per source decision; a "(driver N)" in Decision Outcome refers to the list of the clause's source.

`ADR-rules-declare-their-input-files-undeclared-rules-always-run`:

1. No finding a target can introduce is ever lost.
2. Existing and third-party rules keep working unchanged.
3. One declaration is enough to express what the three rules read (extensions, but also `.devkit/architecture.toml`).
4. The declaration follows the conventions rule authors already use (`BaseRule` fields, the `**` path grammar).

`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`:

1. The commit gate and CI keep evaluating every rule: they are the last check before history.
2. `lint-clean` and `devkit rules check FILES` agree, as they do through `run_project_rules`.
3. A rule author can test a declaration with the existing `check(rule, root, files, targets=...)` helper.
4. Project policy (`[rules]`) cannot change which findings a skip hides without the run noticing.

`ADR-scope-snapshot-runs-to-diff-paths-including-deletions`:

1. The `rules-check` pre-commit gate and branch snapshot runs must not spend time evaluating whole-workspace rules
   whose declared inputs are unaffected by the commit.
2. Deletion-only changes and file renames must never skip rules whose inputs match the removed path (e.g. deleting a
   Python file must trigger `RULE-architecture` to check for broken imports).
3. Scoping candidate paths must be decoupled from `RuleContext.targets`: non-existent deleted files cannot be treated
   as evaluation targets.
4. Project configuration (`.devkit/config.toml`) and installation receipt (`.devkit/installation.json`) changes must
   evaluate every rule.
5. Full workspace CI runs (`just rules-check` in `.github/workflows/ci.yml`, nightly, and release) continue to act as
   an unscoped safety net.

---

## 3. Considered Options

### Declaring what a rule reads (`ADR-rules-declare-their-input-files-undeclared-rules-always-run`)

1. **Keep the current state** (rejected in `ADR-rules-declare-their-input-files-undeclared-rules-always-run`): every
   rule in every run. Correct, but the documentation units keep paying 2.5 s.
2. **File extensions** (`inputs_ext=(".py",)`) (rejected in
   `ADR-rules-declare-their-input-files-undeclared-rules-always-run`): simple, but cannot name
   `.devkit/architecture.toml` or a single configuration file without over-matching every `.toml`.
3. **Path patterns on `BaseRule`** (`inputs=("**/*.py", ".devkit/architecture.toml")`) in the `**` grammar of
   `[rules] exclude` (selected): expresses both; one more optional field for authors.
4. **A "workspace-wide" flag plus an input set** (rejected in
   `ADR-rules-declare-their-input-files-undeclared-rules-always-run`): the flag only says what the input set already
   implies; two fields where one suffices.
5. **Engine-inferred inputs** (from the `find_files` calls a rule makes) (rejected in
   `ADR-rules-declare-their-input-files-undeclared-rules-always-run`): the rules that matter read outside the cache
   (`rglob`), and inference needs a run, which is the cost to avoid.
6. **A guard inside each rule** (`return []` when the run has targets, no snapshot and no matching target) (rejected
   in `ADR-rules-declare-their-input-files-undeclared-rules-always-run`): no engine change, but the snapshot,
   configuration and exclusion conditions are copied into three rules of two bundles and into every later rule,
   `devkit rules explain` cannot show why a rule did not run, and the engine cannot report what it skipped.

### Where working-tree scoping applies (`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`)

1. **In `lint-clean` only** (rejected in `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`): the
   smallest change, but `devkit rules check FILES` would disagree with `lint-clean` on the same files, contradicting
   the one-evaluation-path principle of `CAP-GOV-rules-engine`.
2. **In `run_project_rules`** (rejected in `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`): covers
   both CLI and `lint-clean`, but library callers and rule tests bypass it.
3. **In `evaluate_rules`, for runs with explicit targets and no snapshot** (selected): one place for every caller,
   next to the phase filter; snapshot and whole-workspace runs unchanged.
4. **Also in snapshot runs** (rejected in `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`): would
   speed the commit gate, but deleted paths are no targets, so a deletion-only change to Python could skip
   `RULE-architecture`.

### Scoping snapshot runs (`ADR-scope-snapshot-runs-to-diff-paths-including-deletions`)

1. **Keep snapshot runs unscoped (status quo)** (rejected in
   `ADR-scope-snapshot-runs-to-diff-paths-including-deletions`): keeps every gate complete before Git history, but
   every commit pays ~4.5 s regardless of touched files.
2. **Scope snapshot runs matching only `snapshot.changed`** (rejected in
   `ADR-scope-snapshot-runs-to-diff-paths-including-deletions`): avoids evaluating rules when `changed` does not
   match, but a deletion-only change to Python would skip `RULE-architecture`, hiding broken imports.
3. **Decouple scoping paths from evaluation targets and match diff paths including deletions** (selected):
   - `RuleContext.targets` retains only existing regular files in the snapshot tree (`snapshot.changed` plus inbound
     Markdown linkers).
   - `scope_rules` constructs candidate names from `ctx.targets` plus `snapshot.deleted` and any non-regular diff
     paths (e.g. typechanges).
   - `RunProjectRulesUseCase._run` computes `has_work = bool(targets or (snapshot and snapshot.deleted))` so
     deletion-only commits do not short-circuit before rule loading.
   - Touching `.devkit/config.toml` (`CONFIG_PATH`) or `.devkit/installation.json` (`RECEIPT_PATH`) disables rule
     skipping.

---

## 4. Decision Outcome

Chosen: path patterns on `BaseRule` (declaring option 3), scoping in `evaluate_rules` for working-tree runs with
explicit targets (working-tree option 3), and snapshot scoping against diff paths including deletions (snapshot
option 3).

### Rule input declaration

- Option 3 is chosen because it is the only one that names both the extension and the exact configuration files
  (driver 3) in the grammar authors already use (driver 4), and keeps the skip conditions in one place, unlike
  option 6. (ADR-rules-declare-their-input-files-undeclared-rules-always-run)
- `BaseRule` gains `inputs: tuple[str, ...] | None = None`: the workspace-relative patterns (`match_path` grammar,
  checked with `validate_pattern`) of every file whose content can change the rule's findings. It is not added to the
  `Rule` protocol; the engine reads it with `getattr`, as it reads `guide` and `promote_to`, so rules that do not
  subclass `BaseRule` keep satisfying the protocol. The engine's policy validation checks the attribute of every
  loaded rule, so a protocol-only rule with a string, a list or an empty value fails the run with
  `RULES_DEFINITION_INVALID` before any rule runs.
  (ADR-rules-declare-their-input-files-undeclared-rules-always-run)
- `None` (undeclared) means any file can affect the rule: it runs in every targeted run, exactly as before
  (drivers 1 and 2). An empty tuple or an invalid pattern raises `RuleDefinitionError` (`RULES_DEFINITION_INVALID`)
  at construction, so a rule cannot silence itself by accident.
  (ADR-rules-declare-their-input-files-undeclared-rules-always-run)
- `inputs` is declared on the three Python-source rules only: `RULE-architecture` (`**/*.py`, `**/pyproject.toml`,
  `**/bundle.toml`, `.devkit/architecture.toml`), `RULE-usecase-boundaries` (`**/*.py`, `.devkit/architecture.toml`)
  and `RULE-advisory-unique-code` (`**/*.py`). The Markdown rules stay undeclared.
  (ADR-rules-declare-their-input-files-undeclared-rules-always-run)
- `devkit rules explain` prints the declaration (`inputs=` on the `[RULE: ...]` line, `inputs` in JSON, `-` or `null`
  when undeclared), so a skipped rule's reason is visible.
  (ADR-rules-declare-their-input-files-undeclared-rules-always-run)

### Working-tree targeted runs

- Option 3 is chosen because it keeps the gates complete (driver 1), gives the CLI, `lint-clean` and library callers
  one behavior (driver 2) and is reachable from the rule test helper (driver 3) (for working-tree runs; snapshot scoping
  below supersedes this for the commit gate). (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
- After the phase filter, `evaluate_rules` skips a rule with declared `inputs` when `ctx.has_targets` is true,
  `ctx.snapshot` is `None`, and no target matches one of its patterns. A whole-workspace run (`has_targets` false)
  evaluates every active rule. (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
- Matching uses the targets as named and expanded, before `[rules] exclude` (kept on `RuleContext` beside
  `changed_files`): the target-ignoring rules do not honor exclusions, so an excluded Python target can still change
  their findings. (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
- A target that is the project configuration `.devkit/config.toml` disables the skip for that run: `[rules]` settings
  and exclusions can change any rule's findings (driver 4).
  (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
- The autofix pass uses the reduced rule list; the convergence recheck decides again against the targets plus the
  files the fixes modified, so a fix that writes a skipped rule's input is rechecked by it. Policy validation still
  covers every loaded rule, so a settings error of a skipped rule is reported as before.
  (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
- Skipped rule IDs are returned on `EvaluationResult.skipped` (and so on `ProjectRun`) and logged at `INFO` (visible
  under `-v`); default stdout and the JSON result do not change, because a skip changes no next step.
  (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)

### Snapshot runs

- In `scope_rules(ctx, rules, modified)`, when `ctx.snapshot is not None`, `names` includes `ctx.targets` plus
  `ctx.snapshot.deleted`. Rules declaring `inputs` that match none of `names` are skipped and recorded on
  `EvaluationResult.skipped`. (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
- `RuleContext.targets` continues to hold only existing files in the snapshot workspace. Target-only rules (e.g.
  `RULE-secret-leak`) inspect only present files. (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
- `has_work` in `RunProjectRulesUseCase._run` considers `snapshot.deleted`, ensuring deletion-only commits initialize
  `RuleContext` and invoke `evaluate_rules`. (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
- If `CONFIG_PATH` or `RECEIPT_PATH` is in `names`, no rules are skipped.
  (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
- Skipped rules follow the existing agent-first convention: they are returned on `EvaluationResult.skipped` and
  logged at `INFO` under `-v`; stdout and JSON summaries remain clean and unchanged.
  (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)

---

## 5. Consequences

- **Positive**:
  - A documentation-only targeted run skips the three rules; the declaration is local to the rule that knows what it
    reads. (ADR-rules-declare-their-input-files-undeclared-rules-always-run)
  - `devkit workflow next` on a documentation-only spec unit drops from 3.65 s to about 1.4 s
    (`docs/materials/2026-10/20261022-lint-clean-target-scoped-rules/spike-evidence.md` §5); `devkit rules check
    <docs>` gains the same. (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
  - `rules-check` pre-commit gate latency on documentation/asset commits drops from ~4.49 s to ~1.56 s (~65 %
    reduction, saving ~2.93 s per commit). (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
  - Deletion-only and rename commits accurately trigger rules matching the removed paths.
    (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
- **Negative / Risks**:
  - A declaration that omits a file the rule reads makes a targeted run on that file miss the rule's findings until a
    full run, the commit gate or CI reports them. Each declared rule's completeness test guards it (Confirmation).
    (ADR-rules-declare-their-input-files-undeclared-rules-always-run)
  - A documentation-only targeted run no longer reports violations of a skipped target-ignoring rule in files outside
    its targets, whether pre-existing or introduced by uncommitted work. For `lint-clean` at the build-verify and
    fix-verify exits this includes the unit's own code, which lives outside the unit directory; the `rules-check`
    commit gate on each Development commit, `lint-ci-clean` and full runs still report it.
    (ADR-scope-only-explicit-working-tree-targets-in-the-evaluator)
  - Like working-tree targeted runs, snapshot runs no longer detect latent violations in untouched files;
    whole-workspace CI and nightly checks remain the safety net.
    (ADR-scope-snapshot-runs-to-diff-paths-including-deletions)
- **Follow-ups**: declaring the Markdown rules (`RULE-document-reference` 0.78 s, the spec rules) would speed
  Python-only targeted runs such as `devkit rules check <file.py>`; triggered when such runs become a measured cost.
  (ADR-rules-declare-their-input-files-undeclared-rules-always-run)

---

## 6. Confirmation

- Tests of `BaseRule` construction: an empty tuple and each invalid pattern form raise `RULES_DEFINITION_INVALID`;
  an engine test shows the same code for a protocol-only rule with a malformed `inputs`.
- Each declared rule's `tests/test_rule.py`: a documentation-only target set does not evaluate it, a seeded violation
  in a target matching each declared pattern is reported, and every workspace file the rule opens during a
  whole-workspace check of a fixture matches one of its `inputs` (an `open` audit hook or an equivalent patch).
- `devkit rules explain RULE-architecture` shows the declaration.
- Evaluator tests (`packages/devkit/tests/`): skip with explicit non-matching targets; run with a matching target, a
  matching target `[rules] exclude` removes, a `.devkit/config.toml` target and no targets;
  undeclared rule always runs; `skipped` lists the skipped IDs; a recheck after a fix that modified a matching file
  evaluates the skipped rule.
- The equivalence comparison of the working-tree scoping acceptance outcomes on this repository.
- Unit tests in `packages/devkit/tests/unit/features/rules/engine/test_scoping.py`:
  - Snapshot with only `.md` changes skips `RULE-architecture` and `RULE-usecase-boundaries`.
  - Snapshot with added or modified `.py` evaluates Python rules.
  - Snapshot with deleted `.py` evaluates Python rules.
  - Snapshot with `.devkit/config.toml` or `.devkit/installation.json` evaluates all rules.
  - Non-existent deleted paths are absent from `ctx.targets`.
- Integration tests in `packages/devkit/tests/integration/features/rules/engine/test_project.py`: deletion-only
  commit evaluates matching rules without short-circuiting in `_run`.
- Measured pre-commit gate speedup verified before and after on this repository.
