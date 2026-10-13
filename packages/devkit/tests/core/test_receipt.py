from __future__ import annotations

import copy
import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from devkit.core import CONFIG_PATH, RECEIPT_PATH, ReceiptError, load_receipt, parse_receipt
from devkit.core.receipt import FileRecord, Receipt

SHA_A = hashlib.sha256(b"a").hexdigest()
SHA_B = hashlib.sha256(b"b").hexdigest()


def full_receipt() -> dict[str, Any]:
    """A receipt with every key ``devkit sync`` can write."""
    return {
        "schema": 1,
        "packages": [
            {"package": "team-content", "package_version": "1.2.0", "bundle": "team", "bundle_version": "0.3.0"}
        ],
        "selection": {"agents": ["claude-code", "codex"], "presets": {"team": ["all"]}},
        "assets": [
            {
                "bundle": "team",
                "id": "rules",
                "kind": "rule",
                "paths": [".devkit/managed/team/rules/a.py", ".devkit/managed/team/rules/README.md"],
            },
            {
                "bundle": "team",
                "id": "flow",
                "kind": "workflow",
                "paths": [".devkit/managed/team/flows/flow.md", ".devkit/managed/team/flows/extra.md"],
                "entrypoints": [".devkit/managed/team/flows/flow.md"],
            },
            {"bundle": "team", "id": "docs", "kind": "document", "paths": [], "seeded": ["docs/README.md"]},
            {
                "bundle": "team",
                "id": "check",
                "kind": "workflow-check",
                "paths": [".devkit/overrides/team/checks/c.py"],
            },
        ],
        "files": {
            ".devkit/managed/team/rules/a.py": {"sha256": SHA_A, "mode": 0o644},
            ".claude/skills/x/run.sh": {"sha256": SHA_B, "mode": 0o755},
        },
        "tool": {"package": "devkit", "version": "0.1.0"},
        "overrides": {
            "team": {
                "check": {
                    "kind": "workflow-check",
                    "relative_path": "checks/c.py",
                    "baseline_upstream_sha256": SHA_A,
                    "override_sha256": SHA_B,
                }
            }
        },
        "seeded": [{"bundle": "team", "id": "docs", "path": "docs/README.md"}],
        "guidance_block": SHA_A,
    }


def write(root: Path, data: object) -> None:
    path = root / RECEIPT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


def test_constants() -> None:
    assert RECEIPT_PATH == ".devkit/installation.json"
    assert CONFIG_PATH == ".devkit/config.toml"


def test_missing_receipt_is_none(tmp_path: Path) -> None:
    assert load_receipt(tmp_path) is None


def test_full_receipt_round_trip(tmp_path: Path) -> None:
    write(tmp_path, full_receipt())
    receipt = load_receipt(tmp_path)
    assert receipt is not None
    assert receipt.schema == 1
    assert receipt.packages[0].package == "team-content" and receipt.packages[0].bundle_version == "0.3.0"
    assert receipt.selection.agents == ("claude-code", "codex")
    assert dict(receipt.selection.presets) == {"team": ("all",)}
    assert [a.id for a in receipt.assets()] == ["rules", "flow", "docs", "check"]
    assert [a.id for a in receipt.assets(kind="rule")] == ["rules"]
    assert receipt.assets(kind="gate") == ()
    rules = receipt.assets(kind="rule")[0]
    assert rules.paths == (".devkit/managed/team/rules/a.py", ".devkit/managed/team/rules/README.md")
    assert rules.files(".py") == (".devkit/managed/team/rules/a.py",)
    flow = receipt.assets(kind="workflow")[0]
    assert flow.entrypoints == (".devkit/managed/team/flows/flow.md",)
    assert flow.files(".md") == (".devkit/managed/team/flows/flow.md", ".devkit/managed/team/flows/extra.md")
    assert flow.files() == flow.files(".md")
    docs = receipt.assets(kind="document")[0]
    assert docs.seeded == ("docs/README.md",) and docs.paths == () and docs.entrypoints == ()
    assert receipt.file_hash(".devkit/managed/team/rules/a.py") == SHA_A
    assert receipt.file_hash("nope") is None
    record = receipt.file(".claude/skills/x/run.sh")
    assert record == FileRecord(SHA_B, 0o755)
    assert record is not None and record.matches(b"b") and not record.matches(b"a")
    assert receipt.file("nope") is None
    assert receipt.tool is not None and receipt.tool.package == "devkit"
    override = receipt.overrides["team"]["check"]
    assert override.relative_path == "checks/c.py" and override.override_sha256 == SHA_B
    assert receipt.seeded[0].path == "docs/README.md"
    assert receipt.guidance_block == SHA_A


def test_minimal_receipt_defaults() -> None:
    data = full_receipt()
    for key in ("tool", "overrides", "seeded", "guidance_block"):
        del data[key]
    receipt = parse_receipt(json.dumps(data).encode())
    assert receipt.tool is None and dict(receipt.overrides) == {} and receipt.seeded == ()
    assert receipt.guidance_block is None


def test_receipt_mappings_are_read_only() -> None:
    receipt = parse_receipt(json.dumps(full_receipt()))
    with pytest.raises(TypeError):
        receipt.file_records["x"] = FileRecord(SHA_A, 0o644)  # type: ignore[index]


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("", "invalid JSON"),
        ("{not json", "invalid JSON"),
        ("[]", "receipt: expected an object"),
        ('{"schema": NaN}', "NaN is not valid JSON"),
        ('{"schema": 1, "schema": 1}', "duplicate JSON key 'schema'"),
    ],
)
def test_malformed_content(tmp_path: Path, raw: str, message: str) -> None:
    write(tmp_path, raw)
    with pytest.raises(ReceiptError, match=message):
        load_receipt(tmp_path)


def test_non_utf8_content(tmp_path: Path) -> None:
    path = tmp_path / RECEIPT_PATH
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"schema": "\xff"}')
    with pytest.raises(ReceiptError, match="not UTF-8"):
        load_receipt(tmp_path)


def test_unreadable_receipt(tmp_path: Path) -> None:
    (tmp_path / RECEIPT_PATH).mkdir(parents=True)
    with pytest.raises(ReceiptError, match="cannot be read"):
        load_receipt(tmp_path)


def test_dangling_symlink_is_an_error(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    os.symlink(tmp_path / "gone.json", tmp_path / RECEIPT_PATH)
    with pytest.raises(ReceiptError, match="cannot be read"):
        load_receipt(tmp_path)


def test_duplicate_key_in_a_nested_object() -> None:
    raw = json.dumps(full_receipt()).replace('"bundle": "team", "id": "rules",', '"bundle": "team", "bundle": "x",')
    with pytest.raises(ReceiptError, match="duplicate JSON key 'bundle'"):
        parse_receipt(raw)


def _mutate(path: list[Any], value: Any) -> dict[str, Any]:
    data = copy.deepcopy(full_receipt())
    target: Any = data
    for key in path[:-1]:
        target = target[key]
    if value is KeyError:
        del target[path[-1]]
    else:
        target[path[-1]] = value
    return data


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (["schema"], 2, "unsupported receipt schema 2"),
        (["schema"], True, "unsupported receipt schema True"),
        (["schema"], "1", "unsupported receipt schema '1'"),
        (["schema"], KeyError, r"missing keys \['schema'\]"),
        (["files"], KeyError, r"missing keys \['files'\]"),
        (["extra"], 1, r"unknown keys \['extra'\]"),
        (["packages"], {}, "packages: expected an array"),
        (["packages", 0, "package"], "", "packages\\[0\\].package: expected a nonempty string"),
        (["packages", 0, "bundle"], "Team", "lowercase slug"),
        (["packages", 0, "extra"], "x", "unknown keys"),
        (["selection"], [], "selection: expected an object"),
        (["selection", "agents"], "codex", "selection.agents: expected an array"),
        (["selection", "agents"], [1], "selection.agents\\[0\\]"),
        (["selection", "presets"], [], "selection.presets: expected an object"),
        (["selection", "presets", "team"], "all", "selection.presets.team: expected an array"),
        (["assets"], {}, "assets: expected an array"),
        (["assets", 0], "x", "assets\\[0\\]: expected an object"),
        (["assets", 0, "paths"], KeyError, "missing keys"),
        (["assets", 0, "kind"], 3, "assets\\[0\\].kind: expected a lowercase slug"),
        (["assets", 0, "id"], "Bad Id", "assets\\[0\\].id"),
        (["assets", 0, "paths"], "a.py", "expected an array"),
        (["assets", 0, "paths"], [1], "expected a path string"),
        (["assets", 0, "paths"], ["/abs/a.py"], "unsafe path"),
        (["assets", 0, "paths"], ["../a.py"], "unsafe path"),
        (["assets", 0, "paths"], ["..\\a.py"], "unsafe path"),
        (["assets", 0, "paths"], ["a//b.py"], "canonical"),
        (["assets", 1, "entrypoints"], ["../flow.md"], "assets\\[1\\].entrypoints\\[0\\]: unsafe path"),
        (["assets", 2, "seeded"], ["/docs"], "assets\\[2\\].seeded\\[0\\]: unsafe path"),
        (["files"], [], "files: expected an object"),
        (["files", "../x"], {"sha256": SHA_A, "mode": 420}, "files: unsafe path"),
        (["files", ".devkit/managed/team/rules/a.py", "sha256"], "ABC", "lowercase hex SHA-256"),
        (["files", ".devkit/managed/team/rules/a.py", "mode"], 0o600, "expected 420"),
        (["files", ".devkit/managed/team/rules/a.py", "mode"], 420.0, "expected 420"),
        (["files", ".devkit/managed/team/rules/a.py", "extra"], 1, "unknown keys"),
        (["tool"], {"package": "x"}, "missing keys"),
        (["tool", "version"], "", "tool.version"),
        (["overrides"], [], "overrides: expected an object"),
        (["overrides", "team"], [], "overrides.team: expected an object"),
        (["overrides", "Bad"], {}, "overrides: expected a lowercase slug"),
        (["overrides", "team", "check", "relative_path"], "../c.py", "unsafe path"),
        (["overrides", "team", "check", "override_sha256"], "x", "SHA-256"),
        (["seeded"], {}, "seeded: expected an array"),
        (["seeded", 0, "path"], "/etc/x", "seeded\\[0\\].path: unsafe path"),
        (["guidance_block"], "nothex", "guidance_block"),
    ],
)
def test_schema_violations(path: list[Any], value: Any, message: str) -> None:
    with pytest.raises(ReceiptError, match=message):
        parse_receipt(json.dumps(_mutate(path, value)))


def test_backslash_inside_a_file_name_is_accepted() -> None:
    data = full_receipt()
    data["assets"][0]["paths"] = [".devkit/managed/team/rules/odd\\name.py"]
    receipt = parse_receipt(json.dumps(data))
    assert receipt.assets()[0].paths == (".devkit/managed/team/rules/odd\\name.py",)


def test_verified_asset_file_checks_recorded_hashes_and_snapshot_fallback(tmp_path: Path) -> None:
    from devkit.core import AssetFileError, AssetRecord, verified_asset_file

    def receipt_for(files: dict[str, bytes]) -> Receipt:
        return parse_receipt(
            json.dumps(
                {
                    "schema": 1,
                    "packages": [],
                    "selection": {"agents": [], "presets": {}},
                    "assets": [],
                    "files": {k: {"sha256": hashlib.sha256(v).hexdigest(), "mode": 420} for k, v in files.items()},
                }
            )
        )

    asset = AssetRecord("team", "rules", "rule", ())
    managed, override = ".devkit/managed/team/r.py", ".devkit/overrides/team/o.py"
    (tmp_path / ".devkit/managed/team").mkdir(parents=True)
    (tmp_path / ".devkit/overrides/team").mkdir(parents=True)
    (tmp_path / managed).write_bytes(b"x = 1\n")
    (tmp_path / override).write_bytes(b"y = 2\n")
    receipt = receipt_for({managed: b"x = 1\n"})
    assert verified_asset_file(tmp_path, managed, receipt, asset) == tmp_path / managed
    assert verified_asset_file(tmp_path, override, receipt, asset) == tmp_path / override  # unrecorded: as is

    (tmp_path / managed).write_bytes(b"x = 2\n")
    with pytest.raises(AssetFileError, match="differs from the hash") as info:
        verified_asset_file(tmp_path, managed, receipt, asset)
    assert info.value.code == "ASSET_FILE_INVALID" and info.value.target_files == (managed,)
    assert info.value.fix is not None and "devkit override create team:rules" in info.value.fix

    with pytest.raises(AssetFileError, match=r"is missing$"):
        verified_asset_file(tmp_path, ".devkit/managed/team/gone.py", receipt, asset)

    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (tmp_path / managed).write_bytes(b"x = 1\n")
    assert verified_asset_file(snapshot, managed, receipt, asset, source_root=tmp_path) == tmp_path / managed
    with pytest.raises(AssetFileError, match="no hash in the receipt"):
        verified_asset_file(snapshot, override, receipt, asset, source_root=tmp_path)
    with pytest.raises(AssetFileError, match="missing from the working tree"):
        verified_asset_file(snapshot, ".devkit/managed/team/gone.py", receipt, asset, source_root=tmp_path)

    (tmp_path / ".devkit/managed/team/link.py").symlink_to(tmp_path.parent / "elsewhere.py")
    with pytest.raises(AssetFileError, match="unsafe"):
        verified_asset_file(tmp_path, ".devkit/managed/team/link.py", receipt, asset)


def _plugin_receipt(assets: list[dict[str, Any]], files: dict[str, bytes]) -> Receipt:
    return parse_receipt(
        json.dumps(
            {
                "schema": 1,
                "packages": [],
                "selection": {"agents": [], "presets": {}},
                "assets": assets,
                "files": {
                    rel: {"sha256": hashlib.sha256(data).hexdigest(), "mode": 420} for rel, data in files.items()
                },
            }
        )
    )


def _place(root: Path, files: dict[str, bytes]) -> None:
    for rel, data in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(data)


def test_verified_asset_packages_maps_every_module_of_an_asset_whatever_its_name(tmp_path: Path) -> None:
    from devkit.core import verified_asset_packages

    base = ".devkit/managed/team/rules/x"
    files = {
        f"{base}/_helpers.py": b"a = 1\n",
        f"{base}/entry.py": b"b = 2\n",
        f"{base}/sub/__init__.py": b"",
        f"{base}/sub/deep.py": b"",
        f"{base}/notes.md": b"# notes\n",
        f"{base}/tests/test_entry.py": b"",
        f"{base}/test_entry.py": b"",
    }
    _place(tmp_path, files)
    receipt = _plugin_receipt(
        [
            {"bundle": "team", "id": "x", "kind": "rule", "paths": sorted(files)},
            {"bundle": "team", "id": "g", "kind": "gate", "paths": [f"{base}/entry.py"]},
        ],
        files,
    )
    packages, errors = verified_asset_packages(tmp_path, receipt, "rule")
    assert errors == ()
    (package,) = packages
    assert package.root == tmp_path / base
    assert package.key == f"{(tmp_path / '.devkit/managed/team').as_posix()}:x"
    assert {name: path.relative_to(tmp_path / base).as_posix() for name, path in package.modules.items()} == {
        "_helpers": "_helpers.py",  # never skipped for its name
        "entry": "entry.py",
        "sub": "sub/__init__.py",
        "sub.deep": "sub/deep.py",
    }  # test files are never modules, so they are not verified either
    gates, _ = verified_asset_packages(tmp_path, receipt, "gate")
    assert list(gates[0].modules) == ["entry"]


def test_verified_asset_packages_mixes_overrides_managed_and_snapshot_sources(tmp_path: Path) -> None:
    from devkit.core import verified_asset_packages

    managed = {
        ".devkit/managed/team/rules/x/rule.py": b"r = 1\n",
        ".devkit/managed/team/rules/x/helpers.py": b"h = 1\n",
    }
    override = ".devkit/overrides/team/rules/x/helpers.py"
    _place(tmp_path, {**managed, override: b"h = 2\n"})
    receipt = _plugin_receipt(
        [{"bundle": "team", "id": "x", "kind": "rule", "paths": [override, ".devkit/managed/team/rules/x/rule.py"]}],
        managed,
    )
    (package,), errors = verified_asset_packages(tmp_path, receipt, "rule")
    assert errors == ()
    assert dict(package.modules) == {
        "helpers": tmp_path / override,
        "rule": tmp_path / ".devkit/managed/team/rules/x/rule.py",
    }

    snapshot = tmp_path / "snapshot"
    _place(snapshot, {override: b"h = 2\n"})  # managed copies are Git-ignored: only the override is in the snapshot
    (package,), errors = verified_asset_packages(snapshot, receipt, "rule", source_root=tmp_path)
    assert errors == ()
    assert dict(package.modules) == {
        "helpers": snapshot / override,
        "rule": tmp_path / ".devkit/managed/team/rules/x/rule.py",
    }
    assert package.root == snapshot / ".devkit/managed/team/rules/x"


def test_verified_asset_packages_drops_a_package_with_an_unusable_file(tmp_path: Path) -> None:
    from devkit.core import verified_asset_packages

    a, b = ".devkit/managed/team/a/ok.py", ".devkit/managed/team/b/ok.py"
    files = {a: b"", b: b""}
    _place(tmp_path, files)
    receipt = _plugin_receipt(
        [
            {"bundle": "team", "id": "a", "kind": "rule", "paths": [a]},
            {"bundle": "team", "id": "b", "kind": "rule", "paths": [b, ".devkit/managed/team/b/gone.py"]},
        ],
        files,
    )
    packages, errors = verified_asset_packages(tmp_path, receipt, "rule")
    assert [p.root for p in packages] == [tmp_path / ".devkit/managed/team/a"]
    assert [(e.code, e.target_files) for e in errors] == [("ASSET_FILE_INVALID", (".devkit/managed/team/b/gone.py",))]


def test_verified_asset_packages_reports_two_files_for_one_module(tmp_path: Path) -> None:
    from devkit.core import verified_asset_packages

    files = {".devkit/managed/team/x/a.py": b"", ".devkit/managed/team/x/a/__init__.py": b""}
    _place(tmp_path, files)
    receipt = _plugin_receipt([{"bundle": "team", "id": "x", "kind": "rule", "paths": sorted(files)}], files)
    packages, errors = verified_asset_packages(tmp_path, receipt, "rule")
    assert packages == ()
    assert "both define module a" in errors[0].message and errors[0].code == "ASSET_FILE_INVALID"


def test_deeply_nested_json_is_a_receipt_error() -> None:
    with pytest.raises(ReceiptError, match="nested too deeply"):
        parse_receipt("[" * 100_000 + "]" * 100_000)


def test_an_unsearchable_devkit_directory_is_a_receipt_error(tmp_path: Path, lock: Callable[[Path], None]) -> None:
    write(tmp_path, full_receipt())
    lock(tmp_path / ".devkit")
    with pytest.raises(ReceiptError, match="cannot be read"):
        load_receipt(tmp_path)


def _hashed_receipt(files: dict[str, bytes]) -> Receipt:
    return parse_receipt(
        json.dumps(
            {
                "schema": 1,
                "packages": [],
                "selection": {"agents": [], "presets": {}},
                "assets": [],
                "files": {k: {"sha256": hashlib.sha256(v).hexdigest(), "mode": 420} for k, v in files.items()},
            }
        )
    )


def test_only_a_project_override_loads_without_a_recorded_hash(tmp_path: Path) -> None:
    from devkit.core import AssetFileError, AssetRecord, verified_asset_file

    asset = AssetRecord("team", "rules", "rule", ())
    managed, override = ".devkit/managed/team/r.py", ".devkit/overrides/team/o.py"
    for rel in (managed, override):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes(b"x = 1\n")
    receipt = _hashed_receipt({})
    assert verified_asset_file(tmp_path, override, receipt, asset) == tmp_path / override
    with pytest.raises(AssetFileError, match=r"r\.py has no hash in the receipt") as info:
        verified_asset_file(tmp_path, managed, receipt, asset)
    assert info.value.target_files == (managed,)


def test_an_unreadable_asset_file_is_reported_per_file(tmp_path: Path, lock: Callable[[Path], None]) -> None:
    from devkit.core import verified_asset_packages

    good, locked = ".devkit/managed/team/good.py", ".devkit/managed/team/locked.py"
    for rel in (good, locked):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes(b"x = 1\n")
    data = full_receipt()
    data["assets"] = [{"bundle": "team", "id": "r", "kind": "rule", "paths": [locked, good]}]
    data["files"] = {rel: {"sha256": hashlib.sha256(b"x = 1\n").hexdigest(), "mode": 420} for rel in (good, locked)}
    data.pop("overrides", None)
    data.pop("seeded", None)
    lock(tmp_path / locked)
    packages, errors = verified_asset_packages(tmp_path, parse_receipt(json.dumps(data)), "rule")
    assert packages == ()  # a package with an unusable file is not loaded
    assert [(e.code, e.target_files) for e in errors] == [("ASSET_FILE_INVALID", (locked,))]
    assert "locked.py cannot be read" in errors[0].message


def test_a_symlink_loop_in_an_asset_path_is_reported_per_file(tmp_path: Path) -> None:
    from devkit.core import AssetFileError, AssetRecord, verified_asset_file

    team = tmp_path / ".devkit/managed/team"
    team.mkdir(parents=True)
    (team / "loop").symlink_to(team / "loop2")
    (team / "loop2").symlink_to(team / "loop")
    item = ".devkit/managed/team/loop/x.py"
    with pytest.raises(AssetFileError, match="is unsafe: path cannot be resolved") as info:
        verified_asset_file(tmp_path, item, _hashed_receipt({item: b""}), AssetRecord("team", "r", "rule", ()))
    assert info.value.target_files == (item,)
