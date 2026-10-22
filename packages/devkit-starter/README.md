# devkit-starter

Example content-only wheel for `devkit sync`. Its registered resource module
contains `bundle/bundle.toml`, an instruction, a playbook, and a skill. This
package is the starter example bundle's only copy:
[`src/devkit_starter/bundle`](src/devkit_starter/bundle).

```bash
base=https://github.com/mjkimR/devkit/releases/download/v<version>
uv add --dev "devkit-dist @ $base/devkit_dist-<version>-py3-none-any.whl" \
  "devkit-core @ $base/devkit_core-<version>-py3-none-any.whl" \
  "devkit-cli @ $base/devkit_cli-<version>-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-<version>-py3-none-any.whl" \
  "devkit-starter @ $base/devkit_starter-0.1.0-py3-none-any.whl"
uv run devkit add starter   # records starter = "daily" (the default preset)
```

Content bundles need only `devkit-dist`, which deploys them; a project that uses the harness declares `devkit-agt`
(and its `devkit-dist` wheel) instead.

No rule code is executed by this package. `devkit sync` projects the skill (and
the generated playbook entry skill) for every agent target by default (Codex,
Claude Code and Antigravity); narrow the targets with `--agent codex` or
`--agent claude-code`.
See the `ARCH-05-4-distribution-components`.
