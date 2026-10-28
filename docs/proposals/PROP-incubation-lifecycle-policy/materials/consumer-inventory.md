# Lifecycle consumer inventory and alternatives

Baseline: `d990308eca04fd4f18a80d7b2f7278ca14aa128f`, after document bundle distribution integration.
This is source inspection, not a before/after performance or installation measurement.

## Evidence

- `packages/devkit-spec/pyproject.toml:18-49`: package registration includes bundle/CLI, cleanup, readiness,
  attachment, hygiene, status-overlay and config-template extensions; Python installation is independent of asset selection.
- `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/cleanup.py:66-67` and
  `features/governance/usecases/hygiene.py:40-43`: some lifecycle extensions already use managed spec directory presence.
- `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py:124-153`: SDD policy validation
  and independent cumulative linter rules share the provider. `:166-180` adds SDD unit/branch requirements.
  `:347-405` adds session SDD depth/kind/effort and touched-unit completion requirements.
- `packages/devkit/src/devkit_agt/features/integration/usecases/service.py:176-231`: base approval/provider
  selection, source policy restrictions, generic finish guards and provider readiness precede integration.
- `packages/devkit/src/devkit_agt/features/integration/services/providers.py:42-61,115-160`: the generic policy
  digest and installed-provider lookup already separate provider identity from provider-owned evidence.
- `packages/devkit-dist/src/devkit_dist/features/project/repositories/project.py:195-226`: common shared/committed
  TOML reader; each owner validates its table. devkit-core need not learn application settings.
- `packages/devkit-dist/src/devkit_dist/features/project/repositories/local_config.py:71-84`: local keys are
  allowlisted; delivery approach is not currently a clone preference.
- `packages/devkit-dist/src/devkit_dist/features/distribution/cli/configuration.py:22-40`: JSON-only `config show`
  already exposes effective settings and sources through an owning use case.
- `packages/devkit/src/devkit_agt/features/rules/usecases/project.py:156-175` and
  `features/rules/services/evaluator.py:49-79`: active rule scope and target-only skipped IDs exist; policy omissions
  need explicit reporting rather than returning an empty violation list and calling it a pass.
- `packages/devkit-spec/src/devkit_spec/features/governance/usecases/spec_lifecycle.py:77-109`: lifecycle checks/fixes
  act on discovered spec bundles. Applicability must preserve bound historical ownership, including comparison deletions.
- `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/attach.py`: the installed hook understands only
  SDD activity/anchor relationships; it must not reject a non-SDD custom Unit solely because spec is installed.
- `packages/devkit-spec/src/devkit_spec/features/proposals/services/planning.py:17`: status overlay reports existing
  Planning state. Read-only display need not create a lifecycle obligation.

## Options

| Option | Benefit | Cost or failure trigger |
| --- | --- | --- |
| Infer from installed Python package | No extra setting | Optional tooling installation changes policy; assets and installed extensions disagree. |
| Infer from selected spec assets | Reuses selection | Asset removal becomes a policy switch; existing hooks inspect managed state inconsistently and stale/unsynced files become authority. Clone variables and generic asset choices are not lifecycle consent. |
| Application-owned `[tool.spec]` setting | Reuses SDD policy | Cannot inspect or enforce common policy without optional devkit-spec; contradicts the independent document path. |
| Shared devkit-dist `[development]` setting (recommended) | Explicit project intent, available without SDD, stable snapshot authority | Adds a validated shared key and consumer wiring; generic reporting/provider work is required. |

No existing reader supplies this semantic contract. The recommendation adds behavior across existing components,
not an independently required package-layout refactor. Default SDD preserves existing consumers; selecting incubation
is explicit and does not grant authority to rewrite historical Units or alter independent checks.

## Verification limits

No production code is changed in Planning. Direct library entrypoint coverage, applicability details and runtime
report fields are implementation work constrained by proposal AC-01 through AC-08. A built consumer with devkit-spec
absent, a consumer with it installed and retained-history snapshot tests are required Development evidence.
