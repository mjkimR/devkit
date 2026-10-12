from __future__ import annotations

import functools
import json
import sys
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import click
from agent_advisory import Actor, AdvisoryError, Retry, as_advisory_error

from agent_workflow_engine import frontmatter
from agent_workflow_engine.binding import Binding, HistoryEntry, read_binding, write_binding
from agent_workflow_engine.checks import Registry
from agent_workflow_engine.config import CONFIG_PATH, ConfigError, WorkflowConfig, load_workflow_config
from agent_workflow_engine.definition import (
    HANDOFF_GATE,
    DefinitionError,
    WorkflowDocument,
    discover,
    load_all,
    resolve,
    schema_hash,
    validate,
)
from agent_workflow_engine.envelope import ENVELOPES_DIR, KIND, load_envelopes, skeleton
from agent_workflow_engine.evaluate import Options, UnitNotFoundError, evaluate, is_completed
from agent_workflow_engine.git import is_ancestor
from agent_workflow_engine.layout import TemplateLayout
from agent_workflow_engine.render import render_document, render_result

EXIT_INVALID = 1  # validate/show: a definition has problems (a result, not an advisory)

FORMAT = click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
WORKSPACE = click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Workspace root directory",
)
UNIT = click.option(
    "--unit", "-u", required=True, type=str, help="Work unit directory (workspace-relative or absolute)"
)


class WorkflowError(AdvisoryError):
    """Errors the workflow CLI reports as Agent Advisory Protocol blocks."""


def _boundary(fn: Callable[..., None]) -> Callable[..., None]:
    """Render any error as an advisory on stderr (and as JSON on stdout under --format json)."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            fn(*args, **kwargs)
        except (click.exceptions.Exit, click.ClickException, SystemExit):
            raise
        except Exception as exc:
            error = as_advisory_error(exc)
            if str(kwargs.get("output_format", "text")).lower() == "json":
                click.echo(json.dumps({"error": error.to_dict()}, indent=2))
            click.echo(error.render(), err=True)
            sys.exit(int(error.exit_code))

    return wrapper


class _Env:
    def __init__(self, workspace_root: str) -> None:
        self.root = Path(workspace_root).resolve()
        try:
            self.config: WorkflowConfig = load_workflow_config(self.root)
        except ConfigError as exc:
            raise WorkflowError.invalid_input(
                str(exc),
                code="CONFIG_INVALID",
                target_files=[CONFIG_PATH],
                fix="Correct the [workflow] table in .devkit/config.toml",
            ) from exc
        self.layout = TemplateLayout(self.config.work_dir, self.config.unit_path, self.config.anchor)

    @property
    def definitions_dir(self) -> Path:
        return self.root / self.config.definitions_dir

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def unit_path(self, unit: str) -> Path:
        path = Path(unit)
        path = path if path.is_absolute() else self.root / path
        return path.resolve()

    def require_unit(self, unit: str) -> Path:
        unit_dir = self.unit_path(unit)
        if not (unit_dir / self.config.anchor).is_file():
            raise WorkflowError.invalid_input(
                f"{self.config.anchor} not found in {self.rel(unit_dir)}",
                code="UNIT_NOT_FOUND",
                fix="Pass an existing unit directory (`agent-workflow list`) or create one with `agent-workflow new <slug>`",
            )
        return unit_dir

    def binding(self, unit_dir: Path) -> Binding:
        try:
            return read_binding(unit_dir / self.config.anchor)
        except frontmatter.FrontmatterError as exc:
            raise WorkflowError.invalid_input(
                f"{self.config.anchor}: {exc}",
                code="ANCHOR_INVALID",
                target_files=[self.rel(unit_dir / self.config.anchor)],
                fix="Repair the anchor's YAML frontmatter",
            ) from exc

    def known_ids(self) -> set[str]:
        docs, _ = discover(self.root, self.definitions_dir)
        return {d.id for d in docs}

    def definition(self, ref: str | None, binding: Binding | None = None) -> WorkflowDocument:
        chosen = ref or (binding.workflow if binding and binding.workflow else None) or self.config.default
        if not chosen:
            raise WorkflowError.invalid_input(
                "no workflow selected",
                code="WORKFLOW_NOT_SELECTED",
                fix="Pass --workflow <id>, bind the unit, or set [workflow].default in .devkit/config.toml",
            )
        try:
            doc = resolve(self.definitions_dir, chosen, self.root)
        except DefinitionError as exc:
            raise WorkflowError.invalid_input(
                str(exc),
                code="WORKFLOW_NOT_FOUND",
                fix=f"Add a definition with id {chosen!r} under {self.config.definitions_dir}, sync a bundle that ships it, or pass --workflow <path>",
            ) from exc
        problems = validate(doc, self.config.anchor, self.known_ids() | {doc.id})
        if problems:
            raise WorkflowError.invalid_input(
                f"workflow {doc.id} is invalid",
                *(str(p) for p in problems),
                code="WORKFLOW_INVALID",
                target_files=[self.rel(doc.path)] if doc.path else (),
                fix=f"Run `agent-workflow validate` and fix every problem in {doc.id}",
            )
        return doc


def _lint_func(root: Path, files: list[str]) -> list[str]:
    """Run agent-rule-engine's linter phase over ``files`` and describe each violation."""
    from agent_rule_engine import Phase, RuleContext, default_registry, managed_rule_paths
    from agent_rule_engine import evaluate as rules_evaluate
    from agent_rule_engine.engine.config import load_rules_config

    if not files:
        return []
    config = load_rules_config(root)
    ctx = RuleContext(
        workspace_root=root,
        changed_files=files,
        phase=Phase.LINTER,
        phase_overrides=dict(config.phase_overrides),
        severity_overrides=dict(config.severity_overrides),
        rule_settings=dict(config.settings),
    )
    registry = default_registry()
    registry.discover_from_files(managed_rule_paths(root))
    result = rules_evaluate(ctx, registry.get_all())
    if registry.errors or result.errors:
        raise RuntimeError("; ".join([*registry.errors, *result.errors]))
    if result.errors:
        raise RuntimeError("; ".join(result.errors))
    return [
        f"{v.file}:{v.line} {v.rule_id} {v.message}"
        for v in result.violations
        if v.severity.value == "error" and not v.fixed
    ]


def _echo_json(data: object) -> None:
    click.echo(json.dumps(data, indent=2))


def _evaluate_unit(env: _Env, doc: WorkflowDocument, unit_dir: Path, given: tuple[str, ...], no_lint: bool) -> Any:
    """Evaluate ``unit_dir`` against ``doc``; refuse drift under in-flight work."""
    opts = Options(
        workspace_root=env.root,
        unit_dir=unit_dir,
        anchor=env.config.anchor,
        approvals=dict(env.config.approvals),
        given=tuple(given),
        lint=_lint_func,
        skip_lint=no_lint,
        ancestor=is_ancestor,
    )
    try:
        result = evaluate(doc, opts)
    except UnitNotFoundError as exc:
        raise WorkflowError.invalid_input(str(exc), code="UNIT_NOT_FOUND") from exc

    if result.drift and not is_completed(result):
        raise WorkflowError.blocked(
            "the bound stage schema changed under in-flight work",
            f"recorded={result.drift.recorded}",
            f"current={result.drift.current}",
            code="WORKFLOW_DRIFT",
            target_files=[env.rel(unit_dir / env.config.anchor)],
            fix=f"Review the change to {doc.id}, then run `agent-workflow bind --unit {env.rel(unit_dir)}` to accept it",
        )
    return result


@click.group(name="agent-workflow")
@click.version_option(package_name="agent-workflow-engine")
def cli() -> None:
    """Data-driven delivery workflow engine for coding agents."""


@cli.command(name="new")
@WORKSPACE
@click.argument("slug", type=str)
@click.option(
    "--workflow", "workflow_ref", default=None, help="Workflow id or definition path (default: [workflow].default)"
)
@click.option("--date", "when", default=None, help="Date used by the layout template, YYYY-MM-DD (default: today)")
@click.option("--status", default="planned", show_default=True, help="Initial anchor status")
@_boundary
def new_cmd(workspace_root: str, slug: str, workflow_ref: str | None, when: str | None, status: str) -> None:
    """Create a work unit from the layout template and bind it to a workflow."""
    env = _Env(workspace_root)
    doc = env.definition(workflow_ref)
    try:
        day = date.fromisoformat(when) if when else date.today()
    except ValueError as exc:
        raise WorkflowError.invalid_input(f"--date: {exc}", code="DATE_INVALID", fix="Pass --date YYYY-MM-DD") from exc
    try:
        rel = env.layout.new_unit(slug, day)
    except ValueError as exc:
        raise WorkflowError.invalid_input(
            str(exc), code="SLUG_INVALID", fix="Use lowercase letters, digits and hyphens"
        ) from exc
    unit_dir = env.root / rel
    anchor_path = unit_dir / env.config.anchor
    if anchor_path.exists():
        raise WorkflowError.invalid_input(
            f"unit already exists: {rel.as_posix()}",
            code="UNIT_EXISTS",
            fix="Choose another slug or continue the existing unit with `agent-workflow next --unit <dir>`",
        )
    unit_dir.mkdir(parents=True, exist_ok=True)
    (unit_dir / ENVELOPES_DIR).mkdir(exist_ok=True)
    data = {"id": slug, "status": status, "created": day, "workflow": doc.id, "workflow_hash": schema_hash(doc)}
    anchor_path.write_text(frontmatter.render(data, f"# {slug}\n"), "utf-8")
    click.echo(f"[UNIT: {rel.as_posix()} workflow={doc.id} anchor={env.config.anchor}]")


@cli.command(name="bind")
@WORKSPACE
@UNIT
@click.option(
    "--workflow",
    "workflow_ref",
    default=None,
    help="Workflow id or definition path (default: current binding or [workflow].default)",
)
@_boundary
def bind_cmd(workspace_root: str, unit: str, workflow_ref: str | None) -> None:
    """Record which workflow a unit follows and the hash of its stage schema."""
    env = _Env(workspace_root)
    unit_dir = env.require_unit(unit)
    current = env.binding(unit_dir)
    doc = env.definition(workflow_ref, current)
    binding = Binding(doc.id, schema_hash(doc))
    write_binding(unit_dir / env.config.anchor, binding)
    click.echo(f"[BOUND: {doc.id} hash={binding.hash}]")


@cli.command(name="next")
@WORKSPACE
@UNIT
@click.option("--workflow", "workflow_ref", default=None, help="Evaluate against this workflow instead of the binding")
@click.option("--given", multiple=True, help="Gate, runner or human check the executor holds (repeatable)")
@click.option("--no-lint", is_flag=True, help="Skip lint-class checks")
@FORMAT
@_boundary
def next_cmd(
    workspace_root: str,
    unit: str,
    workflow_ref: str | None,
    given: tuple[str, ...],
    no_lint: bool,
    output_format: str,
) -> None:
    """Report the current stage of a unit, what is unmet and what to do next."""
    env = _Env(workspace_root)
    unit_dir = env.require_unit(unit)
    binding = env.binding(unit_dir)
    doc = env.definition(workflow_ref, binding)

    registry = Registry.build(env.config.anchor, doc.declared_checks)
    gates = {s.gate for s in doc.stages if s.gate}
    for name in given:
        check = registry.lookup(name)
        if name not in gates and (check is None or check.class_.value not in ("runner", "human")):
            raise WorkflowError.invalid_input(
                f"--given {name!r} is not a gate of {doc.id} nor a registered runner or human check",
                code="GIVEN_INVALID",
                fix=f"Use a gate name ({', '.join(sorted(gates)) or 'none'}) or a runner/human check from `agent-workflow checks`",
            )

    result = _evaluate_unit(env, doc, unit_dir, given, no_lint)

    if output_format.lower() == "json":
        _echo_json(result.to_dict())
    else:
        click.echo(render_result(result), nl=False)
    if result.lint_error:
        raise WorkflowError(
            f"lint failed: {result.lint_error}",
            code="LINT_FAILED",
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            fix="Fix the rule execution error reported by agent-rule-engine, or rerun with --no-lint to inspect the stage",
        )


@cli.command(name="handoff")
@WORKSPACE
@UNIT
@click.option(
    "--workflow",
    "workflow_ref",
    default=None,
    help="Candidate to continue with (required under approvals.handoff=ask; optional under auto)",
)
@click.option(
    "--date", "when", default=None, help="Completion date recorded in the history, YYYY-MM-DD (default: today)"
)
@click.option("--no-lint", is_flag=True, help="Skip lint-class checks while confirming completion")
@FORMAT
@_boundary
def handoff_cmd(
    workspace_root: str, unit: str, workflow_ref: str | None, when: str | None, no_lint: bool, output_format: str
) -> None:
    """Hand a completed unit to one of its workflow's ``next`` candidates and rebind it."""
    env = _Env(workspace_root)
    unit_dir = env.require_unit(unit)
    binding = env.binding(unit_dir)
    doc = env.definition(None, binding)
    try:
        day = date.fromisoformat(when) if when else date.today()
    except ValueError as exc:
        raise WorkflowError.invalid_input(f"--date: {exc}", code="DATE_INVALID", fix="Pass --date YYYY-MM-DD") from exc

    result = _evaluate_unit(env, doc, unit_dir, (), no_lint)
    unit_rel = env.rel(unit_dir)
    if not result.complete:
        raise WorkflowError.invalid_input(
            f"unit {unit_rel} has not completed workflow {doc.id}: stage {result.stage.id} is current",  # type: ignore[union-attr]
            *(f"unmet={u.name}" for u in result.unmet),
            code="HANDOFF_NOT_READY",
            fix=f"Finish the current stage (`agent-workflow next --unit {unit_rel}`) before handing off",
        )
    handoff = result.handoff
    policy = env.config.policy(HANDOFF_GATE)
    if not doc.next:
        raise WorkflowError.invalid_input(
            f"workflow {doc.id} declares no next candidates",
            code="HANDOFF_NONE",
            fix=f"Add a `next` list to {doc.id}, or start a new unit with `agent-workflow new`",
        )
    if handoff is None or policy == "off":
        raise WorkflowError.invalid_input(
            f"handoff is disabled by policy (approvals.{HANDOFF_GATE}=off)",
            code="HANDOFF_OFF",
            fix=f"Set [workflow.approvals].{HANDOFF_GATE} to ask or auto in {CONFIG_PATH}",
        )
    by_id = {c.workflow: c for c in handoff.candidates}
    if workflow_ref is None:
        if handoff.chosen is None:
            if policy == "auto":
                raise WorkflowError.invalid_input(
                    f"no candidate of {doc.id} is eligible for automatic handoff",
                    *(
                        f"{c.workflow}: " + ", ".join(f"{k.name}={str(k.satisfied).lower()}" for k in c.checks)
                        for c in handoff.candidates
                    ),
                    code="HANDOFF_UNDECIDED",
                    fix="Satisfy a candidate's `when` checks, or choose one explicitly with --workflow <id>",
                )
            raise WorkflowError.invalid_input(
                f"handoff from {doc.id} requires a choice (approvals.{HANDOFF_GATE}=ask)",
                *(
                    f"{c.workflow}: eligible={str(c.eligible).lower()} recommended={str(c.recommended).lower()}"
                    for c in handoff.candidates
                ),
                code="HANDOFF_CHOICE_REQUIRED",
                fix="Present the candidates to the user and rerun with --workflow <id> after their choice",
            )
        chosen = handoff.chosen
    else:
        candidate = by_id.get(workflow_ref)
        if candidate is None:
            raise WorkflowError.invalid_input(
                f"{workflow_ref!r} is not a next candidate of {doc.id}",
                code="HANDOFF_INVALID",
                fix=f"Choose one of: {', '.join(by_id)}",
            )
        if not candidate.eligible:
            raise WorkflowError.invalid_input(
                f"candidate {workflow_ref!r} is not eligible: its preconditions do not hold",
                *(f"{k.name}={str(k.satisfied).lower()} {k.detail}".rstrip() for k in candidate.checks),
                code="HANDOFF_INELIGIBLE",
                fix="Satisfy the candidate's `when` checks first, or choose another candidate",
            )
        chosen = workflow_ref

    target = env.definition(chosen)
    history = (*binding.history, HistoryEntry(doc.id, binding.hash or schema_hash(doc), day.isoformat()))
    new_binding = Binding(target.id, schema_hash(target), history)
    write_binding(unit_dir / env.config.anchor, new_binding)
    payload = {
        "unit": unit_rel,
        "from": doc.id,
        "to": target.id,
        "workflow_hash": new_binding.hash,
        "policy": policy,
        "history": [h.to_dict() for h in history],
    }
    if output_format.lower() == "json":
        _echo_json(payload)
    else:
        click.echo(f"[HANDOFF: from={doc.id} to={target.id} hash={new_binding.hash} policy={policy}]")
        click.echo(f"[HISTORY: {' '.join(h.workflow for h in history)}]")


@cli.command(name="show")
@WORKSPACE
@click.argument("ref", type=str)
@FORMAT
@_boundary
def show_cmd(workspace_root: str, ref: str, output_format: str) -> None:
    """Print a workflow definition's stages, gates and schema hash."""
    env = _Env(workspace_root)
    try:
        doc = resolve(env.definitions_dir, ref, env.root)
    except DefinitionError as exc:
        raise WorkflowError.invalid_input(str(exc), code="WORKFLOW_NOT_FOUND") from exc
    problems = validate(doc, env.config.anchor, env.known_ids() | {doc.id})
    if output_format.lower() == "json":
        data = doc.to_dict()
        data["problems"] = [str(p) for p in problems]
        data["approvals"] = {s.gate: env.config.policy(s.gate) for s in doc.stages if s.gate}
        _echo_json(data)
    else:
        click.echo(render_document(doc, env.config.approvals), nl=False)
        for p in problems:
            click.secho(f"[PROBLEM: {p}]", fg="red")
    if problems:
        sys.exit(EXIT_INVALID)


@cli.command(name="checks")
@WORKSPACE
@FORMAT
@_boundary
def checks_cmd(workspace_root: str, output_format: str) -> None:
    """List registered check names, classes and parameters."""
    env = _Env(workspace_root)
    entries = Registry.build(env.config.anchor).entries()
    if output_format.lower() == "json":
        _echo_json([c.to_dict() for c in entries])
        return
    for c in entries:
        params = f"({' '.join(c.params)})" if c.params else ""
        alias = f" alias={c.alias}" if c.alias else ""
        click.echo(f'[CHECK: {c.name}{params} class={c.class_.value}{alias} description="{c.description}"]')


@cli.command(name="validate")
@WORKSPACE
@click.argument("paths", nargs=-1, type=click.Path(exists=True, dir_okay=True, file_okay=True))
@_boundary
def validate_cmd(workspace_root: str, paths: tuple[str, ...]) -> None:
    """Validate workflow definitions (default: definitions_dir plus synchronized workflow assets)."""
    env = _Env(workspace_root)
    targets = [Path(p) for p in paths]
    failed = False
    seen = 0
    batches: list[tuple[list[WorkflowDocument], list[str]]] = []
    if not targets:
        batches.append(discover(env.root, env.definitions_dir))
    for target in targets:
        if target.is_dir():
            batches.append(load_all(target))
        else:
            try:
                batches.append(([resolve(env.definitions_dir, str(target), env.root)], []))
            except DefinitionError as exc:
                batches.append(([], [str(exc)]))
    known = env.known_ids() | {doc.id for docs, _ in batches for doc in docs}
    for docs, errors in batches:
        for err in errors:
            failed = True
            click.secho(f"[INVALID: {err}]", fg="red")
        for doc in docs:
            seen += 1
            problems = validate(doc, env.config.anchor, known)
            where = env.rel(doc.path) if doc.path else doc.id
            if problems:
                failed = True
                click.secho(f"[INVALID: {where} id={doc.id} problems={len(problems)}]", fg="red")
                for p in problems:
                    click.echo(f"  - {p}")
            else:
                click.secho(f"[VALID: {where} id={doc.id} hash={schema_hash(doc)}]", fg="green")
    if seen == 0 and not failed:
        click.echo(f"[VALID: no definitions under {env.config.definitions_dir}]")
    if failed:
        sys.exit(EXIT_INVALID)


@cli.command(name="list")
@WORKSPACE
@FORMAT
@_boundary
def list_cmd(workspace_root: str, output_format: str) -> None:
    """List discovered work units with their status and binding."""
    env = _Env(workspace_root)
    rows: list[dict[str, str | None]] = []
    for rel in env.layout.discover(env.root):
        anchor_path = env.root / rel / env.config.anchor
        try:
            data = frontmatter.read(anchor_path)
            binding = read_binding(anchor_path)
        except frontmatter.FrontmatterError:
            data, binding = {}, Binding()
        rows.append(
            {
                "unit": rel.as_posix(),
                "status": frontmatter.field(data, "status") or None,
                "workflow": binding.workflow or None,
                "workflow_hash": binding.hash or None,
                "history": " ".join(h.workflow for h in binding.history) or None,
            }
        )
    if output_format.lower() == "json":
        _echo_json(rows)
        return
    if not rows:
        click.echo(f"[UNITS: none under {env.config.work_dir}]")
        return
    for row in rows:
        click.echo(f"[UNIT: {row['unit']} status={row['status'] or '-'} workflow={row['workflow'] or '-'}]")


@cli.group(name="envelope")
def envelope_group() -> None:
    """Envelope files under <unit>/envelopes/."""


@envelope_group.command(name="new")
@WORKSPACE
@UNIT
@click.option("--kind", required=True, help="Envelope kind, e.g. review, reverify, final-report")
@click.option("--stage", default="", help="Stage the envelope belongs to")
@_boundary
def envelope_new_cmd(workspace_root: str, unit: str, kind: str, stage: str) -> None:
    """Write the next <kind>-NN.yaml skeleton; existing files are never overwritten."""
    env = _Env(workspace_root)
    if not KIND.match(kind):
        raise WorkflowError.invalid_input(
            f"--kind {kind!r} must match [a-z][a-z0-9-]*",
            code="KIND_INVALID",
            fix="Use a lowercase kind such as review",
        )
    unit_dir = env.require_unit(unit)
    envelopes = load_envelopes(unit_dir)
    seq = envelopes.next_sequence(kind)
    directory = unit_dir / ENVELOPES_DIR
    directory.mkdir(exist_ok=True)
    path = directory / f"{kind}-{seq:02d}.yaml"
    while path.exists():
        seq += 1
        path = directory / f"{kind}-{seq:02d}.yaml"
    created = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    path.write_text(skeleton(kind, stage, created), "utf-8")
    click.echo(f"[ENVELOPE: {env.rel(path)} kind={kind} seq={seq:02d}]")


if __name__ == "__main__":
    cli()
