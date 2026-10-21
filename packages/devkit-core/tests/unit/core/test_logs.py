"""Independent package loggers retain the shared CLI logging boundary."""

import logging

import pytest
from devkit_core.core.logs import get_logger


@pytest.mark.parametrize(
    "namespace", ["devkit_core", "devkit_dist", "devkit_agt", "devkit_spec", "devkit_mcp", "devkit_viewer"]
)
def test_application_logs_propagate_through_shared_boundary(namespace: str) -> None:
    logger = get_logger(f"{namespace}.features.probe")
    parent = logger
    while parent.name != "devkit" and parent.parent is not None:
        parent = parent.parent
    assert parent is logging.getLogger("devkit")
    assert any(isinstance(handler, logging.NullHandler) for handler in parent.handlers)


def test_existing_advisory_and_foreign_names_are_preserved() -> None:
    assert get_logger("devkit.advisory").name == "devkit.advisory"
    assert get_logger("consumer.probe").name == "consumer.probe"
