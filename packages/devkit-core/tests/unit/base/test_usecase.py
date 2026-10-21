"""The operation contract supports typed sync and async entrypoints without execution middleware."""

import asyncio

import pytest
from devkit_core.base.usecase import BaseUseCase


def test_an_operation_must_implement_execute() -> None:
    class MissingOperation(BaseUseCase):
        pass

    with pytest.raises(TypeError, match="execute"):
        MissingOperation()  # type: ignore[abstract]


def test_sync_and_async_implementations_keep_their_results_and_exceptions() -> None:
    class SyncOperation(BaseUseCase):
        def execute(self, value: int) -> int:
            if value < 0:
                raise ValueError("negative")
            return value + 1

    class AsyncOperation(BaseUseCase):
        async def execute(self, value: int) -> int:
            return value + 1

    assert SyncOperation().execute(2) == 3
    assert asyncio.run(AsyncOperation().execute(2)) == 3
    with pytest.raises(ValueError, match="negative"):
        SyncOperation().execute(-1)
