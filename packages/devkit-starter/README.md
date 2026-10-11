# devkit-starter

Example content-only wheel for `devkit sync`. Its registered resource module
contains `bundle/bundle.toml`, an instruction, a playbook, and a skill.

```bash
uv add --dev devkit-distribution devkit-starter
uv run devkit sync --preset starter:daily
```

No rule code is executed by this package. Native placement requires an explicit
`--agent codex` or `--agent claude-code` selection on sync.
