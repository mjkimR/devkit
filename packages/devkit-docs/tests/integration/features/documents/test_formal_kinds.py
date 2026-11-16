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
AREA = "core"
AREA_SCOPED = {"DESIGN", "DOMAIN"}


def doc(identifier: str, extra: str = "", body: str = "", status: str = "active", area: str | None = None) -> str:
    """A formal role document; a design or domain document declares ``area: core`` unless ``area`` says otherwise
    (``""`` for none)."""
    if area is None:
        area = AREA if identifier.split("-", 1)[0] in AREA_SCOPED else ""
    area_line = f"area: {area}\n" if area else ""
    return f'---\nid: {identifier}\ntitle: Sample\nstatus: {status}\nsummary: "Sample formal role concepts and mechanisms."\n{area_line}{extra}---\n# [{identifier}] Sample\n{body}'


def role_path(directory: str, identifier: str, root: str = "docs", area: str = AREA) -> str:
    """The canonical path of a formal role document: a design bundle anchor, an area domain file or a flat
    operations file."""
    if directory == "designs":
        return f"{root}/designs/{area}/{identifier}/design.md"
    if directory == "domain":
        return f"{root}/domain/{area}/{identifier}.md"
    return f"{root}/{directory}/{identifier}.md"


def support_dir(directory: str, identifier: str, root: str = "docs", area: str = AREA) -> str:
    """Where parent-owned support lives: the design bundle itself, else ``<ID>/artifacts/`` beside the document."""
    if directory == "designs":
        return f"{root}/designs/{area}/{identifier}"
    return role_path(directory, identifier, root, area).removesuffix(".md") + "/artifacts"


def invoke(root: Path, *args: str) -> dict:
    result = CliRunner().invoke(cli, ["docs", *args, "--format", "json", "-w", str(root)])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_real_role_discovery_alias_refs_history_and_memo(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    identifier = f"{prefix}-sample"
    path = role_path(directory, identifier)
    reader = role_path("designs", "DESIGN-reader")
    files = {
        path: doc(identifier, f"aliases: [{prefix}-old]\n", status="retired"),
        reader: doc(
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
    assert f"[{identifier}]" in (tmp_path / reader).read_text()


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_global_and_namespace_schema_and_negative_controls(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    del kind
    global_path = role_path(directory, f"{prefix}-global")
    package_path = role_path(directory, f"{prefix}-package", root="docs/packages/api")
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
    for field in ["proposal", "decomposed_from", "depends_on", "milestone", "supersedes", "superseded_by"]:
        assert check(SpecFormatRule(), tmp_path, {global_path: doc(f"{prefix}-global", f"{field}: anything\n")})
    if prefix in AREA_SCOPED:  # the area follows the area directory
        assert [
            v.message for v in check(IdConventionRule(), tmp_path, {global_path: doc(f"{prefix}-global", area="x")})
        ] == ['Frontmatter area is "x" but the directory requires "core"']
        assert check(IdConventionRule(), tmp_path, {global_path: doc(f"{prefix}-global", area="")})
        assert not check(SpecFormatRule(), tmp_path)
        flat = f"docs/{directory}/{prefix}-flat.md"
        assert [
            v.message
            for v in check(
                IdConventionRule(), tmp_path, {global_path: doc(f"{prefix}-global"), flat: doc(f"{prefix}-flat")}
            )
        ] == [
            f"Invalid partition path: {'Design' if prefix == 'DESIGN' else 'Domain'} must be stored at"
            f" docs/{directory}/{{area}}/{prefix}-{{word-led-slug}}{'/design.md' if prefix == 'DESIGN' else '.md'}"
        ]
        (tmp_path / flat).unlink()
    else:
        assert [
            v.message for v in check(SpecFormatRule(), tmp_path, {global_path: doc(f"{prefix}-global", area="x")})
        ] == ["frontmatter field 'area' is inapplicable to this role"]
        (tmp_path / global_path).write_text(files[global_path])
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
    nested = (
        f"docs/{directory}/nested/{prefix}-nested.md"
        if prefix == "OPS"
        else role_path(directory, f"{prefix}-nested", area="core/deeper")
    )
    assert check(IdConventionRule(), tmp_path, {nested: doc(f"{prefix}-nested")})
    assert check(IdConventionRule(), tmp_path, {role_path(directory, f"{prefix}-123"): doc(f"{prefix}-123")})
    assert check(IdConventionRule(), tmp_path, {f"docs/elsewhere/{prefix}-outside.md": doc(f"{prefix}-outside")})


@pytest.mark.parametrize(
    "field,target", [("related_designs", "DESIGN"), ("related_domains", "DOMAIN"), ("related_operations", "OPS")]
)
def test_typed_relations_on_existing_kinds_reject_shape_prefix_duplicate_missing(
    tmp_path: Path, field: str, target: str
) -> None:
    destination = {"DESIGN": "designs", "DOMAIN": "domain", "OPS": "operations"}[target]
    base = {role_path(destination, f"{target}-target"): doc(f"{target}-target")}
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
    owner = role_path(directory, parent)
    artifact = f"{support_dir(directory, parent)}/data.md"
    files = {
        owner: doc(parent),
        artifact: f"# Data\nSupport for `{parent}`.\n",
        f"{support_dir(directory, parent)}/data.csv": "a,b\n1,2\n",
    }
    assert not check(IdConventionRule(), tmp_path, files)
    assert not check(SpecFormatRule(), tmp_path)
    assert check(IdConventionRule(), tmp_path, {artifact: doc(f"{prefix}-intruder")})
    assert check(IdConventionRule(), tmp_path, {artifact: "# Data\nNo owner here.\n"})
    assert check(
        IdConventionRule(), tmp_path, {f"{support_dir(directory, f'{prefix}-orphan')}/data.md": f"{prefix}-orphan\n"}
    )
    assert check(IdConventionRule(), tmp_path, {f"docs/{directory}/nested/detail.md": "# Independent question\n"})


def test_design_entrypoints_are_optional_safe_and_canonical(tmp_path: Path) -> None:
    path = role_path("designs", "DESIGN-source")
    files = {path: doc("DESIGN-source", "entrypoints: [src/file.py]\n"), "src/file.py": "x = 1\n"}
    assert not check(CodeEntrypointsRule(), tmp_path, files)
    assert "DESIGN-source" in str(invoke(tmp_path, "list", "--file", "src/file.py"))
    for bearing in [path, role_path("designs", "DESIGN-source", root="docs/packages/api")]:
        assert entrypoint_bearing(bearing)
    for other in [
        "docs/designs/README.md",
        "docs/designs/core/README.md",
        "docs/designs/DESIGN-source.md",
        "docs/designs/core/DESIGN-source.md",
        "docs/designs/core/DESIGN-source/README.md",
        "docs/designs/core/DESIGN-source/data.md",
        "docs/designs/core/DESIGN-source/nested/design.md",
        "docs/designs/core/DESIGN-123/design.md",
        role_path("domain", "DOMAIN-source"),
        role_path("operations", "OPS-source"),
    ]:
        assert not entrypoint_bearing(other), other
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
            {role_path(directory, f"{prefix}-source"): doc(f"{prefix}-source", "entrypoints: []\n")},
        )


@pytest.mark.parametrize("root", ["docs", "docs/packages/api"])
def test_artifact_rename_root_move_split_and_reclassification(tmp_path: Path, root: str) -> None:
    """Composed authored states retain one owner and usable relative data destinations."""
    config = '[[tool.docs.namespaces]]\nname = "api"\npath = "packages/api"\n'
    bundle = tmp_path / support_dir("designs", "DESIGN-original", root)
    write_files(
        tmp_path,
        {
            ".devkit/config.toml": config,
            role_path("designs", "DESIGN-original", root): doc("DESIGN-original", body="[Data](data.csv)\n"),
            f"{support_dir('designs', 'DESIGN-original', root)}/data.csv": "a,b\n1,2\n",
        },
    )
    assert not check(IdConventionRule(), tmp_path)
    # A same-kind rename renames the bundle, which carries its support; the former ID is identity only.
    renamed = bundle.with_name("DESIGN-renamed")
    bundle.rename(renamed)
    (renamed / "design.md").write_text(doc("DESIGN-renamed", "aliases: [DESIGN-original]\n", "[Data](data.csv)\n"))
    assert not check(IdConventionRule(), tmp_path)
    assert DocumentIndex.load(tmp_path).resolve("DESIGN-original").id == "DESIGN-renamed"
    assert (renamed / "data.csv").read_text() == "a,b\n1,2\n"
    # Move roots without changing identity, then split support into an independent peer bundle.
    other = "docs/packages/api" if root == "docs" else "docs"
    dest = tmp_path / support_dir("designs", "DESIGN-renamed", other)
    dest.parent.mkdir(parents=True, exist_ok=True)
    renamed.rename(dest)
    assert not check(IdConventionRule(), tmp_path)
    detail = dest.with_name("DESIGN-detail")
    detail.mkdir()
    (detail / "design.md").write_text(doc("DESIGN-detail", body="[Data](data.csv)\n"))
    (dest / "data.csv").rename(detail / "data.csv")
    (dest / "design.md").write_text(
        doc("DESIGN-renamed", "aliases: [DESIGN-original]\nrelated_designs: [DESIGN-detail]\n")
    )
    assert not check(IdConventionRule(), tmp_path)
    # Cross-kind transfer retains retired predecessor; no cross-prefix aliases.
    ops = tmp_path / other / "operations"
    (ops / "OPS-detail/artifacts").mkdir(parents=True)
    (detail / "data.csv").rename(ops / "OPS-detail/artifacts/data.csv")
    (ops / "OPS-detail.md").write_text(doc("OPS-detail", body="[Data](OPS-detail/artifacts/data.csv)\n"))
    (detail / "design.md").write_text(
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
    path = role_path("designs", "DESIGN-source")
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
        tmp_path, {role_path(directory, f"{prefix}-sample"): doc(f"{prefix}-sample") for directory, prefix, _ in ROLES}
    )
    hits = search_documents(DocumentIndex.load(tmp_path), "sample", mode=mode).hits
    assert {hit.document.kind for hit in hits} == {Kind.DESIGN, Kind.DOMAIN, Kind.OPERATIONS}


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_role_aliases_reject_own_repeated_cross_prefix_legacy_and_colliding_identity(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    del kind
    path = role_path(directory, f"{prefix}-sample")
    for aliases in [f"[{prefix}-sample]", f"[{prefix}-old, {prefix}-old]", "[UC-other]", f"[{prefix}-20261116]"]:
        assert check(DocumentReferenceRule(), tmp_path, {path: doc(f"{prefix}-sample", f"aliases: {aliases}\n")})
    assert check(
        DocumentReferenceRule(),
        tmp_path,
        {
            path: doc(f"{prefix}-sample", f"aliases: [{prefix}-other]\n"),
            role_path(directory, f"{prefix}-other"): doc(f"{prefix}-other"),
        },
    )


def test_summary_quoting_uses_actual_yaml_value_not_body_examples(tmp_path: Path) -> None:
    path = role_path("designs", "DESIGN-summary")
    unquoted = doc("DESIGN-summary", body='```yaml\nsummary: "Body example."\n```\n').replace(
        'summary: "Sample formal role concepts and mechanisms."', "summary: Unquoted summary."
    )
    assert any("double-quoted" in v.message for v in check(SpecFormatRule(), tmp_path, {path: unquoted}))
    quoted_key = doc("DESIGN-summary").replace("summary:", '"summary":')
    assert not check(SpecFormatRule(), tmp_path, {path: quoted_key})


@pytest.mark.parametrize(
    "field,prefix,directory",
    [
        ("related_designs", "DESIGN", "designs"),
        ("related_domains", "DOMAIN", "domain"),
        ("related_operations", "OPS", "operations"),
    ],
)
def test_material_opt_in_role_metadata_is_typed_without_policing_its_prose(
    tmp_path: Path, field: str, prefix: str, directory: str
) -> None:
    material = "docs/materials/MAT-evidence.md"
    parent = role_path(directory, f"{prefix}-sample")
    for value in ["not-a-list", "[12]", "[UC-wrong]", f"[{prefix}-absent]", f"[{prefix}-sample, {prefix}-sample]"]:
        assert check(
            DocumentReferenceRule(),
            tmp_path,
            {parent: doc(f"{prefix}-sample"), material: doc("MAT-evidence", f"{field}: {value}\n")},
        )
    body = "Historical freeform `UC-absent` remains as written.\n"
    files = {
        parent: doc(f"{prefix}-sample", f"aliases: [{prefix}-old]\n"),
        material: doc("MAT-evidence", f"{field}: [{prefix}-old]\n", body),
    }
    assert not [v for v in check(DocumentReferenceRule(), tmp_path, files, fix=True) if not v.fixed]
    text = (tmp_path / material).read_text()
    assert f"{field}: [{prefix}-sample]" in text and body in text


def test_artifact_parent_must_be_indexed_and_not_a_symlink(tmp_path: Path) -> None:
    write_files(
        tmp_path,
        {
            "support/real.md": doc("DESIGN-parent"),
            "docs/designs/core/DESIGN-parent/data.csv": "a,b\n1,2\n",
            "docs/domain/core/DOMAIN-parent/artifacts/data.csv": "a,b\n1,2\n",
        },
    )
    (tmp_path / "docs/designs/core/DESIGN-parent/design.md").symlink_to(tmp_path / "support/real.md")
    (tmp_path / "docs/domain/core/DOMAIN-parent.md").symlink_to(tmp_path / "support/real.md")
    assert not DocumentIndex.load(tmp_path).documents
    assert [(v.file, v.message) for v in check(IdConventionRule(), tmp_path) if v.file.endswith(".csv")] == [
        (
            "docs/designs/core/DESIGN-parent/data.csv",
            "Invalid partition path: bundle has no eligible design.md anchor whose ID is the bundle directory name",
        ),
        (
            "docs/domain/core/DOMAIN-parent/artifacts/data.csv",
            "Invalid partition path: role artifact has no eligible canonical parent document in the same docs root",
        ),
    ]


def test_artifact_uses_exact_parent_id_and_visible_first_heading(tmp_path: Path) -> None:
    path = "docs/designs/core/DESIGN-parent/data.md"
    owner = {role_path("designs", "DESIGN-parent"): doc("DESIGN-parent")}
    assert check(IdConventionRule(), tmp_path, {**owner, path: "# Data\nDESIGN-parent-extra\n"})
    good = "```markdown\n# [DESIGN-example] Fenced example\n```\n# Data\nSupport for `DESIGN-parent`.\n"
    assert not check(IdConventionRule(), tmp_path, {**owner, path: good})


def test_parent_snapshot_deletion_checks_unchanged_artifacts_and_honors_exclusions(tmp_path: Path) -> None:
    import subprocess

    from devkit_agt.features.rules import RuleContext, evaluate_rules, git_snapshot

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "Test")
    parent = role_path("designs", "DESIGN-parent")
    artifact = "docs/designs/core/DESIGN-parent/data.csv"
    write_files(tmp_path, {parent: doc("DESIGN-parent"), artifact: "a,b\n1,2\n"})
    git("add", "-A")
    git("commit", "-qm", "base")
    git("rm", "-q", parent)
    snapshot = git_snapshot(tmp_path, staged=True)
    ctx = RuleContext(workspace_root=tmp_path, changed_files=list(snapshot.changed), snapshot=snapshot)
    result = evaluate_rules(ctx, [IdConventionRule()])
    assert not result.errors
    assert [v.file for v in result.violations] == [artifact]
    excluded = RuleContext(
        workspace_root=tmp_path,
        changed_files=list(snapshot.changed),
        snapshot=snapshot,
        exclude=("docs/designs/core/DESIGN-parent/**",),
    )
    assert not evaluate_rules(excluded, [IdConventionRule()]).violations
    # Composed rename moves the support with the bundle, so the staged snapshot is valid.
    (tmp_path / "docs/designs/core/DESIGN-parent").rename(tmp_path / "docs/designs/core/DESIGN-renamed")
    (tmp_path / "docs/designs/core/DESIGN-renamed/design.md").write_text(
        doc("DESIGN-renamed", "aliases: [DESIGN-parent]\n")
    )
    git("add", "-A")
    snapshot = git_snapshot(tmp_path, staged=True)
    result = evaluate_rules(
        RuleContext(workspace_root=tmp_path, changed_files=list(snapshot.changed), snapshot=snapshot),
        [IdConventionRule()],
    )
    assert not result.errors and not result.violations


def test_persistent_memo_roundtrip_rebuilds_all_role_kinds_and_relations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from devkit_docs.features.documents.repositories import index as index_module

    (tmp_path / ".devkit/transient").mkdir(parents=True)
    write_files(
        tmp_path,
        {
            role_path("designs", "DESIGN-sample"): doc("DESIGN-sample", "related_domains: [DOMAIN-sample]\n"),
            role_path("domain", "DOMAIN-sample"): doc("DOMAIN-sample", "related_operations: [OPS-sample]\n"),
            "docs/operations/OPS-sample.md": doc("OPS-sample", "related_designs: [DESIGN-sample]\n"),
        },
    )
    first = DocumentIndex.load(tmp_path)
    assert (tmp_path / ".devkit/transient/docs/document-index.json").is_file()
    index_module._parsed.clear()

    def no_fresh_parse(relative: str, text: str) -> None:
        raise AssertionError(f"Unexpected fresh parse: {relative}")

    monkeypatch.setattr(index_module, "_fresh", no_fresh_parse)
    second = DocumentIndex.load(tmp_path)
    assert [(d.id, d.kind, d.references) for d in first.documents] == [
        (d.id, d.kind, d.references) for d in second.documents
    ]


def test_persistent_role_memo_is_reused_in_a_separate_process(tmp_path: Path) -> None:
    import subprocess
    import sys

    (tmp_path / ".devkit/transient").mkdir(parents=True)
    write_files(
        tmp_path,
        {
            role_path("designs", "DESIGN-sample"): doc("DESIGN-sample", "related_domains: [DOMAIN-sample]\n"),
            role_path("domain", "DOMAIN-sample"): doc("DOMAIN-sample", "related_operations: [OPS-sample]\n"),
            "docs/operations/OPS-sample.md": doc("OPS-sample", "related_designs: [DESIGN-sample]\n"),
        },
    )
    # First process writes the memo; the second refuses every fresh parse.
    program = """
import json, sys
from pathlib import Path
from devkit_docs.features.documents import DocumentIndex
from devkit_docs.features.documents.repositories import index as module
assert not module._parsed
if sys.argv[2] == 'reuse':
    def forbidden(*args):
        raise AssertionError('fresh parse would hide missing persistent-memo support')
    module._fresh = forbidden
index = DocumentIndex.load(Path(sys.argv[1]))
print(json.dumps([(d.id, str(d.kind), [(r.field, r.target) for r in d.references]) for d in index.documents]))
"""
    outputs = []
    for phase in ("write", "reuse"):
        result = subprocess.run(
            [sys.executable, "-c", program, str(tmp_path), phase], text=True, capture_output=True, check=False
        )
        assert result.returncode == 0, result.stderr
        outputs.append(json.loads(result.stdout))
    assert outputs[0] == outputs[1] and len(outputs[1]) == 3
    assert {row[1] for row in outputs[1]} == {"design", "domain", "operations"}


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_quoted_yaml_identity_keys_are_valid_and_fix_is_idempotent(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    del kind
    path = role_path(directory, f"{prefix}-quoted")
    text = (
        doc(f"{prefix}-quoted")
        .replace("id:", '"id":')
        .replace("title:", '"title":')
        .replace("status:", '"status":')
        .replace("summary:", '"summary":')
    )
    assert not check(IdConventionRule(), tmp_path, {path: text}, fix=True)
    assert not check(SpecFormatRule(), tmp_path)
    assert (tmp_path / path).read_text() == text


@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_artifacts_reject_every_parser_identity_field_but_allow_fenced_examples(
    tmp_path: Path, directory: str, prefix: str, kind: Kind
) -> None:
    del kind
    from devkit_docs.features.documents.models.model import IDENTITY_FIELDS

    parent = f"{prefix}-parent"
    path = f"{support_dir(directory, parent)}/detail.md"
    owner = {role_path(directory, parent): doc(parent)}
    expected = "stray" if directory == "designs" else "ID-free"
    for identity_field in IDENTITY_FIELDS:
        text = f"---\n{identity_field}: REC-support\n---\n# Detail\nSupport for `{parent}`.\n"
        found = check(IdConventionRule(), tmp_path, {**owner, path: text})
        assert any(v.file == path and expected in v.message for v in found), identity_field
    examples = "\n".join(f"{field}: REC-example" for field in IDENTITY_FIELDS)
    text = f"```yaml\n{examples}\n```\n# Detail\nSupport for `{parent}`.\n"
    assert not check(IdConventionRule(), tmp_path, {**owner, path: text})
    assert [d.id for d in DocumentIndex.load(tmp_path).documents] == [parent]


def test_a_bundle_anchor_file_name_pins_no_bundle(tmp_path: Path) -> None:
    write_files(
        tmp_path,
        {
            role_path("designs", "DESIGN-first"): doc("DESIGN-first"),
            role_path("designs", "DESIGN-second", area="other"): doc("DESIGN-second", area="other"),
            role_path("domain", "DOMAIN-sample"): doc("DOMAIN-sample"),
        },
    )
    index = DocumentIndex.load(tmp_path)
    for query in ["design.md", "DESIGN.MD"]:
        assert not [hit for hit in search_documents(index, query, mode=SearchMode.LEXICAL).hits if hit.pinned]
    for query in ["DESIGN-first", "docs/designs/other/DESIGN-second/design.md", "DOMAIN-sample.md"]:
        hits = search_documents(index, query, mode=SearchMode.LEXICAL).hits
        assert hits[0].pinned and query.casefold() in hits[0].document.path.casefold() + hits[0].document.id.casefold()


@pytest.mark.parametrize("root", ["docs", "docs/packages/api"])
def test_an_area_move_keeps_id_aliases_and_incoming_references(tmp_path: Path, root: str) -> None:
    config = '[[tool.docs.namespaces]]\nname = "api"\npath = "packages/api"\n'
    reader = role_path("operations", "OPS-reader")
    write_files(
        tmp_path,
        {
            ".devkit/config.toml": config,
            role_path("designs", "DESIGN-moved", root): doc(
                "DESIGN-moved", "aliases: [DESIGN-former]\nentrypoints: [src/run.py]\n", "[Data](data.csv)\n"
            ),
            f"{support_dir('designs', 'DESIGN-moved', root)}/data.csv": "a,b\n",
            role_path("domain", "DOMAIN-moved", root): doc(
                "DOMAIN-moved", body="[Data](DOMAIN-moved/artifacts/a.csv)\n"
            ),
            f"{support_dir('domain', 'DOMAIN-moved', root)}/a.csv": "a,b\n",
            reader: doc(
                "OPS-reader", "related_designs: [DESIGN-moved]\nrelated_domains: [DOMAIN-moved]\n", "`DESIGN-moved`\n"
            ),
            "src/run.py": "x = 1\n",
        },
    )
    rules = [IdConventionRule(), SpecFormatRule(), DocumentReferenceRule(), CodeEntrypointsRule()]
    assert not [v for rule in rules for v in check(rule, tmp_path)]
    # Move the bundle and the domain file with its support to another area; only `area` follows the directory.
    (tmp_path / root / "designs/next").mkdir(parents=True)
    (tmp_path / support_dir("designs", "DESIGN-moved", root)).rename(
        tmp_path / support_dir("designs", "DESIGN-moved", root, "next")
    )
    (tmp_path / root / "domain/next").mkdir(parents=True)
    (tmp_path / role_path("domain", "DOMAIN-moved", root)).rename(
        tmp_path / role_path("domain", "DOMAIN-moved", root, "next")
    )
    (tmp_path / role_path("domain", "DOMAIN-moved", root).removesuffix(".md")).rename(
        tmp_path / role_path("domain", "DOMAIN-moved", root, "next").removesuffix(".md")
    )
    stale = [(v.file, v.message) for v in check(IdConventionRule(), tmp_path)]
    assert stale == [
        (
            role_path("designs", "DESIGN-moved", root, "next"),
            'Frontmatter area is "core" but the directory requires "next"',
        ),
        (
            role_path("domain", "DOMAIN-moved", root, "next"),
            'Frontmatter area is "core" but the directory requires "next"',
        ),
    ]
    for rule in (SpecFormatRule(), IdConventionRule()):  # the rules `devkit rules fix` runs on these files
        assert not [v for v in check(rule, tmp_path, fix=True) if not v.fixed]
    assert not [v for rule in rules for v in check(rule, tmp_path)]
    assert "id: DESIGN-moved\n" in (tmp_path / role_path("designs", "DESIGN-moved", root, "next")).read_text()
    index = DocumentIndex.load(tmp_path)
    assert index.resolve("DESIGN-former").path == role_path("designs", "DESIGN-moved", root, "next")
    assert index.resolve("DOMAIN-moved").path == role_path("domain", "DOMAIN-moved", root, "next")
    assert "OPS-reader" in str(invoke(tmp_path, "refs", "DESIGN-moved", "--direction", "in"))
    assert "OPS-reader" in str(invoke(tmp_path, "refs", "DOMAIN-moved", "--direction", "in"))
    assert "DESIGN-moved" in str(invoke(tmp_path, "list", "--file", "src/run.py"))
    assert "DESIGN-moved" in str(invoke(tmp_path, "list", "--area", "next"))


def test_rules_fix_writes_a_blank_bundle_anchor_id_and_stale_area(tmp_path: Path) -> None:
    anchor = "docs/packages/api/designs/core/DESIGN-x/design.md"
    write_files(
        tmp_path,
        {
            ".devkit/config.toml": '[[tool.docs.namespaces]]\nname = "api"\npath = "packages/api"\n',
            anchor: '---\nid: ""\ntitle: Sample\nstatus: active\nsummary: "S."\narea: stale\ncreated_at: 2026-01-01\n---\n# [DESIGN-x] Sample\n',
        },
    )
    for rule in (SpecFormatRule(), IdConventionRule()):  # the rules `devkit rules fix` runs on these files
        assert not [v for v in check(rule, tmp_path, fix=True) if not v.fixed]
    text = (tmp_path / anchor).read_text()
    assert "id: DESIGN-x\n" in text and "area: core\n" in text and 'id: ""' not in text
    assert [p.relative_to(tmp_path).as_posix() for p in (tmp_path / "docs").rglob("*.md")] == [anchor]
