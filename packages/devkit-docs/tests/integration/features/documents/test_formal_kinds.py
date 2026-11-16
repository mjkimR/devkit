"""Formal role contracts through real index, CLI, rules and namespace boundaries."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.rules.services.testing import check, write_files
from devkit_dist.cli import cli
from devkit_dist.features.search import SearchMode

from devkit_docs.features.documents import DocumentIndex, Kind
from devkit_docs.features.documents.usecases.search import search_documents
from devkit_docs.features.governance.services.entrypoint_paths import entrypoint_bearing
from devkit_docs.features.governance.usecases.code_entrypoints import CodeEntrypointsRule
from devkit_docs.features.governance.usecases.document_reference import DocumentReferenceRule
from devkit_docs.features.governance.usecases.document_summary import DocumentSummaryRule
from devkit_docs.features.governance.usecases.id_convention import IdConventionRule
from devkit_docs.features.governance.usecases.spec_format import SpecFormatRule

ROLES = [("designs", "DESIGN", Kind.DESIGN), ("domain", "DOMAIN", Kind.DOMAIN), ("operations", "OPS", Kind.OPERATIONS)]


def doc(identifier: str, extra: str = "", body: str = "", status: str = "active") -> str:
    return f'---\nid: {identifier}\ntitle: Sample\nstatus: {status}\nsummary: "Sample formal role concepts and mechanisms."\n{extra}---\n# [{identifier}] Sample\n{body}'


def invoke(root: Path, *args: str) -> dict:
    result = CliRunner().invoke(cli, ["docs", *args, "--format", "json", "-w", str(root)])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_real_role_discovery_alias_refs_history_and_memo(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    identifier = f"{prefix}-sample"
    path = f"docs/{directory}/{identifier}.md"
    files = {
        path: doc(identifier, f"aliases: [{prefix}-old]\n", status="retired"),
        "docs/designs/DESIGN-reader.md": doc(
            "DESIGN-reader",
            f"related_{({'OPS': 'operations', 'DOMAIN': 'domains', 'DESIGN': 'designs'})[prefix]}: [{prefix}-old]\n",
            f"`{identifier}`\n",
        ),
    }
    write_files(tmp_path, files)
    index = DocumentIndex.load(tmp_path)
    assert index.resolve(f"{prefix}-old").id == identifier
    assert index.resolve(identifier).kind is kind
    assert set(index.resolve(identifier).to_dict()) == {"id", "kind", "path", "status", "title", "area", "summary"}
    assert index.resolve(identifier).to_dict()["kind"] == str(kind)
    assert identifier not in [d["id"] for d in invoke(tmp_path, "list", str(kind))["documents"]]
    assert identifier in [d["id"] for d in invoke(tmp_path, "list", str(kind), "--history")["documents"]]
    assert identifier in [d["id"] for d in invoke(tmp_path, "list", str(kind), "--status", "retired")["documents"]]
    assert invoke(tmp_path, "resolve", f"{prefix}-old")["documents"][0]["id"] == identifier
    refs = invoke(tmp_path, "refs", identifier, "--direction", "in")
    assert "DESIGN-reader" in str(refs)
    hits = search_documents(index, identifier, mode=SearchMode.LEXICAL, history=True).hits
    assert hits[0].document.id == identifier and hits[0].pinned
    assert not check(DocumentSummaryRule(), tmp_path)
    assert not check(SpecFormatRule(), tmp_path)
    # Memo reload retains the new enum and every new structured relation.
    assert DocumentIndex.load(tmp_path).resolve(identifier).kind is kind
    assert not [v for v in check(DocumentReferenceRule(), tmp_path, fix=True) if not v.fixed]
    assert f"[{identifier}]" in (tmp_path / "docs/designs/DESIGN-reader.md").read_text()


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_global_and_namespace_schema_and_negative_controls(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    del kind
    global_path = f"docs/{directory}/{prefix}-global.md"
    package_path = f"docs/packages/api/{directory}/{prefix}-package.md"
    config = '[[tool.docs.namespaces]]\nname = "api"\npath = "packages/api"\n'
    files = {
        global_path: doc(f"{prefix}-global"),
        package_path: doc(f"{prefix}-package"),
        ".devkit/config.toml": config,
    }
    for rule in [IdConventionRule(), SpecFormatRule(), DocumentSummaryRule(), DocumentReferenceRule()]:
        assert not check(rule, tmp_path, files)
    assert len(invoke(tmp_path, "list", "--namespace", "api")["documents"]) == 2
    for replacement in ["status: unknown", "status: 3", "status: ''"]:
        bad = files[global_path].replace("status: active", replacement)
        assert check(SpecFormatRule(), tmp_path, {global_path: bad})
    for field in ["area", "proposal", "decomposed_from", "depends_on", "milestone", "supersedes", "superseded_by"]:
        assert check(SpecFormatRule(), tmp_path, {global_path: doc(f"{prefix}-global", f"{field}: anything\n")})
    assert check(
        SpecFormatRule(),
        tmp_path,
        {
            global_path: doc(f"{prefix}-global").replace(
                'summary: "Sample formal role concepts and mechanisms."', "summary: unquoted"
            )
        },
    )
    assert check(
        IdConventionRule(),
        tmp_path,
        {global_path: doc(f"{prefix}-global").replace(f"# [{prefix}-global] Sample", "# Sample")},
    )
    assert check(IdConventionRule(), tmp_path, {f"docs/{directory}/nested/{prefix}-nested.md": doc(f"{prefix}-nested")})
    assert check(IdConventionRule(), tmp_path, {f"docs/{directory}/{prefix}-123.md": doc(f"{prefix}-123")})
    assert check(IdConventionRule(), tmp_path, {f"docs/elsewhere/{prefix}-outside.md": doc(f"{prefix}-outside")})


@pytest.mark.parametrize(
    "field,target", [("related_designs", "DESIGN"), ("related_domains", "DOMAIN"), ("related_operations", "OPS")]
)
def test_typed_relations_on_existing_kinds_reject_shape_prefix_duplicate_missing(
    tmp_path: Path, field: str, target: str
) -> None:
    destination = {"DESIGN": "designs", "DOMAIN": "domain", "OPS": "operations"}[target]
    base = {f"docs/{destination}/{target}-target.md": doc(f"{target}-target")}
    for value in ["scalar", "{}", "[12]", "[UC-wrong]", f"[{target}-missing]", f"[{target}-target, {target}-target]"]:
        files = {**base, "docs/architecture/ARCH-reader.md": doc("ARCH-reader", f"{field}: {value}\n")}
        assert check(DocumentReferenceRule(), tmp_path, files)
    assert not check(
        DocumentReferenceRule(),
        tmp_path,
        {**base, "docs/architecture/ARCH-reader.md": doc("ARCH-reader", f"{field}: [{target}-target]\n")},
    )


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_parent_owned_artifact_exception_is_narrow(tmp_path: Path, directory: str, prefix: str, kind: Kind) -> None:
    del kind
    parent = f"{prefix}-parent"
    owner = f"docs/{directory}/{parent}.md"
    artifact = f"docs/{directory}/{parent}/artifacts/data.md"
    files = {
        owner: doc(parent),
        artifact: f"# Data\nSupport for `{parent}`.\n",
        f"docs/{directory}/{parent}/artifacts/data.csv": "a,b\n1,2\n",
    }
    assert not check(IdConventionRule(), tmp_path, files)
    assert not check(SpecFormatRule(), tmp_path)
    assert check(IdConventionRule(), tmp_path, {artifact: doc(f"{prefix}-intruder")})
    assert check(IdConventionRule(), tmp_path, {artifact: "# Data\nNo owner here.\n"})
    assert check(
        IdConventionRule(), tmp_path, {f"docs/{directory}/{prefix}-orphan/artifacts/data.md": f"{prefix}-orphan\n"}
    )
    assert check(IdConventionRule(), tmp_path, {f"docs/{directory}/nested/detail.md": "# Independent question\n"})


def test_design_entrypoints_are_optional_safe_and_canonical(tmp_path: Path) -> None:
    path = "docs/designs/DESIGN-source.md"
    files = {path: doc("DESIGN-source", "entrypoints: [src/file.py]\n"), "src/file.py": "x = 1\n"}
    assert not check(CodeEntrypointsRule(), tmp_path, files)
    assert "DESIGN-source" in str(invoke(tmp_path, "list", "--file", "src/file.py"))
    for role_path in [path, "docs/packages/api/designs/DESIGN-source.md"]:
        assert entrypoint_bearing(role_path)
    for role_path in [
        "docs/designs/README.md",
        "docs/designs/DESIGN-source/artifacts/data.md",
        "docs/domain/DOMAIN-source.md",
        "docs/operations/OPS-source.md",
    ]:
        assert not entrypoint_bearing(role_path)
    for declaration in ["../escape", "/absolute", "src/missing.py"]:
        assert check(
            CodeEntrypointsRule(),
            tmp_path,
            {path: doc("DESIGN-source", f"entrypoints: [{declaration}]\n", status="retired")},
        )
    for directory, prefix in [("domain", "DOMAIN"), ("operations", "OPS")]:
        assert check(
            SpecFormatRule(),
            tmp_path,
            {f"docs/{directory}/{prefix}-source.md": doc(f"{prefix}-source", "entrypoints: []\n")},
        )


@pytest.mark.parametrize("root", ["docs", "docs/packages/api"])
def test_artifact_rename_root_move_split_and_reclassification(tmp_path: Path, root: str) -> None:
    """Composed authored states retain one owner and usable relative data destinations."""
    config = '[[tool.docs.namespaces]]\nname = "api"\npath = "packages/api"\n'
    parent = f"{root}/designs/DESIGN-original.md"
    artifact = f"{root}/designs/DESIGN-original/artifacts/data.csv"
    write_files(
        tmp_path,
        {
            ".devkit/config.toml": config,
            parent: doc("DESIGN-original", body="[Data](DESIGN-original/artifacts/data.csv)\n"),
            artifact: "a,b\n1,2\n",
        },
    )
    assert not check(IdConventionRule(), tmp_path)
    # A same-kind rename carries support; the former ID is identity only.
    renamed = tmp_path / root / "designs/DESIGN-renamed.md"
    renamed.write_text(
        doc("DESIGN-renamed", "aliases: [DESIGN-original]\n", "[Data](DESIGN-renamed/artifacts/data.csv)\n")
    )
    (tmp_path / parent).unlink()
    (tmp_path / root / "designs/DESIGN-original").rename(tmp_path / root / "designs/DESIGN-renamed")
    assert not check(IdConventionRule(), tmp_path)
    assert DocumentIndex.load(tmp_path).resolve("DESIGN-original").id == "DESIGN-renamed"
    assert (renamed.parent / "DESIGN-renamed/artifacts/data.csv").read_text() == "a,b\n1,2\n"
    # Move roots without changing identity, then split support into an independent detail.
    other = "docs/packages/api" if root == "docs" else "docs"
    dest = tmp_path / other / "designs"
    dest.mkdir(parents=True, exist_ok=True)
    renamed.rename(dest / renamed.name)
    (tmp_path / root / "designs/DESIGN-renamed").rename(dest / "DESIGN-renamed")
    assert not check(IdConventionRule(), tmp_path)
    (dest / "DESIGN-detail.md").write_text(doc("DESIGN-detail", body="[Data](DESIGN-detail/artifacts/data.csv)\n"))
    (dest / "DESIGN-renamed/artifacts/data.csv").rename(dest / "DESIGN-renamed/artifacts/split.csv")
    detail_artifacts = dest / "DESIGN-detail/artifacts"
    detail_artifacts.mkdir(parents=True)
    (dest / "DESIGN-renamed/artifacts/split.csv").rename(detail_artifacts / "data.csv")
    (dest / "DESIGN-renamed.md").write_text(
        doc("DESIGN-renamed", "aliases: [DESIGN-original]\nrelated_designs: [DESIGN-detail]\n")
    )
    assert not check(IdConventionRule(), tmp_path)
    # Cross-kind transfer retains retired predecessor; no cross-prefix aliases.
    ops = tmp_path / other / "operations"
    (ops / "OPS-detail/artifacts").mkdir(parents=True)
    (detail_artifacts / "data.csv").rename(ops / "OPS-detail/artifacts/data.csv")
    (ops / "OPS-detail.md").write_text(doc("OPS-detail", body="[Data](OPS-detail/artifacts/data.csv)\n"))
    (dest / "DESIGN-detail.md").write_text(
        doc("DESIGN-detail", "related_operations: [OPS-detail]\n", "Reclassified as `OPS-detail`.\n", status="retired")
    )
    assert not check(IdConventionRule(), tmp_path)
    assert not check(SpecFormatRule(), tmp_path)
    assert not check(DocumentReferenceRule(), tmp_path)
    assert (ops / "OPS-detail/artifacts/data.csv").read_text() == "a,b\n1,2\n"


def test_retired_design_is_checked_when_only_source_deletion_is_staged(tmp_path: Path) -> None:
    import subprocess

    from devkit_agt.features.rules import RuleContext, evaluate_rules, git_snapshot

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "Test")
    path = "docs/designs/DESIGN-source.md"
    write_files(
        tmp_path, {path: doc("DESIGN-source", "entrypoints: [src/run.py]\n", status="retired"), "src/run.py": "x = 1\n"}
    )
    git("add", "-A")
    git("commit", "-qm", "base")
    git("rm", "-q", "src/run.py")
    snapshot = git_snapshot(tmp_path, staged=True)
    assert snapshot.deleted == ("src/run.py",) or list(snapshot.deleted) == ["src/run.py"]
    ctx = RuleContext(workspace_root=tmp_path, changed_files=list(snapshot.changed), snapshot=snapshot)
    result = evaluate_rules(ctx, [CodeEntrypointsRule()])
    assert not result.errors
    assert [(v.file, v.message) for v in result.violations] == [
        (path, "Dead code entrypoint: 'src/run.py' (missing or outside workspace)")
    ]
    (tmp_path / path).write_text(
        doc("DESIGN-source", body="Historical source src/run.py at the base commit.\n", status="retired")
    )
    git("add", path)
    snapshot = git_snapshot(tmp_path, staged=True)
    assert not evaluate_rules(
        RuleContext(workspace_root=tmp_path, changed_files=list(snapshot.changed), snapshot=snapshot),
        [CodeEntrypointsRule()],
    ).violations


@pytest.mark.parametrize("mode", [SearchMode.DENSE, SearchMode.HYBRID, SearchMode.AUTO])
def test_all_roles_search_with_a_deterministic_local_embedding_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: SearchMode
) -> None:
    from devkit_dist.features.search import Embedder, SearchDocument, SearchIndex
    from distsupport.search import write_model

    from devkit_docs.features.documents.usecases import search

    embedder = Embedder.from_directory(write_model(tmp_path / "model", {"sample": [1.0, 0.0], "formal": [0.9, 0.1]}))

    def ranking(documents: list[SearchDocument]) -> SearchIndex:
        return SearchIndex(documents, embedder=embedder)

    monkeypatch.setattr(search, "SearchIndex", ranking)
    write_files(
        tmp_path, {f"docs/{directory}/{prefix}-sample.md": doc(f"{prefix}-sample") for directory, prefix, _ in ROLES}
    )
    hits = search_documents(DocumentIndex.load(tmp_path), "sample", mode=mode).hits
    assert {hit.document.kind for hit in hits} == {Kind.DESIGN, Kind.DOMAIN, Kind.OPERATIONS}
