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
    YamlBindingUnavailableError,
)
from devkit_core.core.deadline import Deadline
from devkit_core.core.files import atomic_write_bytes, atomic_write_text, remove_empty_tree
from devkit_core.core.frontmatter import Frontmatter, FrontmatterBlock
from devkit_core.core.git import (
    StatusRecord,
    WorktreeRecord,
    changed_paths,
    dirty_paths,
    git_config,
    is_ancestor,
    parse_status_records,
    parse_worktree_records,
    run_git,
    run_git_text,
    status_records,
    worktree_records,
)
from devkit_core.core.locks import file_lock, flock_fd
from devkit_core.core.paths import display_path, is_safe_relpath, normalize_relpath, resolve_within
from devkit_core.core.plugins import (
    LoadedPlugin,
    PluginFailure,
    PluginLoad,
    PluginPackage,
    iter_plugin_packages,
    load_subclasses,
)
from devkit_core.core.yaml import require_libyaml, safe_compose, safe_load

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
    "StatusRecord",
    "UnsafePathError",
    "WorktreeRecord",
    "YamlBindingUnavailableError",
    "atomic_write_bytes",
    "atomic_write_text",
    "changed_paths",
    "dirty_paths",
    "display_path",
    "file_lock",
    "flock_fd",
    "git_config",
    "is_ancestor",
    "is_safe_relpath",
    "iter_plugin_packages",
    "load_subclasses",
    "normalize_relpath",
    "parse_status_records",
    "parse_worktree_records",
    "remove_empty_tree",
    "require_libyaml",
    "resolve_within",
    "run_git",
    "run_git_text",
    "safe_compose",
    "safe_load",
    "status_records",
    "worktree_records",
]
