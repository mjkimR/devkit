"""Small real source checkouts for filesystem and installed-consumer snapshot tests."""

from __future__ import annotations

from pathlib import Path


def content_source(root: Path, names: tuple[str, ...] = ("alpha", "beta"), *, rule: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    package = root / "src/private_content"
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text('"""Private content resources."""\n')
    entries = "\n".join(f'{name} = "private_content.{name}"' for name in names)
    (root / "pyproject.toml").write_text(
        '[project]\nname = "private-content"\nversion = "2.3.4"\nrequires-python = ">=3.12"\ndependencies = []\n'
        'license = {file = "LICENSE"}\n\n[project.entry-points."devkit.bundles"]\n'
        + entries
        + '\n\n[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '\n[tool.hatch.build.targets.wheel]\npackages = ["src/private_content"]\n'
        '\n[tool.uv.sources]\nunused = {git = "ssh://private.invalid/team/assets"}\n'
    )
    (root / "LICENSE").write_text("Fixture license notice.\n")
    for name in names:
        module = package / name
        module.mkdir(exist_ok=True)
        (module / "__init__.py").write_text("")
        bundle = module / "bundle"
        bundle.mkdir(exist_ok=True)
        (bundle / "AGENTS.md").write_text(f"# {name} contracts\n")
        (bundle / "guide.md.jinja").write_text(
            f"---\nname: {name}-guide\ndescription: Read {name} guidance.\n---\n{name} body.\n"
        )
        (bundle / "native").mkdir(exist_ok=True)
        (bundle / "native/reviewer.toml").write_text('model = "custom"\n')
        (bundle / "check.sh").write_text("#!/bin/sh\nexit 0\n")
        (bundle / "check.sh").chmod(0o755)
        manifest = f'''schema = 1
name = "{name}"
version = "1.2.3"
default_preset = "core"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md.jinja"
[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/reviewer.toml"
[presets.core]
assets = ["guide"]
'''
        if rule:
            rules = bundle / "rules/example"
            rules.mkdir(parents=True, exist_ok=True)
            (rules / "__init__.py").write_text("")
            (rules / "helper.py").write_text("VALUE = 'copied'\n")
            (rules / "rule.py").write_text(
                "from __future__ import annotations\nfrom dataclasses import dataclass\nfrom .helper import VALUE\n"
                "from devkit_agt.features.rules import Phase, Severity, Violation\n"
                "from devkit_agt.features.rules.services.builtins import BaseRule\n"
                "@dataclass\nclass ExampleRule(BaseRule):\n"
                "    id: str = 'RULE-snapshot-example'\n    name: str = 'Snapshot example'\n"
                "    description: str = VALUE\n    phase: Phase = Phase.LINTER\n    severity: Severity = Severity.INFO\n"
                "    def check(self, ctx):\n        return [Violation(self.id, 'example.md', 1, VALUE, severity=Severity.INFO)]\n"
            )
            manifest += '\n[[assets]]\nid = "example"\nkind = "rule"\nsource = "rules/example"\n'
        (bundle / "bundle.toml").write_text(manifest)
    return root
