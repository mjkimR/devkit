"""``devkit spec proposal new|padr|accept|handoff|prune|check``: incubate a proposal, record its preliminary decisions,
record the user's acceptance, hand it off, and guard Backlog changes.

Text output (paths are relative to the workspace root):

- ``new``: ``[PROPOSAL: <id> path= dir= target_docs= workflow= planning_effort= dev_effort=]``, with a trailing
  ``namespace=`` when the bundle reports one (``CreatedProposal.namespace``), and, when ``proposal.md`` is bound to a
  workflow, ``[NEXT_CMD: uv run devkit workflow next --unit <dir>]``.
- ``padr``: ``[PADR: <id> path= proposal=]``.
- ``prune``: ``[PRUNED: <dir>]`` per empty proposal directory removed, else ``[OK: nothing to prune]``.
- ``report``: the report template Markdown of the source itself, read-only and nothing published (JSON: ``proposal``,
  ``source_sha``, ``report``); ``source_sha`` defaults to the workspace ``HEAD``.
- ``accept``: ``[ACCEPTED: ...]`` with basic Backlog acceptance, and ``[ACCEPT_CHECK: ... eligible=yes|no]`` with
  ``--check`` and nothing written (exit ``1`` when not eligible). Refusals: ``SPEC_PROPOSAL_ACCEPT_REFUSED``,
  ``SPEC_PROPOSAL_NOT_ELIGIBLE``, ``SPEC_PROPOSAL_WRONG_WORKTREE``, ``SPEC_PROPOSAL_GATE_NOT_OPEN``,
  ``SPEC_PROPOSAL_POLICY_NOT_AUTO``. The composed ``--mode`` form and ``handoff --effort`` print through
  ``_echo_composed``: the success kind, ``<KIND>_STOPPED`` after partial effects (exit ``1``), or the refusal itself
  (exit ``2``).
- ``check``: ``[PROPOSAL: <id> path= status=draft editable=yes]`` when Backlog may edit, split or delete the proposal;
  ``SPEC_PROPOSAL_IN_PLANNING`` (exit ``1``) while its ``plan-<slug>`` exists or once it left ``draft``.
- ``handoff``: ``[HANDOFF: <proposal id> spec= dir= workflow=]`` (with ``dev_effort=`` when the proposal declared it),
  then ``[TARGET_DOCS: <path>]``,
  ``[MATERIALS: <dir>]`` (``merged=yes`` when the materials were merged into an existing directory), one
  ``[DROPPED_DUPLICATE: <path>]`` per kept file whose byte-identical proposal copy was dropped, one
  ``[PROMOTED_ADR: <id> path= padr=]`` per promoted decision, one
  ``[DROPPED_RECORD: <path>]`` per workflow record of the proposal unit removed with it, one
  ``[CARRIED_GATE: <request> decision=<path>]`` per approval of the proposal (``gate:plan-intent``,
  ``gate:plan-accept``) recorded in the spec under its name, one
  ``[REWRITTEN: <path>:<line> kind=link|id|path from= to=]`` per rewritten link, reference or code-span path, one
  ``[UNRESOLVED_LINK: <path>:<line> kind= target= reason=]`` per link or reference left as it was,
  ``[SCOPE: <task> namespace= ... token=]`` when it registered the bundle's work scope, and
  ``[NEXT_CMD: uv run devkit workflow next --unit <dir>]`` when ``spec.md`` is bound to a workflow. With ``--effort``,
  it composes Development worktree creation and handoff, reporting status and authority.

A handoff inside a linked worktree registers the new bundle in the work-scope registry (``devkit spec scope
register``) at either ``[tool.spec] worktree`` level; a registration failure is only a verbose diagnostic and leaves
the handoff done.

A gate of the spec that could not be recorded is a ``SPEC_PROPOSAL_GATE_NOT_CARRIED`` warning, unresolved links a
``SPEC_PROPOSAL_LINK_UNRESOLVED`` warning, rewritten ID references a ``SPEC_PROPOSAL_REFS_REWRITTEN`` notice and an
unbound proposal or spec a ``SPEC_PROPOSAL_UNBOUND`` notice, all on stderr.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
from devkit.advisory import Actor, AdvisoryError, ExitCode, Retry
from devkit_core.core import run_git
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    is_json,
    output_settings,
    resolve_root,
    workspace_option,
)

from devkit_spec.adapters.cli import sentinel
from devkit_spec.base.axes import EFFORTS
from devkit_spec.base.errors import SpecError
from devkit_spec.features.delivery.usecases.handoff import HandoffProposalUseCase
from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase
from devkit_spec.features.delivery.usecases.native_plan_accept import PlanAcceptUseCase
from devkit_spec.features.proposals.usecases.accept import ACTOR, AcceptProposalUseCase
from devkit_spec.features.proposals.usecases.backlog import CheckBacklogUseCase
from devkit_spec.features.proposals.usecases.prune import PruneProposalsUseCase
from devkit_spec.features.proposals.usecases.scaffold import CreateProposalDecisionUseCase, CreateProposalUseCase
from devkit_spec.features.scope.cli.output import echo_registered, registered_dict
from devkit_spec.utils.advisory import restore_advisory

WORKSPACE = workspace_option()


SUCCESS = frozenset({"accepted", "handed_off"})


def _advisory(item: dict[str, Any]) -> AdvisoryError:
    """Rebuild a serialized lifecycle advisory; its ``ERROR`` keeps its exit code."""
    return restore_advisory(
        item,
        actor=Actor.DEVELOPER,
        retry=Retry.AFTER_FIX,
        message="Lifecycle operation reported an advisory",
        restore_exit_code=True,
    )


def _result_advisories(result: dict[str, Any]) -> tuple[list[AdvisoryError], list[AdvisoryError]]:
    """The errors and the warnings and notices of a composed result, its handoff's included, each once."""
    handoff = result.get("handoff") or {}
    seen: set[tuple[object, object]] = set()
    errors: list[AdvisoryError] = []
    notices: list[AdvisoryError] = []
    for key, into in (("errors", errors), ("notices", notices)):
        for item in [*result.get(key, []), *handoff.get(key, [])]:
            identity = (item.get("code"), item.get("message"))
            if identity not in seen:
                seen.add(identity)
                into.append(_advisory(item))
    return errors, notices


def _composed_exit(result: dict[str, Any], errors: list[AdvisoryError], effects: bool) -> int:
    """``0`` for a completed outcome, ``2`` when nothing was done, ``1`` when effects stopped part-way."""
    if result.get("status") in SUCCESS and not errors:
        return 0
    return 1 if effects else 2


def _echo_composed(kind: str, slug: str, result: dict[str, Any], effects: bool, **fields: object) -> None:
    """Print a composed acceptance or handoff and exit with its outcome (``ARCH-08-1-agent-output``).

    A completed outcome prints ``[<kind>: ...]``; one that stopped part-way prints ``[<kind>_STOPPED: ...]`` with the
    completed effects, exits ``1`` and renders its errors last; one that did nothing is its errors, the last
    one deciding (always exit ``2``; ``{"error": <last>, "errors": [<the others>], "notices": [...]}`` under
    ``--format json``). The next command, when there is one, follows as
    ``[NEXT_CMD: ...]``, else the next action as ``[NEXT_ACTION: ...]``.
    """
    errors, notices = _result_advisories(result)
    code = _composed_exit(result, errors, effects)
    if code == 2:
        if not errors:
            errors = [SpecError(f"PROP-{slug}: the composed operation stopped with status {result.get('status')}")]
        if output_settings().json:
            # One error document: the decisive (last) error, the earlier ones beside it, exit 2 whatever they carry.
            document: dict[str, Any] = {"error": errors[-1].to_dict()}
            if len(errors) > 1:
                document["errors"] = [error.to_dict() for error in errors[:-1]]
            echo_json(document | {"notices": [notice.to_dict() for notice in notices]})
        else:
            echo_notices(notices)
            for error in errors:  # every error once; the last one ends the output
                click.echo(error.render(), err=True)
        raise click.exceptions.Exit(int(ExitCode.ERROR))
    if output_settings().json:
        echo_json(result)
    else:
        name = kind if code == 0 else f"{kind}_STOPPED"
        click.echo(sentinel(name, f"PROP-{slug}", status=result.get("status", "-"), **fields))
        handoff = result.get("handoff") or {}
        command = result.get("next_command") or handoff.get("next_command")
        if command:
            click.echo(f"[NEXT_CMD: {command}]")
        elif code and result.get("next_action"):
            click.echo(sentinel("NEXT_ACTION", result["next_action"]))
    echo_notices(notices)
    if code == 0:
        exit_on_warnings(notices)
        return
    if not output_settings().json:
        for error in errors:
            click.echo(error.render(), err=True)
    raise click.exceptions.Exit(code)


@click.group(name="proposal")
def proposal_group() -> None:
    """Incubate proposals in docs/proposals/ and hand approved ones off to spec bundles."""


@proposal_group.command(name="new")
@click.argument("slug")
@click.option("--title", "-t", default=None, help="Proposal title [default: the slug]")
@click.option("--target-area", "-a", default=None, help="Capability area the proposal targets (capabilities/<area>/)")
@click.option("--milestone", "-m", default=None, help="Existing global MS-<slug> milestone ID")
@click.option(
    "--task-kind",
    default=None,
    help="task-kind of the work: feature or bugfix; the spec follows sdd-spec-<task-kind> after handoff "
    "[default: feature]",
)
@click.option(
    "--planning-effort",
    default=None,
    help="Recommended activity-effort hint for Planning: low, medium or high [default: medium]",
)
@click.option(
    "--dev-effort",
    default=None,
    help="Recommended activity-effort hint for Development: low, medium or high [default: medium]",
)
@click.option(
    "--namespace",
    default=None,
    help="Document namespace of the bundle: global or a registered package; carried to spec.md "
    "[default: the current directory's]",
)
@click.option(
    "--summary",
    default=None,
    help="One or two English sentences: what the proposal changes and why; carried to spec.md [default: none]",
)
@click.option(
    "--supersedes",
    default=None,
    help="PROP-<slug> of the accepted proposal this draft replaces (close by supersede) [default: none]",
)
@click.option("--decomposed-from", default=None, help="PROP-<slug> of the editable draft being decomposed")
@click.option("--needs-decompose", is_flag=True, help="Mark the draft to be split in Backlog before Planning starts")
@click.option("--with-target-docs", is_flag=True, help="Also scaffold target-docs.md, the Living Spec blueprint")
@WORKSPACE
@FORMAT_OPTION
@boundary
def new_cmd(
    slug: str,
    title: str | None,
    target_area: str | None,
    milestone: str | None,
    task_kind: str | None,
    planning_effort: str | None,
    dev_effort: str | None,
    namespace: str | None,
    summary: str | None,
    supersedes: str | None,
    decomposed_from: str | None,
    needs_decompose: bool,
    with_target_docs: bool,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Scaffold the proposal bundle docs/proposals/PROP-<SLUG>/."""
    created = CreateProposalUseCase().execute(
        resolve_root(workspace_root),
        slug,
        title=title,
        target_area=target_area,
        milestone=milestone,
        task_kind=task_kind,
        planning_effort=planning_effort,
        dev_effort=dev_effort,
        namespace=namespace,
        summary=summary,
        supersedes=supersedes,
        decomposed_from=decomposed_from,
        needs_decompose=needs_decompose,
        with_target_docs=with_target_docs,
        cwd=Path.cwd(),
    )
    if is_json(output_format):
        echo_json(created.to_dict())
    else:
        click.echo(
            sentinel(
                "PROPOSAL",
                created.id,
                path=created.path,
                dir=created.dir,
                target_docs=created.target_docs,
                workflow=created.workflow,
                planning_effort=created.planning_effort,
                dev_effort=created.dev_effort,
                **({"namespace": created.namespace} if created.namespace else {}),
            )
        )
        if created.next_command:
            click.echo(f"[NEXT_CMD: {created.next_command}]")
    echo_notices(created.notices)
    exit_on_warnings(created.notices)


@proposal_group.command(name="padr")
@click.argument("slug")
@click.argument("title")
@click.option(
    "--summary",
    default=None,
    help="One or two English sentences: what the decision defines; kept by the promoted ADR [default: none]",
)
@click.option(
    "--slug",
    "padr_slug",
    default=None,
    help="Slug of the PADR ID and file name; its first word needs a letter [default: the title's slug]",
)
@WORKSPACE
@FORMAT_OPTION
@boundary
def padr_cmd(
    slug: str,
    title: str,
    summary: str | None,
    padr_slug: str | None,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Record a preliminary decision PADR-<slug> in proposal SLUG's decisions/ (the title's slug unless --slug)."""
    created = CreateProposalDecisionUseCase().execute(
        resolve_root(workspace_root), slug, title, summary=summary, padr_slug=padr_slug
    )
    if is_json(output_format):
        echo_json(created.to_dict())
        return
    click.echo(sentinel("PADR", created.id, path=created.path, proposal=created.proposal))


@proposal_group.command(name="accept")
@click.argument("slug")
@click.option(
    "--by",
    "actor",
    required=True,
    type=click.Choice([ACTOR, "policy"]),
    help="Decision authority: user acceptance or owning plan-accept=auto policy",
)
@click.option(
    "--note",
    default="",
    help="The decision note; with --direct the reason the draft was eligible (required) [default: none]",
)
@click.option(
    "--direct",
    is_flag=True,
    help="Accept an eligible draft on the base checkout without Planning, or repair an accepted proposal that has "
    "no gate:plan-accept record and no worker envelope",
)
@click.option("--check", "check_only", is_flag=True, help="Run every check and write nothing")
@click.option(
    "--mode",
    type=click.Choice(["accept_only", "accept_and_handoff"]),
    default=None,
    help="Compose the Host-authorized lifecycle from the retained base: accept and integrate plan-<slug> "
    "(accept_only), or also start Development (accept_and_handoff) [default: the basic acceptance]",
)
@click.option(
    "--effort",
    type=click.Choice(list(EFFORTS)),
    default=None,
    help="With --mode accept_and_handoff: the Development activity-effort",
)
@WORKSPACE
@FORMAT_OPTION
@boundary
def accept_cmd(
    slug: str,
    actor: str,
    note: str,
    direct: bool,
    check_only: bool,
    mode: str | None,
    effort: str | None,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Accept proposal SLUG; with --mode, compose lifecycle effects.

    Without --mode, preserve the basic Backlog acceptance operation. With --mode, selects
    acceptance only or acceptance plus handoff. Under ask policy this command follows Host conversational approval;
    policy authority is available only when the retained base declares automatic plan-acceptance.
    """
    if mode is not None:
        if direct or check_only:
            raise click.UsageError("composed acceptance cannot use --direct or --check")
        result = PlanAcceptUseCase(resolve_root(workspace_root)).execute(slug, mode=mode, effort=effort, by=actor)
        _echo_composed(
            "ACCEPTED",
            slug,
            result,
            bool(result.get("completed_steps")),
            mode=mode,
            authority=result.get("acceptance_authority", "-"),
            completed=",".join(result.get("completed_steps", [])) or "-",
        )
        return
    if effort is not None:
        raise click.UsageError("--effort requires --mode")
    result = AcceptProposalUseCase().execute(
        resolve_root(workspace_root), slug, by=actor, note=note, direct=direct, check=check_only
    )
    if is_json(output_format):
        echo_json(result.to_dict())
    elif result.checked:
        click.echo(
            sentinel(
                "ACCEPT_CHECK",
                result.proposal,
                form=result.form,
                path=result.path,
                eligible=result.eligible,
                pending=",".join(result.pending) or "-",
            )
        )
    if result.checked or is_json(output_format):
        if not result.eligible:
            # The real run refuses a pending condition (SPEC_PROPOSAL_NOT_ELIGIBLE): the check's answer is negative.
            raise click.exceptions.Exit(int(ExitCode.FINDINGS))
        return
    click.echo(
        sentinel(
            "ACCEPTED",
            result.proposal,
            form=result.form,
            path=result.path,
            status=result.status,
            decision=result.decision,
        )
    )


@proposal_group.command(name="handoff")
@click.argument("slug")
@click.option(
    "--effort",
    type=click.Choice(list(EFFORTS)),
    default=None,
    help="Compose from the retained base: create dev-<slug>, run setup and hand off at this Development "
    "activity-effort [default: the plain handoff in the dev-<slug> checkout]",
)
@WORKSPACE
@FORMAT_OPTION
@boundary
def handoff_cmd(slug: str, effort: str | None, workspace_root: str | None, output_format: str) -> None:
    """Hand off SLUG; with --effort, compose Development worktree creation and handoff."""
    root = resolve_root(workspace_root)
    if effort is not None:
        result = HandoffUseCase(root).execute(slug, effort)
        handoff = result.get("handoff") or {}
        worktree = result.get("worktree") or {}
        _echo_composed(
            "HANDOFF",
            slug,
            result,
            bool(worktree.get("created")) or result.get("status") == "needs_recovery",
            spec=handoff.get("spec", "-"),
            dir=handoff.get("dir", "-"),
            worktree=f"dev-{slug}" if worktree.get("path") else "-",
            effort=effort,
            authority=result.get("authority", "-"),
        )
        return
    completed = HandoffProposalUseCase().execute(root, slug)
    result, registered = completed.handoff, completed.registered
    if is_json(output_format):
        scope = registered_dict(registered.location, registered.record, registered.token) if registered else None
        echo_json(result.to_dict() | {"scope": scope, "notices": [item.to_dict() for item in completed.notices]})
    else:
        click.echo(
            sentinel(
                "HANDOFF",
                result.proposal,
                spec=result.spec,
                dir=result.dir,
                workflow=result.workflow,
                **({"dev_effort": result.dev_effort} if result.dev_effort else {}),
            )
        )
        if result.target_docs:
            click.echo(sentinel("TARGET_DOCS", result.target_docs))
        if result.materials:
            merged = {"merged": "yes"} if result.materials_merged else {}
            click.echo(sentinel("MATERIALS", result.materials, **merged))
        for path in result.dropped_duplicates:
            click.echo(sentinel("DROPPED_DUPLICATE", path))
        for decision in result.decisions:
            click.echo(sentinel("PROMOTED_ADR", decision.id, path=decision.path, padr=decision.padr))
        for path in result.dropped_records:
            click.echo(sentinel("DROPPED_RECORD", path))
        for gate in result.carried_gates:
            click.echo(sentinel("CARRIED_GATE", gate.request, decision=gate.decision))
        for item in result.rewritten:
            click.echo(
                sentinel("REWRITTEN", f"{item.path}:{item.line}", kind=item.kind, **{"from": item.old, "to": item.new})
            )
        for item in result.unresolved:
            click.echo(
                sentinel(
                    "UNRESOLVED_LINK",
                    f"{item.path}:{item.line}",
                    kind=item.kind,
                    target=item.target,
                    reason=item.reason,
                )
            )
        if registered:
            echo_registered(registered.location, registered.record, registered.token)
        if result.next_command:
            click.echo(f"[NEXT_CMD: {result.next_command}]")
    echo_notices(completed.notices)
    exit_on_warnings(completed.notices)


@proposal_group.command(name="prune", hidden=True)
@click.argument("slug", required=False)
@workspace_option()
@FORMAT_OPTION
@boundary
def prune_cmd(slug: str | None, workspace_root: str | None, output_format: str) -> None:
    """Remove the empty docs/proposals/PROP-<SLUG>/ directories a merged handoff left (all of them without SLUG).

    Run it in the base checkout after `devkit worktree finish`; a directory holding any file is kept.
    """
    pruned = PruneProposalsUseCase().execute(resolve_root(workspace_root), slug)
    if is_json(output_format):
        echo_json({"pruned": pruned})
    elif pruned:
        for path in pruned:
            click.echo(sentinel("PRUNED", path))
    else:
        click.echo("[OK: nothing to prune]")


@proposal_group.command(name="check")
@click.argument("slug")
@WORKSPACE
@FORMAT_OPTION
@boundary
def check_cmd(slug: str, workspace_root: str | None, output_format: str) -> None:
    """Check that Backlog may edit, split or delete proposal SLUG: a draft without a plan-<slug> branch.

    Run it before every Backlog change of a proposal. Remote branches count once fetched (git fetch first).
    """
    checked = CheckBacklogUseCase().execute(resolve_root(workspace_root), slug)
    if is_json(output_format):
        echo_json(checked.to_dict())
        return
    click.echo(sentinel("PROPOSAL", checked.id, path=checked.path, status=checked.status, editable="yes"))


@proposal_group.command(name="report")
@click.argument("slug")
@click.option(
    "--source-sha", default=None, help="Exact current committed Planning or accepted base SHA (default: HEAD)"
)
@WORKSPACE
@FORMAT_OPTION
@boundary
def report_cmd(slug: str, source_sha: str | None, workspace_root: str | None, output_format: str) -> None:
    """Print the proposal review report template for SLUG."""
    from devkit_spec.features.proposals.usecases.report import ReportTemplateUseCase

    root = resolve_root(workspace_root)
    if source_sha is None:
        source_sha = run_git(root, "rev-parse", "HEAD").decode().strip()
    text = ReportTemplateUseCase().execute(root, slug, source_sha)
    if is_json(output_format):
        echo_json({"proposal": f"PROP-{slug}", "source_sha": source_sha, "report": text})
    else:
        click.echo(text, nl=False)
