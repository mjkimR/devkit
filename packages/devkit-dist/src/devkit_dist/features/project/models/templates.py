"""Contracts for contributed project configuration templates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateKey:
    """One key: ``default`` as the reader applies it, or ``None`` when it is unset by default.

    A key unset by default shows ``example``, which must then be given, marked as one; its ``help`` says what
    applies while it is unset (``"unset: ..."``). ``kind`` names the accepted values (for example ``"integer from 1
    to 300"``); empty, it is derived from the value shown. ``help`` says what the key does.
    """

    name: str
    default: object = None
    help: str = ""
    kind: str = ""
    example: object = None


@dataclass(frozen=True)
class TemplateTable:
    """One table: ``path`` holds its keys below ``[tool.<name>]`` (``("scope",)`` is ``[tool.<name>.scope]``).

    ``array`` renders an array of tables (``[[...]]``): there is none by default, so its values are examples.
    """

    keys: tuple[TemplateKey, ...]
    path: tuple[str, ...] = ()
    help: str = ""
    array: bool = False
