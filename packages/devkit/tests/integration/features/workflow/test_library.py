"""The documented library surface, the reference example and the delivery-workflow example bundle."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import devkit_agt.features.workflow as workflow
import pytest
from devkit_agt.features.workflow import (
    UnitNotFoundError,
    WorkflowError,
    Workspace,
    create_unit,
    list_units,
    plan_handoff,
    record_answer,
)
from devkit_agt.features.workflow.services.envelope import parse_findings
from testsupport.workflow import WORKFLOW, write_config

REPO = Path(__file__).resolve().parents[6]
REFERENCE = REPO / "docs/development/reference/workflow.md"
EXAMPLE = REPO / "examples/bundles/delivery-workflow"


def _python_blocks(markdown: str) -> list[str]:
    return re.findall(r"```python\n(.*?)```", markdown, flags=re.S)


def _workspace(root: Path) -> Path:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "direct-delivery.md").write_text(WORKFLOW)
    write_config(root, '[workflow]\ndefault = "direct-delivery"\n')
    return root


def test_reference_library_example_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _workspace(tmp_path)
    create_unit(Workspace(root), "login")
    example = next(block for block in _python_blocks(REFERENCE.read_text()) if "Workspace(" in block)
    monkeypatch.chdir(root)
    exec(compile(example, str(REFERENCE), "exec"), {})
    assert capsys.readouterr().out.splitlines() == ["intent", "gate:direction approve intent"]


def test_every_exported_name_exists() -> None:
    missing = [name for name in workflow.__all__ if not hasattr(workflow, name)]
    assert missing == []


def test_library_errors_carry_codes(tmp_path: Path) -> None:
    ws = Workspace(_workspace(tmp_path))
    with pytest.raises(WorkflowError) as raised:
        ws.resolve_unit("nowhere")
    assert raised.value.code == "UNIT_NOT_FOUND"
    unit = create_unit(ws, "login")
    with pytest.raises(WorkflowError) as raised:
        create_unit(ws, "login")
    assert raised.value.code == "UNIT_EXISTS"
    with pytest.raises(WorkflowError) as raised:
        record_answer(ws, unit, "gate:integration", "accept", lint=False)
    assert raised.value.code == "REQUEST_UNKNOWN"
    result = ws.evaluate_unit(unit, lint=False)
    with pytest.raises(WorkflowError) as raised:
        plan_handoff(ws, unit, result)
    assert raised.value.code == "HANDOFF_NOT_READY"
    decision = record_answer(ws, unit, "gate:direction", "accept", by="lib", lint=False)
    assert (decision.file, decision.workflow, decision.stage) == (
        "decisions/01-gate-direction.yaml",
        "direct-delivery",
        "intent",
    )
    assert [row.unit for row in list_units(ws)] == [".devkit/transient/work/login"]
    assert issubclass(UnitNotFoundError, WorkflowError)


def test_example_bundle_definition_validates(tmp_path: Path) -> None:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    shutil.copy(EXAMPLE / "workflows/direct-delivery.md", defs / "direct-delivery.md")
    roles = tmp_path / ".devkit/roles"
    roles.mkdir()
    shutil.copy(EXAMPLE / "subagents/reviewer.md", roles / "reviewer.md")
    report = Workspace(tmp_path).validate_definitions()
    assert report.ok, [str(p) for r in report.definitions for p in r.problems]
    assert [r.doc.id for r in report.definitions] == ["direct-delivery"]


def test_example_reviewer_contract_matches_the_envelope_schema() -> None:
    contract = (EXAMPLE / "subagents/reviewer.md").read_text()
    findings = re.findall(r"```yaml\n(.*?)```", contract, flags=re.S)
    assert findings, "the reviewer contract shows a findings example"
    parsed = parse_findings(findings[0], "review")
    assert parsed and all(f.issue and f.evidence for f in parsed)
    for removed in ("severity", "verdict"):
        assert removed not in contract
