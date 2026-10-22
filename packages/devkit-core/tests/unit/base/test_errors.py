from __future__ import annotations

from devkit import advisory
from devkit.advisory import ActionMode
from devkit_core.base.errors import ArgumentError, DevkitCoreError


def test_argument_error_is_the_advisory_argument_error() -> None:
    error = ArgumentError("--workspace-root is empty")
    assert isinstance(error, advisory.ArgumentError) and isinstance(error, DevkitCoreError)
    assert (error.code, error.mode) == ("ARGUMENT_INVALID", ActionMode.INPUT_ERROR)
