from __future__ import annotations

import re
from pathlib import PurePosixPath

from devkit_agt.features.rules.models.contracts import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins.base import BaseRule

# Each named group is one kind of credential; the group name is reported.
SECRET_PATTERN = re.compile(
    rb"(?P<private_key>-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----)"
    rb"|(?P<aws_access_key>\b(?:AKIA|ASIA)[0-9A-Z]{16}\b)"
    rb"|(?P<github_token>\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b)"
    rb"|(?P<api_key>\bsk-[A-Za-z0-9_-]{20,}\b)"
    rb"|(?P<stripe_key>\b[rs]k_live_[A-Za-z0-9]{20,}\b)"
    rb"|(?P<slack_token>\bxox[abposr]-[A-Za-z0-9-]{10,}\b)"
    rb"|(?P<google_api_key>\bAIza[0-9A-Za-z_-]{35}\b)"
)
TEMPLATE_SUFFIXES = (".example", ".sample", ".template")
KEY_FILES = {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"}
KEY_SUFFIXES = {".key", ".p12", ".pfx", ".jks", ".keystore"}


def is_env_file(name: str) -> bool:
    """``.env``, ``.env.<anything>`` and ``<anything>.env``, except templates (``*.example``/``.sample``/``.template``)."""
    if name.endswith(TEMPLATE_SUFFIXES):
        return False
    return name == ".env" or name.startswith(".env.") or (name.endswith(".env") and len(name) > len(".env"))


def credential_file(name: str) -> bool:
    """Whether a file name alone marks a credential (environment files, SSH private keys, key stores)."""
    return is_env_file(name) or name in KEY_FILES or PurePosixPath(name).suffix.lower() in KEY_SUFFIXES


class SecretLeakRule(BaseRule):
    """Flag credentials in the files under check.

    The rule only inspects explicit targets (``check FILES`` or a Git snapshot's
    changed files); a whole working tree scan would flag ignored local files
    such as ``.env``, so with no targets it reports nothing. Each matching line
    is reported once, with the kind of credential found.
    """

    def __init__(self) -> None:
        super().__init__(
            id="RULE-secret-leak",
            name="secret-leak",
            description="Private keys, API tokens and .env files must not enter the repository.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
        )

    def _violation(self, rel: str, line: int, message: str) -> Violation:
        return Violation(
            rule_id=self.id,
            file=rel,
            line=line,
            message=message,
            remediation="Remove the secret from the change; use placeholders or external credentials",
            severity=self.severity,
            phase=self.phase,
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for rel in ctx.changed_files:
            path = ctx.workspace_root / rel
            if not path.is_file():
                continue
            name = PurePosixPath(rel).name
            if credential_file(name):
                violations.append(self._violation(rel, 1, f"{name} is a credential file"))
                continue
            data = ctx.cache.read_bytes(path)
            reported: set[int] = set()
            for match in SECRET_PATTERN.finditer(data):
                line = data.count(b"\n", 0, match.start()) + 1
                if line in reported:
                    continue
                reported.add(line)
                kind = (match.lastgroup or "secret").replace("_", " ")
                violations.append(self._violation(rel, line, f"Potential secret in file content ({kind})"))
        return violations
