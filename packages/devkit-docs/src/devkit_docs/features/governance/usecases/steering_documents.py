"""``RULE-steering-documents``: the steering directory stays flat, ID-free and small enough to list in every context.

``docs/steering/`` holds project-wide background, one Markdown file per topic, whose ``title`` and ``summary``
``devkit get-context spec`` lists in every agent context (``ADR-background-pointer-in-constitution``). The rule keeps
that list short and readable:

- the directory is flat and holds only ``*.md`` files and ``glossary.yaml``;
- each Markdown file other than ``README.md`` is UTF-8, closes its frontmatter within the first 4096 bytes (all
  ``devkit get-context`` reads), and has a non-empty ``title``, a non-empty English ``summary`` of at most
  ``max_summary_length`` characters (default 300), no ``id`` (steering files stay outside the document index) and a
  body (the text after the frontmatter) of at most ``max_body_bytes`` bytes (default 24576);
- at most ``max_files`` Markdown files other than ``README.md`` (default 10): each one beyond the limit, in sorted
  order, is reported whenever any steering file is targeted, so a commit adding a file is refused even when the new
  file sorts before the others.

The same contract holds in the steering directory of every registered namespace, ``docs/packages/<name>/steering/``
(``[[tool.docs.namespaces]]``), one directory at a time: targeting, the ``max_files`` count and the over-cap findings
are per directory, and each message names its own directory. A namespace steering directory holds no glossary: its
``glossary.md`` is reported as belonging at ``docs/packages/<name>/glossary.md`` and its ``glossary.yaml`` as not
allowed (search synonyms are read from ``docs/steering/glossary.yaml`` only); neither counts toward ``max_files``. An
unregistered ``docs/packages/<name>/steering/`` is not checked. Not fixable: background is written, never generated.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_core.base.errors import FrontmatterError
from devkit_core.core import frontmatter

from devkit_docs.features.documents.services.namespaces import docs_roots
from devkit_docs.features.governance import field_line, namespaces
from devkit_docs.utils.text import foreign_letters

RULE_ID = "RULE-steering-documents"
DIRECTORY = "docs/steering"
SYNONYMS = "glossary.yaml"
GLOSSARY = "glossary.md"
INDEX = "README.md"
# The header prefix ``devkit get-context`` reads of each file (devkit-dist ``context_documents.HEADER_LIMIT``).
HEADER_LIMIT = 4096
type Add = Callable[[str, int, str, str], None]


@dataclass(frozen=True)
class SteeringDocumentsSettings:
    max_files: int = 10
    max_body_bytes: int = 24576
    max_summary_length: int = 300


class SteeringDocumentsRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="steering-documents",
            description="Steering documents stay flat, ID-free, summarized in English and within the count and size caps.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=SteeringDocumentsSettings(),
            guide="guide.md",
            related=("docs:living-spec-writing",),
        )

    def validate_settings(self, settings: SteeringDocumentsSettings) -> None:
        for name in ("max_files", "max_body_bytes", "max_summary_length"):
            value = getattr(settings, name)
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    def check(self, ctx: RuleContext) -> list[Violation]:
        found: list[Violation] = []
        for root in docs_roots(namespaces(ctx)):
            found.extend(self._directory(ctx, root))
        return found

    def _directory(self, ctx: RuleContext, root: str) -> list[Violation]:
        """The findings of one steering directory, ``<root>/steering``: the root ``docs/steering`` or a registered
        namespace's ``docs/packages/<name>/steering``; targeting and the ``max_files`` cap apply to it alone."""
        directory = f"{root}/steering"
        namespaced = directory != DIRECTORY
        files = [
            relative
            for path in ctx.cache.find_files(ctx.workspace_root / directory, extensions=None)
            if (relative := ctx.relative_path(path)) is not None
        ]
        if not any(ctx.is_file_targeted(path) for path in files):
            return []
        found: list[Violation] = []

        def add(path: str, line: int, message: str, remediation: str) -> None:
            found.append(Violation(rule_id=self.id, file=path, line=line, message=message, remediation=remediation))

        documents: list[str] = []
        for path in files:
            name = path.removeprefix(f"{directory}/")
            if "/" in name:
                if ctx.is_file_targeted(path):
                    add(
                        path,
                        1,
                        f"steering documents live directly in {directory}/, not in {name.rsplit('/', 1)[0]}/",
                        f"Move the file into {directory}/ or out of the steering directory",
                    )
                continue
            if name == SYNONYMS:
                if namespaced and ctx.is_file_targeted(path):
                    add(
                        path,
                        1,
                        f"{directory}/ holds only Markdown files",
                        f"Remove the file; search synonyms are read from {DIRECTORY}/{SYNONYMS} only",
                    )
                continue
            if not name.endswith(".md"):
                if ctx.is_file_targeted(path):
                    add(
                        path,
                        1,
                        f"{directory}/ holds only Markdown files" + ("" if namespaced else f" and {SYNONYMS}"),
                        "Move the file out of the steering directory",
                    )
                continue
            if name == INDEX:
                continue
            if namespaced and name == GLOSSARY:
                if ctx.is_file_targeted(path):
                    add(
                        path,
                        1,
                        f"the package glossary lives at {root}/{GLOSSARY}, not in {directory}/",
                        f"Move the file to {root}/{GLOSSARY}",
                    )
                continue
            documents.append(path)
            if ctx.is_file_targeted(path):
                self._document(ctx, path, add)
        limit = ctx.settings(self).max_files
        for path in documents[limit:]:
            add(
                path,
                1,
                f"{directory}/ has {len(documents)} Markdown files; at most {limit} are allowed",
                "Merge steering documents by topic, or raise max_files in [rules.settings.RULE-steering-documents]",
            )
        return found

    def _document(self, ctx: RuleContext, path: str, add: Add) -> None:
        text = ctx.cache.read_text_strict(path)
        if text is None:
            add(
                path,
                1,
                "steering document must be UTF-8",
                "Save the file as UTF-8; get-context lists it with null values",
            )
            return
        try:
            parsed = frontmatter.parse(text)
            block = frontmatter.locate(text)
        except FrontmatterError as exc:
            add(path, 1, f"steering document frontmatter is invalid: {exc}", "Write a closed YAML frontmatter block")
            return
        if block is not None and (size := len(text[: block.end].encode("utf-8"))) > HEADER_LIMIT:
            add(
                path,
                1,
                f"frontmatter ends at byte {size}; get-context reads only the first {HEADER_LIMIT} bytes",
                "Keep only `title` and `summary` in the frontmatter",
            )
        header = parsed.data or {}
        settings = ctx.settings(self, path)
        if "id" in header:
            add(
                path,
                field_line(text, "id"),
                "steering documents carry no id",
                "Remove `id:`; a steering document is read by path, and a document with an ID belongs to its kind",
            )
        title = header.get("title")
        if not isinstance(title, str) or not title.strip():
            add(
                path,
                field_line(text, "title") if "title" in header else 1,
                "steering document has no title",
                "Write `title:`",
            )
        self._summary(path, text, header, settings.max_summary_length, add)
        size = len(parsed.body.encode("utf-8"))
        if size > settings.max_body_bytes:
            add(
                path,
                parsed.body_line,
                f"body has {size} bytes; at most {settings.max_body_bytes} are allowed",
                "Split the topic into another steering document, or raise max_body_bytes",
            )

    @staticmethod
    def _summary(path: str, text: str, header: dict[str, object], limit: int, add: Add) -> None:
        value = header.get("summary")
        line = field_line(text, "summary") if "summary" in header else 1
        remediation = (
            "Write `summary:`: one English sentence saying when an agent reads this file"
            " (it is listed in every agent context)"
        )
        if not isinstance(value, str) or not value.strip():
            add(path, line, "steering document has no summary", remediation)
            return
        letters = foreign_letters(value)
        if letters:
            add(path, line, f"summary must be English; it contains {''.join(letters[:5])}", remediation)
        elif len(value.strip()) > limit:
            add(path, line, f"summary has {len(value.strip())} characters ({limit} at most)", remediation)
