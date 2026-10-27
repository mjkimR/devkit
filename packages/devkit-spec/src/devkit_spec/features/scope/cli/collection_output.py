"""Text rendering for explicit scope observation."""

import json
from typing import Any

import click

from devkit_spec.utils.output import fields_line, sentinel


def _task(key: str | None) -> str:
    """The task identity of an observation's ``[namespace, identity, unit]`` key, ``-`` without one."""
    return json.loads(key)[1] if key else "-"


def _unit(key: str | None) -> str:
    return json.loads(key)[2] if key else "-"


def render(data: dict[str, Any]) -> None:
    for candidate in data["inventory"]:
        click.echo(
            fields_line(
                "SCOPE_CANDIDATE",
                source=candidate["source_id"],
                activity=candidate["activity"],
                reason=candidate["reason"],
            )
        )
    for observation in data["observations"]:
        click.echo(
            fields_line(
                "SCOPE_OBSERVATION",
                id=observation["observation_id"],
                task=_task(observation["task_key"]),
                unit=_unit(observation["task_key"]),
                source=observation["provenance"]["source"],
                sha=observation["provenance"].get("sha", "-"),
                missing=",".join(observation["missing_layers"]) or "-",
            )
        )
    for pair in data["pairs"]:
        click.echo(
            fields_line(
                "PAIR",
                a=pair["a"],
                b=pair["b"],
                docs=len(pair["docs"]),
                code=len(pair["code"]),
                unresolved=pair["unresolved"],
            )
        )
        for evidence in [*pair["docs"], *pair["code"]]:
            click.echo(
                sentinel(
                    "EVIDENCE",
                    evidence["path"],
                    a=pair["a"],
                    b=pair["b"],
                    kind=evidence["kind"],
                    other=evidence["other"],
                    source=evidence["source"],
                    other_source=evidence["other_source"],
                    granularity=evidence["granularity"],
                )
            )
    click.echo(
        fields_line(
            "SUMMARY",
            **data["summary"],
            coverage=data["coverage"]["status"],
            comparisons_complete="yes" if data["coverage"]["comparisons_complete"] else "no",
        )
    )
