"""Paging shared by the ``devkit docs`` listings and their use cases (sentinel output: ``devkit_docs.adapters.cli``)."""

from __future__ import annotations

from collections.abc import Sequence


def page[T](items: Sequence[T], offset: int, limit: int) -> list[T]:
    """``items[offset:offset + limit]``; ``limit`` ``0`` means all from ``offset``."""
    return list(items[offset : offset + limit] if limit else items[offset:])
