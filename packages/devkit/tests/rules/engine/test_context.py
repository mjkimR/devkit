from pathlib import Path

import pytest
from devkit_agt.features.rules import RuleContext, TargetError


def test_context_creates_cache_and_matches_exact_paths(tmp_path: Path) -> None:
    ctx = RuleContext(workspace_root=tmp_path, changed_files=["docs/../docs/a.md"])
    assert ctx.cache.workspace_root == tmp_path
    assert ctx.is_file_targeted("docs/a.md")
    assert ctx.is_file_targeted(str(tmp_path / "docs/a.md"))
    assert not ctx.is_file_targeted("other/docs/a.md")


def test_context_exclusions_apply_to_targets_and_whole_workspace_runs(tmp_path: Path) -> None:
    ctx = RuleContext(workspace_root=tmp_path, exclude=("docs/research/**", "CHANGELOG.md"))
    assert not ctx.has_targets
    assert ctx.is_file_targeted("docs/a.md")
    assert not ctx.is_file_targeted("docs/research/deep/b.md")
    assert not ctx.is_file_targeted(str(tmp_path / "CHANGELOG.md"))

    targeted = RuleContext(
        workspace_root=tmp_path,
        changed_files=["docs/research/b.md", "docs/a.md"],
        exclude=("docs/research/**",),
    )
    assert targeted.has_targets
    assert targeted.changed_files == ["docs/a.md"]
    assert targeted.is_file_targeted("docs/a.md") and not targeted.is_file_targeted("docs/research/b.md")

    # Every explicit target excluded: nothing is targeted, not the whole workspace.
    nothing = RuleContext(workspace_root=tmp_path, changed_files=["docs/research/b.md"], exclude=("docs/research/**",))
    assert nothing.has_targets and nothing.changed_files == []
    assert not nothing.is_file_targeted("docs/a.md")


def test_context_rejects_targets_outside_workspace(tmp_path: Path) -> None:
    with pytest.raises(TargetError, match="outside the workspace"):
        RuleContext(workspace_root=tmp_path, changed_files=["../outside.md"])


def test_symlinked_targets_keep_their_own_name(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/real.md").write_text("x\n")
    (tmp_path / "docs/link.md").symlink_to("real.md")
    ctx = RuleContext(workspace_root=tmp_path, changed_files=["docs/link.md"])
    assert ctx.changed_files == ["docs/link.md"]
    assert ctx.is_file_targeted("docs/link.md") and not ctx.is_file_targeted("docs/real.md")


def test_settings_for_a_path_outside_the_workspace_is_refused(tmp_path: Path) -> None:
    from devkit_agt.features.rules import evaluate_rules
    from devkit_agt.features.rules.services.builtins import FileLengthRule

    rule = FileLengthRule()
    ctx = RuleContext(workspace_root=tmp_path)
    evaluate_rules(ctx, [rule])
    assert ctx.settings(rule).max_lines == 400
    assert ctx.settings(rule, tmp_path / "a.md").max_lines == 400
    with pytest.raises(TargetError, match="outside the workspace"):
        ctx.settings(rule, tmp_path.parent / "elsewhere.md")


def test_cache_is_always_a_workspace_cache(tmp_path: Path) -> None:
    from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache

    own = RuleContext(workspace_root=tmp_path)
    assert isinstance(own.cache, WorkspaceCache) and own.cache.workspace_root == tmp_path.resolve()
    shared = WorkspaceCache(tmp_path)
    assert RuleContext(workspace_root=tmp_path, cache=shared).cache is shared
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(ValueError, match="same workspace root"):
        RuleContext(workspace_root=tmp_path, cache=WorkspaceCache(other))
