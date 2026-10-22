---
name: spec-rule
description: Author, test and register a deterministic project governance rule as a devkit rule (a BaseRule with its guide, in the repository's own bundle), with optional safe autofix and typed settings.
---

# spec-rule: Governance Rule & Autofix Authoring Workflow

Use this skill to turn a project convention, architectural boundary, document integrity check or deterministic
remediation (autofix) into a rule: a fast, deterministic check that runs in the session (`devkit rules check`), the
commit gate (`--staged`) and CI (`--ci --base <ref>`). The spec bundle's own rules (`devkit rules explain
RULE-spec-lifecycle`, ...) are worked examples.

## Constraints

- Edit the bundle source, not deployed copies under `.devkit/managed/` or `.devkit/overrides/`. A changed managed copy
  is a `RULES_LOAD_FAILED` loading error, and fixers cannot write there (`RULES_PINNED_WRITE_REFUSED`).
- Tune a distributed rule only in `[rules]` of `.devkit/config.toml` ([config](references/config.md)), and replace its
  content with `devkit override create`.
- In `check` and `fix`, read and write only through `ctx.cache` (`find_files`, `read_text`, `get_frontmatter`,
  `get_links`, `get_catalog`, `write_text`), because the snapshot gates and the recheck evaluate exactly the staged or
  CI tree through it.
- Use the standard library and devkit's helpers (`devkit_core.core.frontmatter`,
  `devkit_agt.features.rules.extract_links`, `devkit_agt.features.rules.count_tasks`) instead of heavy dependencies. A
  rule file imports only what the project's environment provides.
- Recompute diagnostics on every run instead of persisting state files (debt ledgers, caches).
- Use no non-deterministic heuristics, network access or LLM calls inside rules: evaluation is deterministic, offline
  and fast.
- Return violations instead of printing, and raise nothing for findings; output belongs to `devkit rules`.

## Principles

### A project rule ships in the project's own bundle

- Ship a rule the repository keeps as a `kind = "rule"` asset of its in-repository bundle, a content package under
  `tools/<repo>-devkit/`. `devkit sync` deploys it under `.devkit/managed/<bundle>/` and `devkit rules` loads it
  without flags.
  - Bundle setup: devkit's `in-repo-bundle` instruction.
  - Rule tests and snapshot gates: the `harness` bundle's `harness-assets` instruction.
- Give each rule asset one directory:
  - `rules/<name>/rule.py`: one or more `BaseRule` subclasses with `guide="guide.md"`. Every `.py` file of the asset
    is loaded except under `tests/`.
  - `rules/<name>/guide.md`: the guide `devkit rules explain` prints and violations cite, in devkit's guide sections.
  - `rules/<name>/tests/test_rule.py`: the rule's tests, deployed with it.
- If an instruction or playbook holds the rule's judgment or procedure, name it with
  `related=("<bundle>:<asset-id>",)`. `devkit rules explain` prints its path, the guide's Remediation says when to read
  it, and the instruction names the rule by ID without repeating its checks.
- For a local experiment, load unrecorded rule files with `devkit rules check --rules-dir <dir>`; the commit gate
  never runs them. Promote a finished experiment into the bundle.
- Prefix the ID with the repository name (`RULE-myrepo-no-todo`) unless you intend to shadow an upstream rule: a
  later-loaded rule with an earlier rule's ID replaces it.

### Phase separation (linter vs hygiene)

- **`Phase.LINTER`**: the active gate for sessions, the commit gate and CI. Use it for non-negotiable boundaries and
  contract integrity.
- **`Phase.HYGIENE`**: out-of-session debt collection, run only by `devkit rules check --phase hygiene`. Start a new
  rule that meets many existing violations here with `promote_to=Phase.LINTER`; the run reports
  `[PROMOTION: ... remaining=N]` until it can be flipped.
- A project can park a linter rule in hygiene with `[rules.phase_overrides]` ([config](references/config.md)).

### Deterministic autofix

- Implement `fix(ctx) -> list[str]` (the `Autofixable` protocol) and mark violations `fixable=True` only when
  repository state determines exactly one result (one candidate path, one target ID) or a documented default applies.
- If several candidates remain, report a remediation instead of a fix.
- Write only through `ctx.cache.write_text` and keep every other byte. Leave files that `ctx.cache.read_text_strict`
  rejects alone.
- Return every path written. Under `ctx.dry_run`, return the paths without writing.
- The engine runs one fix pass and one recheck; a second run must produce zero changes and zero violations.

## Authoring Workflow

Read [templates](references/templates.md) at Step 2 for the layout, registration, guide, rule file and tests.

### Step 1: Design ID, phase, severity and targets

1. **Rule ID**: `RULE-<kebab-case>`, prefixed with the repository name.
2. **Phase**: `linter` or `hygiene` (optional `promote_to`).
3. **Severity**: `error` fails the command (exit 1); `warning` and `info` are reported findings that do not fail.
   Suppression comments do not exist: record a justified exception as a path in `[rules] exclude`, a per-path settings
   override or a severity override in `.devkit/config.toml`, each with a comment giving the reason.
4. **Targets and settings**: which files the rule reads, and which limits or paths a project may tune. Read
   [config](references/config.md) when the rule declares settings.

### Step 2: Create the rule files and register the asset

1. Write `rules/<name>/rule.py` and `rules/<name>/guide.md` in the bundle source.
2. Add the asset to its `bundle.toml` and to the preset the project selects.

### Step 3: Implement the check and fix

- Report a file only when `ctx.is_file_targeted(rel)` is true: it applies the run's targets and `[rules] exclude`.
- Read settings with `ctx.settings(self, rel)`.
- Give each `Violation` a message and an actionable `remediation`.

### Step 4: Write tests

- Put the tests in `rules/<name>/tests/test_rule.py`, without an `__init__.py`.
- Use only `devkit_agt.features.rules.services.testing`: `load_rule(__file__)` loads the folder as devkit loads the
  deployed copy, and `check(RULE, tmp_path, files, targets=..., fix=..., settings=...)` evaluates it.
- Keep helpers in the file, because the tests run in isolation (no project `conftest.py`).
- Cover a valid case, a violation, targeting, settings, the fix, and idempotency (a second fix changes nothing).

### Step 5: Validate against devkit

```bash
devkit rules check --rules-dir <bundle>/rules     # trial before deployment
devkit sync                                       # deploy and record the receipt
devkit rules phases                               # default and effective phase
devkit rules explain RULE-<id>                    # settings and the guide as deployed
devkit rules test RULE-<id>                       # the deployed copy's tests, isolated
devkit rules check                                # whole workspace; --phase hygiene for hygiene rules
devkit rules fix --dry-run && devkit rules fix    # fixable findings, then the repair
```

Commit the rule source with the updated `.devkit/installation.json`, because the commit gate
(`devkit rules check --staged`) reads managed rules only when their hash matches the staged receipt. A stale receipt
fails the gate with a `[FIX]` to run `devkit sync`.

## Completion

- `devkit rules test RULE-<id>` passes and `devkit rules explain RULE-<id>` prints the guide and effective settings.
- `devkit rules check` (with `--phase hygiene` for a hygiene rule) exits `0`, or reports only the findings the rule is
  meant to surface.
- A second `devkit rules fix --dry-run` reports no changes.
- The rule source and `.devkit/installation.json` are staged together.
