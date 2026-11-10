# devkit-catalog

Opt-in content bundles for `devkit sync`. Installing the wheel makes every bundle
below available, but none declares `auto_select`: a bundle is deployed only once
the project selects it with `devkit add`, and a preset picks its assets.

| Bundle | Presets (default first) | Contents |
| --- | --- | --- |
| `adaptive-dev` | `core`, `agents`, `import` | Adaptive product iteration, optional support and mutable current context without SDD delivery records; `agents`: the three reusable swarm archetypes alone; `import`: the user-invoked `/adaptive-import` entry and its `agent-asset-conversion` playbook alone |
| `deep-research` | `core` | A user-invoked research team that compares directions and retains one indexed material per investigation, under either development approach |
| `app-uiux-improve` | `core` | User-invoked UI/UX improvement for software interfaces: proportionate object framing, optional local perspectives or a user-selected Impeccable session, and implementation through the consumer workflow |
| `design-explore` | `core` | User-invoked general solution design with optional local premise exploration, mechanisms and tradeoffs; conversation-first result |
| `response-style` | `all` | Answer-first user-facing replies that keep decision-critical facts, with configurable conversation language |
| `maintenance` | `all`, `upkeep`, `reporting`, `refactoring`, `performance`, `testing` | Manual drift reconciliation, evidence-based weekly reporting, review and refactoring passes, performance passes, and test-management assessments |
| `command-design` | `core` | Creation-time guidance for necessary justfile, CLI and MCP entry points; one conditional instruction, no always-loaded pointer |
| `cli-tool` | `all`, `guide` | Structure guide for agent-facing click tools on `devkit-cli`, with rules for the feature layout, layer imports, command boundaries, library output and heavy imports; `CAP-CLI-agent-cli-toolkit` |

```bash
uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
uv run devkit list                                   # catalog bundles are listed as unselected
uv run devkit add response-style                    # an opt-in catalog bundle
```

## Adaptive development

`uv run devkit add adaptive-dev` explicitly selects the `adaptive-dev` bundle. Install devkit-docs alongside catalog for
shared document formats; devkit-spec is not required. `/adaptive-dev` checks the effective development approach through
`uv run devkit config show` before product actions. Selection changes assets, not project policy.

The coordinator adapts clarification, research, implementation and actual-usage verification to the next useful
action, with optional product-clarifier, product-researcher and usage-reviewer assignments and no required team
size or role sequence. A small question can stay inline.

The coordinator keeps mutable current facts, retained note links and useful alternative reopening conditions in
project-owned `.devkit/adaptive-dev.md`; sync never seeds or overwrites it.
No per-change SDD Unit, envelope or immutable experiment history is required. Independent project checks still run.
An explicit adoption request prepares spec assets while keeping adaptive development active, then uses the separately
delivered `sdd-baseline` playbook for readiness and activation.

`/adaptive-import <Git URL or local path> [conditions]` declares `invocation = "user"` and runs only when the user
invokes it; no other asset of the bundle names or suggests it. It reads a third-party repository of subagents or
skills as untrusted data in a temporary clone, executes nothing from it, recommends at most five fitting items and
stops for one selection round. The selection invokes the `agent-asset-conversion` playbook
(`uv run devkit playbook get adaptive-dev/agent-asset-conversion`), which rewrites each selected item, by default as a
role overlay for `swarm-planner`, `swarm-worker` or `swarm-verifier`, without the source's authority, model or
host-specific content, and places it in the project's own in-repository bundle with a provenance line. It never
imports a whole pack, needs no approach check and changes no approach or host setting.
`uv run devkit add adaptive-dev:import` adds the two assets to a project that selects only `adaptive-dev:agents`.
`CAP-DLV-adaptive-development` holds the contract.

## Deep research

`uv run devkit add deep-research` explicitly selects the research bundle. It installs with devkit-docs and catalog,
needs no devkit-spec and runs under either development approach without reading or changing it. Its entry declares
`invocation = "user"` and runs only when the user invokes it; no other skill, pointer or guide suggests it. The
invoking agent coordinates optional direction-explorer, discovery-critic, discovery-planner and
research-investigator assignments in ignored transient run directories and retains each investigation as one
indexed material under `docs/materials/`, which proposals, specs, decisions and current context cite by its
`MAT-<slug>` ID. The entry never commits; its report tells the user to commit the material through the project's
Git policy. It creates no work unit, approval or envelope.

An installation of the former `incubation` bundle from before the research split loses the research entry and the
three moved roles on upgrade; sync removes their unmodified projections and announces the bundle once with
`BUNDLE_UNSELECTED`. Before selecting it, move each customization of a moved role:

- Remove research `incubation:<role>` and `deep-research:<role>` keys under `[subagents.roles]`; these roles are no longer registered subagents and stale keys fail sync.
- Port role body customizations from `.devkit/overrides/incubation/subagents/<role>.md` or `.devkit/overrides/deep-research/subagents/<role>.md` into the skill override's `roles/<role>.md` through `devkit override`; remove obsolete subagent frontmatter.
- Preserve host tool and sandbox restrictions through the invoking host; skill-local role files do not apply native execution settings.
- Move or delete an edited projection that sync left with `ORPHAN_LEFT`; `uv run devkit add deep-research` is
  refused until then.

See `CAP-DLV-deep-research`.

## UI/UX improvement

`uv run devkit add app-uiux-improve` selects the content-only bundle with no required docs or spec package.
Explicitly invoke `/app-uiux-improve <goal>` to improve a software interface or flow. Before restructuring views or
flows, the coordinator frames the affected objects, from the project's glossary, object register and UX documents
when they exist. It implements inline, optionally with the skill-local designer, unconventional-designer,
reference-researcher and critic roles, or, on the user's selection, briefs one separately installed Impeccable session
and accepts its changes against a recorded base. Implementation and checks follow the consumer's existing workflow;
review-only requests stay read-only. Installation, ignore entries and cleanup happen only on the user's request.
No fixed team, design score, research report or comparison experiment is required.
Selection starts no work and changes no development policy. The [usage guide](src/devkit_catalog/app_uiux_improve/bundle/README.md)
covers setup, the per-task flow and troubleshooting. See `CAP-DLV-uiux-improvement`.

## General solution exploration

`uv run devkit add design-explore` selects the content-only bundle; dist and catalog suffice.
Explicitly invoke `/design-explore <problem>` for architecture, data models, module boundaries or workflows.
Optional solution-explorer instances use different premises; reference-researcher and design-critic serve concrete
questions. Local roles stay out of global specialist lists. Small questions can stay inline, with no required cast,
option count, score, research report or comparative-benefit experiment. The result stays in conversation unless a
destination is requested; only the coordinator writes it. Exploration grants no implementation, commit, approval
or publication authority. Selection starts no work and changes no development approach. See `CAP-DLV-design-exploration`.

## Command design

`uv run devkit add command-design` selects one instruction for creating, configuring or extending justfile,
CLI and MCP interfaces. It asks for the operation and caller before adding an entry point, reuses suitable
commands and keeps detailed help conditional. It adds no runtime generator, automatic cleanup or guidance
pointer. `cli-tool` separately covers Python CLI implementation; `maintenance:refactoring` covers requested
cleanup of existing interfaces. See `CAP-HARN-command-design`.

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

`devkit add maintenance` deploys the five playbooks; `maintenance:upkeep` selects
`drift-reconciliation` and `review-refactor`, `maintenance:reporting` selects `weekly-report`,
`maintenance:refactoring` selects `review-refactor` alone and `maintenance:performance` selects `performance-pass`
with `review-refactor`, whose application sections it reads as reference text.
`maintenance:testing` selects `test-management` alone. Invoke them explicitly through
`devkit-playbook` or exact `devkit playbook get maintenance/weekly-report`, or confirm the one-line offer that
`spec` intake makes when a request names their operation; selection never executes them.
Drift reports record evidence, user decisions and coverage gaps. Weekly reports preserve revision-bound evidence,
health limitations and prioritized actions in immutable local artifacts; publication needs separate explicit
authority and records its outcome independently. Review-refactor runs review user-selected code, guidance or CLI roots one
surface batch at a time and apply only agreed consolidations and reductions with preservation evidence; contract
removals become separate work items. Performance passes measure user-selected slow operations unprofiled and
interleaved, attribute their cost, and apply only agreed behavior-preserving speedups with measured before/after and
differential evidence; contract-changing speedups become separate work items, and no timing script is bundled.
Test-management assessments inspect collection/resource prerequisites before execution, preserve consumer test
ownership and completion gates, and route only user-decided changes through the native workflow. Pytest guidance
loads conditionally; runner defaults require local coverage/isolation evidence. Unattended runs apply nothing.
Missing tools remain gaps. No runtime, scheduler, detector, mandatory companion run or history backend is added.
See `CAP-DLV-drift-reconciliation`, `CAP-DLV-weekly-report`, `CAP-DLV-review-refactor` and
`CAP-DLV-performance-pass` and `CAP-DLV-test-management`.
