# devkit-starter

Example content-only wheel for `devkit sync`. Its registered resource module
contains `bundle/bundle.toml`, an instruction, a playbook, and a skill. This
package is the starter example bundle's only copy:
[`src/devkit_starter/bundle`](src/devkit_starter/bundle).

```bash
uv add --dev devkit devkit-starter
uv run devkit add starter   # records starter = "daily" (the default preset)
```

No rule code is executed by this package. `devkit sync` projects the skill (and
the generated playbook entry skill) for every agent target by default (Codex,
Claude Code and Antigravity); narrow the targets with `--agent codex` or
`--agent claude-code`.
See the [distribution documentation](../../docs/distribution/overview.md).
