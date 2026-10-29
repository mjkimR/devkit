"""Procedural prerequisite selection stays base-bound in local and cloud guidance."""

import subprocess
from pathlib import Path

import pytest
from devkit_core.core.frontmatter import parse
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_pickup_order_and_lifecycle_guards(environment: str) -> None:
    next_work = raw("skills/spec-next/references/next-work.md", environment)
    for rule in (
        ("prerequisite procedure", "every candidate", "including critical drafts"),
        ("blocked candidate", "unfinished proposal", "rejected proposal", "unfinished spec", "invalid/unknown target"),
        ("blocked candidate", "a critical blocked draft stays blocked"),
        ("`git rev-parse <base>`", "report the base ref and commit", "`git show <commit>:<path>`"),
        ("`git rev-parse <base>`", "do not fetch implicitly", "never substitute completion", "activity branch"),
        ("`status: completed`", "do not recursively reopen", "prerequisites"),
        ("explicit user pickup can override order", "cannot waive malformed references or cycles"),
        ("explicit proposal pickup", "direct-spec intake"),
        ("critical drafts first", "whatever their milestone"),
    ):
        assert_rule(next_work, *rule)
    backlog = raw("skills/spec/references/backlog.md", environment)
    for rule in (
        ("before splitting, superseding, rejecting, deleting or reclassifying a proposal",),
        ("`devkit docs refs prop-<slug> --direction in -n 0`", "`depends_on`", "leave completed ones unchanged"),
        ("with the user", "required child/successor set", "only when the prerequisite is explicitly waived"),
        ("commit the disposition", "same authorized change"),
        ("dependent", "outside your write scope", "stop", "ask the host to coordinate"),
    ):
        assert_rule(backlog, *rule)
    classification = raw("skills/spec/references/classification.md", environment)
    assert_rule(classification, "before direct-spec intake or explicit proposal pickup", "prerequisite procedure")


def test_templates_separate_membership_and_prerequisites() -> None:
    proposal = text("templates/proposal.md")
    assert "# depends_on: [PROP-foundation, SPEC-parser]" in proposal
    assert "never carried to spec.md" in proposal
    milestone = raw("skills/spec/references/roadmap-catalog.md")
    assert_rule(milestone, "user and agent jointly review", "direct prop members", "initially have one proposal")
    assert_rule(milestone, "prefer observable phase-level outcomes", "cli flags, branch names, file layouts")
    assert_rule(milestone, "handoff does not carry milestone metadata to spec", "no delivery lineage is stored")


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
