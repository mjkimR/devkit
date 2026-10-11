from __future__ import annotations

import difflib
import hashlib
import shutil
from pathlib import Path

from devkit_distribution.bundles import BundleError
from devkit_distribution.bundles.manifest import SLUG, source_files

from .discovery import InstalledBundle
from .sync import read_receipt, sync_project
from .transaction import OVERRIDES, RECEIPT, atomic_write, json_content, project_lock


def _parse_selector(selector: str) -> tuple[str, str]:
    bundle, separator, asset = selector.partition(":")
    if not separator or not bundle or not asset:
        raise BundleError(f"expected bundle:asset selector (e.g. starter:development): {selector}")
    if not SLUG.fullmatch(bundle) or not SLUG.fullmatch(asset):
        raise BundleError(f"bundle and asset must be lowercase slugs: {selector}")
    return bundle, asset


def _find_bundle_and_asset(installed: list[InstalledBundle], bundle_name: str, asset_id: str):
    item = next((b for b in installed if b.bundle.name == bundle_name), None)
    if item is None:
        raise BundleError(f"bundle is not installed: {bundle_name}")
    asset = next((a for a in item.bundle.assets if a.id == asset_id), None)
    if asset is None:
        raise BundleError(f"asset not found in {bundle_name}: {asset_id}")
    return item, asset


def _primary_file(bundle_root: Path, source: str) -> Path:
    path = bundle_root / source
    if path.is_dir():
        skill_entry = path / "SKILL.md"
        if skill_entry.is_file():
            return skill_entry
        files = sorted(source_files(bundle_root, source))
        if files:
            return files[0]
    return path


def create_override(
    root: Path,
    installed: list[InstalledBundle],
    selector: str,
    *,
    force: bool = False,
) -> dict[str, object]:
    root = root.resolve()
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        item, asset = _find_bundle_and_asset(installed, bundle_name, asset_id)
        override_root = root / OVERRIDES / bundle_name
        baseline_root = root / OVERRIDES / ".baseline" / bundle_name
        created_paths: list[str] = []

        for _, source in asset.sources:
            src_path = item.bundle.root / source
            dst_path = override_root / source
            base_path = baseline_root / source

            if dst_path.exists() and not force:
                raise BundleError(f"override already exists: {dst_path.relative_to(root).as_posix()}")

            if src_path.is_dir():
                if dst_path.exists() and force:
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                if base_path.exists() and force:
                    shutil.rmtree(base_path)
                shutil.copytree(src_path, base_path, dirs_exist_ok=True)
                created_paths.append(dst_path.relative_to(root).as_posix())
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                base_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, base_path)
                created_paths.append(dst_path.relative_to(root).as_posix())

    sync_project(root, installed)
    return {
        "bundle": bundle_name,
        "asset": asset_id,
        "paths": created_paths,
    }


def diff_override(
    root: Path,
    installed: list[InstalledBundle],
    selector: str,
) -> dict[str, object]:
    root = root.resolve()
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        item, asset = _find_bundle_and_asset(installed, bundle_name, asset_id)
        source = asset.sources[0][1]
        upstream_file = _primary_file(item.bundle.root, source)
        rel_in_bundle = upstream_file.relative_to(item.bundle.root).as_posix()
        override_file = root / OVERRIDES / bundle_name / rel_in_bundle
        baseline_file = root / OVERRIDES / ".baseline" / bundle_name / rel_in_bundle

        if not override_file.is_file():
            raise BundleError(f"no override found for {selector}")

        try:
            upstream_text = upstream_file.read_text("utf-8")
        except UnicodeError as exc:
            raise BundleError(f"upstream file is not UTF-8: {upstream_file}") from exc

        try:
            override_text = override_file.read_text("utf-8")
        except UnicodeError as exc:
            raise BundleError(f"override file is not UTF-8: {override_file}") from exc

        baseline_text = baseline_file.read_text("utf-8") if baseline_file.is_file() else None

        receipt = read_receipt(root)
        meta = receipt.get("overrides", {}).get(bundle_name, {}).get(asset_id, {})
        baseline_sha = meta.get("baseline_upstream_sha256")
        current_upstream_sha = hashlib.sha256(upstream_file.read_bytes()).hexdigest()
        drift_detected = baseline_sha is not None and baseline_sha != current_upstream_sha

        override_diff = "".join(
            difflib.unified_diff(
                upstream_text.splitlines(keepends=True),
                override_text.splitlines(keepends=True),
                fromfile=f"upstream/{rel_in_bundle}",
                tofile=f"override/{rel_in_bundle}",
            )
        )

        upstream_diff = (
            "".join(
                difflib.unified_diff(
                    baseline_text.splitlines(keepends=True),
                    upstream_text.splitlines(keepends=True),
                    fromfile=f"baseline/{rel_in_bundle}",
                    tofile=f"upstream/{rel_in_bundle}",
                )
            )
            if baseline_text is not None
            else None
        )

        return {
            "bundle": bundle_name,
            "asset": asset_id,
            "relative_path": rel_in_bundle,
            "drift_detected": drift_detected,
            "baseline_upstream_sha256": baseline_sha,
            "current_upstream_sha256": current_upstream_sha,
            "upstream_diff": upstream_diff,
            "diff": override_diff,
        }


def accept_override(
    root: Path,
    installed: list[InstalledBundle],
    selector: str,
) -> dict[str, object]:
    root = root.resolve()
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        item, asset = _find_bundle_and_asset(installed, bundle_name, asset_id)
        source = asset.sources[0][1]
        upstream_file = _primary_file(item.bundle.root, source)
        rel_in_bundle = upstream_file.relative_to(item.bundle.root).as_posix()
        baseline_file = root / OVERRIDES / ".baseline" / bundle_name / rel_in_bundle

        current_upstream_sha = hashlib.sha256(upstream_file.read_bytes()).hexdigest()

        if upstream_file.is_file():
            baseline_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(upstream_file, baseline_file)

        receipt = read_receipt(root)
        if (
            "overrides" in receipt
            and bundle_name in receipt["overrides"]
            and asset_id in receipt["overrides"][bundle_name]
        ):
            receipt["overrides"][bundle_name][asset_id]["baseline_upstream_sha256"] = current_upstream_sha
            atomic_write(root, RECEIPT, json_content(receipt))

        return {
            "bundle": bundle_name,
            "asset": asset_id,
            "accepted_upstream_sha256": current_upstream_sha,
            "status": "up to date",
        }


def remove_override(
    root: Path,
    installed: list[InstalledBundle],
    selector: str,
) -> dict[str, object]:
    root = root.resolve()
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        _bundle, asset = _find_bundle_and_asset(installed, bundle_name, asset_id)
        override_root = root / OVERRIDES / bundle_name
        baseline_root = root / OVERRIDES / ".baseline" / bundle_name

        for _, source in asset.sources:
            dst_path = override_root / source
            base_path = baseline_root / source
            if dst_path.is_dir():
                shutil.rmtree(dst_path)
            elif dst_path.is_file():
                dst_path.unlink()
            if base_path.is_dir():
                shutil.rmtree(base_path)
            elif base_path.is_file():
                base_path.unlink()

        # Clean empty directories up to overrides
        def clean_empty_parents(path: Path, stop: Path) -> None:
            curr = path.parent
            while curr != stop and curr.exists():
                try:
                    curr.rmdir()
                except OSError:
                    break
                curr = curr.parent

        for _, source in asset.sources:
            clean_empty_parents(override_root / source, root / OVERRIDES)
            clean_empty_parents(baseline_root / source, root / OVERRIDES)

    sync_project(root, installed)
    return {
        "bundle": bundle_name,
        "asset": asset_id,
        "status": "removed",
    }


def list_overrides(
    root: Path,
    installed: list[InstalledBundle],
) -> list[dict[str, object]]:
    root = root.resolve()
    with project_lock(root):
        receipt = read_receipt(root)
        overrides = receipt.get("overrides", {})
        installed_map = {item.bundle.name: item.bundle for item in installed}
        results = []

        for b_name, b_assets in sorted(overrides.items()):
            bundle = installed_map.get(b_name)
            for a_id, meta in sorted(b_assets.items()):
                current_sha = None
                if bundle is not None:
                    asset = next((a for a in bundle.assets if a.id == a_id), None)
                    if asset is not None:
                        src = _primary_file(bundle.root, asset.sources[0][1])
                        if src.is_file():
                            current_sha = hashlib.sha256(src.read_bytes()).hexdigest()

                baseline_sha = meta.get("baseline_upstream_sha256")
                results.append(
                    {
                        "bundle": b_name,
                        "asset": a_id,
                        "kind": meta.get("kind"),
                        "relative_path": meta.get("relative_path"),
                        "baseline_upstream_sha256": baseline_sha,
                        "current_upstream_sha256": current_sha,
                        "drift_detected": baseline_sha != current_sha if current_sha and baseline_sha else False,
                    }
                )
        return results
