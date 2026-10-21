"""Shared artifact guidance preserves the explicit connection precondition."""

from pathlib import Path


def test_local_orchestration_requires_project_connection():
    bundle = Path(__file__).resolve().parents[2] / "src/devkit_spec/bundle/skills"
    for path in (bundle / "spec-orchestrate/SKILL.md", bundle / "spec-delegate/references/hosts.md"):
        text = _rendered(path)
        assert "shared_put" in text and "shared_sweep_apply" in text
        assert "Do not automatically fall back to CLI" in text
        assert "stop that dependent operation" in text
        assert "permission refusal grants no rerouting authority" in text


def _rendered(path: Path) -> str:
    from devkit.distribution.bundles.templates import render_template

    if path.name.endswith(".md.jinja"):
        return render_template(path.read_bytes(), {}, str(path), environment="local").decode()
    if path.exists():
        return path.read_text(encoding="utf-8")
    source = path.with_name(path.name + ".jinja")
    return render_template(source.read_bytes(), {}, str(source), environment="local").decode()
