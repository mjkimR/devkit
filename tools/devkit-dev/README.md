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

The `handbook` preset ships the `handbook` playbook: the on-request refresh of the release handbook under
`handbook/` during release preparation (`CAP-DLV-release-handbook`). Its script is the repository's
`scripts/handbook.py` (`just handbook ...`); `tests/integration/test_handbook_script.py` covers the script and the
release-build check.

`RULE-usecase-boundaries` enforces typed `BaseUseCase.execute` at CLI/MCP
execution boundaries. Internal helper functions remain valid. The AST check follows
explicit aliases, facade exports and retained instances; constructors wire dependencies
and defer operations to `execute`. Exact callable transport helper exceptions use
`[[usecase_exceptions]]` with `source`, `target` and `reason` in the architecture
declaration. Stale exceptions fail. Computed dispatch and semantic side effects still
require review; this rule is not a runtime approval or authorization mechanism.
