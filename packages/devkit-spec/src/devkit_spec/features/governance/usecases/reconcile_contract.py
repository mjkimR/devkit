"""``RULE-reconcile-contract``: a ``reconcile.md`` record is well formed.

``specs/<YYYY-MM>/<YYYYMMDD>-<slug>/reconcile.md`` records how a change was reconciled into the Living Spec. Its
frontmatter needs ``reconcile_id`` (its value is ``RULE-id-convention``'s), ``status`` ``pending`` (reconciliation
under way) or ``resolved``, and ``targets``: a list of ``{file, resolution, rationale}`` where ``file`` is a
workspace-relative path in canonical form (``docs/a.md``, not ``./docs/a.md`` or ``docs//a.md``), unique in the
list, ``resolution`` is ``modified`` (the Living Spec file changed with this work) or ``waived`` (no change needed),
and a waiver's ``rationale`` holds at least 20 non-whitespace characters, so it says why. Whether a completed spec has a resolved record is ``RULE-spec-lifecycle``'s.

The design, domain and operations assessment is indexed in the same frontmatter: a role is covered by a nonempty
``related_designs``, ``related_domains`` or ``related_operations`` list, or by ``formal_docs.<role>: "none: <reason>"``
with at least 20 non-whitespace characters of reason, never both. A present ``formal_docs`` is checked for that form
in every run.

Checked on every targeted ``reconcile.md`` of a current bundle (a completed bundle's record is history, checked only
when named as an explicit target). In a snapshot run (``check --staged`` at commit time, ``check --ci`` on a pull
request) a resolved record the diff changes must also have its evidence: every ``modified`` target is changed or
deleted on the branch. ``--ci`` judges the whole branch against its merge base. At commit time the staged diff is
read together with the branch's earlier commits since its merge base with the branch it integrates into (the
``devkitBase`` a ``--no-worktree`` start recorded, else the base checkout's branch, else ``origin/HEAD``), so a
target an earlier commit of the branch changed (an ADR the handoff promoted) counts too. When no such base can be
found, the staged diff alone is the evidence.

A snapshot run also requires every role to be covered on a resolved record the diff changes that no parent of the
commit has ``resolved``: the snapshot base, and in a staged run each commit named by ``MERGE_HEAD``,
``CHERRY_PICK_HEAD`` or ``REVERT_HEAD``, so concluding a merge, cherry-pick or revert never requires coverage of a
record the merged, picked or reverted commit already resolved.
"""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_core.core import (
    FrontmatterError,
    GitError,
    is_safe_relpath,
    normalize_relpath,
    run_git,
    run_git_text,
    worktree_records,
)
from devkit_core.core.frontmatter import parse
from devkit_docs.features.governance import explicitly_targeted

from devkit_spec.features.governance.services.applicability import LifecycleRule as BaseRule
from devkit_spec.features.governance.services.applicability import applies
from devkit_spec.features.policy.repositories.branches import recorded_base

RULE_ID = "RULE-reconcile-contract"
STATUSES = ("pending", "resolved")
RESOLUTIONS = ("modified", "waived")
MIN_RATIONALE = 20
ROLES = {"design": "related_designs", "domain": "related_domains", "operations": "related_operations"}
NONE_PREFIX = "none: "
OPERATION_HEADS = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD")
REMEDIATION = (
    "Give reconcile.md reconcile_id, status pending|resolved and targets: [{file, resolution: modified|waived,"
    f" rationale}}] with a rationale of at least {MIN_RATIONALE} non-whitespace characters for each waiver; cover"
    " each of the design, domain and operations roles by affected IDs in related_designs, related_domains or"
    ' related_operations, or by formal_docs.<role>: "none: <reason>"'
)


def _length(text: str) -> int:
    return sum(not char.isspace() for char in text)


def _listed(data: dict[str, object], role: str) -> bool:
    """Whether the role's ``related_*`` list names at least one ID."""
    value = data.get(ROLES[role])
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _formal_docs_problems(data: dict[str, object]) -> list[str]:
    """Form of a present ``formal_docs``: a mapping of roles to ``none: <reason>``, never beside the role's IDs."""
    if "formal_docs" not in data:
        return []
    value = data.get("formal_docs")
    if not isinstance(value, dict):
        return ["formal_docs must be a mapping of design, domain and operations to a none reason"]
    problems: list[str] = []
    for key, reason in value.items():
        if key not in ROLES:
            problems.append(f"formal_docs.{key} is not a role: use design, domain or operations")
        elif not isinstance(reason, str) or not reason.startswith(NONE_PREFIX):
            problems.append(f'formal_docs.{key} must be a string starting "{NONE_PREFIX}" followed by the reason')
        elif (length := _length(reason[len(NONE_PREFIX) :])) < MIN_RATIONALE:
            problems.append(
                f"formal_docs.{key} needs a reason of at least {MIN_RATIONALE} non-whitespace characters, has {length}"
            )
        elif _listed(data, key):
            problems.append(
                f"formal_docs.{key} conflicts with {ROLES[key]}: give affected IDs or a none reason, not both"
            )
    return problems


def _problems(data: dict[str, object]) -> list[str]:
    problems: list[str] = []
    if not isinstance(data.get("reconcile_id"), str) or not str(data.get("reconcile_id")).strip():
        problems.append("reconcile_id is missing")
    status = data.get("status")
    if status not in STATUSES:
        problems.append(f"status must be pending or resolved, got {status!r}")
    targets = data.get("targets")
    if not isinstance(targets, list):
        problems.append("targets must be a list (empty when nothing in the Living Spec is affected)")
        return problems
    seen: set[str] = set()
    for position, target in enumerate(targets, 1):
        if not isinstance(target, dict):
            problems.append(f"targets[{position}] must be a mapping of file, resolution and rationale")
            continue
        file = target.get("file")
        if isinstance(file, str) and is_safe_relpath(file) and not is_safe_relpath(file, canonical=True):
            # Uniqueness and the diff evidence compare paths as written, so only the canonical form is accepted.
            problems.append(
                f"targets[{position}].file {file!r} must be written in canonical form: {normalize_relpath(file)}"
            )
        elif not isinstance(file, str) or not is_safe_relpath(file) or file in seen:
            problems.append(f"targets[{position}].file {file!r} must be a unique workspace-relative path")
        else:
            seen.add(file)
        resolution = target.get("resolution")
        if resolution not in RESOLUTIONS:
            problems.append(f"targets[{position}].resolution must be modified or waived, got {resolution!r}")
        elif resolution == "waived":
            rationale = target.get("rationale")
            length = _length(rationale) if isinstance(rationale, str) else 0
            if length < MIN_RATIONALE:
                problems.append(
                    f"targets[{position}] waiver of {file} needs a rationale of at least {MIN_RATIONALE}"
                    f" non-whitespace characters, has {length}"
                )
    problems.extend(_formal_docs_problems(data))
    return problems


def _evidence(ctx: RuleContext, relative: str, data: dict[str, object]) -> list[str]:
    """In a snapshot run, the ``modified`` targets of a resolved record that the diff does not change.

    Applies to a record the diff itself changes. A record whose frontmatter equals the base's is retained history
    whose body alone changed (a link rewrite): it claims nothing new about this diff and is skipped.
    """
    snapshot = ctx.snapshot
    if snapshot is None or relative not in snapshot.changed or data.get("status") != "resolved":
        return []
    try:
        base = run_git(snapshot.root, "show", f"{snapshot.base}:{relative}").decode("utf-8", errors="replace")
        if parse(base).data == data:
            return []
    except (GitError, FrontmatterError):
        pass  # a new record, or a base version that cannot be compared: check it
    targets = data.get("targets")
    if not isinstance(targets, list):
        return []
    claimed = [t["file"] for t in targets if isinstance(t, dict) and t.get("resolution") == "modified"]
    diff = {*snapshot.changed, *snapshot.deleted}
    missing = [file for file in claimed if file not in diff]
    if missing and snapshot.mode == "staged":
        earlier = _branch_changes(snapshot.root, snapshot.tree)
        missing = [file for file in missing if file not in earlier]
    where = "the staged diff or the branch's earlier commits" if snapshot.mode == "staged" else "the ci diff"
    return [f"target {file} is resolved as modified but absent from {where}" for file in missing]


def _coverage(ctx: RuleContext, relative: str, data: dict[str, object]) -> list[str]:
    """In a snapshot run, the uncovered roles of a resolved record the diff changes and no parent has resolved."""
    snapshot = ctx.snapshot
    if snapshot is None or relative not in snapshot.changed or data.get("status") != "resolved":
        return []
    parents = [snapshot.base, *(_operation_heads(snapshot.root) if snapshot.mode == "staged" else [])]
    if any(_resolved_at(snapshot.root, parent, relative) for parent in parents):
        return []
    reasons = data.get("formal_docs")
    reasons = reasons if isinstance(reasons, dict) else {}
    return [
        f"formal_docs role {role} is not covered: list affected IDs in {field} or give"
        f' formal_docs.{role}: "{NONE_PREFIX}<reason>"'
        for role, field in ROLES.items()
        if not _listed(data, role) and role not in reasons
    ]


def _resolved_at(root: Path, revision: str, relative: str) -> bool:
    """Whether ``relative`` is a ``resolved`` record at ``revision``; ``False`` when it is absent or unreadable."""
    try:
        text = run_git(root, "show", f"{revision}:{relative}").decode("utf-8", errors="replace")
        data = parse(text).data
    except (GitError, FrontmatterError):
        return False
    return isinstance(data, dict) and data.get("status") == "resolved"


def _operation_heads(root: Path) -> list[str]:
    """The commits an in-progress merge, cherry-pick or revert names (``MERGE_HEAD`` lists one per merged head)."""
    git_dir = _git(root, "rev-parse", "--absolute-git-dir")
    if not git_dir:
        return []
    heads: list[str] = []
    for name in OPERATION_HEADS:
        try:
            content = (Path(git_dir) / name).read_text(encoding="utf-8")
        except OSError:
            continue
        heads.extend(line.strip() for line in content.splitlines() if line.strip())
    return heads


def _git(root: Path, *args: str) -> str | None:
    try:
        return run_git_text(root, *args)
    except GitError:
        return None


def _integration_base(root: Path) -> str | None:
    """The branch the current one integrates into: its recorded ``devkitBase`` (``devkit worktree start
    --no-worktree``), else the base checkout's branch (the first ``git worktree list`` entry) when it is another,
    else ``origin/HEAD``; ``None`` when none resolves."""
    branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if not branch:
        return None
    try:
        recorded = recorded_base(root, branch)
    except GitError:
        recorded = ""
    if recorded:
        return recorded
    try:
        listing = worktree_records(root)
    except GitError:
        listing = []
    first = next((record.branch for record in listing if record.branch), "")
    base_branch = first.removeprefix("refs/heads/")
    if base_branch and base_branch != branch:
        return base_branch
    remote_head = _git(root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    return remote_head or None


def _branch_changes(root: Path, tree: str) -> set[str]:
    """Paths the branch changed since its merge base with the branch it integrates into, up to the staged ``tree``;
    empty when that base cannot be found."""
    base = _integration_base(root)
    merge_base = _git(root, "merge-base", base, "HEAD") if base else None
    if not merge_base:
        return set()
    names = _git(root, "diff", "--name-only", "-z", "--no-renames", merge_base, tree, "--")
    return {name for name in (names or "").split("\0") if name}


class ReconcileContractRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="reconcile-contract",
            description=(
                "A reconcile.md record has an id, a pending or resolved status, well-formed targets and, once newly"
                " resolved, a design, domain and operations assessment."
            ),
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        root = ctx.workspace_root
        if not (root / "specs").is_dir():
            return []
        found: list[Violation] = []
        for path in ctx.cache.find_files(root / "specs", extensions=(".md",)):
            relative = ctx.cache.relative_name(path)
            if not applies(ctx, relative):
                continue
            parts = relative.split("/")
            if path.name != "reconcile.md" or len(parts) != 4 or not ctx.is_file_targeted(relative):
                continue
            if self._completed(ctx, "/".join(parts[:3])) and not explicitly_targeted(ctx, relative):
                continue
            try:
                data = ctx.cache.get_frontmatter(path)
            except FrontmatterError as exc:
                found.append(self._violation(relative, f"frontmatter is malformed: {exc.message}"))
                continue
            if data is None:
                found.append(self._violation(relative, "reconcile.md has no frontmatter"))
                continue
            problems = _problems(data)
            found.extend(self._violation(relative, problem) for problem in problems)
            if not problems:
                found.extend(self._violation(relative, problem) for problem in _evidence(ctx, relative, data))
                found.extend(self._violation(relative, problem) for problem in _coverage(ctx, relative, data))
        return found

    def _completed(self, ctx: RuleContext, bundle: str) -> bool:
        spec = ctx.workspace_root / bundle / "spec.md"
        try:
            data = ctx.cache.get_frontmatter(spec) if spec.is_file() else None
        except FrontmatterError:
            return False
        status = data.get("status") if data else None
        return isinstance(status, str) and status.strip().lower() == "completed"

    def _violation(self, file: str, message: str) -> Violation:
        return Violation(rule_id=self.id, file=file, line=1, message=message, remediation=REMEDIATION)
