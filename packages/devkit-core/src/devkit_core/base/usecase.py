"""Explicit application entrypoints shared by transport adapters and static checks."""

from abc import ABC, abstractmethod
from typing import Any


class BaseUseCase(ABC):
    """Name one operation through ``execute``; concrete methods declare their own input and result types.

    Synchronous and asynchronous operations use the same contract. This base adds no execution,
    authorization, transaction or retry behavior. Constructors only receive operation dependencies.
    """

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Run the concrete operation, or return its awaitable for an asynchronous implementation."""
        raise NotImplementedError
