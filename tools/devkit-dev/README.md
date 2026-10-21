# devkit-dev

Repository-only development bundle. Product packages do not depend on it.
`RULE-architecture` checks `.devkit/architecture.toml` using Python's AST, without
importing the modules under inspection. Its instruction documents the package
and layer convention. Template size budgets are a separate check.

The rule always examines the complete declared graph, including when selected
files change: a public facade or manifest change can affect other packages.
Run its bundled tests with `uv run pytest tools/devkit-dev -q`.
