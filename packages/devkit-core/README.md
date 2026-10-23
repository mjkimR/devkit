# devkit-core

Shared foundation in the independent `devkit_core` Python package. Implementations live in
`devkit_core.core`: atomic file writes, locks, paths, Git execution, deadlines, frontmatter and the shared LibYAML safe parser,
plugin loading, extension dispatch and logging. Shared errors and SDK-free MCP contracts live in
`devkit_core.base.errors` and `devkit_core.base.mcp`. The thin `devkit_core.base.usecase.BaseUseCase`
identifies application entrypoints through an abstract `execute` method. Concrete synchronous or asynchronous
operations declare their own argument and result types. It adds no execution or authorization policy. The dependency direction is `core -> base`;
base imports only the standard library, advisory and its own contracts. Types tied to an implementation
(such as `Frontmatter` and `PluginPackage`) stay with that implementation.

Depends only on `devkit-advisory` and PyYAML. It has no CLI, entry points, project configuration,
installation receipts, host runtime or dependencies on other devkit application packages.
Configuration, receipt policy and CLI helpers remain in `devkit-dist`.

Run `just test devkit-core`, `just lint-check devkit-core` and `just check devkit-core` from the
repository root. Existing behavior tests travel with their implementation; package contract tests
also enforce independent ownership and imports.
