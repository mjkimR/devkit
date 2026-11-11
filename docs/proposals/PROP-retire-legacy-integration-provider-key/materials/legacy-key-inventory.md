# Legacy `[integration] provider` inventory

Evidence for Q1 and Q2, taken at worktree head `ba3bcce4` plus the status commit.

## Q1: consumer configuration (read-only)

`rg -n -A3 '^\[integration' /Users/mj/workspace/workbench/repos/*/.devkit/config.toml`:

| Repository | `[integration]` |
| --- | --- |
| `resource-indexer` | `provider = "spec"` (line 76-77) |
| `app-common`, `autohub`, `rside`, `devkit` and the devkit worktrees | absent |

`resource-indexer` pins every devkit package to rev `76bafbbb` (`pyproject.toml` `[tool.uv.sources]`), so it is
unaffected until it moves its pin; at that upgrade a rejecting reader would fail its `devkit integration` commands
until it deletes the two lines.

## Q2: the reserved-table entry

- `devkit_dist/features/distribution/services/installation/config.py`: `RESERVED_TABLES` holds `integration`; reserved
  tables are passed through unread by devkit-dist and their top-level names are accepted in `FIELDS`. Removing the
  name makes devkit-dist reject `[integration]` as an unknown top-level key on every configuration read.
- devkit-agt registers no `devkit.config_tables` entry for `integration` (`packages/devkit/pyproject.toml`), so the
  template already shows no `[integration]` table.
- The only reader is `devkit_agt/features/integration/services/providers.py` `effective()`; the policy digest already
  excludes `provider`, so dropping the acceptance does not change any digest.

## Development surface

Code: `providers.py` (`effective()` check, its error text and fix, the `policy()` docstring).

Tests writing `provider = "fixture"` or asserting the old fix text:
- `packages/devkit/tests/integration/features/integration/test_policy.py` (`auto_repo`)
- `packages/devkit/tests/integration/features/integration/test_service.py` (`test_unknown_integration_configuration_is_actionable`, the legacy-removal case near line 222)
- `packages/devkit/tests/integration/features/integration/conftest.py` and `packages/devkit/tests/e2e/features/integration/conftest.py` (`repo`)
- `packages/devkit/tests/e2e/features/integration/test_base_advance.py` (config strings)

Documents stating the ignored legacy value:
- `CAP-INT-mcp-services` §5 "Legacy configuration"
- `CAP-DLV-project-policy` §3 (Defaults) sentence
- `CAP-DLV-sdd-baseline-adoption` step 7 and the activation paragraph ("No integration-provider edit is required")
- `UC-adopt-sdd-from-adaptive-development` scenario "Provider-free activation" (Given clause)
- `docs/development/reference/integration.md` lines 11-12 (quick reference)
- `packages/devkit/README.md` integration row still lists "readiness providers"

Left alone: the `ready_provider` test fixtures and the exported `Readiness`/`Evidence` models. The fixtures assert the
provider is never called (the `CAP-INT-mcp-services` §4 content boundary guard), so they are not readers of the key.
