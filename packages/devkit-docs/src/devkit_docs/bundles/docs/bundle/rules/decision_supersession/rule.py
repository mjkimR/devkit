"""Deployed wrapper for the report-only ADR supersession rule."""

from devkit_docs.features.governance.usecases.decision_supersession import DecisionSupersessionRule as _Implementation


class DecisionSupersessionRule(_Implementation):
    """Keep whole and partial ADR replacement records consistent."""
