"""Eligibility and deterministic messages for an explicitly selected envelope."""

from __future__ import annotations

import re
from pathlib import Path

from devkit_agt.features.workflow.models.envelope import KIND_COMMANDS, Envelope
from devkit_agt.features.workflow.models.errors import EnvelopeCommitInvalidError, workflow_command


def commit_message(anchor_id: str, envelope: Envelope) -> tuple[str, str]:
    """Derive identity from a tracked anchor, never from a branch name."""
    match = re.fullmatch(r"(?:SPEC|PROP)-([a-z0-9][a-z0-9-]*)", anchor_id)
    if match is None:
        raise EnvelopeCommitInvalidError(
            f"unsupported anchor id {anchor_id!r}",
            fix="Commit the [TARGET] envelope with a manual git commit: explicit envelope commit supports only SPEC"
            " and PROP anchor ids",
        )
    # The file stem, not the parsed sequence: worker-007.yaml keeps its three digits.
    subject = f"chore(workflow): record {match[1]} {Path(envelope.name).stem}"
    body = f"workflow: {envelope.workflow}\nsegment: {envelope.segment}\nstage: {envelope.stage}"
    return subject, body


def require_authored(
    envelope: Envelope,
    workflow: str,
    segment: int,
    stages: set[str],
    *,
    unit: str = "",
    retry: str = "",
    tracked: bool = False,
) -> None:
    """A summary and exact current identity exclude unfilled skeletons and stale segments.

    The refusal names every failing field and the writer flag that fills it; ``unit`` (shell-quoted,
    workspace-relative) completes the writer command and ``retry`` is the same-file commit command its fix ends with.
    A ``tracked`` file is committed history: its fix writes a new envelope and never removes the file.
    """
    problems: list[str] = []
    flags: list[str] = []
    if not envelope.summary.strip():
        problems.append("summary is empty")
        flags.append('--summary "<1-3 line judgment>"')
    if envelope.stage not in stages:
        problems.append(f"stage {envelope.stage!r} is not a stage of workflow {workflow}")
        flags.append("--stage <a declared stage>")
    stale = envelope.workflow != workflow or envelope.segment != segment
    if stale:
        problems.append(
            f"workflow/segment {envelope.workflow or '-'}/{envelope.segment} is not the current {workflow}/{segment}"
        )
    if not problems:
        return
    writer = f"envelope {envelope.kind}" if envelope.kind in KIND_COMMANDS else f"envelope new --kind {envelope.kind}"
    if unit:
        writer += f" --unit {unit}"
    added = f" plus {' and '.join(flags)}" if flags else ""
    where = " in the current segment" if stale else ""
    write = f"with `{workflow_command(writer)}` and its original options{added}"
    if tracked:
        fix = (
            f"Keep [TARGET]: it is committed history. Write a new envelope{where} {write}, then commit that new file"
            " with `envelope commit`"
        )
    else:
        then = f", then run `{retry}`" if retry else ""
        fix = f"Remove the uncommitted [TARGET] and write it again{where} {write}{then}"
    raise EnvelopeCommitInvalidError(
        f"envelope is not authored: {'; '.join(problems)}", target_files=[envelope.file], fix=fix
    )
