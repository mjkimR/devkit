"""Sentinel text lines for ``next`` and ``show``. JSON comes from ``to_dict``."""

from __future__ import annotations

from agent_workflow_engine.definition import WorkflowDocument, schema_hash
from agent_workflow_engine.evaluate import Request, Result


def _dash(value: str) -> str:
    return value or "-"


def _yn(value: bool) -> str:
    return "yes" if value else "no"


def render_result(res: Result) -> str:
    lines: list[str] = []
    lines.append(
        f"[WORKFLOW: {res.workflow} unit={res.unit} status={_dash(res.status)} bound={_yn(res.binding.bound)}]"
    )
    if res.drift:
        lines.append(f"[DRIFT: recorded={res.drift.recorded} current={res.drift.current}]")
    lines.append(f"[DONE: {_dash(' '.join(res.done))}]")
    for s in res.skipped:
        lines.append(f"[SKIPPED: {s.id} reason={s.reason}]")
    stage = res.stage
    if stage is None:
        lines.append("[STAGE: - complete=true]")
        if res.handoff:
            h = res.handoff
            lines.append(
                f"[HANDOFF: policy={h.policy} candidates={_dash(' '.join(c.workflow for c in h.candidates))} "
                f"eligible={_dash(' '.join(h.eligible))} recommended={_dash(' '.join(h.recommended))} "
                f"chosen={_dash(h.chosen or '')}" + (f" decision={h.decision.file}" if h.decision else "") + "]"
            )
            for c in h.candidates:
                when = " ".join(f"{k.name}={str(k.satisfied).lower()}" for k in c.checks)
                lines.append(
                    f"[CANDIDATE: {c.workflow} eligible={_yn(c.eligible)} recommended={_yn(c.recommended)} when={_dash(when)}]"
                )
            if res.waiting:
                lines.append(f"[WAITING: {res.waiting.class_.value} {' '.join(res.waiting.checks)}]")
    else:
        lines.append(
            f"[STAGE: {stage.id} human_gate={_dash(stage.gate or '')} role={_dash(stage.role)} isolation={_dash(stage.isolation)}]"
        )
        lines.append(f"[UNMET: {_dash(' '.join(u.name for u in res.unmet))}]")
        for u in res.unmet:
            lines.append(
                f'[CHECK: {u.name} class={u.class_.value} evaluated={str(u.evaluated).lower()} detail="{u.detail}"]'
            )
        lines.append(f"[NEXT_SKILL: {_dash(res.next_skill)}]")
        if res.delegate:
            contract = f" contract={res.delegate.contract}" if res.delegate.contract else ""
            lines.append(f"[DELEGATE: role={res.delegate.role} isolation={res.delegate.isolation}{contract}]")
        if stage.returns:
            parts = "; ".join(f"{r.to} when={r.when}" for r in stage.returns)
            lines.append(f"[RETURNS: {parts}]")
        if res.gate:
            lines.append(f"[GATE: {res.gate.name} policy={res.gate.policy} given={_yn(res.gate.given)}]")
        if res.waiting:
            lines.append(f"[WAITING: {res.waiting.class_.value} {' '.join(res.waiting.checks)}]")
    lines.extend(render_requests(res.requests))
    for e in res.envelope_errors:
        lines.append(f"[ENVELOPE_ERROR: {e.file} {e.reason}]")
    for d in res.decision_errors:
        lines.append(f"[DECISION_ERROR: {d.file} {d.reason}]")
    return "\n".join(lines) + "\n"


def render_requests(requests: list[Request]) -> list[str]:
    lines: list[str] = []
    for r in requests:
        if r.kind == "choose":
            lines.append(
                f'[REQUEST: id={r.id} kind=choose title="{r.title}" '
                f"options={_dash(','.join(o.id for o in r.options))} "
                f"eligible={_dash(','.join(o.id for o in r.options if o.eligible))} "
                f"recommended={_dash(','.join(o.id for o in r.options if o.recommended and o.eligible))} "
                f"multi={_yn(r.multi)} other={_yn(r.allow_other)}]"
            )
        else:
            lines.append(
                f'[REQUEST: id={r.id} kind={r.kind} title="{r.title}" target={r.target.type}:{r.target.name} '
                f"stage={_dash(r.target.stage or '')} note={'allowed' if r.allow_note else 'no'}]"
            )
        if r.declined:
            lines.append(f'[DECLINED: id={r.id} file={r.declined.file} note="{r.declined.note}"]')
    return lines


def render_document(
    doc: WorkflowDocument, approvals: dict[str, str] | None = None, stages: dict[str, str] | None = None
) -> str:
    approvals = approvals or {}
    stages = stages or {}
    lines = [
        f'[WORKFLOW: {doc.id} title="{doc.title}" status={_dash(doc.status)} stages={len(doc.stages)} hash={schema_hash(doc)}]'
    ]
    if doc.layout:
        lay = doc.layout
        lines.append(
            f"[LAYOUT: work_dir={_dash(lay.work_dir or '')} unit_path={_dash(lay.unit_path or '')} anchor={_dash(lay.anchor or '')}]"
        )
    for c in doc.declared_checks:
        lines.append(f'[DECLARED_CHECK: {c.name} class={c.class_.value} description="{c.description}"]')
    for s in doc.stages:
        lines.append(
            f'[STAGE: {s.id} name="{s.name}" human_gate={_dash(s.gate or "")} role={_dash(s.role)} '
            f"isolation={_dash(s.isolation)} optional={_yn(s.optional)} exception={_yn(s.exception)}]"
        )
        if stages.get(s.id) == "off":
            lines.append(f"[SKIP: {s.id} reason=stages.{s.id}=off]")
        if s.gate:
            lines.append(f"[GATE: {s.gate} policy={approvals.get(s.gate, 'ask')}]")
        lines.append(f"[ENTRY: {_dash(' '.join(s.entry))}]")
        lines.append(f"[EXIT: {_dash(' '.join(s.exit))}]")
        lines.append(f"[ARTIFACTS: {_dash(' '.join(s.artifacts))}]")
        lines.append(f"[SKILLS: {_dash(' '.join(s.skills))}]")
        if s.returns:
            lines.append(f"[RETURNS: {'; '.join(f'{r.to} when={r.when}' for r in s.returns)}]")
    for c in doc.next:
        lines.append(f"[NEXT: {c.workflow} recommended={_yn(c.recommended)} when={_dash(' '.join(c.when))}]")
    return "\n".join(lines) + "\n"
