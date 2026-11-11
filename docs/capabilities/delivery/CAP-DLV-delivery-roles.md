---
id: CAP-DLV-delivery-roles
title: Delivery roles and worker result validation
summary: "Delivery role contracts bound support, worker and lifecycle-executor authority. Committed worker ranges, scope evidence and read-only inspection support Host acceptance without granting approval."
area: delivery
status: active
created_at: 2026-11-10
usecases:
  - UC-route-development-intent
  - UC-plan-and-hand-off-a-proposal
  - UC-drive-development-to-integration
  - UC-handle-delivery-problems-and-exceptions
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/worker/cli/commands.py
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/SKILL.md
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja
---

# [CAP-DLV-delivery-roles] Delivery roles and worker result validation

## 1. Summary

The spec bundle's role contracts define each delegated actor's authority and returned evidence. The Host owns
acceptance of worker results; `devkit spec worker inspect` supplies read-only evidence for that decision.

## 2. Scope & Boundary

- **In-Scope**: support-role and activity-worker contracts, guarded lifecycle-executor dispatch, worker write
  admission, source/range acceptance and informational worker inspection.
- **Out-of-Scope**: workflow stage order, gates and review effort (`CAP-DLV-delivery-workflows`); native projection
  and model-level mapping (`CAP-DIST-agent-projections`); Git integration effects (`CAP-INT-mcp-services`).
- **Non-Goals**: **Scope Excluded**: native sandbox enforcement, an agent scheduler or automatic worker acceptance.

## 3. Business Rules & Policies

1. **Host acceptance**: The Host MUST validate committed worker ranges against the authority and evidence in §4
   before accepting them. The informational inspection helper does not grant authority.
2. **Read-only inspection**: The inspection helper MUST NOT change files, records, scope or Git state (§4.2).

## 4. Interfaces & Data Contracts

### 4.1 Role Contracts

One Markdown contract per role in devkit's
`CAP-DIST-agent-projections`:
`role`, `title`, `description`, an optional `skill` and a `hosts` block for `claude-code`, `codex` and `antigravity`.
Extension keys devkit does not interpret: `x-execution` (`isolated`), `x-invocation` (`optional`) and
`x-git-actions` (`[read]` for support roles, `[read, commit]` for the two workers and `[read, lifecycle]`
for git-operator, whose lifecycle effects are bounded by the current job).

The source scout contract selects `level: compact`; it requests Haiku, Luna or Flash with effort omitted.
The git-operator contract selects `level: lean`: Sonnet medium, gpt-6.1-terra medium and Flash with effort omitted.
All other shipped roles omit neutral level, model, effort and `x-model-profile` settings and inherit through
native host defaults. Projects can override or reset role levels in `.devkit/config.toml`.
`CAP-DIST-agent-projections` defines mappings and native limitations; `ADR-subagent-levels` defines the scout
exception, the original five presets and lean. `ADR-delivery-approval-and-lifecycle-authority`
supersedes only the scout-only source-level restriction for git-operator. No model level changes `activity-effort`, write scope or verification gates.
`packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` checks every shipped role.

| Role | Skill | Default model level / effort | Writes | Envelope kind |
| --- | --- | --- | --- | --- |
| `challenger` | none: the procedure is in the contract | inherit | nothing | `challenger` |
| `reconcile-reviewer` | `spec-sync` | inherit | nothing: verifies the implementer's reconcile at `medium`/`high`, subject to `CAP-DLV-delivery-workflows` rule 15 | `reconcile-check` |
| `code-reviewer` | `spec-review` | inherit | nothing but throwaway probe tests in its round's own subdirectory of the ignored probe path the payload names, read by no other round, left for worktree removal and never the unit's tests: verifies implementation against requirements and checks | `review`, `reverify`, or a message for a session |
| `scout` | none: the procedure is in the contract | compact / inherited | nothing, or the proposal's `materials/` on request | `scout` |
| `ux-reviewer` | `spec-ux-review` | inherit | nothing: walks the use cases through the drafted screens and scores the rubric, before code, as an optional delegation | `ux-review` |
| `triage` | none: the contract cites `feedback-hygiene` Steps 1 and 2 | inherit | nothing: groups open feedback and recommends a destination per group, in Backlog | none: a message |
| `decomposer` | none: the contract cites the `spec` skill's `references/backlog.md` | inherit | nothing: proposes a split of one draft into children with provenance, edges and an exit, in Backlog | none: a message |
| `planning-worker` | none: the procedure is in `spec/references/planning.md`, which the contract cites | inherit | the proposal directory in its `plan-` worktree, committed | `worker` (its own) |
| `git-operator` | none: operating reference in spec-orchestrate | lean / medium where supported; Flash effort omitted | exact guarded lifecycle effects in the current Host job; no production authoring | none: concise role message |
| `development-worker` | none: the procedure is in the contract | inherit | the unit's write scope in its `dev-` worktree, committed at every stage boundary | `worker` (its own) and the stage envelopes |

The contract body is the role's prompt and holds only what the role needs: purpose, input fields, return fields,
write boundaries, failure handling and, for a role whose procedure no main session runs (`challenger`, `scout`, the
`development-worker`), the procedure itself; `triage` and `decomposer` cite by managed path the procedure a main
session also runs (`feedback-hygiene`, the Backlog reference). Planning runs in a main session in `direct` mode, so its ordered steps
live in the `spec` skill's `references/planning.md`, which the `planning-worker` contract cites; the contract keeps
only the worker's own obligations (worktree, nested roles, return, write boundaries, problems)
(`ADR-orchestration-workers`). Caller guidance (per-role payload, host guarantees, the
post-run comparison of two snapshots of the working tree, each a tree written from a temporary index, so a write
to an already-modified file shows too, envelope recording, range validation) lives in `spec-delegate` (`SPEC-subagent-procedure-in-contract`).

### 4.1.1 Reusable lifecycle execution

WHEN the Host first delegates a lifecycle job in one conversation and repository, it SHOULD create one
`git-operator` and reuse its exact identity through native continuation for later jobs. IF that identity or
continuation is unavailable, THEN it MUST rebuild from current CLI/Git observations and current Host authority.
The role has no persistent service, approval store or global repository lock (`ADR-delivery-approval-and-lifecycle-authority`).

Each job carries operation, absolute repository/base/worktree paths, Unit/branch, source/target refs,
intended_effects, authority, allowed_boundaries, writers_quiesced and expected_checks. It includes prepared_digest
where required, route and separate publication_authority for remote effects. WHEN a job is dispatched, the Host
MUST repeat its current authority and identity even when the operator remembers the Unit. Read-only preparation
grants no mutation authority. The Host retains decisions, scheduling, semantic conflict resolution and result
acceptance; source preparation remains with the implementer or Host.

WHEN a mutation is requested, git-operator MUST refresh identity, refs, cleanliness and writer state before
executing an existing guarded CLI operation. IF authority is missing, refs/scope changed, resources are dirty,
writers are active or permission is unavailable, THEN it MUST preserve resources and return the exact blocker.
The Host quiesces writers before cleanup. Conflicting jobs serialize within this conversation only.

The role message contains status, identity, observed_refs, completed_effects, remaining_effects, checks,
blocker_codes, cli_result and unverified_areas. Original CLI status/exit/effects remain separate. WHEN all requested
effects and checks are verified complete, git-operator MAY return completed. IF the remainder requires Host action,
THEN it MUST return needs_input; execution failures return failed. IF a CLI returns partial/unknown effects,
THEN the role MUST inspect live state before attempting only a supported, currently authorized remainder.
A zero-exit incomplete cleanup cannot be completed; normal integration already includes cleanup.

WHEN a `prepare-worktree` or `handoff` job returns, git-operator MUST report worker-input readiness under
`checks.worker_input: {head, dirty_paths}` from `git -C <worktree> rev-parse HEAD` and `status --porcelain`; the
result has no other readiness, permission or next-actor field. IF `dirty_paths` is not empty, THEN each path MUST
also be a `remaining_effects` entry and the role status is `needs_input`, never `completed`; a zero-exit CLI result
with dirty paths is neither a failed CLI operation nor ready input. Every result returns to the Host, which owns the
next action. WHEN the Host starts a worker on such a result, it MUST first compare `checks.worker_input` with its own
Git observation and start the worker only on a clean HEAD that is the reported `head` or a descendant made only of
its own commits since (the post-handoff link fixes); an exit code alone never stands for ready input. A host refusal before dispatch is a blocker code
with a null CLI status and exit code and empty effects; CLI Git policy or `auto` policy is never reported as host
permission, and live effects, Git observation, host emulation, isolated fixtures and untested cases are reported
apart. The handoff result's
`commit` names the transaction the composed handoff committed itself
(`ADR-proposal-handoff`). The operator returns production edits, semantic conflict
resolution and authority beyond the job to the Host and performs no such mutation.

A dispatch MAY carry a finite, exact preparation list of `prepare-worktree` items; every other operation MUST stay
one job per dispatch. Each item repeats every job field and names its own branch, worktree path and Unit, all items
name the same retained base and base ref, and the list's authority covers only its listed items. WHEN git-operator
runs a preparation list, it MUST run the items one at a time in the listed order, each through the guarded
`prepare-worktree` procedure with its own refresh and, on Codex, its own approval request. WHEN an item is about to
run, git-operator MUST first check that the retained base HEAD still equals the dispatched base ref. IF an item is not
completed (a refusal, a failure, a zero-exit setup or sync warning, a moved base ref, or refused or unavailable host
approval), THEN git-operator MUST stop and return every later item as not attempted. The list return holds `items`,
one unchanged single-job return per attempted item, and `not_attempted`, each entry with the item's identity,
intended effects and the null CLI result; the list status is completed only when every item is completed, else
needs_input when any attempted item is needs_input, else failed, with no partial status. IF an item has a setup or
sync remainder, THEN git-operator MUST return it to the Host and run no setup `[FIX]`, sync or registration repair.
WHEN the Host retries a stopped list, it MUST verify each returned item against its own CLI/Git observation or
`inspect-recovery` and dispatch a new list naming only the remaining items it still authorizes, with current refs; a
completed item is never repeated (`SPEC-git-operator-batch-preparation`,
`MAT-git-operator-batch-dispatch-observation`).

`packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` checks registration, projections,
authority, recovery, worker-input readiness, preparation-list and evidence-separation wording. `MAT-git-operator-development-evidence` records four Terra medium native
continuation jobs and isolated CLI mutation fixtures separately; selected-model mutation, other live hosts, a live
partial preparation list and net cost/latency benefit remain unverified. Codex emulation uses explicit paths, per-operation permission and
Host effect checks without claiming native path enforcement. Flash effort is omitted without prompt emulation.

### 4.1.2 One-shot activity workers

The workers exist for `local-orchestrated` mode (`spec-orchestrate`, user-invoked per activity) and never for
`session` depth. Each is one-shot: it runs one turn of one activity in that activity's devkit worktree, using absolute
paths, an explicit absolute worktree cwd on every command and `git -C <worktree>` because initial cwd may be the
base checkout, runs its role subagents nested (Host → worker → role; Claude Code tool `Agent`, Codex
`collaboration.spawn_agent`) with absolute read/contract scopes that name the worktree's startup skill and
instruction paths (a nested role's read from another checkout is a reported boundary exception) and never ends its turn while one is still running, keeps
scratch files in an ignored path inside its worktree for removing the worktree to clean, writes its own records, commits at every stage boundary and,
when it stops on questions or a problem, makes an emergency commit of the unfinished work with its `worker` envelope
when record/commit access is permitted.
Development worker write admission has three tiers (`ADR-recorded-adjacent-path-extensions-for-development-workers`):

- **Tier A, declared**: the initial payload's paths, task boundaries and reconcile targets. Literal files and narrow
  directory prefixes are supported; globs are not expanded.
- **Tier B, recorded extension**: a worker MAY add an exact adjacent file necessary for an existing task and AC
  inside the approved goal. Same-feature documented ownership roots, project/plan-identified test mirrors, and exact
  existing Living Spec documents restating the changed behavior qualify. Without a documented root use the declared
  file's parent; never infer package-wide ownership. A Living Spec reason MUST name the affected contract ID.
  An exact existing derived reference document also qualifies
  (`ADR-derived-reference-documents-as-worker-scope-extensions`): a quick reference (`docs/development/reference/`),
  a user guide (`guides/`) or the README of a package or tool that owns a source the unit changes, when its edited
  passages restate a public name, command or behavior the task changes. Its reason MUST name that symbol, command
  or contract ID; the edit MUST add no document or section and change only the restating passages. Agent
  instruction files (`AGENTS.md`, `CLAUDE.md`), bundle and agent assets and release documents MUST NOT qualify.
- **Tier C, denied**: explicit payload denies MUST prevail, including over a directory declaration. Other units,
  `.devkit/`, host projections, governance-rule implementations, architecture/dependency declarations, CI/release
  configuration, outside-repository paths, other packages/features and new feature edges MUST NOT self-admit.
  Initial Tier A may expressly authorize protected-class work; an extension cannot grant that authority. Tests
  MAY be strengthened or updated for approved behavior and MUST NOT be weakened to pass. Lockfiles and general
  generated files require initial declared scope. A denied/non-adjacent path stops before writing with a problem.

Before its first source commit, the worker MUST annotate the exact file on its owning `_Boundary:` as
`(scope extension: <reason>)`, committing annotation and reason with that source change. The reason is one nonempty
line without parentheses. The sole final/emergency `worker` envelope MUST mirror path, positive checklist scanner
task ordinal, reason and owning AC IDs in `scope_extensions` (`CAP-DLV-workflow-envelopes`). Review MUST inspect
annotation/task/AC before that record exists and judge adjacency, necessity, custom protected paths and test
strength. Missing annotation/record evidence is P2 and repairable before final return; denied/non-adjacent/out-of-goal
writes are P1 and block the range. The Host MUST compare final records with reviewed annotations; changed metadata
requires re-verification. New unannotated boundary additions are checked against initial payload/task diff; derived
scope alone proves no authority. No sealed original-boundary journal is required. Local and cloud share these
obligations; optional inspect promises no Hub invocation or automatic semantic ownership enforcement. Git, sandbox,
publication, approval and rejected-range recovery rules remain unchanged.

Sync-output admission is an independent path class, not Tier B. A delegated change to a bundle source the project selects admits, as a class in the worker's write scope, every
tracked path `devkit sync` writes in the worktree after the change (seeded and projected files,
`.devkit/installation.json`, the managed `AGENTS.md` block), not only the files `devkit sync --check` lists before it.
The worker records its starting `devkit sync --check` exit as the `sync_start` check (a nonzero exit is a problem),
runs `devkit sync`, commits every output, names each one the payload did not list in the owning task's `_Boundary:`
as `(sync output)` and in its `worker` envelope summary, and never edits `.devkit/managed/`. The Host passes each new
`(sync output)` entry only when `sync_start` is `0`, `devkit sync --check` exits `0` on the returned head and the path
is under `seeded` or `files` in `.devkit/installation.json`, is the receipt itself or is `AGENTS.md`
(`ADR-orchestration-workers`). A before/after acceptance outcome names a baseline the worker can produce in its
worktree (the head with the change disabled, or a Planning measurement on the same machine), or the Host takes the
base measurement, because the worker never checks out another commit (`SPEC-delegation-sandbox-guidance`).
Planning resolves operational instructions and CLI execution in the assigned worktree. When a turn needs newer
base document IDs or CLI features, the Host incorporates the base and synchronizes that worktree's installed
instructions under existing Git and permission policy before resuming. A worker discovering that dependency returns
a problem for Host recovery; it never merges, resolves references from another branch, hides missing IDs in prose,
or fabricates unsupported records. Base advancement alone does not require a refresh.

The Planning payload names an ignored probe path inside the proposal directory and allowed write scope; the Host
verifies or prepares it before delegation. The worker leaves temporary files and throwaway repositories, including
their linked worktrees, in that ignored path and retains evidence in `materials/`; removing the Planning worktree
cleans them. A payload never asks a worker, Planning or Development, to delete a scratch file or fixture it created
(`SPEC-feedback-guidance-and-scope`). A probe that needs an outside
path is a boundary-expansion problem for the Host. Ignored status grants no sandbox or activity-repository Git
permissions; a temporary path under `/tmp` may not exercise repository-local sandbox conditions.

It never reverts, closes, raises the depth or narrows the scope. The `development-worker` runs from the stage
`devkit workflow next` names up to the final change report; the `planning-worker` takes a draft proposal toward
`plan-accept`, collecting its questions in one round. The Host restates either worker's questions for the user (what
each answer decides, what each option leads to) rather than relaying the worker's wording. The Host validates the cumulative committed range from the
unit's last accepted head; a range it rejects is a problem in the Host's own `worker` envelope, which blocks the unit
from review and integration without discarding anything until a resolution names it
(`ADR-orchestration-workers`). The Host records and compares no base-checkout state: base advances by the Host,
another session or an unknown author never block the range, and a worker commit that escapes onto the base branch
while the rest of its turn lands on its branch is an accepted residual no check names
(`ADR-orchestration-workers`). Host statuses: Claude Code
`native`, Codex `emulated` with `sandbox_mode: workspace-write`, Antigravity `unverified`
(`ADR-orchestration-workers`). Native Codex spawning does not enforce the worker's role/path boundary;
Git administration remains shared. Workers declare no model, reasoning effort or approval-policy override; project model levels follow distribution policy.

Prefer the projected named role with payload only. An unavailable role can mean projection or session-root
availability; role absence alone does not prove missing trust. Normal status/sync repairs missing or stale
projections where authorized. A generic native subagent may read the absolute effective managed/override contract
and explicitly emulate it only when host project-instruction loading is permitted; an explicit trust restriction
stops fallback and cannot be bypassed by another role, tool, path, process or host settings edit. Before starting a
worker, missing native spawning, required nested roles or necessary approval capability selects existing Host
`direct` execution when allowed, or `needs_input` for required isolation. Availability grants no future approval.

Each necessary operation beyond active sandbox access requests a separate narrowly scoped approval naming exact
operation, target and justification: sibling writes, shared Git index/commits, scope registry and verification/network
access included. No broad persistent prefix or settings change is introduced; preflight success grants no later
access. Unavailable or denied approval stops that operation and preserves its actual partial state. Do not evade
refusal through another tool, path, process or broader request. Retry another-cause failure only after cause/input
changes and authorization permits it. Failed record/emergency commit operations use only still-permitted scoped
access. Emergency `--no-verify` is limited to ordinary commit-gate refusal, never sandbox or approval denial.
A task worktree is always `<parent of base>/<base name>-wt-<branch>` (`--workspace-root` only names a directory
inside the checkout), and a linked worktree's commits write the base's shared Git directory. When either lies outside
the session's writable roots, the same per-operation approval applies, or the user grants the path; the agent never
relocates the worktree or changes a host setting (the `spec` skill's `references/worktree.md`).

When the worker record or emergency commit also cannot run, return `failed` with cause, commands tried, recovery,
actual last SHA, dirty paths and absent/uncommitted records or commit; never invent a clean committed result or final
HEAD containing it. The Host blocks failed dirty/uncommitted returns even without a worker record and owns a
subsequent recovery run and its records. Successful acceptance still requires cumulative ancestry through final HEAD,
declared paths plus verified Tier B and sync-output admissions, clean worktree, the turn's own `worker` envelope (absent at the last accepted head) and checks.
The one-shot lifecycle and stage gates remain.

Actual generic native Planning and Development runs are recorded in `MAT-codex-native-worker-evidence` for the observed
runtime. Named-role loading on a fresh host, denied approvals, failed emergency commits and wider host/version
coverage remain unverified. Deterministic contract/projection tests cover those instruction branches, not platform
enforcement; no persistent-grant or native confinement guarantee follows.

Stages delegate to `code-reviewer` (`review-refine`), `reconcile-reviewer` (`living-spec-draft`, as verifier) and `scout`
(`spike`); `challenger` has no stage of its own (its return is recorded at `spike`) and is delegated as the Planning effort asks
(at `medium` and `high`, `CAP-DLV-delivery-workflows` rule 15); `ux-reviewer` has no stage either and is delegated before code when screens are
drafted (`CAP-DLV-delivery-workflows` rule 15). `triage` and `decomposer` have no stage: Backlog delegates them from a clean checkout, `triage`
above 5 open feedback items on a host that runs it natively, `decomposer` for a merged `needs_decompose` return, the
user's request to split or an `XL` draft; the Host verifies the return, applies only what the user decides and names
the role in the Backlog commit body, with no envelope. Implementation stages keep
`role: developer`; the orchestration mode hands their turn to a worker. `[DELEGATE: role=<role> isolation=...]` in
`next` names the role; `spec-delegate` decides between a host subagent and a main-session substitute and records the
choice. A projected role receives only the per-call payload, since the host loads the contract body as its system
prompt.

### 4.2 Worker result inspection

`devkit spec worker inspect [--unit <dir>] [--base <accepted>] [--head <returned>]
[--rules-base <commit>] [--scope <prefix>... | --scope-file <file>] [--base-checkout <path>] [--details]` collects evidence in the activity worktree.
It derives its inputs from committed HEAD records and reports each value's source; explicit flags replace only
that input. Scope-file is UTF-8, one nonempty literal repository-relative prefix per line; a scope override
replaces the entire derived scope. Literal paths match themselves and descendants at path-component boundaries.
The devkit root is the Git top level (a `.devkit/` below it is refused with `DEVKIT_ROOT_NESTED`), so `--scope`
entries, task boundaries, reconciliation targets and the `devkitUnit` marker are repository-relative and are
compared with changed paths as they are. `N/A`/`none` boundaries and empty reconciliation targets add no scope.

- Unit: the branch's `devkitUnit` marker, else its activity-branch correspondence. A Development spec takes
  precedence over its accepted pre-handoff proposal; ambiguous or absent correspondence is unresolved.
- Head: the unique commit adding the highest-numbered worker envelope. Base: the commit adding the previous
  worker envelope when its state is unblocked, otherwise the common `diff_scope.base` of its unresolved problems.
  With no previous worker, use the single merge base with `devkitBase`, or the registered base checkout's branch.
- Rules base: `--rules-base` when supplied; otherwise the single merge base with `devkitBase` or the registered
  base checkout branch, independently of previous workers and `--base`. Without a recorded base branch or registered
  checkout, the audit base is used with source `audit-base-fallback`. Invalid recorded references remain errors.
- Scope: a Planning proposal directory; for Development, the unit directory, literal task boundaries, materials
  directory, reconciliation targets and explicitly linked Source feedback files whose returned-head status is `open`.
  WHEN a linked source is `resolved` at returned head and the same exact path and ID was `open` at the audit base,
  inspection MUST retain its `source-feedback` scope entry for that completion transition. Already terminal,
  unknown, missing or different-ID base sources add no implicit completion scope. Other returned-head terminal
  statuses remain excluded. Explicit task boundaries and full-replacement scope overrides remain independent.
  Entries retain their source,
  task number or feedback ID. Absent optional reconciliation adds no scope; malformed present reconciliation or
  missing required anchor/tasks leave the scope check not-run. Workflow stage requirements remain unchanged.
- Base checkout: the worktree's registered common-directory checkout; absent when run in the base itself. Its
  HEAD and dirty paths are information, not checks.

Inspection MUST preserve `scope` entries and `outside_scope`, and add top-level `scope_extensions` plus
`checks.scope_extensions`. Boundary entries add extension reason metadata without changing existing entry fields.
The extension check MUST compare exact annotation/record paths, owning task ordinals, identical reasons and AC IDs
owned by that task and declared by the spec. Committed prior-turn worker records remain relevant to retained
annotations; the highest worker sequence supplies repeated-path metadata. A historical record alone MUST NOT add
scope: its annotation must still exist. Missing/mismatched evidence or recognizable protected trees fail with
`SPEC_WORKER_SCOPE_EXTENSION_INVALID` (exit 1; correct the record or obtain Host authority). Malformed annotation
or input leaves the check not-run with `SPEC_WORKER_SCOPE_UNRESOLVED` or the envelope format cause; it never passes.
Recognizable protected classes include `.devkit/`, agent projections, agent instruction files (`AGENTS.md`,
`CLAUDE.md`), `.github/`, other unit/proposal trees, architecture documents, rule directories and known dependency
manifests/lockfiles. Semantic adjacency, custom protected paths, explicit payload denies and test weakening remain
reviewer judgments. With no extensions the list is empty and the added check passes. Host validation MUST verify this evidence before overriding scope, then name
every admitted extension in the complete override. A narrower `--scope`/`--scope-file` still fails omitted paths;
inspection MUST NOT union extensions into an explicit scope. Sync-output receipt checks remain independent.

Checks report `pass`, `fail` or `not-run`: base ancestry, worktree HEAD equality, changed paths and outside-scope
paths, worktree cleanliness, committed envelope validation (including unresolved problems and pending questions),
cumulative `devkit rules check --ci --base <rules_base>` and `devkit workflow next`. Both old and new paths of renames are
included. Rules run only when worktree HEAD equals returned head. Workflow evaluation is not-run in a dirty
worktree because the existing command reads disk; this prevents uncommitted records from changing its result.
Wrapped results retain their codes and actions.

`--format json` emits one object containing `inputs` (value/source, including `rules_base`), `scope` entries, `base`, `rules_base`, `head`, `changed_paths`,
`scope_extensions`, optional `outside_scope` and `base_checkout`, `checks`, `errors` (one advisory per failed check), `notices` and
`exit_code`. Text output emits `[WORKER_INSPECTION: verdict=pass|fail base= head=]`, then `[INPUT: ...]`, `[SCOPE_ENTRY: <path> source= ...]`,
changed-path and check sentinels; each failed check is an `[ERROR]` block on stderr after the notices. `-w` names
the worktree to inspect instead of the current directory, and `--strict` exits `1` on a warning when no check
failed. The compared commits and changed paths are reviewer payload
information. Default JSON keeps each check status, actionable findings, violations, notices, errors, unresolved problems, pending questions and recovery evidence; envelope entries contain metadata and current open findings rather than historical bodies. Successful wrapped check bodies are omitted. Workflow output retains the next action and approval evidence, with only stage identity, role, isolation and returns instead of the full stage definition. Unknown failed check payloads and diagnostic stdout/stderr remain intact. `--details --format json` includes all original wrapped results and envelope bodies. Both modes run every check and derive the same verdict from complete evidence. Exit 0 means no failed check, 1 means at least one failed check, and 2 means invalid invocation,
invalid Git inputs or unresolved required unit/head/base. A not-run check alone is a notice, not exit 1.

| Code | Meaning and action |
| --- | --- |
| `SPEC_WORKER_UNIT_UNRESOLVED` | `INPUT_ERROR`: supply `--unit` with the committed unit directory. |
| `SPEC_WORKER_HEAD_UNRESOLVED` | `INPUT_ERROR`: supply `--head` when there is no uniquely added latest worker envelope. |
| `SPEC_WORKER_BASE_UNRESOLVED` | `INPUT_ERROR`: supply `--base` when previous blocked records or base branch do not determine it. |
| `SPEC_WORKER_SCOPE_UNRESOLVED` | `INPUT_ERROR`: supply complete literal paths with `--scope` or `--scope-file`. |
| `SPEC_WORKER_SCOPE_EXTENSION_INVALID` | `ERROR` (exit `1`): correct annotation/record/task/AC evidence or obtain Host authority for a protected path. |
| `SPEC_WORKER_CHECK_NOT_RUN` | `NOTICE`: inspect the reported cause and rerun the named check after correcting it. |
| `SPEC_WORKER_ANCESTRY_FAILED`, `SPEC_WORKER_HEAD_FAILED`, `SPEC_WORKER_SCOPE_OUTSIDE`, `SPEC_WORKER_WORKTREE_DIRTY`, `SPEC_WORKER_ENVELOPES_FAILED`, `SPEC_WORKER_RULES_FAILED`, `SPEC_WORKER_WORKFLOW_FAILED` (`SPEC_WORKER_CHECK_FAILED` is their class code) | `ERROR` (`INTERACTION`, exit `1`): the named check failed; `[TARGET]` names the outside or dirty paths, the flags or the `checks.<name>` entry. The Host decides acceptance. |

The helper MUST NOT write records, modify files, repair, retry, synchronize, merge or widen scope. It adds no
approval request, workflow gate, integration refusal or scope registration. The Host's delegation payload remains
authoritative, and the Host decides acceptance under the existing procedure.
