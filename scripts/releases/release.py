"""Build only changed publication artifacts and verify retained original identities."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .artifacts import git, obtain
from .identity import inventory, require, save, sha
from .install import notes
from .prepare import compute


def release(root: Path, tag: str, baseline_path: Path, repository: str) -> dict:
    version = (root / "VERSION").read_text().strip()
    require(tag == "v" + version, f"{tag} does not match VERSION ({version})")
    committed = json.loads(git(root, "show", f"{tag}:scripts/releases/pending.json"))
    require(committed["state"] == "complete", "tagged plan incomplete")
    source = git(root, "rev-parse", tag + "^{commit}")
    require(git(root, "rev-parse", "HEAD") == source, "build HEAD must match authorized tag")
    require(not git(root, "status", "--porcelain", "--untracked-files=normal"), "release tree must be clean")
    subprocess.run(["uv", "lock", "--check"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(
        ["uv", "run", "--no-active", "python", "scripts/handbook.py", "release-check", tag],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    plan, texts, built = compute(root, baseline_path)
    require(committed == plan, "tagged plan stale")
    for relative, text in texts.items():
        require((root / relative).read_text() == text, "generated release metadata stale")
    inventory(baseline_path)
    output = root / "dist/release"
    output.mkdir(parents=True, exist_ok=True)
    require(not list(output.iterdir()), "release output must be empty; choose a fresh build checkout")
    packages = {}
    for name, entry in plan["packages"].items():
        entry = dict(entry)
        if entry["disposition"] == "changed":
            path = built[name]
            entry["artifact"] = {
                "filename": path.name,
                "sha256": sha(path),
                "url": f"https://github.com/{repository}/releases/download/{tag}/{path.name}",
            }
            shutil.copyfile(path, output / path.name)
        else:
            # Verification downloads to ignored cache, never republishes reused package identities.
            obtain(entry["artifact"], root / "dist/reused-artifacts")
        entry.pop("disposition")
        packages[name] = entry
    extras = {}
    for name, original in plan["extras"].items():
        entry = dict(original)
        if "source_path" in entry:
            path = root / entry.pop("source_path")
            require(sha(path) == entry["artifact"]["sha256"], "model source checksum changed after preparation")
            entry["artifact"] = {
                **entry["artifact"],
                "url": f"https://github.com/{repository}/releases/download/{tag}/{path.name}",
            }
            shutil.copyfile(path, output / path.name)
        else:
            obtain(entry["artifact"], root / "dist/reused-artifacts")
        extras[name] = entry
    data = {
        "schema": 1,
        "kind": "completed",
        "release": version,
        "source_sha": source,
        "recipe": plan["recipe"],
        "packages": packages,
        "extras": extras,
        "baseline_digest": plan["baseline_digest"],
    }
    save(output / "release-inventory.json", data)
    inventory(output / "release-inventory.json")
    # Listing covers all referenced artifacts, including original URLs for reused bytes.
    checksums = {
        entry["artifact"]["filename"]: entry["artifact"]["sha256"] for entry in [*packages.values(), *extras.values()]
    }
    (output / "SHA256SUMS").write_text("".join(f"{checksum}  {name}\n" for name, checksum in sorted(checksums.items())))
    (output.parent / "release-notes.md").write_text(notes(data))
    return data
