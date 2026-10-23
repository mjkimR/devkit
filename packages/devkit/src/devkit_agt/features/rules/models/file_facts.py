"""Typed contracts for immutable, rule-owned per-file extraction."""

from __future__ import annotations

import ast
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol, TypeVar

FactsT = TypeVar("FactsT")
JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]

FrozenJsonValue = None | bool | int | float | str | tuple["FrozenJsonValue", ...] | Mapping[str, "FrozenJsonValue"]


class FileFactsSource(Protocol):
    """Extraction's file-local view; returned Python trees and nodes are shared and read-only."""

    @property
    def path(self) -> str: ...

    @property
    def context(self) -> FrozenJsonValue: ...

    def get_python_ast(self) -> ast.Module: ...

    def get_python_nodes(self, *types: type[ast.AST]) -> tuple[ast.AST, ...]: ...


@dataclass(frozen=True)
class FactsDependency:
    """Logical source name and bytes captured when its implementing module loads."""

    name: str
    source: bytes | None


@dataclass(frozen=True, eq=False)
class FileFactsDescriptor[FactT]:
    """A rule's extraction contract; dependencies include its implementation, helpers and codec."""

    rule_id: str
    schema_version: int
    source_dependencies: tuple[FactsDependency, ...]
    extract: Callable[[FileFactsSource], FactT]
    encode: Callable[[FactT], JsonValue]
    decode: Callable[[JsonValue], FactT]
