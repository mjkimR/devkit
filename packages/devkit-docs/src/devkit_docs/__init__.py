"""devkit-docs: the devkit document system.

The package registers the ``devkit docs`` command group (``devkit.commands``, ``devkit_docs.cli``) and the
``[tool.docs]`` config template. It knows no delivery process: a process such as devkit-spec builds on its
document model and registers its own display through ``devkit.docs.status_overlay``. Importing it has no side
effects.
"""
