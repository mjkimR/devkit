"""``RULE-secret-leak``: credentials never enter a commit. Code in ``rule.py``, guide in ``guide.md``."""

from __future__ import annotations

from devkit_agt.features.rules.services.builtins.secret_leak.rule import SecretLeakRule

__all__ = ["SecretLeakRule"]
