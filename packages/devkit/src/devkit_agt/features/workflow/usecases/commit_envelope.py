"""Explicitly commit one existing authored workflow envelope."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from devkit_core.base.errors import FrontmatterError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import GitError

from devkit_agt.features.workflow.models.errors import (
    EnvelopeCommitFailedError,
    EnvelopeCommitInvalidError,
    EnvelopeCommitStateError,
    EnvelopeCommitUncertainError,
    WorkflowError,
)
from devkit_agt.features.workflow.repositories.envelope_commit import EnvelopeCommitRepository
from devkit_agt.features.workflow.repositories.unit.frontmatter import parse
from devkit_agt.features.workflow.services.envelope import FILE, load_envelopes
from devkit_agt.features.workflow.services.envelope.commit import commit_message, require_authored
from devkit_agt.features.workflow.usecases.workspace import Workspace


class CommitEnvelopeUseCase(BaseUseCase):
    """Coordinate eligibility checks and Git effects without changing authored evidence."""

    def execute(self, workspace: Workspace, unit: str, file: str) -> dict[str, Any]:
        repo = EnvelopeCommitRepository(workspace.root)
        target = f"{unit}/{file}"
        retry = f"uv run devkit workflow envelope commit --unit {shlex.quote(unit)} --file {shlex.quote(file)}"
        try:
            before = repo.state()
            raw_unit = Path(unit)
            lexical = raw_unit if raw_unit.is_absolute() else workspace.root / raw_unit
            if any(part == ".." for part in raw_unit.parts):
                raise EnvelopeCommitInvalidError("Unit path must not contain parent traversal")
            repo.regular_path(lexical / workspace.locate_anchor(lexical))
            ref = workspace.resolve_unit(unit)
            if not ref.binding.bound:
                raise EnvelopeCommitInvalidError("Unit anchor must explicitly bind a workflow")
            anchor_path = (ref.dir / ref.anchor).relative_to(workspace.root).as_posix()
            anchor_entry = repo.tree_entry(before, anchor_path)
            if anchor_entry is None:
                raise EnvelopeCommitInvalidError("Unit anchor must be tracked in HEAD")
            anchor = parse(repo.blob(anchor_entry[1]).decode("utf-8"))
            selected = Path(file)
            if (
                selected.parts != ("envelopes", selected.name)
                or FILE.fullmatch(selected.name) is None
                or file != selected.as_posix()
            ):
                raise EnvelopeCommitInvalidError(
                    "--file must name one literal immediate envelopes/<kind>-<NN>.yaml file"
                )
            path = ref.dir / selected
            repo.regular_path(path)
            content = path.read_bytes()
            loaded = load_envelopes(ref.dir)
            errors = [e for e in loaded.errors if e.file == file]
            envelope = next((e for e in loaded.all() if e.file == file), None)
            if errors or envelope is None:
                raise EnvelopeCommitInvalidError("selected envelope is malformed", *(str(e) for e in errors))
            if envelope.kind == "reverify" and not any(e.name == envelope.review for e in loaded.all()):
                raise EnvelopeCommitInvalidError("reverify names no existing review/challenger round")
            require_authored(envelope, ref.doc.id, ref.binding.segment, {s.id for s in ref.doc.stages})
            subject, body = commit_message(str(anchor.get("id", "")), envelope)
            target = path.relative_to(workspace.root).as_posix()
            already = repo.preflight(target, content, before)
            after = before if already else repo.commit(target, content, before, subject, body)
        except EnvelopeCommitFailedError as exc:
            exc.fix = (exc.fix or "Fix the Git cause") + f"; run `{retry}`"
            raise
        except EnvelopeCommitUncertainError:
            raise
        except (EnvelopeCommitInvalidError, EnvelopeCommitStateError) as exc:
            if not exc.target_files or exc.target_files == (file,):
                exc.target_files = (target,)
            if not exc.fix:
                exc.fix = f"Correct the reported precondition, then run `{retry}`; combined changes use a manual commit"
            raise
        except (WorkflowError, FrontmatterError, OSError, UnicodeError, ValueError) as exc:
            raise EnvelopeCommitInvalidError(
                str(exc), target_files=[target], fix=f"Correct the selected Unit/file, then run `{retry}`"
            ) from exc
        except GitError as exc:
            raise EnvelopeCommitStateError(
                str(exc), target_files=[target], fix=f"Inspect Git state, fix the cause, then run `{retry}`"
            ) from exc
        return {
            "unit": ref.rel,
            "file": file,
            "outcome": "already_committed" if already else "committed",
            "head": after,
            "subject": None if already else subject,
            "notices": [],
        }
