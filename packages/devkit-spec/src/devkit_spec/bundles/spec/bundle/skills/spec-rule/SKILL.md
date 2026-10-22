---
name: spec-rule
description: Author, test and register a deterministic project governance rule as a devkit rule (a BaseRule with its guide, in the repository's own bundle), with optional safe autofix and typed settings.
---

# spec-rule: Governance Rule & Autofix Authoring Workflow

Use this skill when introducing a project convention, architectural boundary, document integrity check, or deterministic remediation (autofix) as a rule: a fast, deterministic check that runs in the session (`devkit rules check`), the commit gate (`--staged`) and CI (`--ci --base <ref>`). The spec bundle's own rules (`devkit rules explain RULE-spec-lifecycle`, ...) are worked examples.

---

## 1. Principles

### Principle 1: A project rule ships in the project's own bundle
- Ship a rule the repository keeps as a `kind = "rule"` asset of its in-repository bundle, a content package under `tools/<repo>-devkit/`. `devkit sync` deploys it under `.devkit/managed/<bundle>/` and `devkit rules` loads it without flags.
  - Bundle setup: devkit's `in-repo-bundle` instruction.
  - Rule tests and snapshot gates: the `harness` bundle's `harness-assets` instruction.
- Give each rule asset one directory:
  - `rules/<name>/rule.py`: one or more `BaseRule` subclasses with `guide="guide.md"`. Every `.py` file of the asset is loaded except under `tests/`.
  - `rules/<name>/guide.md`: the guide `devkit rules explain` prints and violations cite, in devkit's guide sections.
  - `rules/<name>/tests/test_rule.py`: the rule's tests, deployed with it.
- If an instruction or playbook holds the rule's judgment or procedure, name it with `related=("<bundle>:<asset-id>",)`. `devkit rules explain` prints its path, the guide's Remediation says when to read it, and the instruction names the rule by ID without repeating its checks.
- For a local experiment, load unrecorded rule files with `devkit rules check --rules-dir <dir>`; the commit gate never runs them. Promote a finished experiment into the bundle.
- Tune a distributed rule only in `[rules]` of `.devkit/config.toml`, and replace its content with `devkit override create`. Never edit `.devkit/managed/`: a changed copy is a `RULES_LOAD_FAILED` loading error.
- Prefix the ID with the repository name (`RULE-myrepo-no-todo`) unless the intent is to shadow an upstream rule of the same ID: a later-loaded rule with an earlier rule's ID replaces it.

### Principle 2: Phase separation (linter vs hygiene)
- **`Phase.LINTER`**: the active gate for sessions, the commit gate and CI. Use for non-negotiable boundaries and contract integrity.
- **`Phase.HYGIENE`**: out-of-session debt collection, run only by `devkit rules check --phase hygiene`. Start a new rule that meets many existing violations here with `promote_to=Phase.LINTER`; the run reports `[PROMOTION: ... remaining=N]` until it can be flipped.
- A project can park a linter rule in hygiene with `[rules.phase_overrides]` ([config](references/config.md)).

### Principle 3: Deterministic autofix
- Implement `fix(ctx) -> list[str]` (the `Autofixable` protocol) and mark violations `fixable=True` only when repository state determines exactly one result (one candidate path, one target ID) or a documented default applies.
- If several candidates remain, report a remediation instead of a fix.
- Write only through `ctx.cache.write_text` and keep every other byte. Leave files that `ctx.cache.read_text_strict` rejects alone.
- Return every path written. Under `ctx.dry_run`, return the paths without writing.
- The engine runs one fix pass and one recheck; a second run must produce zero changes and zero violations (idempotency).

---

## 2. Rule Authoring Workflow

### Step 1: Design ID, phase, severity and targets
1. **Rule ID**: `RULE-<kebab-case>` (prefixed, Principle 1).
2. **Phase**: `linter` or `hygiene` (optional `promote_to`).
3. **Severity**: `error` fails the command (exit 1); `warning` and `info` are reported findings that do not fail. Suppression comments do not exist: record a justified exception as a path in `[rules] exclude`, a per-path settings override or a severity override in `.devkit/config.toml`, each with a comment giving the reason.
4. **Targets and settings**: which files the rule reads, and which limits or paths a project may tune (typed settings, [config](references/config.md)).

### Step 2: Create the rule files and register the asset
1. Write `rules/<name>/rule.py` and `rules/<name>/guide.md` in the bundle source.
2. Add the asset to its `bundle.toml` and to the preset the project selects.

Templates: [templates](references/templates.md).

### Step 3: Implement the check (and fix)
- Read files only through `ctx.cache` (`find_files`, `read_text`, `get_frontmatter`, `get_links`, `get_catalog`), so the snapshot gates evaluate exactly the staged or CI tree.
- Report a file only when `ctx.is_file_targeted(rel)` is true: it applies the run's targets and `[rules] exclude`.
- Read settings with `ctx.settings(self, rel)`.
- Give each `Violation` a message and an actionable `remediation`.

Template: [templates](references/templates.md#rule-file).

### Step 4: Write tests
- Put the tests in the rule's folder, `rules/<name>/tests/test_rule.py`, without an `__init__.py`.
- Use only `devkit_agt.features.rules.services.testing`: `load_rule(__file__)` loads the folder as devkit loads the deployed copy, and `check(RULE, tmp_path, files, targets=..., fix=..., settings=...)` evaluates it.
- Keep helpers in the file, because the tests run in isolation (no project `conftest.py`).
- Cover a valid case, a violation, targeting, settings, the fix, and idempotency (a second fix changes nothing).

Template: [templates](references/templates.md#tests).

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
Commit the rule source with the updated `.devkit/installation.json`, because the commit gate (`devkit rules check --staged`) reads managed rules only when their hash matches the staged receipt. A stale receipt fails the gate with a `[FIX]` to run `devkit sync`.

---

## 3. Negative Constraints (MUST NOT)

- Edit the bundle source, not deployed copies under `.devkit/managed/` or `.devkit/overrides/`; fixers cannot write there either (`RULES_PINNED_WRITE_REFUSED`).
- In `check` and `fix`, read and write through `ctx.cache`, not the disk directly; bypassing it breaks the snapshot gates and the recheck.
- Use the standard library and devkit's helpers (`devkit_core.core.frontmatter`, `devkit_agt.features.rules.extract_links`, `devkit_agt.features.rules.count_tasks`) instead of heavy dependencies. A rule file imports only what the project's environment provides.
- Recompute diagnostics deterministically on every run instead of persisting state files (debt ledgers, caches).
- Use no non-deterministic heuristics, network access or LLM calls inside rules: evaluation must be deterministic, offline and fast.
- Return violations instead of printing, and raise nothing for findings; output belongs to `devkit rules`.
