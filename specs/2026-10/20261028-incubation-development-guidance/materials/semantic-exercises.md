# Incubation semantic exercises

## Scope, inputs and execution identity

This is a bounded evaluation of installed incubation guidance, not a real-user study or a production app.
Product goals and decisions were labelled synthetic fixture inputs; agent choices and observed execution were
reported separately. The coordinator did not infer any real user approval, change approach or create an SDD Unit.

Build source: guidance worktree commit `86263d6e55a87fcb834b24828249bdcc7d462a3d`, containing the Host-stacked real
policy implementation. Python 3.12.8 on macOS executed built docs/catalog wheels with devkit-spec absent.
The permanent no-spec consumer test is `packages/devkit-catalog/tests/e2e/bundles/incubation/test_installed_consumer.py`.
It passed actual default/explicit/invalid policy inspection, docs context/rules, role/skill deployment and context
preservation through removal/re-addition. This is runtime evidence, not a stubbed policy result.

Synthetic product: a single household member remembers shopping items with a local standard-library CLI and
persistent data; no network, concurrent editing, accounts, complete backlog or architecture was supplied.
The first agent reused those known constraints, identified a JSON feasibility question and proceeded inline.
Later reconstruction was another explicit synthetic fixture direction inside the same retained product goal.

## Observed outcomes

| Exercise | Actual result | Coverage and limitation |
| --- | --- | --- |
| Inline installed `/incubate` | Effective incubation inspected; bounded JSON probe completed 100 replacements/2,000 reads; CLI flow passed 32 subprocess interactions | Discovery reached implementation without a backlog or mandatory documents; no real-user usability claim |
| Optional `usage-reviewer` | Frozen source ran add milk/add bread/list/done 1/new-process list twice; output retained bread only | Generic native carrier followed the exact installed role contract because the custom role type is not exposed by this host; Codex boundary emulated |
| Fresh-context resume | Agent read installed skill/current context and pointed-to implementation/checks; did not read the initial scenario, coordinator report or prior conversation | Recovered goal, constraints, choices, limitations and executable next action from current facts |
| Goal-bound reconstruction | Adapter/core split retained existing CLI and data; original checker passed 32 subprocesses before and after; continued list accepted eggs and bread completion | Source evidence was revalidated; maintainability improvement is an inference, not a measurement |
| SDD applicability | Actual config show returned sdd/default; read-only agent stopped product work and explained configuration action | 118 fixture files unchanged; no approach mutation or context creation |
| Invalid applicability | Actual config show returned exit 2, DEVELOPMENT_CONFIG_INVALID; agent stopped and reported correction action | 118 fixture files unchanged; unavailable context was not reported as loaded |

The frozen usage commands used the installed Python, `shopping.py --data <fresh-file>` and the following suffixes:

| Suffix | Exit | Exact stdout | stderr |
| --- | --- | --- | --- |
| `add milk` | 0 | `Added 1: milk\n` | empty |
| `add bread` | 0 | `Added 2: bread\n` | empty |
| `list` | 0 | `1: milk\n2: bread\n` | empty |
| `done 1` | 0 | `Done 1: milk\n` | empty |
| `list` in another process | 0 | `2: bread\n` | empty |

Initial app SHA256: `715738c6c5f618eca8fca9917c0365224a33b428edc210d20509d068420c6a41`.
Reconstructed adapter: `008fd9adc442f96387fd9bd643d611efbb5e16767af3871755c585ac75e05467`.
Reconstructed core: `ce4f5693a09861219507f219009e31ae06d696abd9dab3bd776e1c299304b93b`.
The pre-existing list retained identical bytes, SHA256 `f880c9b1cb3f9a96d17f65acb5f373bc0227eca9ac384d51fc6989c54bbd6eb4`.
Its before/after pending output was `2: bread\n3: 우유\n`; a copy continued with eggs ID 4 and completion of bread ID 2.

`before-checks.json`/`after-checks.json` retain exact argv, streams and exits; corresponding flow transcripts retain
individual CLI interactions. `observed-app.md` preserves actual before/after source and current context as evidence,
not an application catalog. The original checker's adapter-only source identity was supplemented by app/core hashes.

## Boundary verification

All generic exercises used absolute read/write paths and operation-specific approvals. No native confinement is
claimed. The frozen usage role changed test data only; source and README hashes were unchanged. Both policy-stop
fixtures retained every file byte. All 119 original inline fixture files were unchanged after both coordinators.
The production comparison tree remained `bdcf61640c2d12403a1b56eaae64737c797759df` before and after all agents,
and production HEAD remained `86263d6e55a87fcb834b24828249bdcc7d462a3d`. Only authorized ignored fixture artifacts
changed. Authored fixtures remain for worktree cleanup; no source reset, commit or external mutation was delegated.

## Limits and remaining completion work

The exercises do not prove general model reliability, real-user usability, concurrency, crash durability, permission
failure or cross-platform behavior. No build/lint/type configuration exists for the sample app, so those app checks
were unverified; production catalog checks are separate. No SDD activation or historical artifact reconstruction ran.
Policy review fixes, shared documentation and mandatory independent code/reconcile reviews remain pending before
final completion. Source changes to relevant policy or guidance require affected evidence to be rechecked.

## Built-wheel identities

- `devkit_advisory-0.1.4-py3-none-any.whl`: `56618a5dd9e4ef0130a11cd1b24c669c3e1a831dc32c755d268818eb29a96834`
- `devkit_agt-0.1.4-py3-none-any.whl`: `56bd42f805275d421c13948a0058240cd391f6ecd2cac44164bedeb70933dec7`
- `devkit_catalog-0.1.4-py3-none-any.whl`: `015c6178655c6753aa05d252749bcfa74954607555b21ed9e830fbcfb00040cd`
- `devkit_cli-0.1.4-py3-none-any.whl`: `ebcbae0e5d94cfcb3222f6c4991dc3906c62e940960fdb2a66556722268925a5`
- `devkit_core-0.1.4-py3-none-any.whl`: `2d04a6ce900ac79a9bcfcf155d4015baa704e59a05a7d71838327d8dedab544f`
- `devkit_dist-0.1.4-py3-none-any.whl`: `916458fe2714bb100680559ef57118931552b8b5afb290781133489e7e66c604`
- `devkit_docs-0.1.4-py3-none-any.whl`: `3e01a8efa218da9b22938b2c3a600d07324173049d5f6313bb3923d978b41013`

## Scoped-turn regression results

Catalog tests, including the actual no-spec wheel consumer: 33 passed. Ruff/format/Pyright and the committed
new capability/usecase checks passed. Explicit repository-usecase parser regression passed after correcting
extension markers to the parsed template form. The selector omission is tracked as `FB-usecase-parser-affected-selection`.

The official affected selection returned 11 passed and 2 failed tests inherited from the stacked policy snapshot:
its new SPEC_LIFECYCLE_INACTIVE, INTEGRATION_APPROACH_MISMATCH and INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED
codes were not yet documented there. Those policy changes are outside this turn's write scope. They require the
Host's latest verified policy merge and a fresh affected run; this report does not claim that affected suite passed.
