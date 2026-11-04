"""The ``devkit.context_documents`` provider: namespace steering directories selected by the working directory
(``ADR-namespace-steering-directories``), as a library and end to end through ``devkit get-context docs``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib.metadata import entry_points
from pathlib import Path

import pytest
from docs_support.types import Write

from devkit_docs.base.errors import DocsConfigError
from devkit_docs.features.documents.services.context_documents import mirror, provide

CONFIG = (
    '[[tool.docs.namespaces]]\nname = "api"\npath = "packages/api"\n'
    '[[tool.docs.namespaces]]\nname = "web"\npath = "apps/web"\n'
)
API = "docs/packages/api/steering"
WEB = "docs/packages/web/steering"


@pytest.fixture
def monorepo(workspace: Path, write: Write) -> Path:
    write(".devkit/config.toml", CONFIG)
    for directory in ("docs/steering", API, WEB, "packages/api/src", "apps/web", "tools/other"):
        (workspace / directory).mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.mark.parametrize(
    ("working", "expected"),
    [
        ("packages/api/src", ([API], [WEB])),
        ("docs/packages/api", ([API], [WEB])),
        ("apps/web", ([WEB], [API])),
        ("", ([], [API, WEB])),
        ("tools/other", ([], [API, WEB])),
    ],
    ids=["source", "docs-root", "other-package", "root", "outside-every-package"],
)
def test_the_working_directory_selects_the_namespace_to_list(
    monorepo: Path, working: str, expected: tuple[list[str], list[str]]
) -> None:
    assert provide(monorepo, monorepo / working, "docs/steering") == expected


def test_nothing_outside_docs_or_without_namespaces(monorepo: Path, workspace: Path, write: Write) -> None:
    assert provide(monorepo, monorepo / "packages/api", "guides") == ([], [])
    assert provide(monorepo, monorepo / "packages/api", "docs") == (["docs/packages/api"], ["docs/packages/web"])
    write(".devkit/config.toml", "")
    assert provide(workspace, workspace / "packages/api", "docs/steering") == ([], [])


def test_a_malformed_registry_raises_docs_config_invalid(workspace: Path, write: Write) -> None:
    write(".devkit/config.toml", '[[tool.docs.namespaces]]\nname = "global"\npath = "x"\n')
    with pytest.raises(DocsConfigError):
        provide(workspace, workspace, "docs/steering")


def test_mirror_follows_living_path() -> None:
    from devkit_docs.features.documents.models.namespace import Namespace

    api = Namespace("api", "packages/api")
    assert mirror(api, "docs/steering") == API
    assert mirror(api, "docs") == "docs/packages/api"
    assert mirror(api, "guides") is None
    assert mirror(api, "docsx/steering") is None


def test_the_provider_is_registered() -> None:
    [entry] = [item for item in entry_points(group="devkit.context_documents") if item.name == "docs"]
    assert entry.load() is provide


# --- end to end: a monorepo project synchronized with the docs bundle (AC-09) ---


def _devkit(root: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("DEVKIT_")}
    return subprocess.run(
        [sys.executable, "-m", "devkit_dist", *args],
        text=True,
        capture_output=True,
        env=env,
        check=False,
        cwd=cwd or root,
    )


def _steering(title: str, summary: str) -> str:
    return f"---\ntitle: {title}\nsummary: {summary}\n---\n# Body\n"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "mono"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text(CONFIG)
    result = _devkit(root, "sync", "-w", str(root))
    assert result.returncode == 0, result.stdout + result.stderr
    for directory in ("docs/steering", API, WEB, "packages/api", "apps/web"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for directory in ("docs/steering", API, WEB):
        # RULE-steering-documents defaults: max_files 10, max_summary_length 300
        for number in range(10):
            (root / directory / f"topic-{number}.md").write_text(_steering("t" * 60, "s" * 300))
        (root / directory / "README.md").write_text("# Steering\n")
    return root


def _context(root: Path, *args: str, cwd: Path | None = None) -> dict[str, object]:
    result = _devkit(root, "get-context", "docs", *args, cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def _names(context: dict[str, object], prefix: Path) -> list[str]:
    documents = context["documents"]
    assert isinstance(documents, list)
    return [str(Path(item["path"]).relative_to(prefix)) for item in documents]


def _bounded(context: dict[str, object], namespaces: int) -> None:
    documents = context["documents"]
    elsewhere = context["documents_elsewhere"]
    assert isinstance(documents, list) and isinstance(elsewhere, list)
    size = len(json.dumps(documents).encode()) - sum(len(json.dumps(item["path"])) for item in documents)
    assert size <= 2 * 4096, size
    assert len(elsewhere) <= namespaces


def test_a_package_directory_and_for_list_that_package_beside_the_root(project: Path) -> None:
    from_package = _context(project, cwd=project / "packages/api")
    with_for = _context(project, "--for", "packages/api")
    assert from_package["documents"] == with_for["documents"]
    assert from_package["documents_elsewhere"] == with_for["documents_elsewhere"]
    names = _names(from_package, project)
    assert names[:10] == sorted(f"{API}/topic-{n}.md" for n in range(10))
    assert names[10:] == sorted(f"docs/steering/topic-{n}.md" for n in range(10))
    assert not any(name.startswith(WEB) for name in names)
    assert from_package["documents_elsewhere"] == [{"path": str(project / WEB), "files": 10}]
    assert from_package["notices"] == []
    _bounded(from_package, 2)


def test_the_root_lists_the_global_directory_and_names_every_namespace(project: Path) -> None:
    context = _context(project)
    assert _names(context, project) == sorted(f"docs/steering/topic-{n}.md" for n in range(10))
    assert context["documents_elsewhere"] == [
        {"path": str(project / API), "files": 10},
        {"path": str(project / WEB), "files": 10},
    ]
    _bounded(context, 2)


def test_a_malformed_registry_degrades_to_the_root_directory_with_a_warning(project: Path) -> None:
    (project / ".devkit/config.toml").write_text('[[tool.docs.namespaces]]\nname = "global"\npath = "x"\n')
    result = _devkit(project, "get-context", "docs", cwd=project / "packages/api")
    assert result.returncode == 0, result.stdout + result.stderr
    context = json.loads(result.stdout)
    assert _names(context, project) == sorted(f"docs/steering/topic-{n}.md" for n in range(10))
    assert context["documents_elsewhere"] == []
    [notice] = context["notices"]
    assert notice["code"] == "CONTEXT_DOCUMENTS_EXTENSION_FAILED"
    assert result.stderr == ""  # JSON-only command: the one object carries the advisory (ARCH-08-1)
    assert _devkit(project, "get-context", "docs", "--strict", cwd=project / "packages/api").returncode == 1
