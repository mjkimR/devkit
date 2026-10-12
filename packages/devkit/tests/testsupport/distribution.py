"""Distribution test helpers."""

from __future__ import annotations

from pathlib import Path

from devkit.distribution.bundles import load_bundle
from devkit.distribution.installation.discovery import InstalledBundle


def make_bundle(tmp_path: Path, bundle: str, *, directory: bool = False) -> InstalledBundle:
    root = tmp_path / bundle
    root.mkdir()
    (root / "AGENTS.md").write_text("# Shared contracts\n")
    (root / "guide.md").write_text("---\nname: testing\ndescription: Testing constraints.\n---\nInstruction body.\n")
    source = "recovery/SKILL.md" if directory else "recovery.md"
    (root / source).parent.mkdir(exist_ok=True)
    (root / source).write_text(
        "---\nname: restore-replica\ndescription: Restore a PostgreSQL replica.\n"
        "aliases:\n  - postgres standby repair\n  - wal failure\n---\n\nBODY_ONLY_SECRET\n"
    )
    if directory:
        (root / "recovery/reference.md").write_text("Resource containing bodyonlytoken.\n")
    (root / "release.md").write_text(
        "---\nname: publish-release\ndescription: Publish a software release.\n---\nbodyonlytoken\n"
    )
    (root / "bundle.toml").write_text(f'''schema = 1
name = "{bundle}"
version = "0.1.0"
[[assets]]
id = "recovery"
kind = "playbook"
source = "{"recovery" if directory else source}"
[[assets]]
id = "release"
kind = "playbook"
source = "release.md"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[presets.guidance]
assets = ["guide"]
[presets.recovery]
assets = ["recovery", "guide"]
''')
    return InstalledBundle(f"{bundle}-content", "0.1.0", load_bundle(root))


def write_bundle(
    root: Path, manifest: str, files: dict[str, str], *, executable: tuple[str, ...] = (), package: str = "content"
) -> InstalledBundle:
    """Write a bundle source (``bundle.toml`` plus ``files``) under ``root`` and load it as installed."""
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    for rel in executable:
        (root / rel).chmod(0o755)
    (root / "bundle.toml").write_text(manifest)
    return InstalledBundle(package, "0.1.0", load_bundle(root))


def reload(item: InstalledBundle, version: str = "0.2.0") -> InstalledBundle:
    """The same bundle source loaded again, as after an upstream upgrade."""
    return InstalledBundle(item.package, version, load_bundle(item.bundle.root))


def instruction(name: str, body: str = "Body.\n") -> str:
    return f"---\nname: {name}\ndescription: When to read {name}.\n---\n{body}"
