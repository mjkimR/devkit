"""Caller guidance matches the read-only roles' shell access and names the reconcile-check envelope command.

The ``challenger`` and ``reconcile-reviewer`` contracts grant a read-only shell, so the payload reference makes no
"no shell" claim, and ``spec-sync`` names the command that records a ``reconcile-check`` envelope
(``SPEC-guidance-followups``).
"""

from __future__ import annotations

from spec_support.bundle_text import raw, text


# AC-02
def test_payload_reference_makes_no_shell_claim() -> None:
    assert "no shell" not in text("skills/spec-delegate/references/payload.md")


# AC-04
def test_spec_sync_names_the_reconcile_check_envelope_command() -> None:
    verify = text("skills/spec-sync/SKILL.md").split("5. **Verify**", 1)[1].split("6. **Complete**", 1)[0]
    assert "`devkit workflow envelope new --unit <dir> --kind reconcile-check --stage living-spec-draft`" in verify
    assert "[envelope reference](../spec/references/envelope.md)" in raw("skills/spec-sync/SKILL.md")
