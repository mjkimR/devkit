"""The post-handoff link check and the worktree reference name where link fixes are committed after the composed
handoff and how a sibling draft's later base-merge conflict is resolved (SPEC-git-operator-result-readiness AC-08,
``FB-handoff-rewrite-edits-sibling-draft``)."""

from __future__ import annotations

from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw

POST_HANDOFF = "skills/spec-next/references/post-handoff.md"
WORKTREE = "skills/spec/references/worktree.md.jinja"


def test_link_fixes_after_the_composed_handoff_are_a_later_host_commit() -> None:
    text = raw(POST_HANDOFF)
    assert "same change" not in text
    assert_rule(text, "plain handoff commits", "nothing", "commit these fixes with its writes")
    assert_rule(text, "composed handoff", "already committed its transaction", "`commit=`")
    assert_rule(text, "SPEC_PROPOSAL_LINK_UNRESOLVED", "SPEC_PROPOSAL_REFS_REWRITTEN", "outside the new spec")
    assert_rule(text, "later Host commit before a worker", "starts")
    worktree = raw(WORKTREE)
    assert_rule(worktree, "commits its own transaction", "post-handoff link check", "later commit before a worker")
    assert_rule(worktree, "SPEC_HANDOFF_COMMIT_REFUSED", "stay staged", "commit there", "rerun refuses")


def test_a_sibling_conflict_takes_the_base_version_then_rules_fix() -> None:
    text = raw(POST_HANDOFF).split("## Sibling drafts", 1)[1]
    assert_rule(text, "rewrites a sibling draft's `depends_on`", "own Planning", "would dangle")
    assert_rule(text, "conflicts in", "`docs/proposals/PROP-<other>/`")
    assert_rule(text, "Take the base version", "git checkout --theirs", "devkit rules fix <path>")
    assert_rule(text, "`PROP-<slug> was handed off`", "`SPEC-<slug>`", "commit the merge")
