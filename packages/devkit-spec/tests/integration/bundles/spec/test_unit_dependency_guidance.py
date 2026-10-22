"""Procedural prerequisite selection stays base-bound in local and cloud guidance."""

import subprocess
from pathlib import Path

import pytest
from devkit_core.core.frontmatter import parse
from devkit_dist.features.distribution.services.bundles.templates import render_template

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"


def read(rel: str, environment: str = "local") -> str:
    path = BUNDLE / rel
    if not path.exists():
        path = path.with_name(path.name + ".jinja")
    if path.name.endswith(".jinja"):
        return render_template(path.read_bytes(), {}, str(path), environment=environment).decode()
    return path.read_text()


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_pickup_order_and_lifecycle_guards(environment: str) -> None:
    next_work = " ".join(read("skills/spec-next/references/next-work.md", environment).split())
    for phrase in (
        "including critical drafts",
        "A critical blocked draft stays blocked",
        "git rev-parse <base>",
        "git show <commit>:<path>",
        "report the base ref and commit",
        "Do not fetch implicitly",
        "Never substitute completion",
        "unfinished proposal",
        "rejected",
        "proposal, unfinished spec",
        "invalid/unknown target",
        "Do not recursively reopen",
        "Explicit user pickup can override order",
        "cannot waive malformed references or cycle",
        "direct-spec intake",
        "Critical drafts first, whatever their milestone",
    ):
        assert phrase in next_work, phrase
    backlog = read("skills/spec/references/backlog.md", environment)
    for phrase in (
        "--direction in -n 0",
        "leave completed ones unchanged",
        "Before splitting, superseding, rejecting, deleting or reclassifying a proposal",
        "required child/successor set",
        "only when the prerequisite is explicitly waived",
        "same authorized change",
        "If a dependent lies outside your write scope, stop and ask the Host to coordinate",
    ):
        assert phrase in backlog, phrase
    classification = read("skills/spec/references/classification.md", environment)
    assert "Before direct-spec intake or explicit proposal pickup" in classification


def test_templates_separate_membership_and_prerequisites() -> None:
    proposal = read("templates/proposal.md")
    assert "# depends_on: [PROP-foundation, SPEC-parser]" in proposal
    assert "never carried to spec.md" in proposal
    milestone = read("templates/milestone.md")
    assert "direct PROP" in milestone and "phase-level outcomes" in milestone
    assert "initially have one proposal" in milestone and "User and agent jointly review" in milestone
    assert "Handoff does not carry milestone metadata to SPEC" in milestone
    assert "CLI flags, branch names, file layouts" in milestone
    assert "no delivery lineage is stored" in read("seed/docs/roadmap/README.md")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def test_documented_snapshot_read_distinguishes_branch_only_completion(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    paths = {"SPEC-base": "specs/2026-10/base/spec.md", "SPEC-branch": "specs/2026-10/branch/spec.md"}
    for name, rel in paths.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True)
        status = "completed" if name == "SPEC-base" else "in-progress"
        path.write_text(f"---\nid: {name}\nstatus: {status}\n---\n")
    git(tmp_path, "add", "specs")
    git(tmp_path, "commit", "-qm", "base anchors")
    base = git(tmp_path, "rev-parse", "main")
    git(tmp_path, "switch", "-qc", "dev-candidate")
    branch = tmp_path / paths["SPEC-branch"]
    branch.write_text(branch.read_text().replace("in-progress", "completed"))
    git(tmp_path, "add", "specs")
    git(tmp_path, "commit", "-qm", "branch completion only")
    tree = git(tmp_path, "ls-tree", "-r", "--name-only", base, "--", "docs", "specs").splitlines()
    assert set(tree) == set(paths.values())
    snapshot = {name: parse(git(tmp_path, "show", f"{base}:{rel}")).data for name, rel in paths.items()}
    assert snapshot["SPEC-base"] == {"id": "SPEC-base", "status": "completed"}
    assert snapshot["SPEC-branch"] == {"id": "SPEC-branch", "status": "in-progress"}
    assert parse(branch.read_text()).data == {"id": "SPEC-branch", "status": "completed"}
