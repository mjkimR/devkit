# Spec-Driven Delivery

Development here is spec-driven: start it with the `spec` skill (`/spec <intent>`); `/spec-next` orients in work
already under way. Explicit user instructions take precedence. Agents MUST NOT unilaterally terminate the user's
session.

## 1. Context

- Read this guide once per agent context before development work, including work started without a skill.
- Read each relevant instruction listed with it before the action it governs. Instructions hold judgment and policy,
  playbooks (`devkit-playbook`) occasional procedures, rules (`devkit rules`) deterministic checks; an instruction
  never overrides a mandatory check (report a conflict).
- Add a rule or check only for an identifiable failure or a reusable practice, at proportionate cost.

## 2. Living Spec and Scope

- `docs/` is the Living Spec, the current contract (capabilities, stories, architecture, decisions): rewrite changed
  statements in place; history belongs in Git, ADRs and dated materials, temporary task lists in `specs/`.
- A feature spec is `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` (`spec.md`, `plan.md`, `tasks.md`), kept as history once
  completed. Read current contracts and active specs (`devkit spec list spec`) before drafting new work.
- Packages may keep a Living Spec namespace under `docs/packages/<name>/`: `list` and `search` cover the current
  directory's namespace plus global documents (`--all-namespaces` for cross-package impact); IDs are repository-wide.
- Frontmatter `summary` is English, one or two sentences (`devkit spec search` finds it); other text may use any
  language.
- Refer to ID-bearing documents by full ID (`` `CAP-...` ``), never by path (`devkit spec resolve <ID>`,
  `devkit spec refs <ID> --direction out|in`).
- Agents MUST NOT implement Non-Goals or add unrequested features, refactors or speculative scope; unstated assumptions
  are not permissions. A lasting policy change or an exception to a MUST needs an ADR; a one-off exception within the
  approved scope is stated in the review or final report.
- A task's `_Boundary:_` is the expected scope: explain a necessary extension in the report. Write boundaries given to
  a delegated role are strict.

## 3. Classification and Workflows

The agent classifies work on three axes; the user confirms at `plan-intent`:

- **`task-kind`**: `feature` (default) or `bugfix` (a defect against an agreed contract: reproduce, Red then Green).
- **`planning-depth`**: what must be settled first, not size. `session`: nothing, no Unit. `spec`: the contract, with
  a clear direction; a spec Unit. `proposal`: the direction; a proposal Unit, Planning, then handoff.
- **`activity-effort`**: `low`, `medium` (default) or `high` per activity: how thorough review and verification are,
  never lowering gates, exit checks or `required` policies.

The workflow is `sdd-<planning-depth>[-<task-kind>]`: `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`,
`sdd-spec-bugfix` and `sdd-proposal` (handed off to `sdd-spec-<task_kind>`); a team review is `proposal` depth plus PR
policy. Depth is raised by the Host (`[tool.spec] depth_escalation`), never by a worker, and never lowered except by a
proposal's handoff or, on the user's explicit decision at pickup, the session reclassification of a queued draft. Unit depths write `spec.md`, `plan.md` and `tasks.md` before production code. Follow the
workflow definition's stages, checks, gates and returns, never an ad-hoc sequence (`devkit workflow next --unit <dir>`).

Read `devkit spec policy` before classification, gate and Git decisions. `plan-intent` (goal, scope, verification,
expected behavior for a bugfix, `task-kind`, `planning-depth`) and `plan-accept` (a proposal's direction) are always
the user's, recorded with `devkit workflow answer --by user` (`plan-accept` with `devkit spec proposal accept --by
user`, also directly for an eligible draft in Backlog); `dev-integration` follows `devkit spec policy` (the
`spec` skill's `references/completion.md`, Policy). There is no Development direction gate: inside the agreed intent
take the recommended option and record it; only a problem that breaks the agreement stops the work. Records name the
authority (`user` or `policy`) and never carry the conversation (no quotes, paraphrase or dates of it); a decline note
states the reason as a decision. Nothing grants new merge, publication or deletion authority. Report stages the policy
switched off as skipped. Before formal worktree work read the `spec` skill's `references/worktree.md`; before
completion or Git actions its `references/completion.md`.

Mode per activity: `direct` (default; the Host implements), `local-orchestrated` (one-shot workers in their own
worktrees; user-invoked `spec-orchestrate`) or `cloud-pr` (a Cloud Agent from a PR). Heavier modes are the user's
choice; a `session` task runs only in `direct` or the `cloud-pr` general PR path.

## 4. Verification and Completion

Before reporting completion compare the final diff, the agreed requirements, the check results and the Living Spec
impact (`spec-review`, `spec-sync`). Fix implementation defects rather than rewriting documentation to endorse them.
Reconcile changed behavior, capabilities and constraints into the Living Spec; recheck after further changes.

Spec Units keep a resolved `reconcile.md` and stay in place when completed. A `session` task writes no Unit, envelope,
gate record, planning or reconcile file and reports the change, effort, review result, verification and remaining
constraints in its final response or PR body (a needed Living Spec change raises it to `spec`). The `rules-check`
commit gate (on by default) runs the spec rules on every commit (`devkit rules check --staged` reproduces it); CI runs
`devkit rules check --ci --base <ref>`. Completion, commit, integration and ending the session are separate events.

## 5. Templates and Policy Files

- Templates: `.devkit/managed/spec/templates/{capability,story,decision,proposal,milestone}.md`.
- Policy lives in `.devkit/config.toml` (`[workflow.approvals]` with `dev-integration` only, `[workflow.stages]`,
  `[worktree]`, `[tool.spec]`); read it through `devkit spec policy`, never by parsing the file.
- Never edit `.devkit/managed/`; change it through `devkit override` or the project's own bundle.
