"""The approach is shared, inspectable and independent of SDD tooling."""

import pytest
from devkit_dist.features.project.models.development import DevelopmentConfigError, development_approach
from devkit_dist.features.project.repositories.development import read_development_approach
from devkit_dist.features.project.repositories.local_config import LocalKeyForbiddenError, read_effective_config


@pytest.mark.parametrize("value", [None, [], "incubation", {"approach": True}, {"approach": "other"}, {"other": "sdd"}])
def test_invalid_approach(value):
    with pytest.raises(DevelopmentConfigError):
        development_approach({"development": value})


def test_shared_approach_and_source(tmp_path):
    assert read_development_approach(tmp_path).approach == "sdd"
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text('[development]\napproach="incubation"\n')
    report = read_effective_config(tmp_path)
    assert report.values["development"]["approach"] == "incubation"
    assert report.sources["development.approach"] == ".devkit/config.toml"
    (tmp_path / ".devkit/config.local.toml").write_text('[development]\napproach="sdd"\n')
    with pytest.raises(LocalKeyForbiddenError):
        read_effective_config(tmp_path)
