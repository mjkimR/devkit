"""Verified originals, explicit lockstep bootstrap and immutable upload retries."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version

from .errors import ArtifactError
from .identity import RECIPE, VERSION, consistent, inventory, require, save, seal, sha, wheel


def obtain(artifact: dict, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / artifact["filename"]
    if not path.exists():
        with urllib.request.urlopen(artifact["url"]) as response:
            path.write_bytes(response.read())
    if sha(path) != artifact["sha256"]:
        raise ArtifactError("artifact checksum mismatch: " + artifact["filename"])
    return path


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], cwd=root, text=True).strip()


def bootstrap(root: Path, tag: str, source: str, artifacts: Path, output: Path, repository: str) -> dict:
    require(tag.startswith("v") and VERSION.fullmatch(tag[1:]), "bootstrap tag must be vX.Y.Z")
    source_sha = git(root, "rev-parse", source + "^{commit}")
    require(git(root, "rev-parse", tag + "^{commit}") == source_sha, "bootstrap source does not match tag")
    release = tag[1:]
    require(git(root, "show", f"{source}:VERSION") == release, "historical VERSION/tag mismatch")
    sums = {}
    for line in (artifacts / "SHA256SUMS").read_text().splitlines():
        checksum, filename = line.split(maxsplit=1)
        filename = filename.lstrip("*")
        require(filename == Path(filename).name and filename not in sums, "invalid checksum filename")
        sums[filename] = checksum

    def original(filename: str) -> dict:
        require(filename in sums, "original checksum missing: " + filename)
        path = artifacts / filename
        require(path.exists() and sha(path) == sums[filename], "original missing/corrupt: " + filename)
        return {
            "filename": filename,
            "url": f"https://github.com/{repository}/releases/download/{tag}/{filename}",
            "sha256": sums[filename],
        }

    workspace = tomllib.loads(git(root, "show", f"{source}:pyproject.toml"))["tool"]["uv"]["workspace"]
    import fnmatch

    files = git(root, "ls-tree", "-r", "--name-only", source).splitlines()
    packages = {}
    for relative in files:
        if not relative.endswith("/pyproject.toml"):
            continue
        parent = str(Path(relative).parent)
        if not any(fnmatch.fnmatchcase(parent, pattern) for pattern in workspace["members"]) or any(
            fnmatch.fnmatchcase(parent, pattern) for pattern in workspace.get("exclude", [])
        ):
            continue
        project = tomllib.loads(git(root, "show", f"{source}:{relative}"))["project"]
        name = canonicalize_name(project["name"])
        require(project["version"] == release and name not in packages, "baseline is not one lockstep release")

        candidates = [
            filename
            for filename in sums
            if filename.endswith(".whl") and parse_wheel_filename(filename)[:2] == (name, Version(release))
        ]
        require(len(candidates) == 1, "expected one original wheel identity: " + name)
        filename = candidates[0]
        artifact = original(filename)
        manifest_paths = {}
        for bundle_name, module in project.get("entry-points", {}).get("devkit.bundles", {}).items():
            manifest = module.replace(".", "/") + "/bundle/bundle.toml"
            historical = tomllib.loads(git(root, "show", f"{source}:{parent}/src/{manifest}"))
            require(historical["version"] == release, "historical bundle version mismatch")
            manifest_paths[bundle_name] = manifest
        fingerprint, requires = wheel(artifacts / filename, name, release, set(manifest_paths.values()))
        # Extract only the verified original wheel to read its registered bundle enumeration.
        import zipfile

        from .identity import bundles

        snapshot = root / "dist/selective-probes" / ("bootstrap-" + source_sha) / name
        snapshot.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(artifacts / filename) as archive:
            for member in archive.infolist():
                if member.filename.endswith("/"):
                    continue
                target = snapshot / "src" / member.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(member))
                target.chmod((member.external_attr >> 16) & 0o777 or 0o644)
        (snapshot / "pyproject.toml").write_text(git(root, "show", f"{source}:{relative}"))
        bundle_data = bundles(snapshot / "pyproject.toml")
        for value in bundle_data.values():
            require(value["version"] == release, "original/source bundle identity mismatch")
        # Compare all source runtime/optional requirements, even inactive ones, with wheel metadata.
        from .identity import requirements

        source_reqs = {str(Requirement(r)) for r in requirements(project)}
        wheel_reqs = {str(Requirement(r)) for r in requires}
        # Optional requirements add an extra marker in core metadata; verify their pins through consistent().
        for raw in project.get("dependencies", []):
            require(str(Requirement(raw)) in wheel_reqs, "original/source dependency mismatch")
        require(
            all(
                str(Requirement(r).specifier) in {str(Requirement(s).specifier) for s in source_reqs} for r in requires
            ),
            "original/source optional dependency mismatch",
        )
        packages[name] = {
            "path": parent,
            "version": release,
            "fingerprint": fingerprint,
            "requires": requires,
            "bundles": bundle_data,
            "artifact": artifact,
        }
    require(packages, "historical workspace has no packages")
    extras = {}
    for relative in files:
        if relative.startswith("models/") and relative.endswith(".whl"):
            filename = Path(relative).name
            artifact = original(filename)

            name, version, _, _ = parse_wheel_filename(filename)
            # The historical source's committed model bytes must match the original release artifact.
            original_bytes = subprocess.check_output(["git", "-C", str(root), "show", f"{source}:{relative}"], cwd=root)

            require(hashlib.sha256(original_bytes).hexdigest() == artifact["sha256"], "model source/artifact mismatch")
            extras[name] = {"version": str(version), "artifact": artifact}
    data = {
        "schema": 1,
        "kind": "completed",
        "release": release,
        "source_sha": source_sha,
        "recipe": RECIPE,
        "packages": packages,
        "extras": extras,
        "bootstrap": {"tag": tag, "source_sha": source_sha, "checksums_sha256": sha(artifacts / "SHA256SUMS")},
    }
    consistent(packages)
    save(output, data)
    inventory(output)
    return seal(data)


def publish(directory: Path, tag: str, *, root: Path) -> None:
    """gh performs transport only; existing asset bytes must match before any upload."""
    data = inventory(directory / "release-inventory.json")
    require(tag == "v" + data["release"], "publish tag/inventory mismatch")
    require(git(root, "rev-parse", tag + "^{commit}") == data["source_sha"], "publish tag/source mismatch")
    subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", data["source_sha"], "origin/main"], cwd=root, check=True
    )
    expected = {
        a["artifact"]["filename"]: a["artifact"]["sha256"]
        for a in [*data["packages"].values(), *data["extras"].values()]
        if urlparse(a["artifact"]["url"]).path.split("/")[-2] == tag
    }
    require(
        set(p.name for p in directory.iterdir()) == {*expected, "SHA256SUMS", "release-inventory.json"},
        "unexpected/missing local release assets",
    )
    for filename, checksum in expected.items():
        require(sha(directory / filename) == checksum, "local artifact checksum mismatch: " + filename)
    listed = {}
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        checksum, filename = line.split(maxsplit=1)
        require(filename not in listed, "duplicate release checksum entry")
        listed[filename] = checksum
    all_artifacts = {
        entry["artifact"]["filename"]: entry["artifact"]["sha256"]
        for entry in [*data["packages"].values(), *data["extras"].values()]
    }
    require(listed == all_artifacts, "checksum listing does not match complete inventory")
    expected["SHA256SUMS"] = sha(directory / "SHA256SUMS")
    expected["release-inventory.json"] = sha(directory / "release-inventory.json")
    info = subprocess.run(
        ["gh", "release", "view", tag, "--json", "assets,isDraft"], cwd=root, capture_output=True, text=True
    )
    if info.returncode:
        # Creation failures (including an existing inaccessible release) propagate, never overwrite.
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                tag,
                "--verify-tag",
                "--draft",
                "--title",
                tag,
                "--notes-file",
                str(directory.parent / "release-notes.md"),
            ],
            cwd=root,
            check=True,
        )
        assets = []
    else:
        assets = json.loads(info.stdout)["assets"]
    existing = {a["name"]: a for a in assets}
    require(not (existing.keys() - expected.keys()), "unexpected remote release assets")
    for filename in existing:
        result = subprocess.check_output(
            ["gh", "release", "download", tag, "--pattern", filename, "--output", "-"], cwd=root
        )

        require(hashlib.sha256(result).hexdigest() == expected[filename], "existing remote asset mismatch: " + filename)
    # Verify the entire existing set before uploading anything. Completed inventory is always last.
    order = [*sorted(set(expected) - {"release-inventory.json"}), "release-inventory.json"]
    for filename in order:
        if filename not in existing:
            subprocess.run(["gh", "release", "upload", tag, str(directory / filename)], cwd=root, check=True)
            uploaded = subprocess.check_output(
                ["gh", "release", "download", tag, "--pattern", filename, "--output", "-"], cwd=root
            )
            require(
                hashlib.sha256(uploaded).hexdigest() == expected[filename],
                "uploaded asset checksum mismatch: " + filename,
            )
    subprocess.run(["gh", "release", "edit", tag, "--draft=false"], cwd=root, check=True)
