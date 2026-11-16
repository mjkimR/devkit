"""A draft's ordering claim about other proposals is checked when written and at the first Planning turn."""

import subprocess
from pathlib import Path

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw

BRANCH_CHECK = "`git branch -a --list 'dev-<slug>' '*/dev-<slug>'`"


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_backlog_checks_named_proposals_before_committing_the_draft(environment: str) -> None:
    backlog = raw("skills/spec/references/backlog.md", environment)
    for rule in (
        (
            "claims its handoff precedes",
            "cost depends on",
            "before committing the draft",
            "base `status`",
            BRANCH_CHECK,
        ),
        ("claims its handoff precedes", "fetch only within existing network authorization", "never implicitly"),
        ("a `dev-<slug>` branch or a `spec-<slug>`", "handed off", "rewrite the premise"),
        ("still `accepted`", "no `dev-<slug>` branch", "ask the user to sequence", "state the decision in the draft"),
    ):
        assert_rule(backlog, *rule)


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_first_planning_turn_rechecks_ordering_claims(environment: str) -> None:
    planning = raw("skills/spec/references/planning.md", environment)
    assert_rule(planning, "on the first turn", "after the host refreshes the branch", "head-pinned evidence")
    assert_rule(planning, "names as following it", BRANCH_CHECK, "`accepted`", "until its development integrates")
    assert_rule(planning, "names as following it", "cost depends on", BRANCH_CHECK, "update the stale premise")
    assert_rule(planning, BRANCH_CHECK, "still `accepted` with no branch", "ask the user to sequence", "question round")
    assert_rule(planning, "head-pinned evidence", "before the first planning decision")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def branch_check(root: Path, slug: str) -> list[str]:
    command = BRANCH_CHECK.strip("`").replace("<slug>", slug).split()
    patterns = [pattern.strip("'") for pattern in command[4:]]
    return git(root, "branch", "-a", "--format=%(refname:short)", "--list", *patterns).split()


def test_documented_branch_check_finds_a_handoff_the_base_still_lists_as_accepted(tmp_path: Path) -> None:
    origin, clone = tmp_path / "origin", tmp_path / "clone"
    origin.mkdir()
    git(origin, "init", "-q", "-b", "main")
    git(origin, "config", "user.name", "Fixture")
    git(origin, "config", "user.email", "fixture@example.invalid")
    proposal = origin / "docs/proposals/PROP-later/proposal.md"
    proposal.parent.mkdir(parents=True)
    proposal.write_text("---\nid: PROP-later\nstatus: accepted\n---\n")
    git(origin, "add", "docs")
    git(origin, "commit", "-qm", "accept later")
    assert branch_check(origin, "later") == []
    git(origin, "branch", "dev-later-extra")
    assert branch_check(origin, "later") == []
    git(origin, "branch", "dev-later")
    git(tmp_path, "clone", "-q", str(origin), str(clone))
    assert "status: accepted" in git(origin, "show", "main:docs/proposals/PROP-later/proposal.md")
    assert branch_check(origin, "later") == ["dev-later"]
    assert branch_check(clone, "later") == ["origin/dev-later"]
