# devkit-catalog

Opt-in content bundles for `devkit sync`. Installing the wheel makes every bundle
below available, but none declares `auto_select`: a bundle is deployed only once
the project selects it with `devkit add`, and a preset picks its assets.

| Bundle | Presets (default first) | Contents |
| --- | --- | --- |
| `github-milestones` | `all`, `conventions` | Milestone sizing and issue-linking instruction; `decompose-initiative` playbook (`gh` CLI) |

```bash
uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
uv run devkit list                                   # catalog bundles are listed as unselected
uv run devkit add github-milestones                  # the default preset (all)
uv run devkit add github-milestones:conventions      # or only the instruction
```

## Adding a bundle

A catalog bundle holds content only: instructions, playbooks, skills, documents,
guidance fragments and rules. A bundle that needs devkit code (a gate, a workflow
check, a command) belongs in `devkit-agt` instead.

1. Create `src/devkit_catalog/<module>/__init__.py` (empty) and
   `src/devkit_catalog/<module>/bundle/bundle.toml` with the package version.
2. Register it under `[project.entry-points."devkit.bundles"]` with the bundle
   name as the entry point name.
3. Declare a `default_preset`; never declare `auto_select`.
4. Add a row to the table above and to the recommendation table in
   [Bundle Recommendations](../../guides/install/bundle-recommendations.md), with the signal that warrants it.

`tests/test_bundles.py` enforces the entry point, version, opt-in and naming
rules. See [Content Packages](../../docs/distribution/content-packages.md) and the
[Manifest Specification](../../docs/distribution/manifest-spec.md).
