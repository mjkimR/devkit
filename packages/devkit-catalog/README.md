# devkit-catalog

Opt-in content bundles for `devkit sync`. Installing the wheel makes every bundle
below available, but none declares `auto_select`: a bundle is deployed only once
the project selects it with `devkit add`, and a preset picks its assets.

| Bundle | Presets (default first) | Contents |
| --- | --- | --- |
| `response-style` | `all` | Concise user-facing replies with configurable conversation language |
| `host-observer` | `all` | Codex lifecycle hook registrations using devkit's metadata-only observer; `CAP-HOST-lifecycle-observation` |

```bash
uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
uv run devkit list                                   # catalog bundles are listed as unselected
uv run devkit add host-observer                      # the default preset (all)
```

## Adding a bundle

A catalog bundle holds content only: instructions, playbooks, skills, documents,
guidance fragments, rules and declarative hooks using installed devkit handlers. A bundle that needs devkit code (a gate, a workflow
check, a command) belongs in `devkit-agt` instead.

1. Create `src/devkit_catalog/<module>/__init__.py` (empty) and
   `src/devkit_catalog/<module>/bundle/bundle.toml` with the package version.
2. Register it under `[project.entry-points."devkit.bundles"]` with the bundle
   name as the entry point name.
3. Declare a `default_preset`; never declare `auto_select`.
4. Add a row to the table above and to the recommendation table in
   [Bundle Recommendations](../../guides/install/bundle-recommendations.md), with the signal that warrants it.

`tests/test_bundles.py` enforces the entry point, version, opt-in and naming
rules. See `CAP-DIST-content-packages` and the
`CAP-DIST-manifest-spec`.

## Response style

`devkit add response-style` installs independently authored communication instructions. Configure the default
conversation language before syncing (the default `auto` follows the current request):

```toml
[bundles.response-style.variables]
language = "ko"
```

Run `devkit sync` after changing variables. Language values are natural-language names or codes understood by the
agent, not a closed locale registry. Documentation and code-comment language still follow repository requirements.
