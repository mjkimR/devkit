# devkit-catalog

Opt-in content bundles for `devkit sync`. Installing the wheel makes every bundle
below available, but none declares `auto_select`: a bundle is deployed only once
the project selects it with `devkit add`, and a preset picks its assets.

| Bundle | Presets (default first) | Contents |
| --- | --- | --- |
| `response-style` | `all` | Answer-first user-facing replies that keep decision-critical facts, with configurable conversation language |
| `maintenance` | `all`, `upkeep`, `reporting` | Manual drift reconciliation and evidence-based weekly reporting |
| `cli-tool` | `all`, `guide` | Structure guide for agent-facing click tools on `devkit-cli`, with rules for command boundaries, library output and heavy imports; `CAP-CLI-agent-cli-toolkit` |
| `host-observer` | `all` | Codex lifecycle hook registrations using devkit's metadata-only observer; `CAP-HOST-lifecycle-observation` |

```bash
uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
uv run devkit list                                   # catalog bundles are listed as unselected
uv run devkit add host-observer                      # the default preset (all)
```

## Adding a bundle

A catalog bundle holds content only: instructions, playbooks, skills, documents,
guidance fragments, rules and declarative hooks using installed devkit handlers (its rules run where `devkit-agt` is
installed). A bundle that needs devkit code (a gate, a workflow check, a command) belongs in `devkit-agt` instead.
The tests load the bundles with the manifest reader of `devkit-dist`; rule tests use the rules engine of `devkit-agt`.

1. Create `src/devkit_catalog/<module>/__init__.py` (empty) and
   `src/devkit_catalog/<module>/bundle/bundle.toml` with the package version.
2. Register it under `[project.entry-points."devkit.bundles"]` with the bundle
   name as the entry point name.
3. Declare a `default_preset`; never declare `auto_select`.
4. Add a row to the table above and to the recommendation table in
   [Bundle Recommendations](../../guides/install/bundle-recommendations.md), with the signal that warrants it.

`tests/integration/bundles/test_bundles.py` enforces the entry point, version, opt-in and naming
rules. See `CAP-DIST-content-packages` and the
`CAP-DIST-manifest-spec`.

## Response style

`devkit add response-style` installs the `response-style` skill and an `AGENTS.md` line that every session sees: the
core rule for replies to the user (answer first, keep every number, condition or risk they need, cut the rest) and a
reminder to read and apply the skill first. Configure the default conversation language before syncing (the default `auto` follows the current request):

```toml
[bundles.response-style.variables]
language = "ko"
```

Run `devkit sync` after changing variables. Language values are natural-language names or codes understood by the
agent, not a closed locale registry. The language is rendered into the skill from `SKILL.md.jinja`; the root
reminder only references the skill. Documentation and code-comment language still follow repository requirements.

## Maintenance

`devkit add maintenance` deploys both independent playbooks; `maintenance:upkeep` selects
`drift-reconciliation` and `maintenance:reporting` selects `weekly-report`. Invoke explicitly through
`devkit-playbook` or exact `devkit playbook get maintenance/weekly-report`; selection never executes them.
Drift reports record evidence, user decisions and coverage gaps. Weekly reports preserve revision-bound evidence,
health limitations and prioritized actions in immutable local artifacts; publication needs separate explicit
authority and records its outcome independently. Missing tools remain gaps. No runtime, scheduler, detector,
mandatory companion run or history backend is added. See `CAP-DLV-drift-reconciliation` and `CAP-DLV-weekly-report`.
