"""Errors, warnings and notices of devkit-spec: ``AdvisoryError`` subclasses with ``SPEC_`` codes.

Each class carries the code and the Agent Advisory Protocol fields that fit
its condition, so a caller branches on ``error.code`` and the CLI boundary
renders the error as it is. devkit's own errors (``ARGUMENT_INVALID``,
``CONFIG_INVALID``, ``FRONTMATTER_INVALID``, ...) pass through unchanged.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry
from devkit_dist.base.errors import ConfigError

DEVKIT = "uv run devkit"
"""How every command an advisory or sentinel of devkit-spec names is run: devkit_dist's ``AGENT_INVOCATION``
(``ADR-keep-uv-run-as-the-agent-facing-devkit-invocation``). The package base may not import a feature module of
devkit_dist, so it is repeated here; a test keeps both equal."""


class SpecError(AdvisoryError):
    """Base class of every devkit-spec error; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class DocumentInvalidWarning(SpecError):
    """A file under ``docs/`` or ``specs/`` could not be read as a document and was left out (``WARNING``)."""

    code = "SPEC_DOCUMENT_INVALID"
    level = Level.WARNING
    fix = "Correct the file's frontmatter (devkit's frontmatter grammar; id, reconcile_id and status are strings)"


class UnresolvedIdError(SpecError):
    """A document ID given to a command names no document (``INPUT_ERROR``)."""

    code = "SPEC_ID_UNRESOLVED"
    input_error = True
    fix = f"Pass the exact ID of an existing document ({DEVKIT} spec list shows them)"


class DuplicateIdError(SpecError):
    """More than one document declares the ID (``MAINTENANCE``); references to it are ambiguous."""

    code = "SPEC_ID_DUPLICATE"
    fix = "Give each document its own ID: the ID follows the document's path (RULE-id-convention)"


class SpecConfigError(SpecError, ConfigError):
    """The ``[tool.spec]`` table of ``.devkit/config.toml`` is malformed (``INPUT_ERROR``)."""

    code = "SPEC_CONFIG_INVALID"
    target_files = (".devkit/config.toml",)
    fix = "Correct the value the message names in the [tool.spec] table of .devkit/config.toml, then rerun"


class GlossaryInvalidError(SpecError):
    """``docs/steering/glossary.yaml`` cannot be read or does not hold ``terms: [{primary, synonyms}]``
    (``INPUT_ERROR``)."""

    code = "SPEC_GLOSSARY_INVALID"
    input_error = True
    target_files = ("docs/steering/glossary.yaml",)
    fix = (
        "Correct docs/steering/glossary.yaml: terms is a list of mappings, each with a primary string and an optional "
        "synonyms list of strings"
    )


class ProposalSlugError(SpecError):
    """A proposal slug or PADR title keeps no letter or digit after normalization (``INPUT_ERROR``)."""

    code = "SPEC_PROPOSAL_SLUG_INVALID"
    input_error = True
    fix = "Pass a slug or title with at least one letter or digit (for example login-flow)"


class ProposalExistsError(SpecError):
    """The proposal to create already exists (``INPUT_ERROR``)."""

    code = "SPEC_PROPOSAL_EXISTS"
    input_error = True
    fix = "Choose another slug, or edit the existing proposal named in [TARGET]"


class ProposalDecisionExistsError(SpecError):
    """The PADR to create already exists in the proposal's ``decisions/`` (``INPUT_ERROR``)."""

    code = "SPEC_PADR_EXISTS"
    input_error = True
    fix = "Pass another title or --slug, or edit the existing PADR named in [TARGET]"


class ProposalSlugConflictError(SpecError):
    """A spec already uses the proposal's slug (``INTERACTION``): a handed-off ``PROP`` ID maps to one ``SPEC``."""

    code = "SPEC_PROPOSAL_SLUG_CONFLICT"
    actor = Actor.USER
    what_to_report = "Which unused slug the proposal takes, or whether it duplicates the existing spec in [TARGET]"
    fix = "Rerun with the unused slug the user chose; the existing spec keeps its ID"


class ProposalNotFoundError(SpecError):
    """No proposal bundle or single-file proposal has the slug (``INPUT_ERROR``)."""

    code = "SPEC_PROPOSAL_NOT_FOUND"
    input_error = True
    fix = f"Pass the slug of an existing proposal ({DEVKIT} spec list proposal shows them)"


class ProposalInvalidError(SpecError):
    """A proposal file or PADR cannot be read, its frontmatter does not parse, or a field the command reads has no
    valid value (``INPUT_ERROR``); [TARGET] names the file."""

    code = "SPEC_PROPOSAL_INVALID"
    input_error = True
    fix = "Correct the file in [TARGET] (UTF-8 text, devkit's frontmatter grammar), then rerun the command"


class ProposalRejectedPendingWarning(SpecError):
    """``rules check --phase hygiene``: a rejected proposal is still in the base, waiting for the Host's cleanup
    (rejection ADR, then deletion; ``WARNING``)."""

    code = "SPEC_PROPOSAL_REJECTED_PENDING"
    level = Level.WARNING


class MilestoneDoneUnsettledWarning(SpecError):
    """A done milestone still has unsettled base members."""

    code = "SPEC_MILESTONE_DONE_UNSETTLED"
    level = Level.WARNING


class MilestoneDroppedUnsettledWarning(SpecError):
    """A dropped milestone still has unsettled base members."""

    code = "SPEC_MILESTONE_DROPPED_UNSETTLED"
    level = Level.WARNING


class ProposalInPlanningError(SpecError):
    """``proposal check``: Backlog may not change the proposal: its ``plan-<slug>`` exists (Planning runs there), or
    it is no longer a draft (``BLOCKED``): a workflow guardrail. ``proposal check`` raises it as its negative answer
    (exit ``1``); a write it refuses (``padr``, ``new --decomposed-from``) exits ``2``."""

    code = "SPEC_PROPOSAL_IN_PLANNING"
    guardrail = True


class ProposalNotApprovedError(SpecError):
    """The proposal is not approved for handoff (``INTERACTION``)."""

    code = "SPEC_PROPOSAL_NOT_APPROVED"
    actor = Actor.USER
    what_to_report = "The proposal's status, and that its handoff needs the user's plan-accept of its direction"
    fix = (
        f"Ask the user for plan-accept; after the explicit acceptance record it with {DEVKIT} spec proposal accept: "
        "--direct for an eligible draft on the base checkout (Backlog), or without it on the proposal's plan- branch "
        "after Planning. "
        "Commit and merge that acceptance into this branch, then rerun the handoff"
    )


class ProposalNeedsDecomposeError(SpecError):
    """The proposal is marked ``needs_decompose: true`` (``INTERACTION``): Backlog splits it into new drafts; it is
    never planned or handed off as it is."""

    code = "SPEC_PROPOSAL_NEEDS_DECOMPOSE"
    actor = Actor.USER
    what_to_report = "That the proposal must be split in Backlog before Planning and handoff"
    fix = (
        "Split the proposal in Backlog into new draft proposals (or session or spec issues), delete the original "
        "draft, and plan the new drafts"
    )


class ProposalWrongWorktreeError(SpecError):
    """A handoff runs in a checkout whose branch is not ``dev-<slug>``, the Planning form of ``accept`` in one whose
    branch is not ``plan-<slug>``, or a composed ``accept --mode`` or ``handoff --effort`` off the retained base
    checkout (``INPUT_ERROR``): the change would land on another task's branch. The fix names the checkout and the
    exact command."""

    code = "SPEC_PROPOSAL_WRONG_WORKTREE"
    input_error = True


class ProposalAcceptRefusedError(SpecError):
    """``proposal accept``: the command does not accept the proposal in this form (``INPUT_ERROR``): a draft without
    ``--direct``, a proposal in review with it, an accepted proposal whose ``gate:plan-accept`` is recorded, a
    rejected one, or a single-file or unbound proposal, which has no gate records."""

    code = "SPEC_PROPOSAL_ACCEPT_REFUSED"
    input_error = True


class ProposalNotEligibleError(SpecError):
    """``proposal accept --direct``: the proposal fails a direct-acceptance condition (``INTERACTION``); every failed
    condition is a detail line, ``blocking: ...`` or ``pending: ...``. Nothing was written."""

    code = "SPEC_PROPOSAL_NOT_ELIGIBLE"
    actor = Actor.USER
    what_to_report = (
        "Each condition in [DETAIL], and that the draft runs Planning instead unless the condition is resolved"
    )
    fix = (
        "Report the conditions to the user; on the user's decision resolve them and rerun, or start Planning on the "
        "proposal's plan- branch. Never edit the status or the gate records by hand"
    )


class ProposalGateNotOpenError(SpecError):
    """``proposal accept``: the workflow did not open ``gate:plan-accept`` (``INTERACTION``), such as a missing
    ``collect-feedback`` sweep or an envelope hold; the status was restored and nothing was recorded."""

    code = "SPEC_PROPOSAL_GATE_NOT_OPEN"
    actor = Actor.USER
    what_to_report = "The unmet checks and hold reasons in [DETAIL], and that the acceptance is not recorded yet"
    fix = (
        "Once the user agrees, resolve them (for collect-feedback, sweep the session with the spec-feedback skill and "
        "record its feedback envelope; answer an open question with the user), then rerun the same accept command"
    )


class ProposalPolicyNotAutoError(SpecError):
    """``proposal accept --by policy`` while the owning ``plan-accept`` policy is not ``auto`` (``BLOCKED``): only
    the user accepts the proposal, so nothing was written. The tool never suggests recording an acceptance the user
    did not give."""

    code = "SPEC_PROPOSAL_POLICY_NOT_AUTO"
    guardrail = True
    target_files = (".devkit/config.toml",)
    what_to_report = (
        "That plan-accept policy is ask: the user accepts the proposal explicitly, or changes plan-accept to auto in "
        "[workflow.approvals] of the retained base's .devkit/config.toml"
    )


class ProposalAcceptanceUnrecordedError(SpecError):
    """``proposal handoff``: a proposal bound to ``sdd-proposal`` says ``status: accepted`` but has no effective
    accepted ``gate:plan-accept`` record (``INTERACTION``); nothing was written."""

    code = "SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED"
    actor = Actor.USER
    what_to_report = (
        "That the proposal's acceptance is not recorded, and whether a worker envelope shows that Planning ran"
    )
    fix = (
        "Stop and ask the user; never record an acceptance unasked. Without a worker envelope, after the user's "
        "explicit acceptance repair it on the base checkout with the direct form of proposal accept, merge the base "
        "into the dev- branch and rerun the handoff. With one, report it: on the user's decision the whole Planning "
        "merge is reverted on the base and Planning runs again"
    )


def acceptance_unrecorded_fix(slug: str) -> str:
    """The ``ProposalAcceptanceUnrecordedError`` fix with the proposal's exact repair command."""
    repair = f'{DEVKIT} spec proposal accept {slug} --by user --direct --note "<the user\'s reason>"'
    return (
        "Stop and ask the user; never record an acceptance unasked. Without a worker envelope, after the user's "
        f"explicit acceptance repair it on the base checkout with `{repair}`, merge the base into dev-{slug} and rerun "
        "the handoff. With one, report it: on the user's decision the whole Planning merge is reverted on the base "
        "and Planning runs again"
    )


class ProposalWorkflowError(SpecError):
    """The workflow of the proposal's ``task_kind`` (``sdd-spec-<task_kind>``) cannot be resolved or does not
    validate (``MAINTENANCE``)."""

    code = "SPEC_PROPOSAL_WORKFLOW_INVALID"
    fix = (
        f"Make the workflow the proposal's task_kind selects (sdd-spec-feature or sdd-spec-bugfix) available and valid "
        f"({DEVKIT} sync, {DEVKIT} workflow validate), or correct the proposal's task_kind, then rerun the handoff"
    )


class ProposalTargetExistsError(SpecError):
    """A file or directory the handoff would create already exists (``BLOCKED``), or a proposal path conflicts with a
    path of the existing materials directory it would merge into; nothing was written. A merge conflict is raised
    without the guardrail and with the user as actor (``INTERACTION``: ask the user before reconciling), with its own
    fix naming the source path, the destination path and the collision kind, never removal of the directory."""

    code = "SPEC_PROPOSAL_TARGET_EXISTS"
    guardrail = True
    fix = "Move or remove the path in [TARGET] (or rename the PADR whose ADR it is), then rerun the handoff"


class ProposalHandoffError(SpecError):
    """Writing the handoff failed (``MAINTENANCE``); the files it had written were removed and the proposal kept."""

    code = "SPEC_PROPOSAL_HANDOFF_FAILED"
    fix = "Fix the file system problem in [DETAIL], then rerun the handoff"


class ProposalCleanupWarning(SpecError):
    """The handoff completed but the proposal could not be removed, or the post-finish prune of the slug's empty
    proposal directories failed (``WARNING``)."""

    code = "SPEC_PROPOSAL_CLEANUP_FAILED"
    level = Level.WARNING
    fix = "Delete the proposal in [TARGET] by hand: the spec bundle replaces it"


class ProposalGateNotCarriedWarning(SpecError):
    """The handoff completed but one of the proposal's approvals (``plan-intent``, ``plan-accept``) could not be
    carried to the spec (``WARNING``); the gates recorded before it stay."""

    code = "SPEC_PROPOSAL_GATE_NOT_CARRIED"
    level = Level.WARNING
    fix = f"Once the cause in [DETAIL] is resolved, ask the user again for each gate {DEVKIT} workflow next reports as waiting"


class ProposalLinkUnresolvedWarning(SpecError):
    """Links or ID references into the removed proposal have no new target (``WARNING``)."""

    code = "SPEC_PROPOSAL_LINK_UNRESOLVED"
    level = Level.WARNING
    fix = (
        "Edit each [UNRESOLVED_LINK] location by hand: point it at the spec, ADR or material that replaced the "
        "target, or remove it"
    )


class ApprovalKeyIgnoredWarning(SpecError):
    """A ``[workflow.approvals]`` key that names no gate of the spec workflows' policy, such as ``exception`` (a stage,
    always handled by a person) (``WARNING``): it has no effect and is not listed as a policy."""

    code = "SPEC_APPROVAL_KEY_IGNORED"
    level = Level.WARNING


class ProposalReferencesRewrittenNotice(SpecError):
    """ID references to the proposal or its PADRs now name the spec or the ADRs (``NOTICE``)."""

    code = "SPEC_PROPOSAL_REFS_REWRITTEN"
    level = Level.NOTICE
    fix = (
        "Reread the sentence at each [REWRITTEN ... kind=id] location: one that names the proposal as an origin may "
        "need rewording"
    )


class ProposalUnboundNotice(SpecError):
    """A new proposal or handed-off spec is not bound to a workflow: its default workflow is not available
    (``NOTICE``)."""

    code = "SPEC_PROPOSAL_UNBOUND"
    level = Level.NOTICE
    fix = f"Once a workflow fits the unit, bind it with {DEVKIT} workflow bind ({DEVKIT} workflow validate lists them)"


class ListStatusUnknownNotice(SpecError):
    """``devkit spec list --status``: a requested status occurs on no indexed document of the selected kinds
    (``NOTICE``); the filter still applies, since a valid status may simply be unused so far."""

    code = "SPEC_LIST_STATUS_UNKNOWN"
    level = Level.NOTICE
    fix = f"Pass a status the documents of the selected kinds carry ({DEVKIT} spec list shows them)"


class PostFinishCleanupNotice(SpecError):
    """``devkit.post_finish``: a proposal directory was pruned or a finished worktree's scope record removed
    during scoped local integration (``NOTICE``)."""

    code = "SPEC_POST_FINISH_CLEANUP"
    level = Level.NOTICE


class SpecSlugError(SpecError):
    """A spec slug keeps no letter or digit after normalization (``INPUT_ERROR``)."""

    code = "SPEC_SLUG_INVALID"
    input_error = True
    fix = "Pass a slug with at least one letter or digit (for example login-flow)"


class SpecWrongBranchError(SpecError):
    """``devkit spec new`` on another branch than ``dev-<slug>`` (``INPUT_ERROR``): a spec unit is Development's and
    lives on its activity branch (inline Planning starts that branch first)."""

    code = "SPEC_WRONG_BRANCH"
    input_error = True


class SpecExistsError(SpecError):
    """``devkit spec new``: the slug is taken by a spec or a proposal, or the bundle directory exists
    (``INPUT_ERROR``)."""

    code = "SPEC_EXISTS"
    input_error = True
    fix = (
        f"Choose an unused slug; for a proposal of the same slug, hand it off with {DEVKIT} spec proposal handoff "
        "instead"
    )


class SpecWorkflowError(SpecError):
    """``devkit spec new --workflow`` names a workflow that does not resolve or validate (``INPUT_ERROR``)."""

    code = "SPEC_WORKFLOW_INVALID"
    input_error = True
    fix = f"Pass the id of a valid workflow ({DEVKIT} workflow validate), or omit --workflow for sdd-spec-feature"


class SpecWriteError(SpecError):
    """``devkit spec new``: writing the bundle failed (``MAINTENANCE``); what was written was removed, except what
    the details list when the roll-back was incomplete."""

    code = "SPEC_WRITE_FAILED"
    fix = "Fix the file system problem in [DETAIL], then rerun the command"


class SpecUnboundNotice(SpecError):
    """``devkit spec new``: the spec is not bound, ``sdd-spec-feature`` is not available (``NOTICE``)."""

    code = "SPEC_UNBOUND"
    level = Level.NOTICE
    fix = f"Once a workflow fits the unit, bind it with {DEVKIT} workflow bind ({DEVKIT} workflow validate lists them)"


class EntrypointsInputMissingError(SpecError):
    """``devkit spec entrypoints derive --spec``: the bundle has no ``tasks.md`` or ``reconcile.md``
    (``INPUT_ERROR``)."""

    code = "SPEC_ENTRYPOINTS_INPUT_MISSING"
    input_error = True
    fix = (
        "Write the file in [TARGET] first (tasks.md with the spec-tasks skill, reconcile.md with the spec-sync "
        "skill), then rerun the derivation"
    )


class EntrypointsInputInvalidError(SpecError):
    """``devkit spec entrypoints derive --spec``: ``tasks.md`` or ``reconcile.md`` cannot be read, or the
    frontmatter of ``reconcile.md`` is not the shape ``RULE-reconcile-contract`` checks (``INPUT_ERROR``)."""

    code = "SPEC_ENTRYPOINTS_INPUT_INVALID"
    input_error = True
    fix = (
        "Repair the file in [TARGET] (UTF-8 text; reconcile.md frontmatter with targets: [{file, resolution}]), "
        "then rerun the derivation"
    )


class EntrypointsPathError(SpecError):
    """An entrypoint path is not a literal workspace-relative path: empty, absolute, with a ``..`` segment, a glob,
    a backslash, a drive colon or a control character (``INPUT_ERROR``)."""

    code = "SPEC_ENTRYPOINTS_PATH_INVALID"
    input_error = True
    fix = "Pass a literal workspace-relative file or directory path (no glob, no leading /, no .. segment)"


class EntrypointsTargetError(SpecError):
    """``devkit spec entrypoints derive --apply --target``: the ID or path is not among the derived documents
    (``INPUT_ERROR``)."""

    code = "SPEC_ENTRYPOINTS_TARGET_UNKNOWN"
    input_error = True
    fix = "Pass the ID or path of a document that appears in the derive output without --apply"


class EntrypointsCodeUnmatchedError(SpecError):
    """``devkit spec entrypoints derive --code``: a path equals, contains and lies under no candidate of the derived
    documents (of the ``--target`` documents with ``--apply``) (``INPUT_ERROR``); [TARGET] lists every such value and
    nothing was written."""

    code = "SPEC_ENTRYPOINTS_CODE_UNMATCHED"
    input_error = True
    fix = (
        "Run the same derive without --code to list the candidates, then pass only --code paths equal to, containing "
        "or under a candidate of the targeted documents, or drop the --code values in [TARGET]"
    )


class EntrypointsApplyError(SpecError):
    """``devkit spec entrypoints derive --apply``: some documents could not be written (``MAINTENANCE``); the
    documents in [TARGET] are unchanged, the others listed as applied were written."""

    code = "SPEC_ENTRYPOINTS_APPLY_FAILED"
    fix = "Fix the problem in [DETAIL] for each document in [TARGET], then rerun the same command with --apply"


class ScopeError(SpecError):
    """Base class of the work-scope registry errors (``devkit spec scope``)."""


class ScopeCollectionPartialWarning(ScopeError):
    """``scope collect``: some requested observation or comparison evidence is unavailable (``WARNING``); [TARGET]
    names each source with a gap, [DETAIL] each source and reason once. The base checkout is never a gap."""

    code = "SPEC_SCOPE_COLLECTION_PARTIAL"
    level = Level.WARNING
    fix = (
        f"For source-timeout or result-limit run `{DEVKIT} spec scope collect --timeout 120 --source-timeout 30`; "
        "a source that is identity-ambiguous or has an unknown base needs its unit committed on its activity branch"
    )


class ScopeCollectionFailedError(ScopeError):
    """``scope collect``: no selected inventory source could be read (``INPUT_ERROR``); [TARGET] names the
    unreadable sources."""

    code = "SPEC_SCOPE_COLLECTION_FAILED"
    input_error = True
    fix = (
        "Run it inside a Git work tree of the project (or pass it with -w) and select a readable source with --mode, "
        "then rerun scope collect"
    )


class ScopeNotAWorktreeError(ScopeError):
    """The workspace is not inside a Git work tree, so it has no registry location or token (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_NOT_A_WORKTREE"
    input_error = True
    fix = "Run the command inside a Git work tree of the project, or pass it with -w"


class ScopeSpecNotFoundError(ScopeError):
    """``--spec`` names no directory in the workspace (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_SPEC_NOT_FOUND"
    input_error = True
    fix = f"Pass an existing spec bundle directory ({DEVKIT} spec list spec --history lists them)"


class ScopeInputInvalidError(ScopeError):
    """A scope input (``tasks.md``, ``reconcile.md``, ``target-docs.md``) cannot be read, or its ``targets``
    frontmatter is not a list of mappings with a string ``file`` (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_INPUT_INVALID"
    input_error = True
    fix = (
        "Repair the file in [TARGET] (UTF-8 text; targets is a list of mappings, each with a workspace-relative file), "
        "then rerun"
    )


class ScopeTokenMissingError(ScopeError):
    """This worktree holds no registry token: it registered no task, or released it (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_TOKEN_MISSING"
    input_error = True
    fix = (
        "A worktree that does not take part in the registry skips scope update; to take part, register first: "
        f"{DEVKIT} spec scope register --spec with the spec bundle directory"
    )


class ScopeTokenExistsError(ScopeError):
    """This worktree already registered a task; a second registration would orphan the first (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_TOKEN_EXISTS"
    input_error = True
    fix = (
        f"Keep the registration ({DEVKIT} spec scope query shows it with own=yes) and run {DEVKIT} spec scope update, "
        f"or run {DEVKIT} spec scope release first"
    )


class ScopeTaskExistsError(ScopeError):
    """Another record of the namespace has the task ID (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_TASK_EXISTS"
    input_error = True
    fix = "Pass a distinct --task-id, or release the other record from the worktree that registered it"


class ScopeRecordMissingError(ScopeError):
    """The record of this worktree's token no longer exists: it was released or swept (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_RECORD_MISSING"
    input_error = True
    fix = (
        f"Run {DEVKIT} spec scope release (it removes the orphaned token), then {DEVKIT} spec scope register --spec "
        "with the spec bundle directory"
    )


class ScopeTokenMismatchError(ScopeError):
    """The token does not own the record: only the registering worktree updates or releases it (``BLOCKED``)."""

    code = "SPEC_SCOPE_TOKEN_MISMATCH"
    guardrail = True
    fix = (
        "Update or release the record from the worktree that registered it; sweep removes records of removed worktrees"
    )


class ScopeStaleRevisionError(ScopeError):
    """The record changed between the read and the write (``AUTO``); nothing was written."""

    code = "SPEC_SCOPE_STALE_REVISION"
    actor = Actor.TOOL
    retry = Retry.SAFE
    fix = "Rerun the same command: it reads the current revision"


class ScopeTimeoutError(ScopeError):
    """The operation exceeded ``[tool.spec.scope] timeout``: the namespace lock or Git stayed busy (``DEFER``)."""

    code = "SPEC_SCOPE_TIMEOUT"
    actor = Actor.NONE
    retry = Retry.SAFE
    fix = (
        "Retry once the other registry command has finished (an update with the --request-id its [SCOPE_ACK] "
        "printed); raise [tool.spec.scope] timeout when the registry is busy for longer"
    )


class ScopeLockUnsupportedError(ScopeError):
    """The platform has no ``fcntl.flock``: the local registry runs on Linux and macOS only (``BLOCKED``)."""

    code = "SPEC_SCOPE_LOCK_UNSUPPORTED"
    guardrail = True
    fix = f"Run {DEVKIT} spec scope on Linux or macOS"


class ScopeNamespaceError(ScopeError):
    """A registry namespace is empty, contains a path separator or starts with a dot (``INPUT_ERROR``)."""

    code = "SPEC_SCOPE_NAMESPACE_INVALID"
    input_error = True
    fix = "Set [tool.spec.scope] namespace to a plain name of letters, digits, '.', '_' and '-' not starting with '.'"


class ScopeSharedPathError(ScopeError):
    """The shared registry directory cannot be created, read or written (``INTERACTION``)."""

    code = "SPEC_SCOPE_SHARED_PATH_UNAVAILABLE"
    actor = Actor.USER
    retry = Retry.AFTER_FIX
    what_to_report = "The registry directory in [TARGET] and the file system error"
    fix = "Fix the permissions of the directory in [TARGET], or set [tool.spec.scope] shared_path to a writable one"


class ScopeUnsupportedError(ScopeError):
    """An adapter operation reserved by the registry contract (``claim``) is not implemented (``MAINTENANCE``)."""

    code = "SPEC_SCOPE_UNSUPPORTED"
    fix = "Do not call the reserved operation: exclusive claims are not part of the local registry"


class ScopeAckFailedError(ScopeError):
    """``devkit spec scope update`` did not apply for a cause without its own code (``MAINTENANCE``); the record is
    unchanged."""

    code = "SPEC_SCOPE_ACK_FAILED"
    fix = f"Fix the cause in [DETAIL], then rerun {DEVKIT} spec scope update"


class ScopeSharedWorktreeWarning(ScopeError):
    """Another task of the namespace registered the same worktree (``WARNING``): changes observed there are
    attributed to both."""

    code = "SPEC_SCOPE_SHARED_WORKTREE"
    level = Level.WARNING
    fix = "Run one registered task per worktree; release the other task's record when it is done"


class ScopeRecordInvalidWarning(ScopeError):
    """A record file of the namespace cannot be read or parsed and was left out (``WARNING``)."""

    code = "SPEC_SCOPE_RECORD_INVALID"
    level = Level.WARNING
    fix = (
        f"Delete the record file in [TARGET] once its task is known to be finished ({DEVKIT} spec scope sweep lists it)"
    )


class ScopeJournalWarning(ScopeError):
    """The event journal could not be written (``WARNING``); the operation itself succeeded or failed as reported."""

    code = "SPEC_SCOPE_JOURNAL_UNAVAILABLE"
    level = Level.WARNING
    fix = "Make journal.jsonl in [TARGET] a writable file; the registry works without it"


class ScopeJournalLineWarning(ScopeError):
    """Lines of the event journal are not JSON events and were skipped (``WARNING``)."""

    code = "SPEC_SCOPE_JOURNAL_LINE_INVALID"
    level = Level.WARNING
    fix = "Remove or repair the lines named in [DETAIL] of journal.jsonl in [TARGET]"


class ScopeRegisterFailedWarning(ScopeError):
    """``devkit spec proposal handoff`` completed in the task worktree but registering its scope failed
    (``WARNING``)."""

    code = "SPEC_SCOPE_REGISTER_FAILED"
    level = Level.WARNING
    fix = (
        f"Fix the cause in [DETAIL], then run {DEVKIT} spec scope register --spec with the handed-off spec bundle "
        "directory in the worktree"
    )


class HandoffNotReadyError(SpecError):
    """The composed handoff (``proposal handoff --effort``): the committed proposal on the base is not accepted,
    needs decomposition, or its ``sdd-proposal`` workflow lacks a completed Planning with its own ``plan-intent`` and
    ``plan-accept`` (``INTERACTION``); [DETAIL] names the condition, [TARGET] the proposal and nothing was written."""

    code = "SPEC_HANDOFF_NOT_READY"
    actor = Actor.USER
    what_to_report = (
        "The proposal's state in [DETAIL], and that Development starts only from an accepted proposal whose Planning "
        "completed"
    )


class HandoffBaseDirtyError(SpecError):
    """The composed handoff: the retained base checkout has uncommitted changes (``INTERACTION``); [TARGET] lists
    them and nothing was written."""

    code = "SPEC_HANDOFF_BASE_DIRTY"
    actor = Actor.USER
    what_to_report = "The uncommitted paths in [TARGET] of the retained base checkout"
    fix = (
        "Once the user decides, commit or move those changes so the base checkout is clean, then rerun the same command"
    )


class HandoffWorktreeConflictError(SpecError):
    """The composed handoff: a ``dev-<slug>`` worktree exists that devkit did not create for this accepted base, or it
    holds changes or another commit (``INTERACTION``); it is never reused or removed."""

    code = "SPEC_HANDOFF_WORKTREE_CONFLICT"
    actor = Actor.USER
    what_to_report = "The existing Development worktree in [TARGET] and why it cannot be reused ([DETAIL])"
    fix = (
        "Once the user decides what happens to its changes, preserve them and remove the worktree in [TARGET], then "
        "rerun the same command"
    )


class HandoffReplyError(SpecError):
    """The CLI handoff has no valid activity effort (``INPUT_ERROR``)."""

    code = "SPEC_HANDOFF_REPLY_INVALID"
    input_error = True
    target_files = ("--effort",)
    fix = f"Rerun {DEVKIT} spec proposal handoff with --effort low, --effort medium or --effort high"


class HandoffStaleError(SpecError):
    """The approved proposal, base commit, policy or new worktree changed between the check and an effect of the
    composed handoff (``INTERACTION``); the effects completed before it are kept."""

    code = "SPEC_HANDOFF_STALE"
    actor = Actor.USER
    what_to_report = "What changed ([DETAIL] and the message) and the effects the result reports as completed"
    fix = "After the user has reviewed the change, rerun the same command for the remaining effects"


class ProposalApprovalStaleError(SpecError):
    """The composed acceptance: the reviewed source, base, environment or exact acceptance delta changed
    (``INTERACTION``); completed effects are kept and the remaining ones need fresh approval."""

    code = "SPEC_PROPOSAL_APPROVAL_STALE"
    actor = Actor.USER
    what_to_report = "What changed (the message and [DETAIL]) and the completed effects the result reports"
    fix = "After the user has reviewed the change and approved again, rerun the same command for the remaining effects"


class ProposalApprovalNotReadyError(SpecError):
    """The composed acceptance (``proposal accept --mode``): the proposal on ``plan-<slug>`` is not ready for
    ``plan-accept``: Planning has unmet checks, open questions or holds, it needs decomposition, or it is not in
    review (``INTERACTION``); [DETAIL] lists the conditions and nothing was written."""

    code = "SPEC_PROPOSAL_APPROVAL_NOT_READY"
    actor = Actor.USER
    what_to_report = "The Planning conditions in [DETAIL] that keep the proposal from plan-accept"


class ProposalApprovalReplyError(SpecError):
    """The requested or confirmed acceptance mode or Development effort is invalid (``INPUT_ERROR``)."""

    code = "SPEC_PROPOSAL_APPROVAL_REPLY_INVALID"
    input_error = True
    target_files = ("--mode", "--effort")
    fix = "Choose accept_only, or accept_and_handoff with a low, medium or high Development effort, then rerun"


class ProposalAcceptCommitRefusedError(SpecError):
    """The composed acceptance: devkit's commit gate refused the acceptance commit on ``plan-<slug>``
    (``INPUT_ERROR``); the acceptance writes were withdrawn, [DETAIL] carries the gate's last output lines."""

    code = "SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED"
    input_error = True


class WorkerUnitUnresolvedError(SpecError):
    """``spec worker inspect``: the committed unit could not be derived from the branch (``INPUT_ERROR``)."""

    code = "SPEC_WORKER_UNIT_UNRESOLVED"
    input_error = True
    target_files = ("--unit",)
    fix = "Pass --unit with the committed unit directory"


class WorkerHeadUnresolvedError(SpecError):
    """``spec worker inspect``: no uniquely added latest worker envelope names the returned commit
    (``INPUT_ERROR``)."""

    code = "SPEC_WORKER_HEAD_UNRESOLVED"
    input_error = True
    target_files = ("--head",)
    fix = "Pass --head with the returned commit"


class WorkerBaseUnresolvedError(SpecError):
    """``spec worker inspect``: the previous worker records or the base branch do not determine the base
    (``INPUT_ERROR``)."""

    code = "SPEC_WORKER_BASE_UNRESOLVED"
    input_error = True
    target_files = ("--base",)
    fix = "Pass --base with the last accepted commit"


class WorkerScopeUnresolvedError(SpecError):
    """``spec worker inspect``: the unit's scope records are missing or invalid, or a given scope path is not
    literal (``INPUT_ERROR``); the scope check is not run."""

    code = "SPEC_WORKER_SCOPE_UNRESOLVED"
    input_error = True
    target_files = ("--scope", "--scope-file")
    fix = "Pass --scope with each authorized path or --scope-file with the complete scope"


class WorkerCheckNotRunNotice(SpecError):
    """``spec worker inspect``: a check could not run (``NOTICE``); a not-run check alone does not fail the
    inspection."""

    code = "SPEC_WORKER_CHECK_NOT_RUN"
    level = Level.NOTICE
    fix = "Inspect the reported cause and run the named check after correcting it"


class WorkerCheckFailedError(SpecError):
    """``spec worker inspect``: a check of the returned worker result failed (``INTERACTION``, exit ``1``): the
    inspection's negative answer, one advisory per failed check with its own code
    (``SPEC_WORKER_<CHECK>_FAILED``, ``SPEC_WORKER_SCOPE_OUTSIDE``); [TARGET] names the paths or check it concerns.
    The Host decides acceptance; the command never repairs."""

    code = "SPEC_WORKER_CHECK_FAILED"
    actor = Actor.USER
    exit_code = ExitCode.FINDINGS
    what_to_report = (
        "The failed check, its cause and [TARGET]; the Host decides whether to return the result to the worker"
    )


class ReportArgumentError(SpecError):
    """``proposal report``: the slug is not a proposal slug or ``--source-sha`` is not a full lowercase commit SHA
    (``INPUT_ERROR``); checked before the checkout is read."""

    code = "SPEC_REPORT_ARGUMENT_INVALID"
    input_error = True


class ReportSourceNotHeadError(SpecError):
    """``proposal report``: ``--source-sha`` is neither the current commit of this checkout nor of the proposal's
    ``plan-<slug>`` worktree (``INPUT_ERROR``)."""

    code = "SPEC_REPORT_SOURCE_NOT_HEAD"
    input_error = True
    target_files = ("--source-sha",)


class ReportSourceDirtyError(SpecError):
    """``proposal report``: the source checkout has uncommitted changes (``INPUT_ERROR``); the report reads committed
    records only, [TARGET] lists the changed paths."""

    code = "SPEC_REPORT_SOURCE_DIRTY"
    input_error = True


class ReportWrongCheckoutError(SpecError):
    """``proposal report``: the source is neither ``plan-<slug>`` with a proposal in review or accepted, nor the
    retained base with an accepted proposal (``INPUT_ERROR``)."""

    code = "SPEC_REPORT_WRONG_CHECKOUT"
    input_error = True


class ReportSourceInvalidError(SpecError):
    """``proposal report``: a committed record of the proposal cannot be read: not a regular file, a PADR whose ID
    differs from its file name, an envelope that is not a mapping, or an effort outside low, medium and high
    (``INPUT_ERROR``); [TARGET] names the record."""

    code = "SPEC_REPORT_SOURCE_INVALID"
    input_error = True
