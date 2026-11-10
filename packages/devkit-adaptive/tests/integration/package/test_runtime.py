"""The extension imports without SDD and refuses content-only snapshot export."""

import json
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner
from devkit_dist.features.distribution.cli.bundles import snapshot

PACKAGE = Path(__file__).resolve().parents[3]


def test_fresh_imports_do_not_load_spec():
    script = "import pkgutil,importlib,sys,json,devkit_adaptive; [importlib.import_module(m.name) for m in pkgutil.walk_packages(devkit_adaptive.__path__,devkit_adaptive.__name__+'.')]; print(json.dumps(list(sys.modules)))"
    result = subprocess.run([sys.executable, "-c", script], text=True, capture_output=True, check=True)
    assert not any(name == "devkit_spec" or name.startswith("devkit_spec.") for name in json.loads(result.stdout))


def test_snapshot_refuses_runtime_package(tmp_path):
    result = CliRunner().invoke(
        snapshot,
        [str(PACKAGE), "--to", str(tmp_path / "snapshot"), "--package", "snapshot-adaptive", "-w", str(tmp_path)],
    )
    assert result.exit_code == 2, result.output
    assert "BUNDLE_SNAPSHOT_UNSUPPORTED" in result.output
