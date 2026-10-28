"""Document indexing and targeting shared by the spec governance rules.

Each rule is a ``BaseRule`` subclass under ``governance/usecases``; the bundle
ships one directory per rule, as devkit's own rules are laid out: ``bundle/rules/<name>/rule.py``, a
thin subclass (``devkit rules`` instantiates only the classes a rule file
defines), and ``guide.md`` beside it (``guide="guide.md"`` resolves relative to
the deployed ``rule.py``). The rule's tests sit in ``tests/test_rule.py`` of
the same folder and deploy with it: they load the folder with
``devkit_agt.features.rules.services.testing.load_rule``, so they exercise the deployed subclass and
this implementation together, and ``devkit rules test`` runs them.
``related`` names the bundle instructions that hold a rule's judgment. The
rules read documents through ``document_index``,
which goes through the run's workspace cache: a Git snapshot run
(``check --staged``, ``--ci``) sees the snapshot, and a fix is seen by the
recheck.

Reporting follows devkit's targeting: a violation is reported for a file only
when ``ctx.is_file_targeted`` accepts it. Files of completed spec bundles are
work history and are checked only when named as explicit targets.

Document namespaces (``[[tool.docs.namespaces]]``) are read with
``namespaces(ctx)``: a namespace docs root ``docs/packages/<name>/`` holds
Living Spec documents under the same conventions as ``docs/``. A malformed
``[tool.docs]`` table is not a violation: ``DocsConfigError`` propagates and
fails the run (``DOCS_CONFIG_INVALID`` with the rule's ID, exit 2), as devkit treats its own
malformed configuration, because no document can be checked against a
namespace registry that cannot be read.
"""

from __future__ import annotations

import re
from pathlib import Path

from devkit_agt.features.rules import RuleContext
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION as DEVKIT

from devkit_docs.base.layout import PROPOSAL_FILE, PROPOSALS
from devkit_docs.features.documents import SOURCE_DIRECTORIES, Document, DocumentIndex
from devkit_docs.features.documents.models.namespace import Namespace
from devkit_docs.features.documents.repositories.config import read_docs_config

FIX_COMMAND = f"{DEVKIT} rules fix"
CACHE_KEY = "devkit_docs.document_index"


def document_index(ctx: RuleContext) -> DocumentIndex:
    """The document index of the run's workspace, read through its cache."""
    root = ctx.workspace_root

    def _load() -> DocumentIndex:
        def read(path: Path) -> str:
            return ctx.cache.read_bytes(path).decode("utf-8")

        files = [
            path
            for directory in SOURCE_DIRECTORIES
            if (root / directory).is_dir()
            for path in ctx.cache.find_files(root / directory, extensions=(".md",))
        ]
        return DocumentIndex.load(root, files=files, read=read)

    return ctx.cache.get_or_compute(CACHE_KEY, _load)


def field_line(text: str, key: str) -> int:
    """The 1-based line of the first top-level ``key:`` line of ``text``'s frontmatter (core grammar: byte order
    mark, ``---`` or ``...`` closer); 1 when the text has no frontmatter, an unclosed one, or no such line."""
    try:
        block = locate(text)
    except FrontmatterError:
        return 1
    if block is None:
        return 1
    match = re.search(rf"^{re.escape(key)}[ \t]*:", block.header, re.M)
    if match is None:
        return 1
    return text.count("\n", 0, block.header_start + match.start()) + 1


def namespaces(ctx: RuleContext) -> tuple[Namespace, ...]:
    """The document namespaces of the run's workspace; raises ``DocsConfigError`` for a malformed ``[tool.docs]``."""
    return read_docs_config(ctx.workspace_root).namespaces


def explicitly_targeted(ctx: RuleContext, path: str) -> bool:
    """Whether the run named ``path`` as a target (not merely a whole-workspace run)."""
    return ctx.has_targets and path in ctx.changed_files


def reportable(ctx: RuleContext, index: DocumentIndex, document: Document) -> bool:
    """Whether violations in ``document`` are reported: targeted, and current unless explicitly targeted."""
    if not ctx.is_file_targeted(document.path):
        return False
    return not index.is_historical(document) or explicitly_targeted(ctx, document.path)


def is_proposal_anchor(path: str) -> bool:
    """Whether ``path`` is a proposal anchor: ``docs/proposals/PROP-<slug>/proposal.md`` or a single-file proposal
    ``docs/proposals/PROP-<slug>.md``."""
    if not path.startswith(f"{PROPOSALS}/"):
        return False
    parts = path.removeprefix(f"{PROPOSALS}/").split("/")
    if len(parts) == 1:
        return parts[0].startswith("PROP-") and parts[0].endswith(".md")
    return len(parts) == 2 and parts[0].startswith("PROP-") and parts[1] == PROPOSAL_FILE


def is_material(document: Document) -> bool:
    """Free-form materials (``docs/materials/``, any ``/materials/`` directory) follow no authoring convention."""
    return document.path.startswith("docs/materials/") or "/materials/" in document.path
