"""The delivery workflow engine as a library (``devkit workflow`` is a thin CLI over it).

Start from ``Workspace``: it loads the project's configuration, definitions,
roles and plugin checks, resolves a unit directory (``resolve_unit``) and
evaluates it with the project's policies (``evaluate_unit``), including the
drift guard. ``create_unit``, ``list_units``, ``record_answer``,
``return_to``, ``plan_handoff``/``apply_handoff`` and the envelope helpers
cover the commands; ``evaluate`` is the pure evaluation underneath. Errors are
``WorkflowError`` instances with a stable ``code``.
"""

from devkit.workflow.answers import record_answer, return_to, validate_answer
from devkit.workflow.binding import Binding, HistoryEntry, read_binding, write_binding
from devkit.workflow.checks import Check, CheckClass, CheckError, CheckResult, Invocation, Registry, parse_check
from devkit.workflow.config import ConfigError, WorkflowConfig, load_workflow_config
from devkit.workflow.decisions import Decision, DecisionError, Decisions, load_decisions, new_decision, write_decision
from devkit.workflow.definition import (
    Candidate,
    DefinitionError,
    Problem,
    Return,
    Stage,
    WorkflowDocument,
    load,
    parse,
    schema_hash,
)
from devkit.workflow.discovery import discover, find, load_all, resolve
from devkit.workflow.envelope import (
    AuthoringError,
    Envelope,
    EnvelopeError,
    Envelopes,
    Finding,
    compose,
    load_envelopes,
    render_envelope,
    write_next,
)
from devkit.workflow.errors import AnchorInvalidError, DriftError, UnitNotFoundError, WorkflowError
from devkit.workflow.evaluate import LintFunc, Options, evaluate
from devkit.workflow.git import is_ancestor
from devkit.workflow.handoff import CandidateResult, Handoff, HandoffOutcome, HandoffPlan, apply_handoff, plan_handoff
from devkit.workflow.layout import LayoutSpec, TemplateLayout, parse_layout_spec, validate_template
from devkit.workflow.lint import rules_lint
from devkit.workflow.plugins import BaseCheck, CheckContext, PluginError, load_check_files, load_plugin_checks
from devkit.workflow.render import render_document, render_requests, render_result
from devkit.workflow.requests import Option, Request, Target
from devkit.workflow.results import Delegate, Drift, Gate, Result, Skipped, Waiting
from devkit.workflow.roles import discover_roles
from devkit.workflow.units import UnitInfo, create_unit, list_units
from devkit.workflow.validation import (
    DefinitionReport,
    ValidationReport,
    shared_stage_problems,
    validate,
    validate_workspace,
)
from devkit.workflow.workspace import UnitRef, Workspace, record_return

__all__ = [
    "AnchorInvalidError",
    "AuthoringError",
    "BaseCheck",
    "Binding",
    "Candidate",
    "CandidateResult",
    "Check",
    "CheckClass",
    "CheckContext",
    "CheckError",
    "CheckResult",
    "ConfigError",
    "Decision",
    "DecisionError",
    "Decisions",
    "DefinitionError",
    "DefinitionReport",
    "Delegate",
    "Drift",
    "DriftError",
    "Envelope",
    "EnvelopeError",
    "Envelopes",
    "Finding",
    "Gate",
    "Handoff",
    "HandoffOutcome",
    "HandoffPlan",
    "HistoryEntry",
    "Invocation",
    "LayoutSpec",
    "LintFunc",
    "Option",
    "Options",
    "PluginError",
    "Problem",
    "Registry",
    "Request",
    "Result",
    "Return",
    "Skipped",
    "Stage",
    "Target",
    "TemplateLayout",
    "UnitInfo",
    "UnitNotFoundError",
    "UnitRef",
    "ValidationReport",
    "Waiting",
    "WorkflowConfig",
    "WorkflowDocument",
    "WorkflowError",
    "Workspace",
    "apply_handoff",
    "compose",
    "create_unit",
    "discover",
    "discover_roles",
    "evaluate",
    "find",
    "is_ancestor",
    "list_units",
    "load",
    "load_all",
    "load_check_files",
    "load_decisions",
    "load_envelopes",
    "load_plugin_checks",
    "load_workflow_config",
    "new_decision",
    "parse",
    "parse_check",
    "parse_layout_spec",
    "plan_handoff",
    "read_binding",
    "record_answer",
    "record_return",
    "render_document",
    "render_envelope",
    "render_requests",
    "render_result",
    "resolve",
    "return_to",
    "rules_lint",
    "schema_hash",
    "shared_stage_problems",
    "validate",
    "validate_answer",
    "validate_template",
    "validate_workspace",
    "write_binding",
    "write_decision",
    "write_next",
]
