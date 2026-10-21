# devkit-dev

Repository-only development package and convention bundle. Product runtime packages
do not depend on it. Shared test helpers may live in a named `devkit_dev.testing`
module when multiple devkit packages actually need them; consume them only from
tests through development dependencies. Keep package-specific helpers in that
package's `tests/support/`, and do not create a test framework before there is a
shared need.

`RULE-architecture` checks `.devkit/architecture.toml` using Python's AST, without
importing the modules under inspection. Its instruction documents the package
and layer convention, test boundary categories, and executable bundle placement.
Package management code is allowed in `__init__.py`; business behavior belongs in
named layer modules, a responsibility checked in review. Template size budgets
are a separate check.

The rule always examines the complete declared graph, including when selected
files change: a public facade or manifest change can affect other packages.
Feature dependency declarations and the actual import graph must be acyclic.
Every feature declares its permitted feature dependencies, including dependencies
across packages; public API access does not grant permission to reverse direction.
Run its bundled tests with `uv run pytest tools/devkit-dev -q`.
