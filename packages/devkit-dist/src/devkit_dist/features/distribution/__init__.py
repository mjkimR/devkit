"""Devkit bundle distribution: validate and package bundles, synchronize them into projects.

The feature root exports nothing and imports nothing, so loading one module of the feature never loads the rest;
import each name from the module that defines it. Results are frozen dataclasses in ``models.results`` (with
``usecases.status`` and ``services.installation.plan``) whose ``to_dict()`` is the JSON object the command prints.
Every operation raises an ``AdvisoryError``: a ``DistributionError`` subclass from ``models.errors``
(``BUNDLE_INVALID``, ``SYNC_CONFLICT``, ``LOCK_HELD``, ...) or a ``devkit_dist.base.errors`` error it passes
through (``RECEIPT_INVALID``, ``CONFIG_INVALID``, ``ARGUMENT_INVALID``). What a successful sync still reports is
collected as coded ``SyncNotice`` entries in ``SyncResult.notices``. The receipt model is
``devkit_dist.features.project.repositories.receipt``.
"""
