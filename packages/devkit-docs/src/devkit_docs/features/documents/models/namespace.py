"""Document namespaces: packages of a monorepo with their own Living Spec under ``docs/packages/<name>/``."""

from __future__ import annotations

import re
from dataclasses import dataclass

from devkit_docs.base.layout import PACKAGES_DIR

GLOBAL = "global"
NAMESPACE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Namespace:
    """A package of the workspace: ``path`` is its source directory, ``docs`` its Living Spec root."""

    name: str
    path: str

    @property
    def docs(self) -> str:
        return f"{PACKAGES_DIR}/{self.name}"
