"""Scripted formal-document maintenance using actual CLI, Git snapshots and source comparisons.

These scenarios execute author procedures; they do not claim autonomous semantic judgment.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

APPROACH = "sdd"
ROLES = [("designs", "DESIGN", "design"), ("domain", "DOMAIN", "domain"), ("operations", "OPS", "operations")]
AREA = "core"
AREA_DIRECTORIES = ("designs", "domain")
DESIGN_ANCHOR = "design.md"


def home(root: str, directory: str, identifier: str, area: str = AREA) -> str:
    """The ID-named directory that moves with its document: a DESIGN bundle, or a DOMAIN/OPS support parent."""
    scope = f"/{area}" if directory in AREA_DIRECTORIES else ""
    return f"{root}/{directory}{scope}/{identifier}"


def canonical(root: str, directory: str, identifier: str, area: str = AREA) -> str:
    owned = home(root, directory, identifier, area)
    return f"{owned}/{DESIGN_ANCHOR}" if directory == "designs" else f"{owned}.md"


def support(root: str, directory: str, identifier: str, name: str, area: str = AREA) -> str:
    owned = home(root, directory, identifier, area)
    return f"{owned}/{name}" if directory == "designs" else f"{owned}/artifacts/{name}"


def is_support(path: str) -> bool:
    """Parent-owned support: any non-anchor file in a DESIGN bundle, or a file under a DOMAIN/OPS artifacts directory."""
    bundled = re.search(r"/designs/[^/]+/DESIGN-[^/]+/(.+)$", path)
    return "/artifacts/" in path or (bundled is not None and bundled.group(1) != DESIGN_ANCHOR)


def is_canonical(path: str) -> bool:
    return path.endswith(".md") and not is_support(path) and not path.endswith("/README.md")


UNRELATED = canonical("docs", "domain", "DOMAIN-unrelated")
ROUTER = canonical("docs", "designs", "DESIGN-router")


class Exercise:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("DEVKIT_", "PYTHONPATH"))}
        self.events: list[dict[str, object]] = []
        self.run("git", "init", "-q", "-b", "exercise", str(root), cwd=root.parent)
        self.run("git", "config", "user.name", "Synthetic lifecycle exercise")
        self.run("git", "config", "user.email", "synthetic@example.invalid")
        self.write(
            ".devkit/config.toml",
            f'[development]\napproach="{APPROACH}"\n[presets]\ndocs="core"\nspec="core"\n[[tool.docs.namespaces]]\nname="api"\npath="packages/api"\n',
        )
        self.write("packages/api/.keep", "registered package\n")
        self.write("src/mechanism.py", "MODE = 1\n")
        self.write("src/other.py", "LIVE = True\n")
        self.history = self.write(
            "specs/2026-10/20261001-history/spec.md",
            '---\nid: SPEC-history\nsummary: "Retained historical delivery."\nstatus: completed\n---\n# Retained historical bytes\n',
        )
        self.write(
            "specs/2026-10/20261001-history/reconcile.md",
            "---\nreconcile_id: REC-history\nstatus: resolved\ntargets: []\n---\n# Retained reconciliation\n",
        )
        self.history_bytes = self.history.read_bytes()
        self.cli("sync")
        if APPROACH == "adaptive-dev":
            self.cli("add", "adaptive-dev")
        self.initial_history = {
            p.relative_to(root).as_posix(): p.read_bytes() for p in (root / "specs").rglob("*") if p.is_file()
        }
        context = self.json("get-context", "docs")
        assert {p["path"].split("/")[-1] for p in context["instructions"]} >= {
            "design-writing.md",
            "domain-writing.md",
            "operations-writing.md",
        }
        guide = (
            self.root
            / ".devkit/managed"
            / (
                "spec/skills/spec-sync/SKILL.md"
                if APPROACH == "sdd"
                else "adaptive-dev/skills/adaptive-dev/references/documents.md"
            )
        )
        assert "Reclassify" in guide.read_text() and "obsolete DESIGN entrypoints" in guide.read_text()

    def run(self, *args: str, expected: int = 0, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(args, cwd=cwd or self.root, env=self.env, text=True, capture_output=True, check=False)
        self.events.append(
            {"argv": list(args), "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        )
        assert result.returncode == expected, result.stdout + result.stderr
        return result

    def cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        return self.run(sys.executable, "-m", "devkit_dist", *args, "-w", str(self.root), expected=expected)

    def json(self, *args: str) -> dict:
        return json.loads(self.cli(*args, "--format", "json").stdout)

    def write(self, path: str, text: str) -> Path:
        result = self.root / path
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(text)
        return result

    def relative(self, origin: str, target: str) -> str:
        return os.path.relpath(self.root / target, (self.root / origin).parent)

    def doc(self, path: str, identifier: str, body: str, extra: str = "", status: str = "active") -> Path:
        """Write a formal document; a document in an area directory carries that directory as its ``area``."""
        scoped = re.search(r"(?:^|/)(?:designs|domain)/([^/]+)/", path)
        area = f"area: {scoped.group(1)}\n" if scoped else ""
        return self.write(
            path,
            f'---\nid: {identifier}\ntitle: Retained subject\nsummary: "Retained subject and its source-specific support."\nstatus: {status}\n{area}{extra}---\n# [{identifier}] Retained subject\n\n{body}\n',
        )

    def relocate(self, directory: str, source: str, target: str) -> None:
        """Move a document's home: a DESIGN bundle whole, or a DOMAIN/OPS file with its support directory."""
        (self.root / target).parent.mkdir(parents=True, exist_ok=True)
        if directory != "designs":
            (self.root / f"{source}.md").rename(self.root / f"{target}.md")
        (self.root / source).rename(self.root / target)

    def prune(self, path: Path) -> None:
        """Remove the empty directories left above ``path`` inside ``docs``."""
        for directory in path.parents:
            if directory == self.root / "docs" or not directory.exists() or any(directory.iterdir()):
                break
            directory.rmdir()

    def orphaned(self, output: str, owned: str) -> None:
        """The rule output reports a file inside the parentless home ``owned``."""
        assert any(path.startswith(f"{owned}/") for path in re.findall(r"file=(\S+)", output)), output

    def rules(self, expected: int = 0, staged: bool = False) -> str:
        return self.cli("rules", "check", *(["--staged"] if staged else ["docs"]), expected=expected).stdout

    def resolve(self, identifier: str) -> dict:
        return self.json("docs", "resolve", identifier)["documents"][0]

    def links(self, path: str) -> None:
        for target in re.findall(r"\]\(([^)]+)\)", (self.root / path).read_text()):
            assert ((self.root / path).parent / target).resolve().exists(), (path, target)

    def commit(self, message: str) -> str:
        self.run("git", "add", "docs", "src", ".devkit/config.toml", ".devkit/installation.json", "specs", "packages")
        self.run("git", "commit", "-qm", message)
        return self.run("git", "rev-parse", "HEAD").stdout.strip()

    def reconcile_snapshot(self, require_removed: bool = False) -> None:
        """Author checks completeness; the native rule checks each declared modified target's diff evidence."""
        self.run("git", "add", "docs", "src")
        targets = self.run("git", "diff", "--cached", "--name-only", "--no-renames", "--", "docs").stdout.splitlines()
        removed = self.run(
            "git", "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=D", "--", "docs"
        ).stdout.splitlines()
        assert targets and any(is_support(path) for path in targets)
        canonical = next(path for path in targets if is_canonical(path))
        if require_removed:
            assert removed and any(is_support(path) for path in removed)

        def missing(selected: list[str]) -> set[str]:
            return set(targets) - set(selected)

        # Omissions are rejected by explicit author comparison, not a claimed reverse-discovery runtime rule.
        assert canonical in missing([path for path in targets if path != canonical])
        for path in removed:
            assert path in missing([candidate for candidate in targets if candidate != path])
        assert not missing(targets)
        self.events.append(
            {
                "comparison": "author impact completeness",
                "changed": targets,
                "removed": removed,
                "missing_canonical_control": "rejected",
                "missing_removed_controls": "rejected",
            }
        )
        bundle = "specs/2026-11/20261116-maintenance"
        self.write(
            f"{bundle}/spec.md",
            '---\nid: SPEC-maintenance\nsummary: "Maintain formal statements and support."\nstatus: completed\n---\n# Maintenance\n\n## Acceptance Criteria\n\n### [AC-01] Maintained subject\n- Given a retained subject\n- When maintained\n- Then its actual links and owners agree\n',
        )
        self.write(
            f"{bundle}/tasks.md",
            "---\nid: TASKS-maintenance\nspec: SPEC-maintenance\n---\n- [x] **Task 1**: retained maintenance\n  - **_Boundary**: `src/`\n  - _Requirements: AC-01_\n",
        )
        record = f"{bundle}/reconcile.md"

        def write_record(paths: list[str]) -> None:
            self.write(
                record,
                "---\nreconcile_id: REC-maintenance\nstatus: resolved\ntargets:\n"
                + "".join(f"  - file: {path}\n    resolution: modified\n" for path in paths)
                + "---\n# Source-identified maintenance\nCanonical and support paths compared against actual source and staged changes.\n",
            )
            self.run("git", "add", bundle)

        write_record([*targets, UNRELATED])
        negative = self.rules(expected=1, staged=True)
        assert "RULE-reconcile-contract" in negative and "DOMAIN-unrelated.md" in negative
        write_record(targets)
        self.rules(staged=True)
        assert all(f"file: {path}\n" in (self.root / record).read_text() for path in removed)

    def finish(self, identifier: str, source: str) -> None:
        self.rules()
        assert self.history.read_bytes() == self.history_bytes
        assert self.json("config", "show")["configuration"]["development"]["approach"] == APPROACH
        if APPROACH == "adaptive-dev":
            current = {
                p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in (self.root / "specs").rglob("*")
                if p.is_file()
            }
            assert current == self.initial_history
            assert not list(self.root.glob("**/envelopes/*.yaml"))
            assert not list((self.root / ".devkit").glob("workflow-record*"))
            self.write(
                ".devkit/adaptive-dev.md",
                f"# Current facts\nDocuments: {identifier}; missing required operational source: undocumented.\nSource identity: {source}; check: actual CLI observations in fixture.\n",
            )
        self.write(
            "observations.json",
            json.dumps(
                {
                    "approach": APPROACH,
                    "document": identifier,
                    "source": source,
                    "scripted": True,
                    "events": self.events,
                },
                indent=2,
            ),
        )


@pytest.mark.parametrize("docs_root", ["docs", "docs/packages/api"])
@pytest.mark.parametrize(("directory", "prefix", "kind"), ROLES)
def test_composed_formal_maintenance(tmp_path: Path, docs_root: str, directory: str, prefix: str, kind: str) -> None:
    e = Exercise(tmp_path / "consumer")
    identifier = f"{prefix}-original"
    owned = home(docs_root, directory, identifier)
    parent = canonical(docs_root, directory, identifier)
    detail = canonical(docs_root, directory, f"{prefix}-detail")
    artifact = support(docs_root, directory, identifier, "example.md")
    data = support(docs_root, directory, identifier, "data.csv")
    router = ROUTER
    unaffected = e.doc(UNRELATED, "DOMAIN-unrelated", "Unrelated conceptual meaning.\n").read_bytes()
    csv = "size,latency\n4,12\n"
    e.write(data, csv)
    e.write(artifact, f"# Example\nParent `{identifier}`. [data](data.csv).\n")
    source_hash = hashlib.sha256((e.root / "src/mechanism.py").read_bytes()).hexdigest()

    def body(owner_path: str, data_path: str, revision: str) -> str:
        return f"Source identity: {revision}. [source]({e.relative(owner_path, 'src/mechanism.py')}).\n[data]({e.relative(owner_path, data_path)}). Independent detail `{prefix}-detail`."

    e.doc(parent, identifier, body(parent, data, source_hash))
    e.doc(detail, f"{prefix}-detail", f"Independent maintained detail for `{identifier}`.")
    e.doc(
        router,
        "DESIGN-router",
        f"Owner `{identifier}`. [data]({e.relative(router, data)}).",
        f"related_{ {'DESIGN': 'designs', 'DOMAIN': 'domains', 'OPS': 'operations'}[prefix] }: [{identifier}]\n",
    )
    e.rules()
    assert e.resolve(identifier)["path"] == parent
    assert identifier in str(e.json("docs", "search", identifier, "--mode", "lexical"))
    assert "DESIGN-router" in str(e.json("docs", "refs", identifier, "--direction", "in"))
    assert len(e.json("docs", "list", kind, "--namespace", "api")["documents"]) >= 1
    e.commit("create formal subject and support")
    original_bytes = (e.root / parent).read_bytes()
    (e.root / parent).unlink()
    e.run("git", "add", parent)
    # Without its canonical document the support has no parent: an anchor-less bundle, or an orphan artifacts directory.
    e.orphaned(e.rules(expected=1, staged=True), owned)
    (e.root / parent).write_bytes(original_bytes)
    e.run("git", "add", parent)
    # Update source and compare the precise retained bytes, without changing unrelated roles.
    e.write("src/mechanism.py", "MODE = 2\n")
    source_hash = hashlib.sha256((e.root / "src/mechanism.py").read_bytes()).hexdigest()
    e.doc(parent, identifier, body(parent, data, source_hash))
    assert source_hash in (e.root / parent).read_text()
    assert e.run(sys.executable, "-c", "exec(open('src/mechanism.py').read()); print(MODE)").stdout.strip() == "2"
    # Same-kind rename carries parent-owned support; aliases preserve identity, not filesystem paths.
    renamed = f"{prefix}-renamed"
    new_home = home(docs_root, directory, renamed)
    new_parent = canonical(docs_root, directory, renamed)
    e.relocate(directory, owned, new_home)
    data = support(docs_root, directory, renamed, "data.csv")
    artifact = support(docs_root, directory, renamed, "example.md")
    e.doc(new_parent, renamed, body(new_parent, data, source_hash), f"aliases: [{identifier}]\n")
    e.write(
        artifact,
        f"# Example\nParent `{renamed}`. [data](data.csv).\n[source]({e.relative(artifact, 'src/mechanism.py')}).\n",
    )
    e.doc(
        router,
        "DESIGN-router",
        f"Owner `{identifier}`. [data]({e.relative(router, data)}).",
        f"related_{ {'DESIGN': 'designs', 'DOMAIN': 'domains', 'OPS': 'operations'}[prefix] }: [{identifier}]\n",
    )
    e.cli("rules", "fix", "docs")
    assert e.resolve(identifier)["id"] == renamed
    assert not (e.root / parent).exists() and not (e.root / owned).exists()
    # Support left at the old ID is parentless; the old-ID alias never legalizes it.
    orphan = e.write(support(docs_root, directory, identifier, "orphan.csv"), csv)
    e.orphaned(e.rules(expected=1), owned)
    orphan.unlink()
    e.prune(orphan)
    # Move unchanged identity between global and registered roots in both directions, changing area on the way out.
    original_root = docs_root
    area = AREA
    for destination, destination_area in [
        ("docs/packages/api" if docs_root == "docs" else "docs", "moved"),
        (original_root, AREA),
    ]:
        moved_home = home(destination, directory, renamed, destination_area)
        e.relocate(directory, new_home, moved_home)
        e.prune(e.root / new_home)
        assert not (e.root / new_parent).exists()
        docs_root, area, new_home = destination, destination_area, moved_home
        new_parent = canonical(docs_root, directory, renamed, area)
        data = support(docs_root, directory, renamed, "data.csv", area)
        artifact = support(docs_root, directory, renamed, "example.md", area)
        e.doc(new_parent, renamed, body(new_parent, data, source_hash), f"aliases: [{identifier}]\n")
        e.write(
            artifact,
            f"# Example\nParent `{renamed}`. [data](data.csv).\n[source]({e.relative(artifact, 'src/mechanism.py')}).\n",
        )
        e.doc(router, "DESIGN-router", f"Owner `{renamed}`. [data]({e.relative(router, data)}).")
        assert e.resolve(identifier)["path"] == new_parent
        for linked in [new_parent, artifact, router]:
            e.links(linked)
        assert (e.root / data).read_text() == csv
        e.rules()
    # A split gives retained CSV one new canonical parent and keeps independent detail identity.
    split = f"{prefix}-split"
    split_path = canonical(docs_root, directory, split)
    split_data = support(docs_root, directory, split, "data.csv")
    e.doc(split_path, split, "Owns the measured support subject.")
    (e.root / split_data).parent.mkdir(parents=True, exist_ok=True)
    (e.root / data).rename(e.root / split_data)
    e.doc(new_parent, renamed, body(new_parent, split_data, source_hash), f"aliases: [{identifier}]\n")
    e.write(artifact, f"# Example\nParent `{renamed}`. [data]({e.relative(artifact, split_data)}).\n")
    e.doc(router, "DESIGN-router", f"Owner `{renamed}`. [data]({e.relative(router, split_data)}).")
    assert not (e.root / data).exists() and e.resolve(f"{prefix}-detail")["path"] == detail
    # Cross-kind transfer retires the previous node, never gives the receiving prefix an old-prefix alias.
    receiving_dir, receiving_prefix, _ = ROLES[(next(i for i, row in enumerate(ROLES) if row[1] == prefix) + 1) % 3]
    receiving = f"{receiving_prefix}-transferred"
    receiving_path = canonical(docs_root, receiving_dir, receiving)
    receiving_data = support(docs_root, receiving_dir, receiving, "data.csv")
    e.doc(receiving_path, receiving, "Owns the transferred support subject.")
    (e.root / receiving_data).parent.mkdir(parents=True, exist_ok=True)
    (e.root / split_data).rename(e.root / receiving_data)
    e.prune(e.root / split_data)
    e.doc(split_path, split, f"Receiving owner `{receiving}`.", status="retired")
    e.doc(new_parent, renamed, body(new_parent, receiving_data, source_hash), f"aliases: [{identifier}]\n")
    e.write(artifact, f"# Example\nParent `{renamed}`. [data]({e.relative(artifact, receiving_data)}).\n")
    e.doc(router, "DESIGN-router", f"Owner `{renamed}`. [data]({e.relative(router, receiving_data)}).")
    e.doc(receiving_path, receiving, "Transferred support.", f"aliases: [{split}]\n")
    e.rules(expected=1)
    e.doc(receiving_path, receiving, "Owns the transferred support subject.")
    assert len(list((e.root / "docs").rglob("data.csv"))) == 1
    assert (e.root / receiving_data).read_text() == csv
    e.rules()
    # SDD uses actual existing derive/select/apply. Adaptive authors optional anchors without inventing SDD input.
    extra = f"aliases: [{identifier}]\n"
    if prefix == "DESIGN":
        if APPROACH == "sdd":
            bundle = "specs/2026-11/20261116-mechanism"
            e.write(
                f"{bundle}/spec.md",
                '---\nid: SPEC-mechanism\nsummary: "Maintain retained mechanism anchors."\nstatus: in-progress\n---\n# Mechanism\n\n## Acceptance Criteria\n\n### [AC-01] Retained source\n- Given source\n- When read\n- Then anchors identify it\n',
            )
            e.write(
                f"{bundle}/tasks.md",
                "---\nid: TASKS-mechanism\nspec: SPEC-mechanism\n---\n- [x] **Task 1**: mechanism\n  - **_Boundary**: `src/`\n  - _Requirements: AC-01_\n",
            )
            e.write(
                f"{bundle}/reconcile.md",
                f"---\nreconcile_id: REC-mechanism\nstatus: pending\ntargets:\n  - file: {new_parent}\n    resolution: modified\n---\n",
            )
            before_body = (e.root / new_parent).read_text().split("---\n", 2)[2]
            args = (
                "spec",
                "entrypoints",
                "derive",
                "--spec",
                bundle,
                "--apply",
                "--target",
                identifier,
                "--code",
                "src/mechanism.py",
                "--code",
                "src/other.py",
            )
            assert "applied=1" in e.cli(*args).stdout
            assert (e.root / new_parent).read_text().split("---\n", 2)[2] == before_body
            before = (e.root / new_parent).read_bytes()
            assert "applied=0" in e.cli(*args).stdout and (e.root / new_parent).read_bytes() == before
        extra += "entrypoints: [src/mechanism.py, src/other.py]\n"
        e.doc(new_parent, renamed, body(new_parent, receiving_data, source_hash), extra)
    e.reconcile_snapshot(require_removed=True)
    retained = e.commit("retain updated source and composed maintenance")
    # Retirement and real source-deletion snapshot; obsolete live declarations cannot be waived by status.
    (e.root / "src/mechanism.py").unlink()
    history_body = f"Historical source src/mechanism.py at commit {retained}. [data]({e.relative(new_parent, receiving_data)}). Useful source src/other.py."
    e.doc(new_parent, renamed, history_body, extra, status="retired")
    e.write(
        artifact,
        f"# Example\nParent `{renamed}`. [data]({e.relative(artifact, receiving_data)}).\nHistorical source src/mechanism.py at commit {retained}. [live]({e.relative(artifact, 'src/other.py')}).\n",
    )
    e.run("git", "add", "docs", "src")
    if prefix == "DESIGN":
        assert "Dead code entrypoint" in e.rules(expected=1, staged=True)
        extra = f"aliases: [{identifier}]\nentrypoints: [src/other.py]\n"
        e.doc(new_parent, renamed, history_body, extra, status="retired")
        e.run("git", "add", new_parent)
    e.reconcile_snapshot()
    e.rules(staged=True)
    listed = e.json("docs", "list", kind, "--all-namespaces")["documents"]
    assert renamed not in {d["id"] for d in listed}
    assert renamed in {d["id"] for d in e.json("docs", "list", kind, "--history", "--all-namespaces")["documents"]}
    assert e.resolve(identifier)["status"] == "retired"
    assert "DESIGN-router" in str(e.json("docs", "refs", renamed, "--direction", "in"))
    for linked in [new_parent, artifact, router]:
        e.links(linked)
    assert (e.root / UNRELATED).read_bytes() == unaffected
    e.finish(renamed, source_hash)


@pytest.mark.parametrize("multi_role", [False, True])
def test_source_bound_sdd_impact_plan_review_and_reconcile(tmp_path: Path, multi_role: bool) -> None:
    e = Exercise(tmp_path / "impact")
    e.write("app.py", 'import json\nprint(json.dumps(["ready"]))\n')
    capability = "docs/capabilities/app/CAP-APP-state.md"

    def contract(values: list[str]) -> str:
        return f'---\nid: CAP-APP-state\ntitle: State sequence\nsummary: "Returns the retained state sequence."\narea: app\nstatus: active\nusecases: []\n---\n# [CAP-APP-state] State sequence\n\n## 1. Summary\nLocal observed state output.\n\n## 2. Scope & Boundary\nLocal JSON output only.\n\n## 3. Business Rules & Policies\nThe app MUST output {values} as JSON.\n\n## 4. Interfaces & Data Contracts\nRun python app.py.\n'

    e.write(capability, contract(["ready"]))
    capability_before = (e.root / capability).read_bytes()
    documents = {
        "DOMAIN-state": ("domain", "Ready names the retained state."),
        "DESIGN-state-list": ("designs", "A list literal supplies the returned state sequence."),
        "OPS-state-observation": (
            "operations",
            "Observe ready as the normal state; execution authority stays with its existing owner.",
        ),
    }
    for identifier, (directory, statement) in documents.items():
        e.doc(canonical("docs", directory, identifier), identifier, statement)
    before = {
        identifier: (e.root / canonical("docs", directory, identifier)).read_bytes()
        for identifier, (directory, _) in documents.items()
    }
    old_source = hashlib.sha256((e.root / "app.py").read_bytes()).hexdigest()
    new_app = (
        'import json\nprint(json.dumps(["ready", "expired"]))\n'
        if multi_role
        else 'import json\nprint(json.dumps(list(("ready",))))\n'
    )
    e.write("app.py", new_app)
    observed = json.loads(e.run(sys.executable, "app.py").stdout)
    assert observed == (["ready", "expired"] if multi_role else ["ready"])
    source = hashlib.sha256((e.root / "app.py").read_bytes()).hexdigest()
    assert source != old_source
    e.cli(
        "spec", "proposal", "new", "impact", "--with-target-docs", "--summary", "Assess retained formal source impact."
    )
    blueprint = e.root / "docs/proposals/PROP-impact/target-docs.md"
    assert "Formal Responsibility Impact and Maintenance" in blueprint.read_text()
    affected = list(documents) if multi_role else ["DESIGN-state-list"]
    assessment = "\n".join(
        f"{identifier}: source {source}; sole statement owner {identifier}; update and verify observed states {observed}."
        if identifier in affected
        else f"{identifier}: unaffected, output remains ready and conceptual/operational meaning unchanged."
        for identifier in documents
    )
    blueprint.write_text(blueprint.read_text() + "\n## Selected impact\n" + assessment + "\n")
    bundle = "specs/2026-11/20261116-impact"
    e.write(f"{bundle}/plan.md", "# Source-bound plan\n" + assessment + "\n")
    targets = []
    for identifier in affected:
        directory, statement = documents[identifier]
        path = canonical("docs", directory, identifier)
        if identifier == "DESIGN-state-list":
            statement = (
                "Two literal state entries supply JSON output."
                if multi_role
                else "A tuple is materialized to a list for JSON output."
            )
        elif identifier == "DOMAIN-state":
            statement = "Ready and expired are distinct retained state names."
        elif identifier == "OPS-state-observation":
            statement = "Observe ready and expired through app.py; action authority remains with CAP-APP-state."
        e.doc(path, identifier, f"{statement} Current observed state sequence: {observed}. Source SHA256: {source}.")
        targets.append(path)
    for identifier in set(documents) - set(affected):
        directory, _ = documents[identifier]
        assert (e.root / canonical("docs", directory, identifier)).read_bytes() == before[identifier]
    if multi_role:
        e.write(capability, contract(observed))
        targets.append(capability)
    else:
        assert (e.root / capability).read_bytes() == capability_before
    # Scripted review compares the source actually executed with the authoring evidence, not a presence-only gate.
    assert hashlib.sha256((e.root / "app.py").read_bytes()).hexdigest() == source
    for path in targets:
        assert str(observed) in (e.root / path).read_text()
        if path != capability:
            assert source in (e.root / path).read_text()
    e.write(
        f"{bundle}/review.md",
        f"# Scripted comparison\nSource {source}; executed app.py returned {observed}.\n" + assessment + "\n",
    )
    reconcile = e.write(
        f"{bundle}/reconcile.md",
        "---\nreconcile_id: REC-impact\nstatus: pending\ntargets:\n"
        + "".join(f"  - file: {path}\n    resolution: modified\n" for path in targets)
        + "---\n# Source comparison\n"
        + assessment
        + "\n",
    )
    e.rules()
    assert all(path in reconcile.read_text() for path in targets)
    assert len(targets) == (4 if multi_role else 1)
    e.write(
        "observations.json",
        json.dumps({"source": source, "scripted": True, "affected": targets, "events": e.events}, indent=2),
    )


def test_brownfield_formal_destination_preserves_current_content_and_history(tmp_path: Path) -> None:
    e = Exercise(tmp_path / "brownfield")
    e.cli("playbook", "get", "spec/brownfield-adoption")
    migration = (e.root / ".devkit/managed/spec/playbooks/brownfield-adoption/references/migration.md").read_text()
    assert "Formal DESIGN" in migration and "Formal DOMAIN" in migration and "Formal OPS" in migration
    current = e.doc(canonical("docs", "domain", "DOMAIN-retained"), "DOMAIN-retained", "Retained conceptual meaning.")
    current_bytes = current.read_bytes()
    legacy = e.write(
        "docs/materials/_legacy/mechanism.md", "# Local mechanism\nMODE is the retained implementation constant.\n"
    )
    history = e.write("docs/materials/_legacy/experiment.txt", "Historical discarded experiment; not current design.\n")
    history_bytes = history.read_bytes()
    source = hashlib.sha256((e.root / "src/mechanism.py").read_bytes()).hexdigest()
    destination = canonical("docs", "designs", "DESIGN-retained-mechanism")
    e.doc(
        destination,
        "DESIGN-retained-mechanism",
        legacy.read_text().split("\n", 1)[1] + f"Source SHA256: {source}.",
    )
    legacy.unlink()
    e.rules()
    assert e.resolve("DESIGN-retained-mechanism")["path"] == destination
    assert current.read_bytes() == current_bytes and history.read_bytes() == history_bytes
    assert e.history.read_bytes() == e.history_bytes and not legacy.exists()
