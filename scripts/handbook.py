"""Report, regenerate and verify the release handbook under ``handbook/`` (``CAP-DLV-release-handbook``).

The handbook is a derived view of the Living Spec for people: English pages are written from ``docs/``, other
languages are translated from English. This script owns its deterministic parts and checks; the narrative is written
by an agent following the ``devkit-dev/handbook`` playbook, and only a refresh the user requests runs it.

- ``status``: stale English pages, stale translations, uncited use cases and capabilities, parity and term gaps.
- ``stamp``: record pages as refreshed (source blob SHAs, or the English narrative hash a translation follows).
- ``generate [--preview]``: provenance headers, generated sections and pages, and ``manifest.json``.
- ``verify``: the checks a refreshed handbook passes before it is committed.
- ``release-check <tag>``: in ``scripts/release.sh``; verifies only a release the handbook was refreshed for.

stdout carries one-line sentinels; exit ``0`` clean, ``1`` findings, ``2`` could not run.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import click
import yaml
from devkit.advisory import Actor, AdvisoryError, Retry
from devkit_dist.adapters.cli import boundary

ROOT = Path(__file__).resolve().parents[1]
HANDBOOK = "handbook"
PREVIEW = "dist/handbook-preview"
MANIFEST = "manifest.json"
PIVOT = "en"
DEFAULT_LANGS = ("en", "ko")
TERMS = "terms.yaml"
# Pages the script writes whole in every language; they carry `generated: true` and are never translated.
GENERATED_PAGES = ("decisions.md", "changes.md", "glossary.md")
SOURCE_DIRECTORIES = ("docs", "specs")
KINDS = {"UC": "usecase", "CAP": "capability", "ADR": "decision", "ARCH": "architecture", "SPEC": "spec"}

PROVENANCE_START = "<!-- handbook:provenance -->"
PROVENANCE_END = "<!-- /handbook:provenance -->"
GENERATED_START = re.compile(r"^<!-- handbook:generated ([a-z][a-z0-9-]*) -->$")
GENERATED_END = "<!-- /handbook:generated -->"
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
DOCUMENT_ID = re.compile(r"^(?:UC|CAP|ADR|ARCH|SPEC)-[A-Za-z0-9][A-Za-z0-9-]*$")
NORMATIVE = re.compile(r"\b(MUST|SHALL|SHOULD|MAY)\b")
SOURCE_LINK = re.compile(r"https://github\.com/([^/\s)]+/[^/\s)]+)/blob/([^/\s)]+)/([^\s)#]+)")
GLOSSARY_ROW = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|")

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "provenance": (
            "Snapshot of devkit {release} at source commit `{commit}`, generated {date}. The Living Spec under"
            " `docs/` prevails on any conflict; this page is not updated between refreshes."
        ),
        "unreleased": "(unreleased preview)",
        "english": "",
        "decisions": "Decisions",
        "decisions_intro": "The accepted decisions of this snapshot, each with its summary and source.",
        "changes": "Changes",
        "changes_first": "This is the first handbook snapshot.",
        "changes_since": "Since the handbook snapshot {previous}:",
        "changes_decisions": "New decisions",
        "changes_specs": "Completed specs",
        "changes_none": "None.",
        "glossary": "Glossary",
        "glossary_intro": "The terms of devkit as its documents use them, from the Living Spec glossary.",
        "term": "Term",
        "rendering": "Rendering",
        "definition": "Definition",
        "owner": "Owner",
    },
    "ko": {
        "provenance": (
            "소스 커밋 `{commit}` 기준 devkit {release} 스냅숏이며 {date}에 생성되었습니다. 내용이 다르면"
            " `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다."
        ),
        "unreleased": "(릴리스 전 미리보기)",
        "english": " (영어 원문)",
        "decisions": "결정",
        "decisions_intro": "이 스냅숏에서 채택된 결정의 요약과 원문 링크입니다.",
        "changes": "변경 사항",
        "changes_first": "첫 번째 핸드북 스냅숏입니다.",
        "changes_since": "핸드북 스냅숏 {previous} 이후:",
        "changes_decisions": "새 결정",
        "changes_specs": "완료된 스펙",
        "changes_none": "없음.",
        "glossary": "용어집",
        "glossary_intro": "devkit 문서가 쓰는 용어이며 Living Spec 용어집에서 생성됩니다.",
        "term": "용어",
        "rendering": "번역어",
        "definition": "정의",
        "owner": "출처",
    },
}


class HandbookError(AdvisoryError):
    """The handbook command could not run; the code names the cause."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


# --- git -----------------------------------------------------------------------------------------------------------


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise HandbookError(
            f"git {' '.join(args)} failed",
            result.stderr.strip(),
            code="HANDBOOK_GIT_FAILED",
            fix="Run the command in a Git checkout of the repository with the named revision",
        )
    return result.stdout


def has_object(root: Path, spec: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", spec], cwd=root, capture_output=True, check=False).returncode == 0


def read_blobs(root: Path, shas: Iterable[str]) -> dict[str, str]:
    """The text of each blob, read with one ``git cat-file --batch``."""
    wanted = list(dict.fromkeys(shas))
    if not wanted:
        return {}
    output = subprocess.run(
        ["git", "cat-file", "--batch"], cwd=root, input="\n".join(wanted).encode() + b"\n", capture_output=True
    ).stdout
    texts: dict[str, str] = {}
    offset = 0
    for sha in wanted:
        header_end = output.index(b"\n", offset)
        header = output[offset:header_end].split()
        offset = header_end + 1
        if len(header) < 3 or header[1] != b"blob":
            continue
        size = int(header[2])
        texts[sha] = output[offset : offset + size].decode("utf-8", errors="replace")
        offset += size + 1
    return texts


# --- documents ------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Document:
    id: str
    kind: str
    path: str
    blob: str
    title: str
    summary: str
    status: str


@dataclass
class Documents:
    """The Living Spec and spec documents at one commit, by ID and alias."""

    commit: str
    by_id: dict[str, Document] = field(default_factory=dict)
    paths: frozenset[str] = frozenset()

    def get(self, identifier: str) -> Document | None:
        return self.by_id.get(identifier)

    def canonical(self) -> list[Document]:
        seen: dict[str, Document] = {}
        for document in self.by_id.values():
            seen.setdefault(document.id, document)
        return sorted(seen.values(), key=lambda document: document.id)

    def of_kind(self, kind: str) -> list[Document]:
        return [document for document in self.canonical() if document.kind == kind]


def frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """The YAML frontmatter of a Markdown text and the body after it; no frontmatter is ``{}``."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return {}, text
    return (meta if isinstance(meta, dict) else {}), text[end + 5 :]


def load_documents(root: Path, commit: str) -> Documents:
    listing = git(root, "ls-tree", "-r", commit, "--", *SOURCE_DIRECTORIES)
    entries: list[tuple[str, str]] = []
    for line in listing.splitlines():
        meta_part, _, path = line.partition("\t")
        parts = meta_part.split()
        if len(parts) == 3 and parts[1] == "blob":
            entries.append((parts[2], path))
    all_paths = frozenset(git(root, "ls-tree", "-r", "--name-only", commit).splitlines())
    texts = read_blobs(root, (sha for sha, path in entries if path.endswith(".md")))
    documents = Documents(commit=commit, paths=all_paths)
    for sha, path in entries:
        if sha not in texts:
            continue
        meta, _ = frontmatter(texts[sha])
        identifier = meta.get("id")
        if not isinstance(identifier, str):
            continue
        kind = KINDS.get(identifier.split("-", 1)[0])
        if kind is None:
            continue
        document = Document(
            id=identifier,
            kind=kind,
            path=path,
            blob=sha,
            title=str(meta.get("title", identifier)),
            summary=" ".join(str(meta.get("summary", "")).split()),
            status=str(meta.get("status", "")),
        )
        documents.by_id[identifier] = document
        aliases = meta.get("aliases") or []
        for alias in aliases if isinstance(aliases, list) else []:
            documents.by_id.setdefault(str(alias), document)
    return documents


@dataclass(frozen=True)
class Term:
    section: str
    term: str
    definition: str
    owner: str


def glossary_terms(text: str) -> list[Term]:
    """The rows of the glossary's term tables, with the section heading each belongs to."""
    terms: list[Term] = []
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        match = GLOSSARY_ROW.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if len(cells) < 3:
            continue
        terms.append(Term(section=section, term=match.group(1).strip(), definition=cells[1], owner=cells[2]))
    return terms


# --- pages ----------------------------------------------------------------------------------------------------------


@dataclass
class Page:
    """One handbook page: ``rel`` is ``<lang>/<path>``."""

    rel: str
    meta: dict[str, Any]
    body: str

    @property
    def lang(self) -> str:
        return self.rel.split("/", 1)[0]

    @property
    def path(self) -> str:
        return self.rel.split("/", 1)[1]

    @property
    def generated(self) -> bool:
        return bool(self.meta.get("generated"))

    def render(self) -> str:
        if not self.meta:
            return self.body
        header = yaml.safe_dump(self.meta, sort_keys=True, allow_unicode=True, default_flow_style=False)
        return f"---\n{header}---\n{self.body}"

    @property
    def title(self) -> str:
        for line in self.body.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return self.path


def read_page(directory: Path, rel: str) -> Page:
    meta, body = frontmatter((directory / rel).read_text(encoding="utf-8"))
    return Page(rel=rel, meta=meta, body=body)


def page_names(directory: Path, lang: str) -> list[str]:
    base = directory / lang
    if not base.is_dir():
        return []
    return sorted(path.relative_to(base).as_posix() for path in base.rglob("*.md"))


def strip_blocks(body: str) -> list[str]:
    """The body's lines without the provenance block and the generated blocks."""
    kept: list[str] = []
    skipping: str | None = None
    for line in body.splitlines():
        stripped = line.strip()
        if skipping is None and stripped == PROVENANCE_START:
            skipping = PROVENANCE_END
            continue
        if skipping is None and GENERATED_START.match(stripped):
            skipping = GENERATED_END
            continue
        if skipping is not None:
            if stripped == skipping:
                skipping = None
            continue
        kept.append(line.rstrip())
    return kept


def narrative_hash(body: str) -> str:
    """The hash of a page's narrative: the body without provenance and generated blocks, with runs of blank lines
    collapsed, so inserting or removing a block never changes it."""
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(strip_blocks(body))).strip()  # blocks leave blank lines
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def set_provenance(body: str, sentence: str) -> str:
    block = f"{PROVENANCE_START}\n> {sentence}\n{PROVENANCE_END}"
    lines = body.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == PROVENANCE_START), None)
    if start is not None:
        end = next((i for i in range(start, len(lines)) if lines[i].strip() == PROVENANCE_END), start)
        lines[start : end + 1] = block.splitlines()
    else:
        heading = next((i for i, line in enumerate(lines) if line.startswith("# ")), -1)
        lines[heading + 1 : heading + 1] = ["", *block.splitlines()]
    return "\n".join(lines).rstrip("\n") + "\n"


def unclosed_block(body: str) -> int | None:
    """The body line (from 1) of a provenance or generated block that has no end marker, else ``None``."""
    opened: tuple[int, str] | None = None
    for number, line in enumerate(body.splitlines(), start=1):
        stripped = line.strip()
        if opened is None:
            if stripped == PROVENANCE_START:
                opened = (number, PROVENANCE_END)
            elif GENERATED_START.match(stripped):
                opened = (number, GENERATED_END)
        elif stripped == opened[1]:
            opened = None
    return opened[0] if opened else None


def require_closed_blocks(directory: Path, langs: Iterable[str]) -> None:
    """Refuse to generate over a page whose block has no end marker: its narrative would be replaced."""
    for lang in langs:
        for name in page_names(directory, lang):
            page = read_page(directory, f"{lang}/{name}")
            if (line := unclosed_block(page.body)) is not None:
                at = line + body_offset(page, directory)
                raise HandbookError(
                    f"{lang}/{name}:{at} opens a handbook block without its end marker",
                    code="HANDBOOK_BLOCK_UNCLOSED",
                    fix="Close the block with its end marker (<!-- /handbook:generated --> or"
                    " <!-- /handbook:provenance -->), then rerun",
                    target_files=[f"{HANDBOOK}/{lang}/{name}"],
                )


def fill_blocks(body: str, render: dict[str, str]) -> str:
    """Replace the content of every generated block ``render`` names; other text stays as it is."""
    out: list[str] = []
    lines = body.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = GENERATED_START.match(line.strip())
        out.append(line)
        index += 1
        if not match or match.group(1) not in render:
            continue
        while index < len(lines) and lines[index].strip() != GENERATED_END:
            index += 1
        out.extend(render[match.group(1)].rstrip("\n").splitlines())
        if index < len(lines):
            out.append(lines[index])
            index += 1
        else:
            out.append(GENERATED_END)
    return "\n".join(out).rstrip("\n") + "\n"


def prose(body: str) -> Iterator[tuple[int, str]]:
    """``(line number, text)`` of body lines outside fenced code; numbers count from the body's first line."""
    fenced = False
    for number, line in enumerate(body.splitlines(), start=1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def body_offset(page: Page, directory: Path) -> int:
    """Lines before the body in the file, so findings name file line numbers."""
    text = (directory / page.rel).read_text(encoding="utf-8")
    return text[: len(text) - len(page.body)].count("\n")


# --- manifest -------------------------------------------------------------------------------------------------------


def read_manifest(directory: Path) -> dict[str, Any] | None:
    path = directory / MANIFEST
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise _manifest_invalid(path, str(exc)) from None
    langs = data.get("langs") if isinstance(data, dict) else None
    if not isinstance(langs, list) or PIVOT not in langs or not isinstance(data.get("source_commit"), str):
        raise _manifest_invalid(path, "expected source_commit and langs including en")
    return data


def require_manifest(directory: Path) -> dict[str, Any]:
    manifest = read_manifest(directory)
    if manifest is None:
        raise _manifest_invalid(directory / MANIFEST, "no manifest")
    return manifest


def _manifest_invalid(path: Path, detail: str) -> HandbookError:
    return HandbookError(
        f"{path} is not a valid handbook manifest",
        detail,
        code="HANDBOOK_MANIFEST_INVALID",
        fix="Run `just handbook generate` to write the manifest",
        target_files=[str(path)],
    )


def require_source(root: Path, commit: str) -> None:
    if not has_object(root, f"{commit}^{{commit}}"):
        raise HandbookError(
            f"the manifest source commit {commit} is not in this repository",
            code="HANDBOOK_SOURCE_UNAVAILABLE",
            fix="Fetch the full history (a release checkout uses fetch-depth 0) and rerun",
        )


# --- findings -------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    kind: str  # the sentinel kind
    fields: tuple[tuple[str, str], ...]

    def line(self) -> str:
        return f"[{self.kind}: " + " ".join(f"{key}={value}" for key, value in self.fields) + "]"


@dataclass(frozen=True)
class Invalid:
    page: str
    line: int
    code: str
    detail: str

    def sentinel(self) -> str:
        detail = self.detail.replace('"', "'")
        return f'[HANDBOOK_INVALID: page={self.page} line={self.line} code={self.code} detail="{detail}"]'


@dataclass
class Status:
    stale: list[Finding] = field(default_factory=list)
    translations: list[Finding] = field(default_factory=list)
    gaps: list[Finding] = field(default_factory=list)
    parity: list[Finding] = field(default_factory=list)
    terms: list[Finding] = field(default_factory=list)

    def all(self) -> list[Finding]:
        return [*self.stale, *self.translations, *self.gaps, *self.parity, *self.terms]


def langs_of(manifest: dict[str, Any] | None) -> list[str]:
    return list(manifest["langs"]) if manifest else list(DEFAULT_LANGS)


def collect_status(root: Path, directory: Path, documents: Documents, langs: list[str]) -> Status:
    status = Status()
    english = page_names(directory, PIVOT)
    cited: set[str] = set()
    for name in english:
        page = read_page(directory, f"{PIVOT}/{name}")
        if page.generated:
            continue
        sources = page.meta.get("sources") or {}
        changed = []
        for identifier, sha in sources.items() if isinstance(sources, dict) else []:
            document = documents.get(str(identifier))
            if document is None or document.blob != sha:
                changed.append(str(identifier))
            if document is not None:
                cited.add(document.id)
        if changed:
            status.stale.append(Finding("HANDBOOK_STALE", (("page", page.rel), ("sources", ",".join(changed)))))
    for document in [*documents.of_kind("usecase"), *documents.of_kind("capability")]:
        if document.id not in cited and document.status != "deprecated":
            status.gaps.append(Finding("HANDBOOK_GAP", (("id", document.id), ("kind", document.kind))))
    glossary = documents.paths and "docs/glossary.md" in documents.paths
    terms = glossary_terms(git(root, "show", f"{documents.commit}:docs/glossary.md")) if glossary else []
    for lang in langs:
        if lang == PIVOT:
            continue
        names = page_names(directory, lang)
        for name in sorted(set(english) - set(names)):
            status.parity.append(Finding("HANDBOOK_PARITY", (("page", f"{lang}/{name}"), ("problem", "missing"))))
        for name in sorted(set(names) - set(english)):
            status.parity.append(Finding("HANDBOOK_PARITY", (("page", f"{lang}/{name}"), ("problem", "extra"))))
        for name in sorted(set(english) & set(names)):
            source = read_page(directory, f"{PIVOT}/{name}")
            if source.generated:
                continue
            expected = f"{PIVOT}/{name}@{narrative_hash(source.body)}"
            if read_page(directory, f"{lang}/{name}").meta.get("translated_from") != expected:
                status.translations.append(
                    Finding("HANDBOOK_TRANSLATION_STALE", (("page", f"{lang}/{name}"), ("source", f"{PIVOT}/{name}")))
                )
        rendered = read_terms(directory, lang)
        for term in dict.fromkeys(term.term for term in terms):
            if term not in rendered:
                status.terms.append(Finding("HANDBOOK_TERM_MISSING", (("lang", lang), ("term", json.dumps(term)))))
    return status


def read_terms(directory: Path, lang: str) -> dict[str, str]:
    path = directory / lang / TERMS
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(key): str(value) for key, value in data.items()} if isinstance(data, dict) else {}


# --- generation -----------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Snapshot:
    tag: str | None  # None for a preview
    commit: str
    repository: str
    date: str

    @property
    def ref(self) -> str:
        return self.tag or self.commit

    def link(self, path: str) -> str:
        return f"https://github.com/{self.repository}/blob/{self.ref}/{path}"


def strings(lang: str) -> dict[str, str]:
    return STRINGS.get(lang, STRINGS[PIVOT])


def provenance(snapshot: Snapshot, lang: str) -> str:
    text = strings(lang)
    release = f"`{snapshot.tag}`" if snapshot.tag else text["unreleased"]
    return text["provenance"].format(release=release, commit=snapshot.commit[:12], date=snapshot.date)


def document_line(document: Document, snapshot: Snapshot, lang: str, text: str) -> str:
    return f"- [`{document.id}`]({snapshot.link(document.path)}){strings(lang)['english']}: {text}"


def render_usecases(documents: Documents, snapshot: Snapshot, lang: str) -> str:
    return "\n".join(document_line(d, snapshot, lang, d.title) for d in documents.of_kind("usecase"))


def render_capabilities(documents: Documents, snapshot: Snapshot, lang: str) -> str:
    areas: dict[str, list[Document]] = {}
    for document in documents.of_kind("capability"):
        parts = PurePosixPath(document.path).parts
        areas.setdefault(parts[2] if len(parts) > 3 else "", []).append(document)
    out: list[str] = []
    for area in sorted(areas):
        out.extend([f"- **{area}**", *(f"  {document_line(d, snapshot, lang, d.title)}" for d in areas[area])])
    return "\n".join(out)


TOC_ORDER = ("README.md", "concepts.md")


def render_toc(directory: Path, page: Page) -> str:
    names = page_names(directory, page.lang)

    def order(name: str) -> tuple[int, str]:
        if name in TOC_ORDER:
            return (TOC_ORDER.index(name), name)
        if name in GENERATED_PAGES:
            return (4, f"{GENERATED_PAGES.index(name)}")
        return (2 if name.startswith("journeys/") else 3, name)

    here = PurePosixPath(page.path).parent
    lines = []
    for name in sorted(names, key=order):
        if name == page.path:
            continue
        title = read_page(directory, f"{page.lang}/{name}").title
        lines.append(f"- [{title}]({os.path.relpath(name, here.as_posix() or '.')})")
    return "\n".join(lines)


def render_decisions(documents: Documents, snapshot: Snapshot, lang: str) -> str:
    text = strings(lang)
    accepted = [d for d in documents.of_kind("decision") if d.status == "accepted"]
    return "\n".join([text["decisions_intro"], "", *(document_line(d, snapshot, lang, d.summary) for d in accepted)])


def render_changes(
    root: Path, documents: Documents, previous: dict[str, Any] | None, snapshot: Snapshot, lang: str
) -> str:
    text = strings(lang)
    if not previous or not has_object(root, f"{previous.get('source_commit')}^{{commit}}"):
        return text["changes_first"]
    before = load_documents(root, str(previous["source_commit"]))
    decisions = [d for d in documents.of_kind("decision") if d.status == "accepted" and before.get(d.id) is None]
    specs = [
        d
        for d in documents.of_kind("spec")
        if d.status == "completed" and ((old := before.get(d.id)) is None or old.status != "completed")
    ]
    label = f"`{previous.get('tag')}`" if previous.get("tag") else f"`{str(previous['source_commit'])[:12]}`"
    out = [text["changes_since"].format(previous=label), "", f"### {text['changes_decisions']}", ""]
    out.extend([document_line(d, snapshot, lang, d.summary) for d in decisions] or [text["changes_none"]])
    out.extend(["", f"### {text['changes_specs']}", ""])
    out.extend([document_line(d, snapshot, lang, d.title) for d in specs] or [text["changes_none"]])
    return "\n".join(out)


def render_glossary(root: Path, documents: Documents, directory: Path, lang: str) -> str:
    text = strings(lang)
    source = git(root, "show", f"{documents.commit}:docs/glossary.md") if "docs/glossary.md" in documents.paths else ""
    rendered = read_terms(directory, lang) if lang != PIVOT else {}
    out = [text["glossary_intro"]]
    section = None
    for term in glossary_terms(source):
        if term.section != section:
            section = term.section
            out.extend(["", f"### {section}", ""])
            if lang == PIVOT:
                out.extend([f"| {text['term']} | {text['definition']} | {text['owner']} |", "| :--- | :--- | :--- |"])
            else:
                out.extend(
                    [
                        f"| {text['term']} | {text['rendering']} | {text['definition']} | {text['owner']} |",
                        "| :--- | :--- | :--- | :--- |",
                    ]
                )
        if lang == PIVOT:
            out.append(f"| **{term.term}** | {term.definition} | {term.owner} |")
        else:
            out.append(f"| **{term.term}** | {rendered.get(term.term, '')} | {term.definition} | {term.owner} |")
    return "\n".join(out)


def generated_page(title: str, content: str) -> Page:
    body = f"# {title}\n\n<!-- handbook:generated page -->\n{content}\n{GENERATED_END}\n"
    return Page(rel="", meta={"generated": True}, body=body)


def repository_name(root: Path, manifest: dict[str, Any] | None) -> str:
    if name := os.environ.get("GITHUB_REPOSITORY"):
        return name
    url = git(root, "remote", "get-url", "origin", check=False).strip()
    if match := re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url):
        return match.group(1)
    if manifest and isinstance(manifest.get("repository"), str):
        return manifest["repository"]
    raise HandbookError(
        "the GitHub repository of the handbook links is unknown",
        code="HANDBOOK_REPOSITORY_UNKNOWN",
        fix="Set GITHUB_REPOSITORY=<owner>/<name> or an origin remote on github.com and rerun",
    )


def generate(root: Path, *, preview: bool, date: str) -> tuple[Path, Snapshot, int]:
    tracked = root / HANDBOOK
    manifest = read_manifest(tracked)
    require_closed_blocks(tracked, langs_of(manifest))
    commit = git(root, "rev-parse", "HEAD").strip()
    if preview:
        directory = root / PREVIEW
        if directory.exists():
            shutil.rmtree(directory)
        if tracked.is_dir():
            shutil.copytree(tracked, directory)
        else:
            directory.mkdir(parents=True)
        tag = None
    else:
        if git(root, "status", "--porcelain", "--", "docs").strip():
            raise HandbookError(
                "docs/ has uncommitted changes; a handbook describes committed Living Spec content only",
                code="HANDBOOK_DOCS_DIRTY",
                fix="Commit or set aside the docs/ changes, then rerun `just handbook generate`",
                target_files=["docs/"],
            )
        directory = tracked
        tag = "v" + (root / "VERSION").read_text(encoding="utf-8").strip()
    snapshot = Snapshot(tag=tag, commit=commit, repository=repository_name(root, manifest), date=date)
    documents = load_documents(root, commit)
    langs = langs_of(manifest)
    if manifest and manifest.get("tag") == tag and not preview:
        previous = manifest.get("previous")
    elif manifest:
        previous = {"tag": manifest.get("tag"), "source_commit": manifest["source_commit"]}
    else:
        previous = None
    count = 0
    for lang in langs:
        (directory / lang).mkdir(parents=True, exist_ok=True)
        text = strings(lang)
        whole = {
            "decisions.md": (text["decisions"], render_decisions(documents, snapshot, lang)),
            "changes.md": (text["changes"], render_changes(root, documents, previous, snapshot, lang)),
            "glossary.md": (text["glossary"], render_glossary(root, documents, directory, lang)),
        }
        for name, (title, content) in whole.items():
            (directory / lang / name).write_text(generated_page(title, content).render(), encoding="utf-8")
        for name in page_names(directory, lang):
            page = read_page(directory, f"{lang}/{name}")
            body = set_provenance(page.body, provenance(snapshot, lang))
            body = fill_blocks(
                body,
                {
                    "toc": render_toc(directory, page),
                    "usecases": render_usecases(documents, snapshot, lang),
                    "capabilities": render_capabilities(documents, snapshot, lang),
                },
            )
            page.body = body
            (directory / page.rel).write_text(page.render(), encoding="utf-8")
            count += 1
    data: dict[str, Any] = {
        "tag": tag,
        "source_commit": commit,
        "repository": snapshot.repository,
        "langs": langs,
        "generated": date,
    }
    if previous:
        data["previous"] = previous
    (directory / MANIFEST).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return directory, snapshot, count


def stamp(root: Path, directory: Path, rels: Iterable[str]) -> list[str]:
    commit = git(root, "rev-parse", "HEAD").strip()
    documents = load_documents(root, commit)
    stamped = []
    for rel in rels:
        if not (directory / rel).is_file() or "/" not in rel:
            raise HandbookError(
                f"{rel} is not a handbook page",
                code="HANDBOOK_PAGE_UNKNOWN",
                fix="Name a page as <lang>/<path> relative to handbook/, such as en/README.md",
            )
        page = read_page(directory, rel)
        if page.lang == PIVOT:
            sources = page.meta.get("sources") or {}
            refreshed: dict[str, str] = {}
            for identifier in sources if isinstance(sources, dict) else []:
                document = documents.get(str(identifier))
                if document is None:
                    raise HandbookError(
                        f"{rel} cites {identifier}, which no document declares",
                        code="HANDBOOK_ID_UNRESOLVED",
                        fix="Correct the ID under the page's sources, then stamp it again",
                        target_files=[rel],
                    )
                refreshed[str(identifier)] = document.blob
            page.meta["sources"] = refreshed
        else:
            source = directory / PIVOT / page.path
            if not source.is_file():
                raise HandbookError(
                    f"{rel} has no English page {PIVOT}/{page.path} to follow",
                    code="HANDBOOK_PAGE_UNKNOWN",
                    fix="Write the English page first; every translated page follows one",
                )
            english = read_page(directory, f"{PIVOT}/{page.path}")
            page.meta["translated_from"] = f"{PIVOT}/{page.path}@{narrative_hash(english.body)}"
        (directory / rel).write_text(page.render(), encoding="utf-8")
        stamped.append(rel)
    return stamped


# --- verification ---------------------------------------------------------------------------------------------------


def verify(root: Path, directory: Path) -> tuple[list[Invalid], dict[str, Any], int]:
    manifest = require_manifest(directory)
    commit = str(manifest["source_commit"])
    require_source(root, commit)
    documents = load_documents(root, commit)
    if manifest.get("tag"):
        expected_refs = {str(manifest["tag"])}
    else:  # a preview: generated links name the commit, written links the upcoming tag
        version = root / "VERSION"
        expected_refs = {commit, *(["v" + version.read_text(encoding="utf-8").strip()] if version.exists() else [])}
    repository = manifest.get("repository")
    found: list[Invalid] = []
    pages = [
        read_page(directory, f"{lang}/{name}") for lang in manifest["langs"] for name in page_names(directory, lang)
    ]
    for page in pages:
        offset = body_offset(page, directory)
        if "id" in page.meta:
            found.append(Invalid(page.rel, 1, "HANDBOOK_FRONTMATTER_ID", "pages carry no id frontmatter"))
        if (line := unclosed_block(page.body)) is not None:
            found.append(Invalid(page.rel, line + offset, "HANDBOOK_BLOCK_UNCLOSED", "a block has no end marker"))
        sources = page.meta.get("sources") or {}
        for identifier in sources if isinstance(sources, dict) else []:
            if documents.get(str(identifier)) is None:
                found.append(Invalid(page.rel, 1, "HANDBOOK_ID_UNRESOLVED", f"sources cites {identifier}"))
        for number, line in prose(page.body):
            at = number + offset
            for span in CODE_SPAN.findall(line):
                if DOCUMENT_ID.match(span) and documents.get(span) is None:
                    found.append(Invalid(page.rel, at, "HANDBOOK_ID_UNRESOLVED", f"{span} resolves to no document"))
            for match in SOURCE_LINK.finditer(line):
                if repository and match.group(1) != repository:
                    continue
                if match.group(2) not in expected_refs:
                    pinned = " or ".join(sorted(expected_refs))
                    found.append(
                        Invalid(page.rel, at, "HANDBOOK_LINK_REF", f"{match.group(0)} is not pinned to {pinned}")
                    )
                if match.group(3) not in documents.paths and not has_object(root, f"{commit}:{match.group(3)}"):
                    found.append(
                        Invalid(page.rel, at, "HANDBOOK_SOURCE_MISSING", f"{match.group(3)} is not in {commit[:12]}")
                    )
            if keyword := NORMATIVE.search(CODE_SPAN.sub("", line)):
                found.append(Invalid(page.rel, at, "HANDBOOK_NORMATIVE_KEYWORD", f"{keyword.group(1)} outside code"))
    status = collect_status(root, directory, documents, list(manifest["langs"]))
    for finding in status.stale:
        found.append(Invalid(dict(finding.fields)["page"], 1, "HANDBOOK_PAGE_STALE", finding.line()))
    for finding in status.translations:
        found.append(Invalid(dict(finding.fields)["page"], 1, "HANDBOOK_TRANSLATION_STALE", finding.line()))
    for finding in status.parity:
        found.append(Invalid(dict(finding.fields)["page"], 0, "HANDBOOK_PARITY", finding.line()))
    for finding in status.terms:
        lang = dict(finding.fields)["lang"]
        found.append(Invalid(f"{lang}/{TERMS}", 0, "HANDBOOK_TERM_MISSING", finding.line()))
    found.extend(rule_findings(directory, [page.rel for page in pages]))
    return found, manifest, len(pages)


def rule_findings(directory: Path, rels: list[str]) -> list[Invalid]:
    """``RULE-cli-contract`` and ``RULE-markdown-link`` on a scratch copy of the pages, so they check them unexcluded
    against the running command line and resolve relative links only between handbook pages."""
    from devkit_agt.features.rules.services.builtins.cli_contract import CliContractRule
    from devkit_agt.features.rules.services.builtins.markdown_link.rule import MarkdownLinkRule
    from devkit_agt.features.rules.services.testing import check
    from devkit_dist.cli import cli

    found: list[Invalid] = []
    with tempfile.TemporaryDirectory(prefix="handbook-") as scratch:
        workspace = Path(scratch)
        files = {f"{HANDBOOK}/{rel}": (directory / rel).read_text(encoding="utf-8") for rel in rels}
        for rule, code in (
            (CliContractRule(root=cli), "HANDBOOK_COMMAND_UNKNOWN"),
            (MarkdownLinkRule(), "HANDBOOK_LINK_BROKEN"),
        ):
            for violation in check(rule, workspace, files):
                page = violation.file.removeprefix(f"{HANDBOOK}/")
                found.append(Invalid(page, violation.line or 0, code, violation.message))
            files = {}
    return found


def release_check(root: Path, tag: str) -> tuple[list[Invalid], str, int] | str:
    """The findings of a refreshing release, or the manifest tag (``none``) when the release does not refresh."""
    directory = root / HANDBOOK
    manifest = read_manifest(directory)
    manifest_tag = str(manifest.get("tag")) if manifest else "none"
    if manifest is None or manifest.get("tag") != tag:
        return manifest_tag
    commit = str(manifest["source_commit"])
    require_source(root, commit)
    found: list[Invalid] = []
    if git(root, "rev-parse", "HEAD:docs").strip() != git(root, "rev-parse", f"{commit}:docs").strip():
        found.append(
            Invalid(MANIFEST, 0, "HANDBOOK_DOCS_MISMATCH", f"docs/ at HEAD differs from docs/ at {commit[:12]}")
        )
    findings, _, count = verify(root, directory)
    return [*found, *findings], commit, count


# --- command line ---------------------------------------------------------------------------------------------------


def _root(ctx: click.Context) -> Path:
    return ctx.obj


@click.group()
@click.option("-w", "--workspace-root", type=click.Path(file_okay=False, path_type=Path), default=ROOT, hidden=True)
@click.pass_context
def main(ctx: click.Context, workspace_root: Path) -> None:
    """Report, regenerate and verify the release handbook (CAP-DLV-release-handbook)."""
    ctx.obj = workspace_root.resolve()


@main.command("status")
@click.pass_context
@boundary
def status_command(ctx: click.Context) -> None:
    """Report stale pages, stale translations, coverage gaps, parity and missing terms; exit 1 on any."""
    root = _root(ctx)
    directory = root / HANDBOOK
    manifest = read_manifest(directory)
    documents = load_documents(root, git(root, "rev-parse", "HEAD").strip())
    result = collect_status(root, directory, documents, langs_of(manifest))
    for finding in result.all():
        click.echo(finding.line())
    click.echo(
        f"[HANDBOOK_STATUS: tag={manifest.get('tag') if manifest else 'none'} stale={len(result.stale)}"
        f" translations={len(result.translations)} gaps={len(result.gaps)} parity={len(result.parity)}"
        f" terms={len(result.terms)}]"
    )
    if result.all():
        raise SystemExit(1)


@main.command("stamp")
@click.argument("pages", nargs=-1, required=True)
@click.pass_context
@boundary
def stamp_command(ctx: click.Context, pages: tuple[str, ...]) -> None:
    """Record PAGES (<lang>/<path>) as refreshed: current source SHAs, or the English narrative hash."""
    root = _root(ctx)
    for rel in stamp(root, root / HANDBOOK, pages):
        click.echo(f"[HANDBOOK_STAMPED: page={rel}]")


@main.command("generate")
@click.option("--preview", is_flag=True, help=f"Write an unreleased preview to {PREVIEW}/ instead of handbook/.")
@click.option("--date", default=lambda: datetime.date.today().isoformat(), hidden=True)
@click.pass_context
@boundary
def generate_command(ctx: click.Context, preview: bool, date: str) -> None:
    """Rewrite provenance, generated sections and pages and the manifest; narrative stays as written."""
    root = _root(ctx)
    directory, snapshot, count = generate(root, preview=preview, date=date)
    click.echo(
        f"[HANDBOOK_GENERATED: dir={directory.relative_to(root).as_posix()} tag={snapshot.tag or 'unreleased'}"
        f" commit={snapshot.commit} pages={count}]"
    )


def _report(findings: list[Invalid], tag: str, commit: str, count: int) -> None:
    for finding in findings:
        click.echo(finding.sentinel())
    if findings:
        raise SystemExit(1)
    click.echo(f"[HANDBOOK_VERIFIED: tag={tag} commit={commit} pages={count}]")


@main.command("verify")
@click.option("--preview", is_flag=True, help=f"Verify {PREVIEW}/ instead of handbook/.")
@click.pass_context
@boundary
def verify_command(ctx: click.Context, preview: bool) -> None:
    """Check the handbook against its source commit; exit 1 with one line per finding."""
    root = _root(ctx)
    findings, manifest, count = verify(root, root / (PREVIEW if preview else HANDBOOK))
    _report(findings, str(manifest.get("tag") or "unreleased"), str(manifest["source_commit"]), count)


@main.command("release-check")
@click.argument("tag")
@click.pass_context
@boundary
def release_check_command(ctx: click.Context, tag: str) -> None:
    """Verify the handbook when the release TAG refreshed it (manifest tag equals TAG); skip otherwise."""
    result = release_check(_root(ctx), tag)
    if isinstance(result, str):
        click.echo(f"[HANDBOOK_SKIPPED: tag={tag} manifest_tag={result}]")
        return
    findings, commit, count = result
    _report(findings, tag, commit, count)


if __name__ == "__main__":
    main()
