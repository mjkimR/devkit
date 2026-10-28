# Baseline adoption scenario evidence

Source: accepted stacked head `a137b7011df36c3fe19335fc70560060e779a9f3` plus this turn's baseline assets and exercise test.

Executed command:

```sh
uv run pytest packages/devkit-spec/tests/e2e/bundles/spec/test_sdd_baseline_scenarios.py packages/devkit-spec/tests/integration/bundles/spec/test_sdd_baseline_guidance.py --basetemp .devkit/transient/incubation-baseline/run-03 -q
```

Observed result: 8 passed in 19.33 seconds (five scripted product scenarios and three asset checks). Actual policy, catalog guidance and CLI code ran without runtime stubs. User decisions and sample product inputs are explicitly synthetic test data.

The coordinator actions are scripted; these results do not establish autonomous product-scope inference. This feature has no deterministic baseline readiness engine. Actual terminal observations and source identities are retained in ignored fixture reports; semantic comparison remains a coordinator/reviewer responsibility.

Retained flow: append/list a local JSON note. Excluded: multi-user/network behavior. Independent check: Python unittest invokes the actual app in a temporary store. Usage check: actual add/list commands use the same store. Document verification: actual devkit rules check.

| Scenario | Actual outcome |
| --- | --- |
| Ready, initial project provider | Independent app test, add/list and document checks passed; explicitly simulated effects changed approach and provider; sync/config inspection passed; subsequent spec new/next requested ordinary plan-intent |
| Ready, initial spec provider | Same checks passed; provider remained spec; subsequent SDD routing observed |
| Missing usage evidence | Document rules passed, required usage intentionally unexecuted; report gap, incubation retained and no Unit created |
| Changed source | App hash changed after verification; actual repeated unittest failed with AssertionError; report gap and incubation retained |
| Partial sync failure | Injected missing preset caused actual sync exit 2 after policy edit; approach remained sdd, proving no automatic rollback; explicit valid-preset recovery restored sync consistency |

Successful cases create only the subsequent-request skeleton, never a historical baseline Unit or reconstructed approval. Provider project-to-spec is included in the exact simulated activation effects; an existing spec provider is preserved.

## Observed fixture identities

### test_actual_sync_failure_repor0

Fixture report: `.devkit/transient/incubation-baseline/run-03/test_actual_sync_failure_repor0/consumer/docs/materials/2026-10/20261028-sdd-baseline/report.md`.

Revision: 17148d8c240d7aa8aac19ffc6e1e5a4301eb8b11
Evidence app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Current app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Retained coverage status: verified. Explicit recovery restored core selection and sync consistency; original app evidence unchanged.
Simulated user decision (test data, not real user authority): synthetic recovery for same effects

### test_changed_source_invalidate0

Fixture report: `.devkit/transient/incubation-baseline/run-03/test_changed_source_invalidate0/consumer/docs/materials/2026-10/20261028-sdd-baseline/report.md`.

Revision: 2d7642047865b6eb44d95746cf0aa936287b198a
Evidence app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Current app SHA256: 68de0cc774571953c8688d6d3faf85f92f8e6769f31b9b74088ee103b8e6cf50
Retained coverage status: gap. Relevant source changed; recheck failed the retained behavior, so activation is blocked.
Simulated user decision (test data, not real user authority): pending

### test_missing_required_usage_ev0

Fixture report: `.devkit/transient/incubation-baseline/run-03/test_missing_required_usage_ev0/consumer/docs/materials/2026-10/20261028-sdd-baseline/report.md`.

Revision: 95defef2c7cddd2f4eda36547101ad6612b30044
Evidence app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Current app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Retained coverage status: gap. Usage was intentionally not executed; format pass alone is insufficient.
Simulated user decision (test data, not real user authority): pending

### test_ready_product_activates_e0

Fixture report: `.devkit/transient/incubation-baseline/run-03/test_ready_product_activates_e0/consumer/docs/materials/2026-10/20261028-sdd-baseline/report.md`.

Revision: ba081d3080c66e5d88b870a29b38c2d5a60b2e61
Evidence app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Current app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Retained coverage status: verified. Activation succeeded; next requested change uses ordinary SDD plan-intent.
Simulated user decision (test data, not real user authority): activate 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773 local notes; approach=sdd; provider=spec (was project)

### test_ready_product_activates_e1

Fixture report: `.devkit/transient/incubation-baseline/run-03/test_ready_product_activates_e1/consumer/docs/materials/2026-10/20261028-sdd-baseline/report.md`.

Revision: 17abd2153197d38b18b2693cfe1e0892a83df3d1
Evidence app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Current app SHA256: 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773
Retained coverage status: verified. Activation succeeded; next requested change uses ordinary SDD plan-intent.
Simulated user decision (test data, not real user authority): activate 0e496259a7b52ef9a54b64a7dfa8fab5339314299550809d849cd34dd580b773 local notes; approach=sdd; provider=spec (was spec)

## Remaining completion work

Host must refresh verified policy/guidance/base content before final tests. Shared current contracts/guides, independent code/reconcile review and final completion records remain pending. Source is stacked implementation, not released prerequisite evidence.

## Final dependency and missing-provider correction

The verified final policy source is incorporated at accepted head9fc51885b409707f0ae268624b4c6df23fba10bb.
Initial independent review reproduced an absent integration-provider gap: approach/sync inspection passed but the
actual provider reader refused normal integration. The playbook now includes configuring spec among the exact
authorized effects when the provider is absent, as well as replacing project; compatible existing spec is preserved.

Executed after the correction:

```sh
uv run pytest packages/devkit-spec/tests/e2e/bundles/spec/test_sdd_baseline_scenarios.py packages/devkit-spec/tests/integration/bundles/spec/test_sdd_baseline_guidance.py packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py --basetemp .devkit/transient/incubation-baseline/run-provider-fix -q
```

Observed result:10 passed in24.91seconds. This includes six scripted scenarios (three initial-provider cases:
project, spec and absent), three deployed asset checks and the actual repository use-case parser check. No policy
runtime was stubbed. The absent-provider case executes the actual approach inspection, app checks, authorized
provider configuration, sync consistency and next-change SDD routing. User decisions remain synthetic test data.
The final document influence selection also passed12tests; source Ruff/Pyright and cumulative governance passed.
