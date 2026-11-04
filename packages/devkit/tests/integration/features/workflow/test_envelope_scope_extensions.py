"""Typed worker extension evidence remains optional and refuses malformed inputs before writes."""

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.models.errors import EnvelopeFormatError
from devkit_agt.features.workflow.services.envelope import load_envelopes
from devkit_agt.features.workflow.services.envelope.model import parse_envelope
from testsupport.workflow import SIMPLE_UNIT, run_cli, simple_workspace

VALID = {
    "path": "src/feature/helper.py",
    "task": 1,
    "reason": "shares parsing: AC-01, AC-02",
    "requirements": ["AC-01"],
}


@pytest.fixture
def root(tmp_path: Path) -> Path:
    simple_workspace(tmp_path)
    assert run_cli("new", "-w", str(tmp_path), "u").exit_code == 0
    return tmp_path


def invoke(root: Path, text: str, *args: str):
    return CliRunner().invoke(
        cli,
        [
            "envelope",
            "worker",
            "-w",
            str(root),
            "--unit",
            SIMPLE_UNIT,
            "--stage",
            "s",
            "--summary",
            "implemented",
            "--scope-extensions-file",
            "-",
            *args,
        ],
        input=text,
    )


@pytest.mark.parametrize("stdin", [True, False])
def test_roundtrip_file_and_stdin(root: Path, stdin: bool) -> None:
    text = yaml.safe_dump([VALID])
    if stdin:
        result = invoke(root, text)
    else:
        source = root / "extensions.yaml"
        source.write_text(text)
        result = run_cli(
            "envelope",
            "worker",
            "-w",
            str(root),
            "--unit",
            SIMPLE_UNIT,
            "--stage",
            "s",
            "--scope-extensions-file",
            str(source),
        )
    assert result.exit_code == 0, result.output
    loaded = load_envelopes(root / SIMPLE_UNIT)
    assert not loaded.errors
    record = loaded.latest("worker")
    assert record is not None
    assert record.scope_extensions[0].to_dict() == VALID
    assert record.to_dict()["scope_extensions"] == [VALID]
    raw = yaml.safe_load((root / SIMPLE_UNIT / record.file).read_text())
    assert raw["scope_extensions"] == [VALID]


@pytest.mark.parametrize(
    "changes",
    [
        {"path": "/tmp/x"},
        {"path": "C:/tmp/x"},
        {"path": "../x"},
        {"path": "src/../x"},
        {"path": "src/*.py"},
        {"path": "src/"},
        {"path": "src//x"},
        {"path": "."},
        {"path": "src\\x"},
        {"path": "src/x\n"},
        {"task": True},
        {"task": 0},
        {"task": "1"},
        {"reason": ""},
        {"reason": "nested (note)"},
        {"reason": "two\nlines"},
        {"requirements": []},
        {"requirements": ["AC-1"]},
        {"requirements": ["AC-01", "AC-01"]},
        {"extra": "unknown"},
    ],
)
def test_bad_items_write_nothing(root: Path, changes: dict) -> None:
    result = invoke(root, yaml.safe_dump([{**VALID, **changes}]))
    assert result.exit_code == 2, result.output
    assert "ENVELOPE_ITEMS_INVALID" in result.stderr
    assert not list((root / SIMPLE_UNIT / "envelopes").glob("worker-*.yaml"))


@pytest.mark.parametrize(
    "text", ["", "null", "{}", "false", "[", "- {}", "- path: src/x", yaml.safe_dump([VALID, VALID])]
)
def test_bad_lists_and_duplicates_write_nothing(root: Path, text: str) -> None:
    result = invoke(root, text)
    assert result.exit_code == 2
    assert not list((root / SIMPLE_UNIT / "envelopes").glob("worker-*.yaml"))


def test_old_record_and_wrong_kind() -> None:
    old = {"kind": "worker", "stage": "s", "status": "completed"}
    assert parse_envelope("worker-01.yaml", 1, "worker", old).scope_extensions == ()
    for value in ([], [VALID], None):
        with pytest.raises(EnvelopeFormatError, match="only worker"):
            parse_envelope(
                "review-01.yaml", 1, "review", {"kind": "review", "status": "completed", "scope_extensions": value}
            )


def test_cli_worker_only_and_stdin_collision(root: Path) -> None:
    result = run_cli("envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT, "--scope-extensions-file", "-")
    assert result.exit_code == 2
    result = invoke(root, yaml.safe_dump([VALID]), "--questions-file", "-")
    assert result.exit_code == 2
    assert "ENVELOPE_FLAG_INVALID" in result.stderr
    assert not list((root / SIMPLE_UNIT / "envelopes").glob("worker-*.yaml"))
