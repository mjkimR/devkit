"""Consumer recommendations keep worker checks separate from Host execution."""

from pathlib import Path

ROOT = Path(__file__).parents[3] / "src/devkit_catalog/maintenance/bundle/playbooks/test-management"


def test_execution_recommendation_preserves_native_worker_and_combined_coverage() -> None:
    text = " ".join((ROOT / "references/execution.md").read_text().split())
    assert "workers run required native checks synchronously in their assigned worktree" in text
    assert "Keep the Host's asynchronous launch, wait and cleanup out of worker payloads" in text
    assert "For the active Host's post-integration asynchronous verification" in text
    assert "devkit, a harness, a spec workflow and a verifier subagent are optional" in text
    assert "combined synchronous/CI commands and suites without E2E" in text
    assert "Keep existing required commands synchronous when the split is unclear" in text
