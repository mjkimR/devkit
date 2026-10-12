# Transitive Dependencies and Python Packaging Integration

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit-distribution`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Bundle Manifest Specification](manifest-spec.md)
- [Synchronization & Transactions](sync-and-transactions.md)
- [In-Repository Bundles](in-repo-bundles.md)

---

## 1. The uv Dev Dependency Model

Rather than establishing an external artifact registry or proprietary CLI resolver, `devkit` relies on Python's mature packaging ecosystem:

```bash
# Add distribution CLI and content packages to the project
uv add --dev devkit-distribution devkit-starter

# Select the bundle (records it in .devkit/config.toml) and synchronize
uv run devkit add starter
uv run devkit sync --agent codex --agent claude-code

# Verify synchronized resources
uv run devkit list
```

### Why Project-Level Dev Dependencies?

Running `uv tool install --global devkit-distribution` installs the CLI into an isolated tool environment. In that isolated environment, `importlib.metadata` cannot discover content packages installed inside the consumer project's virtual environment. Using `uv run devkit sync` ensures the CLI executes within the project's dev environment, discovering all installed content wheels seamlessly.

### Upgrades and Teardown
- **Upgrade**: Run `uv lock --upgrade-package <package>`, then run `uv run devkit sync`.
- **Teardown**: Run `uv run devkit remove <bundle>`, then `uv remove --dev <package>`. A bundle still selected in `config.toml` but no longer installed is a sync error, so deselect before uninstalling.
- **Clean Checkout Replication**: Run `uv sync`, then run `uv run devkit sync`. If the repository ignores managed and native files, `sync` cleanly reconstructs the selected projections from installed wheels.

---

## 2. Transitive Bundle Distribution and Dependency Boundaries

Python content wheels naturally inherit `uv` and Python packaging dependency resolution semantics. When a bundle package (`packageB`) depends on an upstream package (`packageA`), the distribution boundary between runtime inheritance and internal tooling is determined by standard dependency declarations in `packageB`'s `pyproject.toml`:

### 1. Layered / Meta Bundles (`dependencies = [...]`)
- Declaring `packageA` in `[project.dependencies]` includes it in the built wheel's `Requires-Dist` metadata.
- When consumer project `repo C` adds `packageB` as a dev dependency (`uv add --dev packageB`), `uv` transitively installs `packageA` into `repo C`'s virtual environment.
- Because `devkit` discovers bundles via `importlib.metadata.entry_points(group="devkit_distribution.bundles")`, `packageA`'s bundle becomes **available** in `repo C`. It is deployed only after `repo C` selects it (`devkit add packageA`); until then `devkit sync` lists it under `unselected`.
- **Use Case**: Composing layered agent configurations (e.g., a domain bundle `team-backend` inheriting organization-wide base standards from `company-base`).

### 2. Isolated Tooling & Testing (`dependency-groups.dev = [...]`)
- Declaring `packageA` in development groups (`[dependency-groups.dev]`) keeps the dependency strictly internal to `packageB`'s local repository.
- Wheel builds omit development dependencies. When `repo C` installs `packageB`, `packageA` is neither installed nor discovered.
- **Use Case**: Authoring packages that consume utility bundles or test suites locally without leaking upstream assets to downstream consumers.

### 3. Consumer Opt-In (`[presets]`)
- Availability follows Python dependency resolution; deployment follows the consumer's `.devkit/config.toml`. A transitively installed bundle is never deployed until the consumer selects it:
  ```toml
  schema = 1

  [presets]
  packageB = "default-preset-name"
  packageA = "all"
  ```
- Because opt-in is the default, there is no opt-out list. See [Synchronization & Transactions](sync-and-transactions.md#2-asset-selection-model).
