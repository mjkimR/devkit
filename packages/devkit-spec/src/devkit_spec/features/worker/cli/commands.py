"""Informational worker inspection CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
from devkit.advisory import Actor, Retry
from devkit_core.base.errors import ArgumentError
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_spec.base.errors import WorkerCheckNotRunNotice
from devkit_spec.features.worker.usecases.inspect import InspectWorkerUseCase
from devkit_spec.features.worker.usecases.summary import summarize_inspection
from devkit_spec.utils.advisory import restore_advisory
from devkit_spec.utils.output import fields_line, sentinel


@click.group(name="worker")
def worker_group() -> None:
    """Inspect committed worker results without changing workflow decisions."""


@worker_group.command(name="inspect")
@click.option("--unit", default=None, help="Committed unit directory; otherwise derive from the activity branch")
@click.option("--base", default=None, help="Last accepted commit; otherwise derive from committed worker records")
@click.option("--head", default=None, help="Returned commit; otherwise the latest worker envelope's adding commit")
@click.option("--scope", multiple=True, help="Complete literal path scope (repeat); replaces derived scope")
@click.option(
    "--scope-file", type=click.Path(path_type=Path), default=None, help="UTF-8 complete scope, one prefix per line"
)
@click.option("--base-checkout", default=None, help="Base checkout to observe; otherwise the registered base")
@click.option("--details", is_flag=True, help="Include complete wrapped results and envelope history in JSON output")
@workspace_option()
@FORMAT_OPTION
@boundary
def inspect_cmd(
    unit: str | None,
    base: str | None,
    head: str | None,
    scope: tuple[str, ...],
    scope_file: Path | None,
    base_checkout: str | None,
    details: bool,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Collect range, scope, cleanliness, envelope, rules and workflow evidence. Never writes or repairs."""
    if scope and scope_file is not None:
        raise ArgumentError(
            "--scope and --scope-file are mutually exclusive",
            target_files=["--scope", "--scope-file"],
            fix="Pass one complete scope input",
        )
    entries = list(scope) if scope else None
    if scope_file is not None:
        try:
            entries = [line.strip() for line in scope_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, UnicodeError) as exc:
            raise ArgumentError(
                f"Cannot read scope file: {exc}",
                target_files=["--scope-file"],
                fix="Pass --scope-file with a readable UTF-8 file",
            ) from exc
    root = resolve_root(workspace_root) if workspace_root is not None else Path.cwd()
    result = InspectWorkerUseCase().execute(
        root, unit=unit, base=base, head=head, scope=entries, base_checkout=base_checkout, details=details
    )
    if is_json(output_format):
        echo_json(result if details else summarize_inspection(result))
    else:
        verdict = "fail" if result["exit_code"] else "pass"
        click.echo(fields_line("WORKER_INSPECTION", verdict=verdict, base=result["base"], head=result["head"]))
        for name, entry in result["inputs"].items():
            click.echo(sentinel("INPUT", name, **entry))
        for entry in result["scope"]:
            click.echo(sentinel("SCOPE_ENTRY", entry["path"], **{k: v for k, v in entry.items() if k != "path"}))
        for path in result["changed_paths"]:
            flags = {"outside": path in result["outside_scope"]} if "outside_scope" in result else {}
            click.echo(sentinel("CHANGED", path, **flags))
        for name, check in result["checks"].items():
            _echo_check(name, check)
        if "base_checkout" in result:
            click.echo(sentinel("BASE_CHECKOUT", result["inputs"]["base_checkout"]["value"], **result["base_checkout"]))
        # Text extracts advisories from the complete evidence, without historical envelope bodies.
        rendered: set[str] = set()
        for check in result["checks"].values():
            stderr = check.get("stderr", "")
            if stderr:
                click.echo(stderr, err=True, nl=False)
            for advisory in _advisories(check):
                key = str(advisory.to_dict())
                if key not in rendered and f"({advisory.code})" not in stderr:
                    echo_notices([advisory])
                    rendered.add(key)
    notices = [WorkerCheckNotRunNotice(notice["message"]) for notice in result["notices"]]
    echo_notices(notices)
    if not result["exit_code"]:
        exit_on_warnings(notices)
    elif not is_json(output_format):
        # The failed checks end the output: one advisory per check, rendered after the notices.
        for error in _advisories(result["errors"]):
            click.echo(error.render(), err=True)
    raise click.exceptions.Exit(result["exit_code"])


def _echo_check(name: str, check: dict[str, Any]) -> None:
    fields: dict[str, Any] = {"status": check["status"]}
    payload = check.get("result", {})
    if name == "workflow" and isinstance(payload, dict):
        stage = payload.get("stage")
        fields["stage"] = stage.get("id") if isinstance(stage, dict) else stage
    if "actual" in check:
        fields["actual"] = check["actual"]
    cause = check.get("cause")
    if cause:
        fields["cause"] = cause.get("code") if isinstance(cause, dict) else cause
    click.echo(sentinel("CHECK", name, **fields))
    for path in check.get("dirty_paths", []):
        click.echo(sentinel("DIRTY", path))
    if not isinstance(payload, dict):
        return
    if payload.get("blocked"):
        click.echo(sentinel("BLOCKED_UNIT", name, problems=payload.get("problems", [])))
    for question in payload.get("pending_questions", []):
        click.echo(sentinel("PENDING_QUESTION", name, question=question))
    for violation in payload.get("violations", []):
        click.echo(
            sentinel(
                "VIOLATION", violation.get("rule_id", ""), **{k: v for k, v in violation.items() if k != "rule_id"}
            )
        )


def _advisories(value: Any):
    """Restore protocol fields through the existing advisory renderer, once per structured advisory."""
    if isinstance(value, list):
        for item in value:
            yield from _advisories(item)
    elif isinstance(value, dict):
        data = value.get("advisory")
        if isinstance(data, dict) and "code" in value and "message" in value:
            yield restore_advisory(value, actor=Actor.NONE, retry=Retry.UNSAFE, restore_brief=True)
            return
        for key, item in value.items():
            if key != "envelopes":
                yield from _advisories(item)
