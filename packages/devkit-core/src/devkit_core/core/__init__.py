"""Shared foundation; no project configuration, receipts or transport runtime."""

from devkit_core.base.errors import (
    ArgumentError,
    DeadlineExceededError,
    DevkitCoreError,
    FrontmatterError,
    GitError,
    LockHeldError,
    LockUnsupportedError,
    UnsafePathError,
)
from devkit_core.core.deadline import Deadline
from devkit_core.core.files import atomic_write_bytes, atomic_write_text, remove_empty_tree
from devkit_core.core.frontmatter import Frontmatter, FrontmatterBlock
from devkit_core.core.git import run_git
from devkit_core.core.locks import file_lock
from devkit_core.core.paths import is_safe_relpath, normalize_relpath, resolve_within
from devkit_core.core.plugins import (
    LoadedPlugin,
    PluginFailure,
    PluginLoad,
    PluginPackage,
    iter_plugin_packages,
    load_subclasses,
)

__all__ = [
    "ArgumentError",
    "Deadline",
    "DeadlineExceededError",
    "DevkitCoreError",
    "Frontmatter",
    "FrontmatterBlock",
    "FrontmatterError",
    "GitError",
    "LoadedPlugin",
    "LockHeldError",
    "LockUnsupportedError",
    "PluginFailure",
    "PluginLoad",
    "PluginPackage",
    "UnsafePathError",
    "atomic_write_bytes",
    "atomic_write_text",
    "file_lock",
    "is_safe_relpath",
    "iter_plugin_packages",
    "load_subclasses",
    "normalize_relpath",
    "remove_empty_tree",
    "resolve_within",
    "run_git",
]
