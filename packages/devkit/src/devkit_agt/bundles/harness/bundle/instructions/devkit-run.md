---
name: devkit-run
description: Read before running tests, linters or type checks outside a project recipe, reading devkit run output, or setting up such recipes.
---

# Running verification commands with `devkit run`

- Run a recipe that already calls `devkit run` as it is, not inside a second
  `devkit run`.
- Act on the printed excerpt first. Read the log at `log=` only for what the
  excerpt lacks: the line range a `[... log lines A-B ...]` marker names
  (`sed -n 'A,Bp' <log>`), or a search (`rg -n "<test name>" <log>`).
- Rerun a `[RUN_FAILURE: "<test>" ...]` by its node ID.

In a project that runs checks through recipes (`just`, `make`, `npm` scripts),
put `devkit run` inside the recipe and shorten the tools' own reports unless the
project needs the long forms:

```just
test *args:
    uv run devkit run -- uv run pytest --tb=short {{args}}

lint:
    uv run devkit run -- uv run ruff check --output-format=concise .
```
