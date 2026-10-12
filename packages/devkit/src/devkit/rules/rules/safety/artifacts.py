from __future__ import annotations

from pathlib import PurePosixPath

from devkit.rules.engine.models import Phase, RuleContext, Severity, Violation
from devkit.rules.rules.base import BaseRule

BINARY_MAGIC = (
    b"\x7fELF",  # ELF
    b"MZ",  # PE / DOS
    b"\xcf\xfa\xed\xfe",  # Mach-O 64-bit
    b"\xce\xfa\xed\xfe",  # Mach-O 32-bit
    b"\xca\xfe\xba\xbe",  # Mach-O universal
)
DATABASE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
MAX_LOG_BYTES = 1024 * 1024


class CleanArtifactsRule(BaseRule):
    """Flag compiled binaries, database files and oversized logs among the files under check.

    Like ``RULE-secret-leak`` it inspects explicit targets only.
    """

    def __init__(self) -> None:
        super().__init__(
            id="RULE-clean-artifacts",
            name="clean-artifacts",
            description="Generated binaries, databases and oversized logs must not be committed.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="artifacts.md",
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for rel in ctx.changed_files:
            path = ctx.workspace_root / rel
            if not path.is_file():
                continue
            suffix = PurePosixPath(rel).suffix.lower()
            size = path.stat().st_size
            with path.open("rb") as handle:
                head = handle.read(4)
            if head.startswith(BINARY_MAGIC):
                message = "Compiled binary"
            elif suffix in DATABASE_SUFFIXES:
                message = "Database file"
            elif suffix == ".log" and size > MAX_LOG_BYTES:
                message = f"Log file larger than {MAX_LOG_BYTES} bytes"
            else:
                continue
            violations.append(
                Violation(
                    rule_id=self.id,
                    file=rel,
                    line=1,
                    message=f"{message} should not be committed",
                    remediation="Remove the generated artifact from the change and add an ignore rule",
                    severity=self.severity,
                    phase=self.phase,
                )
            )
        return violations
