"""Policy problems that name the rule they concern."""

from __future__ import annotations


class PolicyError(str):
    """A human-readable policy problem; ``rule_id`` is the rule it concerns, if any.

    It is a ``str``, so lists of policy errors print and compare as messages.
    """

    rule_id: str | None

    def __new__(cls, message: str, rule_id: str | None = None) -> PolicyError:
        instance = super().__new__(cls, message)
        instance.rule_id = rule_id
        return instance
