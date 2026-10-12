"""Shared foundation for devkit packages.

One implementation of what several packages need to agree on: the frontmatter
grammar, the installation receipt, safe workspace-relative paths, the Git
runner, plugin file loading and project discovery. Free of import-time side
effects; the only third-party dependency is PyYAML, and the only devkit module
it imports is ``devkit.advisory`` (every core error is an ``AdvisoryError``).

Frontmatter functions are used through their module
(``devkit.core.frontmatter.parse`` / ``locate`` / ``load_header``).
"""

from devkit.core.errors import (
    AssetFileError,
    ConfigError,
    DevkitCoreError,
    FrontmatterError,
    GitError,
    ReceiptError,
    UnsafePathError,
)
from devkit.core.frontmatter import Frontmatter, FrontmatterBlock
from devkit.core.git import run_git
from devkit.core.paths import is_safe_relpath, normalize_relpath, resolve_within
from devkit.core.plugins import LoadedPlugin, PluginFailure, PluginLoad, iter_plugin_files, load_subclasses
from devkit.core.project import find_project_root, git_toplevel, read_project_config
from devkit.core.receipt import (
    CONFIG_PATH,
    RECEIPT_PATH,
    AssetRecord,
    FileRecord,
    OverrideRecord,
    PackageRecord,
    Receipt,
    SeededRecord,
    Selection,
    ToolRecord,
    load_receipt,
    parse_receipt,
    verified_asset_file,
)

__all__ = [
    "CONFIG_PATH",
    "RECEIPT_PATH",
    "AssetFileError",
    "AssetRecord",
    "ConfigError",
    "DevkitCoreError",
    "FileRecord",
    "Frontmatter",
    "FrontmatterBlock",
    "FrontmatterError",
    "GitError",
    "LoadedPlugin",
    "OverrideRecord",
    "PackageRecord",
    "PluginFailure",
    "PluginLoad",
    "Receipt",
    "ReceiptError",
    "SeededRecord",
    "Selection",
    "ToolRecord",
    "UnsafePathError",
    "find_project_root",
    "git_toplevel",
    "is_safe_relpath",
    "iter_plugin_files",
    "load_receipt",
    "load_subclasses",
    "normalize_relpath",
    "parse_receipt",
    "read_project_config",
    "resolve_within",
    "run_git",
    "verified_asset_file",
]
