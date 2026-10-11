# devkit-distribution

Initial Python tooling for devkit agent asset bundles. The CLI is `devkit`; the
proposed consumer root is `.devkit/`.

```bash
uv run --package devkit-distribution devkit bundle validate examples/bundles/starter
uv run --package devkit-distribution devkit bundle build examples/bundles/starter --output /tmp/starter.zip
uv run --package devkit-distribution devkit plan examples/bundles/starter --preset daily
```

Build refuses to replace existing output. ZIP entries have stable timestamps,
sorted paths, SHA-256 inventory, and normalized modes (0644 or 0755). Skill trees
include their references, scripts, and other assets. Symlinks and nonregular files
are rejected. Builds copy declared sources without rendering native content.

## Manifest v1

`bundle.toml` declares `schema = 1`, a lowercase slug `name`, an `X.Y.Z` version,
and a nonempty `[[assets]]` list. Each asset has a bundle-unique slug `id`, a
`kind` (`skill`, `subagent`, `instruction`, `playbook`, or `rule`), and exactly
one `source` or `variants` table. Sources are existing relative POSIX paths.
Skills must be directories containing `SKILL.md`. Optional `[presets.<name>]`
tables select a nonempty list of asset IDs through `assets`.

Native variants can be declared without converting their contents:

```toml
[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/codex/reviewer.toml"
claude-code = "native/claude-code/reviewer.md"
```

Variant names are labels, not claims of supported agent loading. Agent adapters
and version compatibility checks are not implemented yet. The schema rejects
unknown manifest keys; native file contents remain opaque bytes.

## Current boundary

Implemented: local validation, deterministic packaging, and managed inventory
planning with optional preset selection. Plan does not inspect a consumer or
detect installed-file conflicts. It does not perform native projection.

Not implemented: archive ingestion, install/restore/upgrade/recover, receipts,
agent adapters, dependencies, rule runtime, and remote release acquisition.
Rule files are packaged as content and are not imported by this tool.
See the [distribution design](../../docs/architecture/agent-distribution.md).
