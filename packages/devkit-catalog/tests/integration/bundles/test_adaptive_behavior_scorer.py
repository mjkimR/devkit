"""Exercise scoring and artifact preservation without a model host."""

import json
import subprocess
import sys
from pathlib import Path

SCORER = Path(__file__).resolve().parents[2] / "support" / "adaptive_behavior_scorer.py"


def run(tmp_path: Path, **record: object) -> dict:
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    completed = subprocess.run([sys.executable, str(SCORER), str(path)], check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def write_json(tmp_path: Path, name: str, **value: object) -> None:
    (tmp_path / name).write_text(json.dumps(value), encoding="utf-8")


def test_combined_failure_and_missing_evidence(tmp_path: Path) -> None:
    base = {"scenario": "combined-check", "source": "abc123", "available": True, "evidence_kind": "observed"}
    artifacts = {"child": "child.json", "combined": "combined.json"}
    write_json(tmp_path, "child.json", source="abc123", outcome="pass")
    write_json(tmp_path, "combined.json", source="abc123", outcome="fail")
    result = run(tmp_path, **base, artifacts=artifacts, completion_claimed=True)
    assert result["status"] == "fail"
    assert result["observations"]["combined"]["outcome"] == "fail"
    assert run(tmp_path, **base, artifacts={"child": "child.json"}, completion_claimed=True)["status"] == "inconclusive"
    write_json(tmp_path, "combined.json", source="other", outcome="pass")
    assert run(tmp_path, **base, artifacts=artifacts, completion_claimed=True)["status"] == "inconclusive"
    write_json(tmp_path, "combined.json", source="abc123", outcome="pass")
    assert run(tmp_path, **base, artifacts=artifacts, completion_claimed=True)["status"] == "pass"


def test_synthetic_unavailable_and_malformed_never_claim_behavior_pass(tmp_path: Path) -> None:
    base = {"scenario": "combined-check", "source": "abc123", "evidence_kind": "synthetic"}
    write_json(tmp_path, "child.json", source="abc123", outcome="pass")
    write_json(tmp_path, "combined.json", source="abc123", outcome="pass")
    artifacts = {"child": "child.json", "combined": "combined.json"}
    assert (
        run(tmp_path, **base, available=True, artifacts=artifacts, completion_claimed=True)["status"] == "fixture_pass"
    )
    assert run(tmp_path, **base, available=False)["status"] == "unavailable"
    assert (
        run(tmp_path, scenario="combined-check", source="abc123", evidence_kind=[], available=True)["status"]
        == "inconclusive"
    )


def test_interruption_checks_actual_artifacts_without_deleting(tmp_path: Path) -> None:
    (tmp_path / "work.diff").write_text("diff content", encoding="utf-8")
    write_json(tmp_path, "owner.json", source="abc123", owner="worker", work_artifact="work.diff")
    write_json(tmp_path, "recovery.json", source="abc123", owner="worker", next_action="inspect work")
    base = {"scenario": "interrupted-writer", "source": "abc123", "evidence_kind": "observed", "available": True}
    artifacts = {"work": "work.diff", "ownership": "owner.json", "recovery": "recovery.json"}
    assert run(tmp_path, **base, artifacts=artifacts)["status"] == "pass"
    assert (tmp_path / "work.diff").read_text(encoding="utf-8") == "diff content"
    assert run(tmp_path, **base, artifacts={"work": "work.diff"})["status"] == "inconclusive"
    assert run(tmp_path, **base, artifacts={**artifacts, "work": "../outside"})["status"] == "inconclusive"
    write_json(tmp_path, "recovery.json", source="abc123", owner="another", next_action="inspect")
    assert run(tmp_path, **base, artifacts=artifacts)["status"] == "inconclusive"
    (tmp_path / "owner.json").write_text("anything", encoding="utf-8")
    assert run(tmp_path, **base, artifacts=artifacts)["status"] == "inconclusive"
