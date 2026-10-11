from pathlib import Path


def test_resource_manifest_and_skill_are_in_package() -> None:
    root = Path(__file__).parents[1] / "src/devkit_starter/bundle"
    assert (root / "bundle.toml").is_file()
    assert (root / "skills/review/SKILL.md").is_file()
    assert (root / "instructions/development.md").is_file()
    assert (root / "playbooks/review.md").is_file()
    example = Path(__file__).parents[3] / "examples/bundles/starter"
    for path in root.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (example / path.relative_to(root)).read_bytes()
