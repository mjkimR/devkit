"""``devkit.docs.status_overlay``: overlays change the shown status and add fields; a broken one is left out with a
``DOCS_OVERLAY_FAILED`` warning, and ``list`` keeps working."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from docs_support.types import Write

from devkit_docs.features.documents.usecases import browse

CAPABILITY = "---\nid: CAP-CORE-x\ntitle: X\nsummary: The x capability.\nstatus: active\n---\n# X\n"


@dataclass(frozen=True)
class _Entry:
    name: str
    overlay: Callable[..., object]

    @property
    def value(self) -> str:
        return f"tests:{self.name}"

    def load(self) -> Callable[..., object]:
        return self.overlay


def _install(monkeypatch: pytest.MonkeyPatch, **overlays: Callable[..., object]) -> None:
    """Register ``overlays`` for the browse use case only, so devkit's own command entry points still load."""
    entries = [_Entry(name, overlay) for name, overlay in overlays.items()]
    stub = SimpleNamespace(entry_points=lambda *, group: entries if group == browse.OVERLAY_GROUP else [])
    monkeypatch.setattr(browse, "metadata", stub)


def _list(workspace: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["docs", "list", *args, "-w", str(workspace)])


def _reviewing(_root: Path, documents: Sequence[object]) -> Mapping[str, Mapping[str, str]]:
    return {"CAP-CORE-x": {"status": "reviewing", "owner": "planning"}}


def test_an_overlay_replaces_the_shown_status_and_adds_fields(
    workspace: Path, write: Write, monkeypatch: pytest.MonkeyPatch
) -> None:
    write("docs/capabilities/core/CAP-CORE-x.md", CAPABILITY)
    _install(monkeypatch, a=_reviewing)
    text = _list(workspace)
    assert text.exit_code == 0, text.output
    assert "status=reviewing" in text.stdout and "owner=planning" in text.stdout
    record = json.loads(_list(workspace, "--status", "reviewing", "--format", "json").stdout)["documents"][0]
    assert record["status"] == "reviewing" and record["owner"] == "planning"


@pytest.mark.parametrize(
    "overlay",
    [
        lambda _root, _documents: (_ for _ in ()).throw(RuntimeError("overlay broke")),
        lambda _root, _documents: ["not", "a", "mapping"],
        lambda _root, _documents: {"CAP-CORE-x": {"title": "taken"}},
        lambda _root, _documents: {"CAP-CORE-x": {"status": 3}},
    ],
    ids=["raises", "not a mapping", "reserved field", "non-text value"],
)
def test_a_broken_overlay_is_left_out_with_a_warning(
    workspace: Path, write: Write, monkeypatch: pytest.MonkeyPatch, overlay: Callable[..., object]
) -> None:
    write("docs/capabilities/core/CAP-CORE-x.md", CAPABILITY)
    _install(monkeypatch, a=overlay, b=_reviewing)
    result = _list(workspace, "--format", "json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["documents"][0]["status"] == "reviewing"  # the working overlay still applies
    [notice] = payload["notices"]
    assert notice["code"] == "DOCS_OVERLAY_FAILED" and "extension: a" in notice["advisory"]["details"]
