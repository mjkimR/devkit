"""The approach is shared, inspectable and independent of SDD tooling."""

import pytest
from devkit_dist.features.project.models.development import DevelopmentConfigError, development_approach
from devkit_dist.features.project.repositories.development import read_development_approach
from devkit_dist.features.project.repositories.local_config import LocalKeyForbiddenError, read_effective_config

FIX = 'Use [development] approach = "sdd" or "adaptive-dev" in .devkit/config.toml'


@pytest.mark.parametrize("value", ["sdd", "adaptive-dev"])
def test_valid_approach(value):
    approach = development_approach({"development": {"approach": value}})
    assert (approach.approach, approach.source) == (value, ".devkit/config.toml")


@pytest.mark.parametrize(
    "value",
    [None, [], "adaptive-dev", {"approach": True}, {"approach": "other"}, {"approach": "incubation"}, {"other": "sdd"}],
)
def test_invalid_approach(value):
    with pytest.raises(DevelopmentConfigError) as raised:
        development_approach({"development": value})
    assert (raised.value.code, raised.value.fix) == ("DEVELOPMENT_CONFIG_INVALID", FIX)


def test_shared_approach_and_source(tmp_path):
    assert read_development_approach(tmp_path).approach == "sdd"
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text('[development]\napproach="adaptive-dev"\n')
    report = read_effective_config(tmp_path)
    assert report.values["development"]["approach"] == "adaptive-dev"
    assert report.sources["development.approach"] == ".devkit/config.toml"
    (tmp_path / ".devkit/config.local.toml").write_text('[development]\napproach="sdd"\n')
    with pytest.raises(LocalKeyForbiddenError):
        read_effective_config(tmp_path)


def test_former_incubation_value_is_refused_like_any_unknown_value(tmp_path):
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text('[development]\napproach="incubation"\n')
    with pytest.raises(DevelopmentConfigError) as raised:
        read_development_approach(tmp_path)
    assert (raised.value.code, raised.value.fix) == ("DEVELOPMENT_CONFIG_INVALID", FIX)
