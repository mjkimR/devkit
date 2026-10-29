"""Backlog roles, the XL size gate and the support-role snapshot as the bundle text states them
(``SPEC-backlog-subagent-roles``)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw, text
from spec_support.proposals import TODAY

from devkit_spec.features.proposals import create_proposal

DELEGATE = "skills/spec-delegate/SKILL.md"
BACKLOG = "skills/spec/references/backlog.md"
XL_DEFINITION = "would need two or more specs or task kinds"


def test_triage_is_delegated_above_five_open_items_on_a_native_host() -> None:
    hygiene = raw("playbooks/feedback-hygiene/SKILL.md")
    assert_rule(hygiene, "more than 5 items", "`triage` role natively", "delegate", "`spec-delegate`")
    assert_rule(hygiene, "`triage`", "clean checkout", "`git status --porcelain` empty")
    assert_rule(hygiene, "`triage`", "otherwise run this step inline", "dirty checkout", "clean task worktree")
    assert_rule(hygiene, "commit", "body names the `triage` role", "when one was used")


def test_the_decomposer_runs_from_backlog_only_and_the_host_verifies_and_applies() -> None:
    backlog = raw(BACKLOG)
    for rule in (
        (
            "`decomposer`",
            "only from backlog",
            "never on your own initiative",
            "`needs_decompose` draft",
            "planning return is merged",
            "user's request to split",
            "`xl` draft",
        ),
        ("`triage`", "`decomposer`", "read-only", "no envelope", "applies only what the user decides"),
        ("before", "checkout is clean", "`git status --porcelain` empty"),
        ("after", "`git status --porcelain` is still empty", "`spec-delegate` step 4"),
        ("before applying a split", "`git diff <head> -- docs/proposals/prop-<slug>` is empty"),
        ("every existing id", "resolves with `devkit docs resolve`"),
        ("proposed child or milestone slug", "must not resolve"),
        ("never assign the parent's open feedback to a child",),
        ("backlog commit body", "names the role used"),
    ):
        assert_rule(backlog, *rule)
    assert_rule(
        raw("skills/spec-next/references/next-work.md"),
        "`needs_decompose`",
        "`xl` drafts",
        "decompose first",
        "`decomposer`",
        "backlog.md#the-xl-size-gate",
    )


def test_the_backlog_commit_rule_stays_in_requests_and_decomposition() -> None:
    backlog = raw(BACKLOG)
    requests = backlog.split("## Requests and decomposition", 1)[1].split("\n## ", 1)[0]
    assert "- Commit Backlog edits in the current checkout" in requests


def test_spec_delegate_names_both_roles_and_their_payload() -> None:
    delegate = raw(DELEGATE)
    assert_rule(delegate, "support role", "`ux-reviewer`", "`triage`", "`decomposer`")
    assert_rule(delegate, "backlog role", "`triage`", "`decomposer`", "returns a message", "no envelope")
    payload = raw("skills/spec-delegate/references/payload.md")
    assert "| `triage` |" in payload and "| `decomposer` |" in payload


def _snapshot_command() -> str:
    block = re.search(r"```bash\n(.*?)```", raw(DELEGATE), re.S)
    assert block is not None
    return block.group(1)


def _sh(root: Path, command: str) -> str:
    return subprocess.run(
        ["sh", "-c", command], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()  # fmt: skip


def test_the_support_role_snapshot_sees_a_write_to_an_already_modified_file(tmp_path: Path) -> None:
    # FB-support-role-diff-check-on-dirty-tree: the status code of a dirty path does not change on a second write.
    root = tmp_path
    for command in ("git init -q", "git config user.email t@t", "git config user.name t"):
        _sh(root, command)
    (root / ".gitignore").write_text("probe/\n")
    (root / "f").write_text("a\n")
    _sh(root, "git add -A && git commit -q -m base")
    (root / "f").write_text("a\nb\n")
    (root / "new.txt").write_text("u\n")
    status, index = _sh(root, "git status --short"), _sh(root, "git ls-files -s")
    before = _sh(root, _snapshot_command())
    assert _sh(root, "git status --short") == status and _sh(root, "git ls-files -s") == index
    assert _sh(root, _snapshot_command()) == before  # stable while nothing changes
    with (root / "f").open("a") as handle:
        handle.write("c\n")
    with (root / "new.txt").open("a") as handle:
        handle.write("v\n")
    (root / "probe").mkdir()
    (root / "probe/test_x.py").write_text("x\n")  # an ignored probe path is not a write
    assert _sh(root, "git status --short") == status  # the old check passes
    after = _sh(root, _snapshot_command())
    assert after != before
    assert _sh(root, f"git diff --name-only {before} {after}").splitlines() == ["f", "new.txt"]
    assert _sh(root, "git ls-files -s") == index


def test_the_snapshot_replaces_the_status_comparison() -> None:
    delegate = text(DELEGATE)
    assert "leaves `git status --short` unchanged" not in delegate
    assert_rule(raw(DELEGATE), "`git diff --name-only <before> <after>`", "snapshots", "before and after the run")


def test_the_size_gate_reads_as_decompose_first_everywhere() -> None:
    assert_rule(raw(BACKLOG), "decompose first", "never edit the size to pass")
    # The workflow and the pickup reference point at the backlog's gate instead of restating it.
    assert_rule(raw("workflows/sdd-proposal.md"), "decompose first", "`references/backlog.md`", "the xl size gate")
    assert "../../spec/references/backlog.md#the-xl-size-gate" in raw("skills/spec-next/references/next-work.md")
    assert_rule(
        raw("skills/spec/SKILL.md"),
        "judge `size` against the `XL` definition ([backlog](references/backlog.md))",
        "`planning_effort`",
        "plan-intent request",
    )
    assert "exit: [anchor-exists, frontmatter(proposal.md size S|M|L|)]" in raw("workflows/sdd-proposal.md")
    planning = raw("skills/spec/references/planning.md")
    assert_rule(
        planning,
        "must be split",
        "`needs_decompose: true`",
        "`size` other than absent or exactly `s`, `m` or `l`",
        "return it",
        "`status: draft`",
    )
    assert_rule(raw(BACKLOG), "no `needs_decompose`, `size: xl`, `supersedes` or depth escalation")


def test_xl_has_a_judgeable_definition_with_an_example_of_each_side(tmp_path: Path) -> None:
    template = raw("templates/proposal.md")
    assert XL_DEFINITION in template
    assert "a new CLI command with a viewer redesign it does not need (two specs)" in template
    assert "a parser bugfix with a new search" in template
    assert "Not XL: two agent contracts and the command checks that route work to them" in template
    assert_rule(raw(BACKLOG), "`size: xl`", "two or more specs", "different `task_kind`")
    assert_rule(raw("skills/spec/references/proposals-catalog.md"), "`size: xl`", "backlog.md#the-xl-size-gate")
    (tmp_path / ".devkit").mkdir()
    scaffolded = (tmp_path / create_proposal(tmp_path, "x", today=TODAY).path).read_text(encoding="utf-8")
    assert XL_DEFINITION in scaffolded
    for document in (template, text("skills/spec/references/proposals-catalog.md"), scaffolded, text(BACKLOG)):
        assert "major overhaul" not in document


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_the_backlog_reference_renders_the_gate_in_every_environment(environment: str) -> None:
    assert "## The XL size gate" in raw(BACKLOG, environment)
    assert "## Backlog roles" in raw(BACKLOG, environment)
