"""Normal YAML spellings and root Unit companion ownership."""

from devkit_agt.features.rules import committed_anchors, touched_owners
from testsupport.rules import git, init_repo, write


def test_quoted_workflow_and_history_keys(tmp_path):
    repo = init_repo(tmp_path / "repo")
    write(repo, "anchor.md", "\n".join(["---", '"workflow": sdd-spec-feature', "---", "# Unit", ""]))
    write(
        repo,
        "other/anchor.md",
        "\n".join(["---", "'workflow_history':", "  - workflow: sdd-spec-feature", "---", "# Prior Unit", ""]),
    )
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "record Units")
    anchors = committed_anchors(repo, "HEAD")
    assert anchors == {"anchor.md": ("sdd-spec-feature",), "other/anchor.md": ("sdd-spec-feature",)}
    assert touched_owners(anchors, ("tasks.md",)) == (".",)
    assert touched_owners({"other/anchor.md": ("sdd-spec-feature",)}, ("unrelated.py",)) == ()
