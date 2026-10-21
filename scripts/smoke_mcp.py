"""Built-wheel MCP combinations in isolated environments; no host configuration or publication."""

from __future__ import annotations

import argparse
import os
import subprocess
import zipfile
from pathlib import Path


def run(args: list[str], cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(args, cwd=cwd, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    wheels = work / "wheels"
    wheels.mkdir(exist_ok=True)
    env = {
        **os.environ,
        "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR", str(Path.home() / ".cache/uv")),
        "HOME": str(work / "home"),
        "CODEX_HOME": str(work / "codex"),
        "PYTHONPATH": "",
    }
    packages = ["devkit-advisory", "devkit-core", "devkit-dist", "devkit-agt", "devkit-mcp", "devkit-spec"]
    for package in packages:
        run(["uv", "build", "--offline", "--wheel", "--package", package, "--out-dir", str(wheels)], root, env)
    paths = {}
    files = {}
    for wheel in wheels.glob("*.whl"):
        paths[wheel.name.split("-")[0].replace("_", "-")] = wheel
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                if ".dist-info/" in name or name.endswith("/"):
                    continue
                if name in files:
                    raise RuntimeError(f"duplicate installed path {name}: {files[name]} and {wheel.name}")
                files[name] = wheel.name
    combinations = {
        "dist": ["devkit-dist"],
        "runtime": ["devkit-dist", "devkit-mcp"],
        "agt": ["devkit-dist", "devkit-agt"],
        "agt-mcp": ["devkit-dist", "devkit-agt[mcp]", "devkit-mcp"],
        "spec-runtime": ["devkit-dist", "devkit-agt", "devkit-spec", "devkit-mcp"],
    }
    for label, chosen in combinations.items():
        target = work / label
        run(["uv", "venv", "--clear", str(target)], work, env)
        python = target / "bin/python"
        requirements = [str(paths["devkit-advisory"])]
        for package in chosen:
            base, _, extra = package.partition("[")
            requirements.append(str(paths[base]) + ("[" + extra if extra else ""))
        run(
            ["uv", "pip", "install", "--offline", "--python", str(python), "--find-links", str(wheels), *requirements],
            work,
            env,
        )
        runtime = "devkit-mcp" in chosen
        harness = any(item.startswith("devkit-agt") for item in chosen)
        spec = "devkit-spec" in chosen
        script = f"""
import importlib.util, importlib.metadata
from devkit_core.base.mcp import McpTool
from devkit.cli import cli
from click.testing import CliRunner
from pathlib import Path
assert bool(importlib.util.find_spec("devkit_mcp")) == {runtime!r}
assert bool(importlib.util.find_spec("mcp")) == {runtime!r}
assert [e.dist.name for e in importlib.metadata.entry_points(group="console_scripts", name="devkit")] == ["devkit-dist"]
assert {{e.name for e in importlib.metadata.entry_points(group="devkit.host.services")}} == {({"integration"} if harness else set()) | ({"spec"} if spec else set())!r}
assert CliRunner().invoke(cli, ["host", "mcp", "--help"]).exit_code != 0
"""
        if runtime:
            script += """
from devkit_mcp.services import load_tools
from devkit_mcp.server import build_server
server = build_server(load_tools(Path.cwd()))
assert server.version == importlib.metadata.version("devkit-mcp")
assert CliRunner().invoke(cli, ["mcp", "--help"]).exit_code == 0
"""
        run([str(python), "-c", script], work, env)
        print(f"[MCP_MATRIX: combination={label} result=PASS]", flush=True)


if __name__ == "__main__":
    main()
