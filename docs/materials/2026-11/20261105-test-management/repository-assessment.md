# Three-repository test-management assessment

## Evidence boundary

Read-only inspection on 2026-11-05. Devkit base `86d8e359`; Auto Hub
`01e1bd2251c526c3fe5107f3c2929931a073df77`; Resource Indexer
`2af60a0cf48554d6972377c293f9e3af68c6b6d3`. Siblings were clean at intake.
No application suite, service, collection hook or benchmark was executed. Historical guide counts/timings are
context, not current measurements. No source snapshots/raw inventories are retained.
All lockfiles select pytest 9.1.1 and xdist 3.8.0; both apps select pytest-asyncio 1.4.0.

## Devkit

Evidence: `justfile:17-46`, `scripts/module.sh:89-142`, `scripts/affected_tests.py:461-518`,
`.github/workflows/ci.yml:12-85`, `ARCH-05-2-components`, `ADR-post-merge-verification`.

Retain package-owned unit/integration/e2e directories and `just test-affected --base <known-base>` with its full
fallback. The selector filters ordinary e2e paths unless requested/changed but retains data-triggered e2e targets;
this is not an unconditional e2e exclusion. Keep automatic workers capped at eight with worksteal as the existing
baseline, not a universal optimum. Follow socket preflight and explicit viewer frontend checks.
Final integration saves the premerge target SHA, synchronizes the landed runtime and checks that final HEAD with
required lint/types/rules, generated checks and affected tests. Nightly CI adds coverage, never replaces this.
No runner/layout/branch change is recommended without a measured problem. `CAP-DLV-performance-pass` already owns
performance-only measurement and application procedures.

## Auto Hub

Scout inspected HEAD `01e1bd2251c526c3fe5107f3c2929931a073df77`; the Host cross-checked native recipes,
runner, root fixtures, flow database override, testing guide and CI source. No tests/services were executed.
Evidence: `../autohub/justfile:97-145`, `scripts/run-tests.sh:26-34`, `modules/hub/tests/conftest.py:38-59`,
`modules/hub/tests/integration/features/execution/flows/conftest.py:16-25`,
`docs/development/testing.md:8-40,55-110`, `.github/workflows/ci.yml:4-142`.

- Keep `tests/unit/integration/e2e` ownership and the collection guard. The guide reports no deployed-process
  e2e suite; an available tier name does not establish that such coverage exists.
- Use `just test-unit` or `just test tests/unit/features/<owner>` for logic and an owning integration path for
  database/API changes. Keep SQLite `just test`/`test-integration` on capped automatic worksteal workers;
  unit and SDK remain serial. `PYTEST_WORKERS=0` is the repository's documented serial override.
- Keep `just test-pg <owning-path>` serial by default. SQLite-only checks do not establish PostgreSQL locking,
  persistence or migration behavior. PostgreSQL needs Docker/testcontainers unless the supported flow override
  is explicitly supplied. Keep migrations in the database verification set when schema/migration behavior changes.
- Preserve the shared flow PostgreSQL URL worker guard and its loopback/test-name validation. The optional
  `TEST_SCHEMA_DATABASE_URL` creates/drops unique schemas but has no equivalent host/name guard; inspect it as
  a separate disposable-resource requirement. Never infer that all PostgreSQL fixtures have the same protection.
- Completion follows native lint/type/build and relevant test gates. Use `just lint-check` as the read-only lint
  equivalent. UI changes need `just check hub-ui` and `just test-ui`; API changes need generation and
  `just check-ui-api`. SDK changes need `just test-sdk` and `just build-sdk` alongside lint/types.
- SDD/native-delivery changes additionally use `just check-devkit`, the reviewed runtime profiles, `just test-sdd`
  and `just test-sdd-pg` with documented setup. Missing runtime/OS-isolation/DB prerequisites are unverified,
  not a successful contract check. Do not provision private sources or invoke secret-backed CI during assessment.
- CI declares only `workflow_dispatch`. Preserve local checks; do not assume a PR/push automatically runs the
  backend, PostgreSQL, SDD-contract or frontend jobs. No trigger change is proposed.

Recommendation: retain the existing split runner and change-specific gates. Do not introduce a `dev` promotion
branch, global parallel PostgreSQL default or new affected selector to make this repository resemble devkit.
The shared app-testing-base fixture implementation was not audited; its registration and consumer guards were.

## Resource Indexer

Evidence: `../resource-indexer/justfile:8-38`, `scripts/check.sh:37-53`, `tests/conftest.py:11-37`,
`pyproject.toml:156-164`, `tests/README.md:57-83`, AGENTS.md Sandbox Tests / Verification Gate.

Keep source-owned tests and unit/integrate/e2e markers; explicit marks override path inference. Labels do not prove
isolation: `tests/integrations/test_host_storage.py:5-6` imports sockets/subprocesses outside the server/e2e path.
Use owning-path or existing tier/fast recipes during iteration. Keep `just test` and `just check` serial and
`just test-parallel` as an optional same-suite eight-worker/load/no-restart candidate.
`just check` includes rules/evidence budget, Python lint/tests/types, Go tests, Windows cross-build, web checks and
build. It is not replaced by Python-only or parallel tests. Changed browser flows need `just test-browser`, which
builds first. Existing storage checks are already in the full gate.
The VECTOR_DB_ stripping fixture is application-specific. Async tests require socket wakeups even in fast tiers;
run in a suitable environment instead of altering the tested behavior. Never exercise a real library or paid
models implicitly. No `.github/workflows/` directory was found; external CI/release coverage is unknown.
Retain current defaults. Refresh stale guide counts/time comments only after measurement; do not add an affected
selector or directory migration merely to resemble devkit.

## Parallelism references and limits

Consulted on 2026-11-05: [distribution options](https://pytest-xdist.readthedocs.io/en/stable/distribution.html),
[worker/run identifiers and fixture scope](https://pytest-xdist.readthedocs.io/en/stable/how-to.html).
These stable-channel docs distinguish automatic/explicit workers, schedulers and restart settings; session fixtures
may execute per worker. Worker/run identity can support isolation; a worker cap alone cannot prove it.
The examples were not executed against locked 3.8.0. Retain only already configured options unless Development
checks additional options against its installed version. No speedup/default promotion is claimed here.
