from pathlib import Path

import pytest
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.local_config import LOCAL_CONFIG_PATH
from devkit_dist.features.project.services.presentation import resolve_language


@pytest.mark.parametrize("requested", ["auto", "en", "ko"])
def test_shared_and_local_language(tmp_path: Path, requested: str) -> None:
    root = tmp_path
    (root / ".devkit").mkdir()
    assert resolve_language(root).source == "default"
    assert resolve_language(root).requested == "auto"
    shared = root / ".devkit/config.toml"
    shared.write_text('[presentation]\nlanguage="en"\n')
    local = root / LOCAL_CONFIG_PATH
    local.write_text(f'[presentation]\nlanguage="{requested}"\n')
    result = resolve_language(root)
    assert (result.requested, result.resolved, result.fallback) == (requested, requested, False)
    assert result.source == str(local)
    assert resolve_language(root, effective=False).resolved == "en"
    assert resolve_language(root, effective=False).source == str(shared)
    assert result.approval_language == ("ko" if requested == "ko" else "en")


@pytest.mark.parametrize("requested", ["korean", "KO", "ja", ""])
@pytest.mark.parametrize("filename", ["config.toml", "config.local.toml"])
def test_unsupported_language_is_refused_with_the_accepted_values(
    tmp_path: Path, requested: str, filename: str
) -> None:
    (tmp_path / ".devkit").mkdir()
    path = tmp_path / ".devkit" / filename
    path.write_text(f'[presentation]\nlanguage="{requested}"\n')
    with pytest.raises(ConfigError) as error:
        resolve_language(tmp_path)
    assert error.value.code == "CONFIG_INVALID"
    assert repr(requested) in error.value.message
    assert error.value.fix is not None and "auto, en, ko" in error.value.fix
    assert list(error.value.target_files or ()) == [str(path)]


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
