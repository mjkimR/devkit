# Adopt SDD from an incubation app

Use the `sdd-baseline` playbook when the user chooses to maintain the implemented product through SDD.
A small app can remain in incubation. Neither elapsed time nor package installation forces adoption.
Legacy Markdown debt containment is the separate `brownfield-adoption` playbook.

## Prepare without activation

Inspect `uv run devkit config show` and keep the shared `.devkit/config.toml` explicit:

```toml
[development]
approach = "incubation"
```

Reuse an existing table rather than add a duplicate. Preserve the project's other settings.
If the spec package is absent, present the dependency/asset effects before installing it through the project's
supported source. For a uv project using this repository's Git source:

```bash
uv add --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"
uv run devkit sync
uv run devkit add spec
uv run devkit config show
uv run devkit playbook get spec/sdd-baseline
```

The document package brings its existing dependencies; docs and spec core assets are selected for SDD preparation.
Verify `configuration.development.approach` remains `incubation`. Retrieval alone authorizes no playbook execution;
run the procedure only on explicit invocation or confirmation. Existing live product context is optional semantic input.

## Establish retained evidence

Read `get-context docs` before authoring documents. Follow the playbook to identify the product scope the user
intends to preserve, important structure, current choices and representative flows. Reuse accurate current documents.
The ordinary report defaults to `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md`; it is not a Unit or envelope.

For each retained item, connect implementation, current document and actual check/usage evidence at the recorded
source identity. Failed, skipped or unavailable required evidence remains a gap. A passing format check does not
prove that the selected product works. Correct authorized mismatches, obtain the user's scope decision, or stay
in incubation; required retained-scope gaps cannot be waived into readiness.

## Apply only the ready effects

Present the ready report/revision, retained scope, actual outcomes and exact activation effects. Reuse explicit
user authority already bound to those same effects; otherwise obtain it when the effects are concrete. Preparation
intent alone does not authorize activation against an unknown final scope.

Authorized activation edits only the necessary shared settings:

```toml
[development]
approach = "sdd"

[integration]
provider = "spec"
```

Retain an existing `spec` provider. If the project uses `project`, present its necessary switch to `spec` as an
explicit activation effect requiring authority. Without that authority, report the mismatch and claim no successful
adoption. Preserve approval, worktree, other integration and project-check settings unless their change was authorized.
This example is not a universal settings profile or a command to overwrite the configuration.

```bash
uv run devkit sync
uv run devkit config show
uv run devkit spec policy
uv run devkit sync --check
```

Verify observed SDD approach, selected guidance and next-change routing agree. The baseline itself creates no
retrospective proposal, Unit, approval or ADR for discarded experiments. Current retained choices need truthful
known reasons; missing reasons remain unknown rather than reconstructed history.

If source changes before activation, revalidate affected observations. If installation/update/sync fails, record
actual partial state and the supported recovery; claim neither successful adoption nor automatic rollback. Resume
from the existing report after rechecking its evidence. Preserve unrelated edits and existing SDD history.

The current contract is `CAP-DLV-incubation-sdd-baseline`; the actor flow is `UC-adopt-sdd-from-incubation`.
