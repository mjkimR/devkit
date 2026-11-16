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

APPROACH = "adaptive-dev"
ROLES = [("designs", "DESIGN", "design"), ("domain", "DOMAIN", "domain"), ("operations", "OPS", "operations")]


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
        return self.write(
            path,
            f'---\nid: {identifier}\ntitle: Retained subject\nsummary: "Retained subject and its source-specific support."\nstatus: {status}\n{extra}---\n# [{identifier}] Retained subject\n\n{body}\n',
        )

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
    parent = f"{docs_root}/{directory}/{identifier}.md"
    detail = f"{docs_root}/{directory}/{prefix}-detail.md"
    artifact = f"{docs_root}/{directory}/{identifier}/artifacts/example.md"
    data = f"{docs_root}/{directory}/{identifier}/artifacts/data.csv"
    router = "docs/designs/DESIGN-router.md"
    unaffected = e.doc(
        "docs/domain/DOMAIN-unrelated.md", "DOMAIN-unrelated", "Unrelated conceptual meaning.\n"
    ).read_bytes()
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
    assert "artifact" in e.rules(expected=1, staged=True).lower()
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
    new_parent = f"{docs_root}/{directory}/{renamed}.md"
    (e.root / parent).rename(e.root / new_parent)
    (e.root / f"{docs_root}/{directory}/{identifier}").rename(e.root / f"{docs_root}/{directory}/{renamed}")
    data = f"{docs_root}/{directory}/{renamed}/artifacts/data.csv"
    artifact = f"{docs_root}/{directory}/{renamed}/artifacts/example.md"
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
    assert not (e.root / parent).exists() and not (e.root / f"{docs_root}/{directory}/{identifier}").exists()
    orphan = e.write(f"{docs_root}/{directory}/{identifier}/artifacts/orphan.csv", csv)
    assert "artifact" in e.rules(expected=1).lower()
    orphan.unlink()
    orphan.parent.rmdir()
    orphan.parent.parent.rmdir()
    # Move unchanged identity between global and registered roots in both directions.
    original_root = docs_root
    for destination in ["docs/packages/api" if docs_root == "docs" else "docs", original_root]:
        moved = f"{destination}/{directory}/{renamed}.md"
        e.write(f"{destination}/{directory}/.keep", "")
        (e.root / new_parent).rename(e.root / moved)
        (e.root / f"{docs_root}/{directory}/{renamed}").rename(e.root / f"{destination}/{directory}/{renamed}")
        assert not (e.root / new_parent).exists()
        docs_root, new_parent = destination, moved
        data = f"{docs_root}/{directory}/{renamed}/artifacts/data.csv"
        artifact = f"{docs_root}/{directory}/{renamed}/artifacts/example.md"
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
    split_path = f"{docs_root}/{directory}/{split}.md"
    split_data = f"{docs_root}/{directory}/{split}/artifacts/data.csv"
    e.doc(split_path, split, "Owns the measured support subject.")
    (e.root / split_data).parent.mkdir(parents=True)
    (e.root / data).rename(e.root / split_data)
    e.doc(new_parent, renamed, body(new_parent, split_data, source_hash), f"aliases: [{identifier}]\n")
    e.write(artifact, f"# Example\nParent `{renamed}`. [data]({e.relative(artifact, split_data)}).\n")
    e.doc(router, "DESIGN-router", f"Owner `{renamed}`. [data]({e.relative(router, split_data)}).")
    assert not (e.root / data).exists() and e.resolve(f"{prefix}-detail")["path"] == detail
    # Cross-kind transfer retires the previous node, never gives the receiving prefix an old-prefix alias.
    receiving_dir, receiving_prefix, _ = ROLES[(next(i for i, row in enumerate(ROLES) if row[1] == prefix) + 1) % 3]
    receiving = f"{receiving_prefix}-transferred"
    receiving_path = f"{docs_root}/{receiving_dir}/{receiving}.md"
    receiving_data = f"{docs_root}/{receiving_dir}/{receiving}/artifacts/data.csv"
    e.doc(receiving_path, receiving, "Owns the transferred support subject.")
    (e.root / receiving_data).parent.mkdir(parents=True)
    (e.root / split_data).rename(e.root / receiving_data)
    (e.root / split_data).parent.rmdir()
    (e.root / split_data).parent.parent.rmdir()
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
    e.rules(staged=True)
    listed = e.json("docs", "list", kind, "--all-namespaces")["documents"]
    assert renamed not in {d["id"] for d in listed}
    assert renamed in {d["id"] for d in e.json("docs", "list", kind, "--history", "--all-namespaces")["documents"]}
    assert e.resolve(identifier)["status"] == "retired"
    assert "DESIGN-router" in str(e.json("docs", "refs", renamed, "--direction", "in"))
    for linked in [new_parent, artifact, router]:
        e.links(linked)
    assert (e.root / "docs/domain/DOMAIN-unrelated.md").read_bytes() == unaffected
    e.finish(renamed, source_hash)
