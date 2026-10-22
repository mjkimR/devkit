from pathlib import Path

import pytest
from devkit.advisory import ExitCode, Level
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.local_config import LOCAL_CONFIG_PATH
from devkit_dist.features.project.services.presentation import language_notices, resolve_language


@pytest.mark.parametrize(
    "requested,resolved,fallback",
    [
        ("auto", "auto", False),
        ("en", "en", False),
        ("ko", "ko", False),
        ("KO", "en", True),
        ("ja", "en", True),
        ("", "en", True),
    ],
)
def test_shared_and_local_language(tmp_path: Path, requested: str, resolved: str, fallback: bool) -> None:
    root = tmp_path
    (root / ".devkit").mkdir()
    assert resolve_language(root).source == "default"
    assert resolve_language(root).requested == "auto"
    shared = root / ".devkit/config.toml"
    shared.write_text('[presentation]\nlanguage="en"\n')
    local = root / LOCAL_CONFIG_PATH
    local.write_text(f'[presentation]\nlanguage="{requested}"\n')
    result = resolve_language(root)
    assert (result.requested, result.resolved, result.fallback) == (requested, resolved, fallback)
    assert result.source == str(local)
    assert resolve_language(root, effective=False).resolved == "en"
    assert resolve_language(root, effective=False).source == str(shared)
    assert result.approval_language == ("ko" if resolved == "ko" else "en")


@pytest.mark.parametrize(
    "shared,local,warned",
    [
        (None, None, []),
        ("ko", "en", []),
        ("korean", None, ["config.toml"]),
        ("en", "KO", ["config.local.toml"]),
        ("korean", "ko", ["config.toml"]),
        ("ja", "", ["config.local.toml", "config.toml"]),
    ],
)
def test_unsupported_language_is_a_visible_warning(
    tmp_path: Path, shared: str | None, local: str | None, warned: list[str]
) -> None:
    (tmp_path / ".devkit").mkdir()
    for name, value in (("config.toml", shared), ("config.local.toml", local)):
        if value is not None:
            (tmp_path / ".devkit" / name).write_text(f'[presentation]\nlanguage="{value}"\n')
    notices = language_notices(tmp_path)
    assert [list(notice.target_files) for notice in notices] == [[str(tmp_path / ".devkit" / n)] for n in warned]
    for notice in notices:
        assert (notice.code, notice.level, notice.exit_code) == (
            "PRESENTATION_LANGUAGE_UNSUPPORTED",
            Level.WARNING,
            ExitCode.OK,
        )
        assert "resolves to 'en'" in notice.message
        assert notice.fix == f"Set [presentation] language in {notice.target_files[0]} to one of: auto, en, ko"


@pytest.mark.parametrize(
    "text",
    [
        "[presentation]\nlanguage=false",
        "[presentation]\nlanguage=123",
        "[presentation]\nlanguage=[]",
        'presentation="ko"',
        '[presentation]\nother="ko"',
        "[presentation",
    ],
)
@pytest.mark.parametrize("filename", ["config.toml", "config.local.toml"])
def test_invalid_presentation(tmp_path: Path, text: str, filename: str) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit" / filename).write_text(text)
    with pytest.raises(ConfigError) as error:
        resolve_language(tmp_path)
    assert error.value.code == "CONFIG_INVALID"
