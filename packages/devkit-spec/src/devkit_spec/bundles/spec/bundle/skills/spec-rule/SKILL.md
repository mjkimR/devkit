---
name: spec-rule
description: Author, test and register a deterministic project governance rule as a devkit rule (a BaseRule with its guide, in the repository's own bundle), with optional safe autofix and typed settings.
---

# spec-rule: Governance Rule & Autofix Authoring Workflow

Turn a project convention, boundary or document check into a rule that `devkit rules check` runs in the session,
the commit gate (`--staged`) and CI. Worked examples: `devkit rules explain RULE-spec-lifecycle` and the spec bundle's
other rules.

## Constraints

- Ship the rule as a `kind = "rule"` asset of the repository's in-repository bundle (devkit's `in-repo-bundle`
  instruction); `devkit sync` deploys it. Edit that source, never `.devkit/managed/` or `.devkit/overrides/`.
- Tune a distributed rule in `[rules]` of `.devkit/config.toml` ([config](references/config.md)); replace its content
  with `devkit override create`.
- In `check` and `fix`, read and write only through `ctx.cache`, because the snapshot gates evaluate the staged or CI
  tree through it.
- Keep rules deterministic, offline and stateless: no network, LLM calls, heuristics or persisted state files.
- Import only the standard library, devkit's helpers and what the project's environment provides.
- Return violations; do not print or raise for findings.

## Procedure

Read [templates](references/templates.md) before Step 2.

1. **Design**:
   - ID `RULE-<repo>-<kebab-case>`; reuse an upstream ID only to shadow that rule.
   - Phase `Phase.LINTER` for the active gate; `Phase.HYGIENE` with `promote_to=Phase.LINTER` for a rule that meets
     existing debt (`devkit rules check --phase hygiene` runs it).
   - Severity `error` fails the run; `warning` and `info` do not. Exceptions go in `.devkit/config.toml` with a reason
     comment; there are no suppression comments.
   - Settings a project may tune ([config](references/config.md)).
   - If the rule reads files beyond its targets (a whole-workspace scan, a configuration file), declare
     `inputs=("<pattern>", ...)`: workspace patterns (`[rules] exclude` `**` grammar) for every file whose content can
     change its findings. A run with explicit targets then skips the rule when no target matches; full runs and the
     snapshot gates always run it. A rule that reports only its targets leaves `inputs` unset.
2. **Create** `rules/<name>/rule.py`, `guide.md` and `tests/test_rule.py`, and register the asset in `bundle.toml` and
   the project's preset. If an instruction holds the rule's judgment, name it with `related=("<bundle>:<asset-id>",)`.
3. **Implement** `check`. Give each `Violation` an actionable `remediation`. Add `fix` only when repository state
   determines exactly one result; otherwise report a remediation. A second fix run must change nothing.
4. **Test** valid input, a violation, targeting, settings, the fix and its idempotency. Keep helpers in the test file:
   `devkit rules test` runs it without the project's `conftest.py`. With `inputs`, also test that a target matching
   each pattern reports a seeded violation and, with `opened_files`, that every file a whole-workspace check opens
   matches a pattern.
5. **Validate**:

   ```bash
   devkit rules check --rules-dir <bundle>/rules     # trial before deployment
   devkit sync
   devkit rules test RULE-<id>
   devkit rules check                                # --phase hygiene for a hygiene rule
   devkit rules fix --dry-run
   ```

## Completion

- `devkit rules test RULE-<id>` passes, and `devkit rules check` reports only the findings the rule is meant to surface.
- A second `devkit rules fix --dry-run` reports no changes.
- The rule source and `.devkit/installation.json` are staged together, because the commit gate loads a managed rule
  only when its hash matches the staged receipt.
