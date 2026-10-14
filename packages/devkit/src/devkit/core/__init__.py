"""Shared foundation for devkit packages.

One implementation of what several packages need to agree on: the frontmatter
grammar, the installation receipt, safe workspace-relative paths, atomic file
replacement, the Git runner, plugin package loading, project discovery and configuration reading, and
the command-line plumbing every command group uses (``devkit.core.cli``, the
only module that imports click; it is not imported here). Free of import-time
side effects; the only devkit module it imports is ``devkit.advisory`` (every
core error is an ``AdvisoryError``).

Frontmatter functions are used through their module
(``devkit.core.frontmatter.parse`` / ``locate`` / ``load_header``), as are the
config template's (``devkit.core.config_template.render_tool_template`` /
``uncomment``).
"""

from devkit.core.config_template import TemplateKey, TemplateTable
from devkit.core.errors import (
    ArgumentError,
    AssetFileError,
    CommandPluginError,
    ConfigError,
    DevkitCoreError,
    FrontmatterError,
    GitError,
    ReceiptError,
    UnsafePathError,
)
from devkit.core.files import atomic_write_bytes, atomic_write_text
from devkit.core.frontmatter import Frontmatter, FrontmatterBlock
from devkit.core.git import run_git
from devkit.core.paths import is_safe_relpath, normalize_relpath, resolve_within
from devkit.core.plugins import (
    LoadedPlugin,
    PluginFailure,
    PluginLoad,
    PluginPackage,
    iter_plugin_packages,
    load_subclasses,
)
from devkit.core.project import (
    config_table,
    find_project_root,
    git_toplevel,
    read_project_config,
    read_toml,
    require_devkit_root,
    require_git_toplevel,
)
from devkit.core.receipt import (
    AGENTS_FILE,
    CONFIG_PATH,
    GUIDANCE_END,
    GUIDANCE_START,
    MANAGED_PATH,
    OVERRIDES_PATH,
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
    verified_asset_packages,
)

__all__ = [
    "AGENTS_FILE",
    "CONFIG_PATH",
    "GUIDANCE_END",
    "GUIDANCE_START",
    "MANAGED_PATH",
    "OVERRIDES_PATH",
    "RECEIPT_PATH",
    "ArgumentError",
    "AssetFileError",
    "AssetRecord",
    "CommandPluginError",
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
    "PluginPackage",
    "Receipt",
    "ReceiptError",
    "SeededRecord",
    "Selection",
    "TemplateKey",
    "TemplateTable",
    "ToolRecord",
    "UnsafePathError",
    "atomic_write_bytes",
    "atomic_write_text",
    "config_table",
    "find_project_root",
    "git_toplevel",
    "is_safe_relpath",
    "iter_plugin_packages",
    "load_receipt",
    "load_subclasses",
    "normalize_relpath",
    "parse_receipt",
    "read_project_config",
    "read_toml",
    "require_devkit_root",
    "require_git_toplevel",
    "resolve_within",
    "run_git",
    "verified_asset_file",
    "verified_asset_packages",
]
