"""SPEC-scope-activity-write-evidence: horizon labels, coverage-gap inputs and the self-base guard of ``collect``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli
from spec_support.scope import git, write

from devkit_spec.features.scope.models.observation import CollectionOptions
from devkit_spec.features.scope.usecases.collection import CollectScopesUseCase

CAP_A = "docs/capabilities/x/CAP-X-a.md"
CAP_B = "docs/capabilities/x/CAP-X-b.md"
CAP_NEW = "docs/capabilities/x/CAP-X-new.md"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, ".devkit/config.toml", "")
    write(root, "src/shared.py", "shared = 1\n")
    write(root, CAP_A, "---\nid: CAP-X-a\nstatus: active\nentrypoints: [src/shared.py]\n---\n")
    write(root, CAP_B, "---\nid: CAP-X-b\nstatus: active\nentrypoints: [src/]\n---\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
    return root


def proposal(root: Path, slug: str, *targets: str, status: str = "reviewing") -> None:
    write(root, f"docs/proposals/PROP-{slug}/proposal.md", f"---\nid: PROP-{slug}\nstatus: {status}\n---\n")
    lines = "".join(f"  - file: {target}\n" for target in targets)
    write(root, f"docs/proposals/PROP-{slug}/target-docs.md", f"---\ntargets:\n{lines}---\n")


def planning(root: Path, slug: str, *targets: str, extra: dict[str, str] | None = None) -> None:
    """A ``plan-<slug>`` branch from main whose only commit adds its proposal (and ``extra`` files)."""
    git(root, "checkout", "-qb", f"plan-{slug}", "main")
    proposal(root, slug, *targets)
    for path, text in (extra or {}).items():
        write(root, path, text)
    git(root, "add", ".")
    git(root, "commit", "-qm", f"plan {slug}")
    git(root, "checkout", "-q", "main")


def development(root: Path, slug: str, boundary: str, *, reconcile: bool = True) -> str:
    """A ``dev-<slug>`` branch from main with a spec bundle declaring ``boundary``."""
    unit = f"specs/2026-10/20261030-{slug}"
    git(root, "checkout", "-qb", f"dev-{slug}", "main")
    write(root, f"{unit}/spec.md", f"---\nid: SPEC-{slug}\nstatus: planned\n---\n")
    write(root, f"{unit}/tasks.md", f"- [ ] **Task 1**: change\n  - **_Boundary**: {boundary}\n")
    if reconcile:
        write(root, f"{unit}/reconcile.md", "---\ntargets: []\n---\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", f"dev {slug}")
    git(root, "checkout", "-q", "main")
    return unit


def collect(root: Path, **kwargs: Any) -> dict[str, Any]:
    options = CollectionOptions(mode=kwargs.pop("mode", "refs"), **kwargs)
    return CollectScopesUseCase().execute(root, options).data


def invoke(root: Path, *args: str):
    return CliRunner().invoke(cli, ["spec", "scope", "collect", "-w", str(root), *args])


def pair(data: dict[str, Any], a: str, b: str) -> dict[str, Any]:
    return next(p for p in data["pairs"] if {p["a"], p["b"]} == {f"refs/heads/{a}", f"refs/heads/{b}"})


def observation(data: dict[str, Any], branch: str) -> dict[str, Any]:
    return next(o for o in data["observations"] if o["observation_id"] == f"refs/heads/{branch}")


def problems(data: dict[str, Any], branch: str) -> list[dict[str, Any]]:
    return [p for p in data["coverage"]["problems"] if p["source_id"] == f"refs/heads/{branch}"]


def test_ac01_disjoint_planning_writes_with_future_overlap_stay_informational(repo: Path) -> None:
    planning(repo, "a", CAP_A)
    planning(repo, "b", CAP_B, CAP_NEW)
    normal = invoke(repo, "--mode", "refs", "--base", "main", "--format", "json")
    strict = invoke(repo, "--mode", "refs", "--base", "main", "--format", "json", "--strict")
    assert normal.exit_code == 0, normal.output
    assert strict.exit_code == 1
    data = json.loads(normal.stdout)
    assert set(data) == {
        "mode", "started_at", "finished_at", "coverage", "inventory", "observations", "pairs", "summary", "notices"
    }  # fmt: skip
    assert all(set(p) == {"a", "b", "docs", "code", "unresolved", "current", "future"} for p in data["pairs"])
    observed = {p["path"] for o in data["observations"] for p in o["scope"]["observed"]}
    assert {"docs/proposals/PROP-a/proposal.md", "docs/proposals/PROP-b/proposal.md"} <= observed
    assert pair(data, "plan-a", "plan-b")["future"] >= 1
    assert problems(data, "plan-b")[0]["inputs"] == ["planned-doc"]
    text = invoke(repo, "--mode", "refs", "--base", "main")
    assert text.exit_code == 0
    assert "[EVIDENCE: src/shared.py a=refs/heads/plan-a b=refs/heads/plan-b " in text.stdout
    assert "horizon=future]" in text.stdout
    assert "[DETAIL] refs/heads/plan-b: unresolved-input (planned-doc)" in text.output


def test_ac02_planning_candidate_overlap_is_future(repo: Path) -> None:
    planning(repo, "a", CAP_A)
    planning(repo, "b", CAP_B)
    data = collect(repo, base="main")
    found = pair(data, "plan-a", "plan-b")
    entries = [*found["docs"], *found["code"]]
    assert entries and all(e["horizon"] == "future" for e in entries)
    assert all({e["source"], e["other_source"]} == {"candidate"} for e in found["code"])
    assert found["current"] == 0 and found["future"] == len(found["docs"]) + len(found["code"])
    assert data["summary"]["overlapping"] == 1 and data["summary"]["current_overlapping"] == 0
    text = invoke(repo, "--mode", "refs", "--base", "main").stdout
    line = next(x for x in text.splitlines() if x.startswith("[PAIR: a=refs/heads/plan-a b=refs/heads/plan-b"))
    assert f" code={len(found['code'])} " in line and line.endswith(f"current=0 future={found['future']}]")
    assert " overlapping=1 current_overlapping=0 " in text.splitlines()[-1]


def test_ac03_development_paths_stay_current_beside_a_planning_candidate(repo: Path) -> None:
    planning(repo, "p", CAP_A)  # a candidate only
    planning(repo, "w", CAP_A, extra={"src/shared.py": "edited in planning = 1\n"})  # also an observed write
    development(repo, "d", "`src/shared.py`")
    development(repo, "e", "`src/`")
    data = collect(repo, base="main")
    future = pair(data, "dev-d", "plan-p")
    assert [(e["source"], e["other_source"], e["horizon"]) for e in future["code"]] == [
        ("declared-code", "candidate", "future")
    ]
    assert (future["current"], future["future"]) == (0, 1)
    # src/shared.py is both a candidate and an observed write of plan-w: its one entry reports the current overlap.
    written = pair(data, "dev-d", "plan-w")
    assert [(e["path"], e["other_source"], e["horizon"]) for e in written["code"]] == [
        ("src/shared.py", "observed", "current")
    ]
    assert (written["current"], written["future"]) == (1, 0)
    developers = pair(data, "dev-d", "dev-e")
    assert developers["code"] and all(e["horizon"] == "current" for e in developers["code"])
    assert developers["current"] == len(developers["code"]) and developers["future"] == 0
    assert data["summary"]["current_overlapping"] == sum(bool(p["current"]) for p in data["pairs"])
    assert pair(data, "plan-p", "plan-w")["current"] == 0  # a candidate beside an observed write is future


def test_ac04_handed_off_proposal_on_a_dev_ref_is_current(repo: Path) -> None:
    proposal(repo, "h", CAP_A, status="accepted")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "accepted proposal on the base")
    git(repo, "branch", "dev-h", "main")  # handed off, before its first commit
    development(repo, "d", "`src/shared.py`")
    data = collect(repo, base="main")
    handed = observation(data, "dev-h")
    assert handed["provenance"]["unit"] == "docs/proposals/PROP-h"
    found = pair(data, "dev-d", "dev-h")
    assert found["code"] and all(e["horizon"] == "current" for e in found["code"])
    assert found["current"] == len(found["code"]) and found["future"] == 0
    assert data["summary"]["current_overlapping"] >= 1


def test_ac05_coverage_gap_names_its_unresolved_inputs(repo: Path) -> None:
    development(repo, "d", "`src/shared.py`, `docs/capabilities/x/`", reconcile=False)
    result = invoke(repo, "--mode", "refs", "--base", "main", "--format", "json")
    data = json.loads(result.stdout)
    assert data["coverage"]["status"] == "partial"
    found = problems(data, "dev-d")
    assert [p["reason"] for p in found] == ["unresolved-input"]
    assert {"excluded-tree", "missing-reconcile"} <= set(found[0]["inputs"])
    assert found[0]["inputs"] == sorted(found[0]["inputs"])
    reasons = {u["reason"] for u in observation(data, "dev-d")["scope"]["unresolved"]}
    assert set(found[0]["inputs"]) == reasons
    notice = next(n for n in data["notices"] if n["code"] == "SPEC_SCOPE_COLLECTION_PARTIAL")
    expected = f"refs/heads/dev-d: unresolved-input ({', '.join(found[0]['inputs'])})"
    assert expected in notice["advisory"]["details"]
    assert all(isinstance(p["inputs"], list) for p in data["coverage"]["problems"])


def test_ac06_branch_at_its_base_commit_has_a_known_empty_range(repo: Path) -> None:
    proposal(repo, "c", CAP_A, status="draft")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "proposal on the base")
    git(repo, "branch", "plan-c", "main")
    for base in ("main", None):  # explicit, and the integration hint of the main checkout
        data = collect(repo, base=base)
        found = observation(data, "plan-c")
        assert "committed" in found["observed_layers"] and "committed" not in found["missing_layers"]
        assert found["scope"]["observed"] == []
        assert all(u["reason"] != "unknown-base" for u in found["scope"]["unresolved"])
        assert all(p["reason"] != "unknown-base" for p in problems(data, "plan-c"))
        assert all("unknown-base" not in p["inputs"] for p in problems(data, "plan-c"))


@pytest.mark.parametrize("how", ["explicit-short", "marker-head", "marker-short", "tracking-peer"])
def test_ac07_a_base_naming_the_branch_itself_stays_unknown(repo: Path, how: str) -> None:
    planning(repo, "a", CAP_A)
    options: dict[str, Any] = {}
    if how == "explicit-short":
        options["base"] = "plan-a"
    elif how == "tracking-peer":
        git(repo, "remote", "add", "cloud", str(repo.parent / "absent"))
        git(repo, "update-ref", "refs/remotes/cloud/plan-a", "plan-a")
        options["base"] = "cloud/plan-a"
    else:
        git(repo, "checkout", "-q", "plan-a")  # HEAD names the branch in the collecting checkout
        git(repo, "config", "branch.plan-a.devkitBase", "HEAD" if how == "marker-head" else "plan-a")
    data = collect(repo, **options)
    found = observation(data, "plan-a")
    assert "committed" in found["missing_layers"] and "committed" not in found["observed_layers"]
    assert found["provenance"]["base_sha"] == ""
    assert [p["reason"] for p in problems(data, "plan-a")] == ["unknown-base"]
    assert "unknown-base" in problems(data, "plan-a")[0]["inputs"]


def test_a_repeated_gap_merges_its_inputs_without_a_second_count(repo: Path) -> None:
    from devkit_spec.features.scope.services.collection import Collector

    collector = Collector(repo, CollectionOptions())
    collector.problem("refs/heads/dev-a", "unknown-base", ["missing-tasks", "unknown-base"])
    collector.problem("refs/heads/dev-a", "unknown-base")
    collector.problem("refs/heads/dev-a", "unknown-base", ["excluded-tree"])
    assert collector.problem_count == 1
    assert collector.problems == [
        dict(
            source_id="refs/heads/dev-a",
            reason="unknown-base",
            inputs=["excluded-tree", "missing-tasks", "unknown-base"],
        )
    ]
