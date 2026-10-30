# devkit-catalog

Opt-in content bundles for `devkit sync`. Installing the wheel makes every bundle
below available, but none declares `auto_select`: a bundle is deployed only once
the project selects it with `devkit add`, and a preset picks its assets.

| Bundle | Presets (default first) | Contents |
| --- | --- | --- |
| `incubation` | `core` | Adaptive product iteration, optional support and mutable current context without SDD delivery records |
| `deep-research` | `core` | A user-invoked research team that compares directions and retains one indexed material per investigation, under either development approach |
| `response-style` | `all` | Answer-first user-facing replies that keep decision-critical facts, with configurable conversation language |
| `maintenance` | `all`, `upkeep`, `reporting`, `refactoring`, `performance` | Manual drift reconciliation, evidence-based weekly reporting, review and refactoring passes, and performance passes |
| `cli-tool` | `all`, `guide` | Structure guide for agent-facing click tools on `devkit-cli`, with rules for the feature layout, layer imports, command boundaries, library output and heavy imports; `CAP-CLI-agent-cli-toolkit` |

```bash
uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
uv run devkit list                                   # catalog bundles are listed as unselected
uv run devkit add response-style                    # an opt-in catalog bundle
```

## Incubation

`uv run devkit add incubation` explicitly selects the incubation bundle. Install devkit-docs alongside catalog for
shared document formats; devkit-spec is not required. `/incubate` checks the effective development approach through
`uv run devkit config show` before product actions. Selection changes assets, not project policy.

The coordinator adapts clarification, research, implementation and actual-usage verification to the next useful
action, with optional product-clarifier, incubation-researcher and usage-reviewer assignments and no required team
size or role sequence. A small question can stay inline.

The coordinator keeps mutable current facts, retained note links and useful alternative reopening conditions in
project-owned `.devkit/incubation.md`; sync never seeds or overwrites it.
No per-change SDD Unit, envelope or immutable experiment history is required. Independent project checks still run.
An explicit adoption request prepares spec assets while keeping incubation active, then uses the separately
delivered `sdd-baseline` playbook for readiness and activation.

## Deep research

`uv run devkit add deep-research` explicitly selects the research bundle. It installs with devkit-docs and catalog,
needs no devkit-spec and runs under either development approach without reading or changing it. Its entry declares
`invocation = "user"` and runs only when the user invokes it; no other skill, pointer or guide suggests it. The
invoking agent coordinates optional direction-explorer, discovery-critic, discovery-planner and
research-investigator assignments in ignored transient run directories and retains each investigation as one
indexed material under `docs/materials/`, which proposals, specs, decisions and current context cite by its
`MAT-<slug>` ID. The entry never commits; its report tells the user to commit the material through the project's
Git policy. It creates no work unit, approval or envelope.

An incubation installation from before the research split loses the research entry and the three moved roles on
upgrade; sync removes their unmodified projections and announces the bundle once with `BUNDLE_UNSELECTED`. Before
selecting it, move each customization of a moved role:

- Rename an `incubation:<role>` key under `[subagents.roles]` to `deep-research:<role>`; sync fails until then.
- Move `.devkit/overrides/incubation/subagents/<role>.md` to `.devkit/overrides/deep-research/subagents/`; the
  override silently stops applying until then.
- Move or delete an edited projection that sync left with `ORPHAN_LEFT`; `uv run devkit add deep-research` is
  refused until then.

See `CAP-DLV-deep-research`.

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

`devkit add maintenance` deploys the four playbooks; `maintenance:upkeep` selects
`drift-reconciliation` and `review-refactor`, `maintenance:reporting` selects `weekly-report`,
`maintenance:refactoring` selects `review-refactor` alone and `maintenance:performance` selects `performance-pass`
with `review-refactor`, whose application sections it reads as reference text. Invoke them explicitly through
`devkit-playbook` or exact `devkit playbook get maintenance/weekly-report`, or confirm the one-line offer that
`spec` intake makes when a request names their operation; selection never executes them.
Drift reports record evidence, user decisions and coverage gaps. Weekly reports preserve revision-bound evidence,
health limitations and prioritized actions in immutable local artifacts; publication needs separate explicit
authority and records its outcome independently. Review-refactor runs review user-selected code, guidance or CLI roots one
surface batch at a time and apply only agreed consolidations and reductions with preservation evidence; contract
removals become separate work items. Performance passes measure user-selected slow operations unprofiled and
interleaved, attribute their cost, and apply only agreed behavior-preserving speedups with measured before/after and
differential evidence; contract-changing speedups become separate work items, and no timing script is bundled.
Missing tools remain gaps. No runtime, scheduler, detector, mandatory companion run or history backend is added.
See `CAP-DLV-drift-reconciliation`, `CAP-DLV-weekly-report`, `CAP-DLV-review-refactor` and
`CAP-DLV-performance-pass`.
