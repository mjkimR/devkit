# devkit-starter

Example content-only wheel for `devkit sync`. Its registered resource module
contains `bundle/bundle.toml`, an instruction, a playbook, and a skill. This
package is the starter example bundle's only copy:
[`src/devkit_starter/bundle`](src/devkit_starter/bundle).

```bash
# Read each URL from the chosen release-inventory.json.
uv add --dev "devkit-dist @ <devkit-dist-inventory-wheel-url>" \
  "devkit-core @ <devkit-core-inventory-wheel-url>" \
  "devkit-cli @ <devkit-cli-inventory-wheel-url>" \
  "devkit-advisory @ <devkit-advisory-inventory-wheel-url>" \
  "devkit-starter @ <devkit-starter-inventory-wheel-url>"
uv run devkit add starter   # records starter = "daily" (the default preset)
```

Content bundles need only `devkit-dist`, which deploys them; a project that uses the harness declares `devkit-agt`
(and its `devkit-dist` wheel) instead.

No rule code is executed by this package. `devkit sync` projects the skill (and
the generated playbook entry skill) for every agent target by default (Codex,
Claude Code and Antigravity); narrow the targets with `--agent codex` or
`--agent claude-code`.
See the `ARCH-05-4-distribution-components`.
