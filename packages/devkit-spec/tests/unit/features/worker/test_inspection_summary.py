"""Compact inspection keeps evidence needed to act without changing the complete result."""

from copy import deepcopy

from devkit_spec.features.worker.usecases.summary import summarize_inspection


def test_summary_preserves_actions_and_verdict_without_success_bodies_or_history() -> None:
    result = {
        "inputs": {"head": {"value": "sha", "source": "argument"}},
        "base": "base-sha",
        "head": "sha",
        "scope": [{"path": "src", "source": "boundary"}],
        "changed_paths": ["outside.py"],
        "outside_scope": ["outside.py"],
        "exit_code": 1,
        "checks": {
            "rules": {
                "status": "fail",
                "result": {
                    "violations": [{"rule_id": "R", "message": "fix"}],
                    "errors": [],
                    "notices": [],
                    "executed": ["long history"],
                },
            },
            "envelopes": {
                "status": "fail",
                "result": {
                    "envelopes": [{"file": "review-02.yaml", "findings": [{"issue": "fix current"}]}],
                    "blocked": True,
                    "problems": [{"cause": "failed", "recovery": "retry"}],
                    "pending_questions": [{"id": "q1"}],
                    "errors": [],
                },
            },
            "workflow": {
                "status": "pass",
                "result": {
                    "workflow": "sdd",
                    "stage": {"id": "build", "role": "worker", "entry": ["long definition"], "exit": []},
                    "done": ["history"],
                    "unmet": [{"check": "test", "detail": "run tests"}],
                    "next_skill": "verify",
                    "stale_approvals": ["old.yaml"],
                },
            },
            "other": {"status": "pass", "result": {"historical_body": "long"}},
        },
    }
    before = deepcopy(result)
    summary = summarize_inspection(result)
    assert result == before
    assert summary["exit_code"] == 1 and summary["outside_scope"] == ["outside.py"]
    assert summary["inputs"] == result["inputs"]
    checks = summary["checks"]
    assert checks["rules"]["result"]["violations"] == [{"rule_id": "R", "message": "fix"}]
    assert "executed" not in checks["rules"]["result"]
    assert checks["envelopes"]["result"]["problems"][0]["recovery"] == "retry"
    assert checks["envelopes"]["result"]["pending_questions"] == [{"id": "q1"}]
    assert checks["envelopes"]["result"]["envelopes"][0]["findings"] == [{"issue": "fix current"}]
    assert checks["workflow"]["result"]["stage"] == {"id": "build", "role": "worker"}
    assert checks["workflow"]["result"]["next_skill"] == "verify"
    assert checks["workflow"]["result"]["stale_approvals"] == ["old.yaml"]
    assert "result" not in checks["other"]


def test_unknown_failure_and_success_advisories_keep_diagnostics() -> None:
    checks = {
        "rules": {"status": "not-run", "cause": "bad output", "result": {"stdout": "trace"}, "stderr": "repair"},
        "workflow": {"status": "fail", "result": {"unknown_failure": "evidence"}},
        "other": {"status": "pass", "result": {"notices": [{"code": "NOTICE", "message": "report"}]}},
    }
    assert summarize_inspection({"checks": checks})["checks"] == checks
