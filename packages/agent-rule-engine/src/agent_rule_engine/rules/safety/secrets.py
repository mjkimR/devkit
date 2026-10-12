from __future__ import annotations

import re
from pathlib import PurePosixPath

from agent_rule_engine.engine.models import Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules.base import BaseRule

SECRET_PATTERN = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    rb"|\bAKIA[0-9A-Z]{16}\b"
    rb"|\bgh[pousr]_[A-Za-z0-9]{36,}\b"
    rb"|\bsk-[A-Za-z0-9_-]{20,}\b"
)
ENV_EXAMPLES = {".env.example", ".env.sample", ".env.template"}
KEY_FILES = {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"}


def is_env_file(name: str) -> bool:
    return name == ".env" or (name.startswith(".env.") and name not in ENV_EXAMPLES)


class SecretLeakRule(BaseRule):
    """Flag credentials in the files under check.

    The rule only inspects explicit targets (``check FILES`` or a Git snapshot's
    changed files); a whole working tree scan would flag ignored local files
    such as ``.env``, so with no targets it reports nothing.
    """

    def __init__(self) -> None:
        super().__init__(
            id="RULE-secret-leak",
            name="secret-leak",
            description="Private keys, API tokens and .env files must not enter the repository.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="secrets.md",
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for rel in ctx.changed_files:
            path = ctx.workspace_root / rel
            if not path.is_file():
                continue
            name = PurePosixPath(rel).name
            if is_env_file(name) or name in KEY_FILES:
                message = f"{name} is a credential file"
            elif SECRET_PATTERN.search(ctx.cache.read_bytes(path)):
                message = "Potential secret in file content"
            else:
                continue
            violations.append(
                Violation(
                    rule_id=self.id,
                    file=rel,
                    line=1,
                    message=message,
                    remediation="Remove the secret from the change; use placeholders or external credentials",
                    severity=self.severity,
                    phase=self.phase,
                )
            )
        return violations
