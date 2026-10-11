from pathlib import Path

import pytest
from agent_rule_engine import RuleContext


def test_context_creates_cache_and_matches_exact_paths(tmp_path: Path) -> None:
    ctx = RuleContext(workspace_root=tmp_path, changed_files=["docs/../docs/a.md"])
    assert ctx.cache.workspace_root == tmp_path
    assert ctx.is_file_targeted("docs/a.md")
    assert ctx.is_file_targeted(str(tmp_path / "docs/a.md"))
    assert not ctx.is_file_targeted("other/docs/a.md")


def test_context_rejects_targets_outside_workspace(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="outside the workspace"):
        RuleContext(workspace_root=tmp_path, changed_files=["../outside.md"])
