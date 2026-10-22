# Rule configuration (`[rules]`)

Read this when a rule declares settings a project may tune, or when a project changes how a rule runs.

## Declaring settings (rule author)

- Pass a frozen dataclass instance with every default as `settings=` ([templates](templates.md#rule-file)). Fields
  are `int`, `float`, `str`, `bool` or `list[str]`, each optionally `| None`.
- Override `validate_settings(settings)` to raise `ValueError` for values the types cannot express; check patterns
  with `devkit_agt.features.rules.validate_pattern`.
- Read the values per file with `ctx.settings(self, rel)`; do not cache or mutate them.
- If settings can change the result for unchanged files, rescan the rule's own targets.

## Configuring (project)

```toml
[rules]
exclude = ["docs/research/**", "CHANGELOG.md"]   # never targeted by any rule

[rules.phase_overrides]
RULE-myrepo-final-newline = "hygiene"            # only "hygiene": park a linter rule while debt is cleared

[rules.severity_overrides]
RULE-myrepo-final-newline = "warning"            # error | warning | info

[rules.settings.RULE-myrepo-final-newline]
paths = ["docs/**", "guides/**"]

[[rules.settings.RULE-myrepo-final-newline.overrides]]
path = "docs/generated/**"                       # later matching overrides win; arrays replace
extensions = [".txt"]
```

- Give each exception a TOML comment with its reason; record a lasting policy exception as an ADR.
- `devkit rules explain <RULE-id>` prints the effective settings and each override.
