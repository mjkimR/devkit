"""Synchronize static release metadata from the workspace's VERSION file."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")


def metadata_updates(root: Path) -> tuple[str, int, dict[Path, str]]:
    """Validate all inputs before returning formatting-preserving metadata updates."""
    version = (root / "VERSION").read_text().strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("VERSION must contain X.Y.Z without leading zeroes")
    workspace = tomllib.loads((root / "pyproject.toml").read_text())["tool"]["uv"]["workspace"]
    excluded = {p for pattern in workspace.get("exclude", []) for p in root.glob(pattern)}
    paths = sorted(
        {p / "pyproject.toml" for pattern in workspace["members"] for p in root.glob(pattern) if p not in excluded}
    )
    if not paths:
        raise ValueError("workspace has no package metadata")
    texts = {p: p.read_text() for p in paths}
    projects = {p: tomllib.loads(content)["project"] for p, content in texts.items()}
    names = "|".join(re.escape(project["name"]) for project in projects.values())
    # Only versioned requirement strings: project names and unversioned extra pass-throughs stay intact.
    requirement = re.compile(
        rf"""(["'])((?:{names})(?:\[[^\]"']+\])?)[ \t]*[<>=!~](?:(?!\1)[^;\r\n])*([ \t]*;(?:(?!\1)[^\r\n])*)?\1"""
    )
    updates: dict[Path, str] = {}
    for path, content in texts.items():
        project = projects[path]
        if not isinstance(project.get("version"), str):
            raise ValueError(f"{path.relative_to(root)} must declare a static project.version")
        # Limit version replacement to [project], never a tool's own version key.
        section = re.search(r"(?ms)^\[project\][^\n]*\n.*?(?=^\[|\Z)", content)
        if section is None:
            raise ValueError(f"{path.relative_to(root)} has no [project] section")
        updated_section, count = re.subn(
            r"""(?m)^(version\s*=\s*)(["'])[^"'\r\n]*\2""",
            lambda match: f"{match[1]}{match[2]}{version}{match[2]}",
            section[0],
        )
        if count != 1:
            raise ValueError(f"{path.relative_to(root)} must declare one project.version")
        updated = content[: section.start()] + updated_section + content[section.end() :]
        updated = requirement.sub(lambda m: f"{m[1]}{m[2]}=={version}{m[3] or ''}{m[1]}", updated)
        if updated != content:
            updates[path] = updated
    return version, len(paths), updates


def error(code: str, message: str, action: str) -> None:
    print(
        f"[ERROR]  ({code}) {message}\n"
        "[ACTION] INPUT_ERROR — Do not retry with identical input. Correct the input or environment before rerunning.\n"
        f"[FIX]    {action}",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check metadata without writing or running uv")
    args = parser.parse_args(argv)
    try:
        version, count, updates = metadata_updates(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error("VERSION_INPUT_INVALID", str(exc), "Set root VERSION to X.Y.Z and verify workspace pyproject.toml files.")
        return 2
    if args.check and updates:
        paths = ", ".join(str(p.relative_to(root)) for p in updates)
        error(
            "VERSION_METADATA_STALE", paths, "Run just version-sync and commit VERSION, package metadata and uv.lock."
        )
        return 1
    if not args.check:
        try:
            for path, content in updates.items():
                path.write_text(content)
            subprocess.run(["uv", "lock"], cwd=root, check=True, stdout=sys.stderr)
        except (OSError, subprocess.CalledProcessError) as exc:
            error("VERSION_SYNC_FAILED", str(exc), "Resolve the write or uv lock failure and rerun just version-sync.")
            return 2
    state = "checked" if args.check else "synced"
    print(f"[VERSION: {version} state={state} packages={count}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
