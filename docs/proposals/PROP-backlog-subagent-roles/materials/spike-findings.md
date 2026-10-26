# Spike findings: Backlog triage and decomposer roles

Evidence gathered in the first Planning turn (scout `envelopes/scout-01.yaml`, head `d4a22409`, base `main` at
`3302ff9d`). Paths are relative to the repository root.

## F1. Registering a role needs no engine code

| Concern | Where | Change for a new role |
| --- | --- | --- |
| Asset and preset | `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml:253-283`, `:343-348` | One `[[assets]]` entry with `kind = "subagent"`, and the id added to `presets.core` |
| Projection | `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py:23-129` | None: role must equal the asset id, `x-*` keys pass verbatim, every host (`claude-code`, `codex`, `antigravity`) needs a block |
| Workflow role vocabulary | `packages/devkit/src/devkit_agt/features/workflow/repositories/project/roles.py:34`, `:52-68` | None: roles come from the receipt's subagent assets |
| Envelope kinds | `packages/devkit/src/devkit_agt/features/workflow/models/ids.py:8-14`, `services/envelope/model.py:473-487` | None: any `[a-z][a-z0-9-]*` kind is accepted by `envelope new` |
| Role-set tests | `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py:14-29`, `:60`, `:232-233`; `test_workflows.py:27`, `:62-66` | Add both roles to `ROLES`, `EFFORT_PRESETS` and the per-role assertions |
| Payload table | `bundle/skills/spec-delegate/references/payload.md:16-21` | One row per role (the test asserts it) |
| Wording rule | `packages/devkit/src/devkit_agt/bundles/authoring/bundle/rules/agent_asset_wording/rule.py:28` | None: applies to every `bundle/subagents/**` file |

Conclusion: `packages/devkit/` and `packages/devkit-dist/` stay untouched; the draft's
`packages/devkit-spec/src/devkit_spec/features/` entry covers nothing this work changes.

## F2. Backlog has no record location

- `devkit workflow envelope new` requires `--unit` naming a directory with a workflow anchor
  (`packages/devkit/src/devkit_agt/features/workflow/cli/app.py:21-23`, `usecases/workspace.py:393`).
- Envelopes live only under a spec or proposal directory (`skills/spec/references/envelope.md` section 4).
- Feedback triage spans `specs/**/feedback/` and has no unit. A decomposition deletes its parent proposal in the same
  commit that creates the children (`skills/spec/references/backlog.md.jinja:10`), so the parent's `envelopes/` does not
  survive.
- `spec-delegate` already defines the no-unit case for a `session` task: the role returns a message and no envelope is
  written (`skills/spec-delegate/SKILL.md`, Constraints).

## F3. Invocation points

- `[DELEGATE: ...]` is printed only for a workflow stage that names a role; only the `sdd-proposal` spike stage names
  one (`bundle/workflows/sdd-proposal.md:36-37`). `challenger` has no stage and is invoked from skills
  (`docs/capabilities/delivery/CAP-DLV-delivery-workflows.md:275-276`, `:471-472`).
- Backlog runs outside workflows. The callers are the `feedback-hygiene` playbook (Step 1 collects and groups), the
  Backlog reference (`skills/spec/references/backlog.md.jinja`, decomposition and the return-for-decomposition
  procedure) and `spec-next` (recommends a hygiene pass and lists `needs_decompose` drafts as Backlog actions).

## F4. Living Spec owners

| Document | What it states today |
| --- | --- |
| `CAP-DLV-delivery-workflows` section 4.6 | Role contracts table with an envelope-kind column (`:365`, `:384-391`) |
| `CAP-DLV-proposal-incubation` | `decomposed_from`, `needs_decompose` and the decomposition flags (`:143-156`, `:253-254`, `:470-475`) |
| `CAP-HARN-agent-guidance` | The subagent asset list naming six roles (`:111`), feedback-hygiene and Backlog guidance (`:270`, `:316-346`) |
| `ARCH-04-1-ecosystem-boundaries` | The Subagent Roles row (`:86`) |
| `UC-route-development-intent` | Triage of feedback routes to `feedback-hygiene` (`:151-154`) |

`docs/capabilities/collaboration/` holds only `CAP-COLL-shared-artifacts` and `CAP-COLL-work-scope-registry`; neither
concerns roles, feedback or decomposition. `handbook/` names the roles but is a release snapshot refreshed on request,
never a reconcile target (`CAP-DLV-release-handbook`).

## F5. Present workload

- Open feedback at Planning time: 3 items (`devkit spec list feedback --status open --all-namespaces -n 0`).
- Dispositioned feedback files in the tree (`status: promoted` or `dismissed`): 86.
- Live documents carrying `decomposed_from:` in frontmatter: 0. Decomposition by `--decomposed-from` has not yet been
  used on this repository's Backlog.

## F6. Overlap with SPEC-foundation-documents

`SPEC-foundation-documents` is handed off on `dev-foundation-documents` (`f12ab876`), not yet merged into `main`. It
moves `scout`, `challenger` and `reconcile-reviewer` to `uv run devkit get-context spec`, as `code-reviewer` already
does (`bundle/subagents/code-reviewer.md:33`), and adds a guidance test that every role contract loads the spec context.
Its `_Boundary:` covers the whole spec bundle and `packages/devkit-spec/tests/`. New contracts written with
`get-context` from the start pass that test whichever change lands first; the shared role tests are a textual overlap
only.
