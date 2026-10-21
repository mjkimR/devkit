import json
from pathlib import Path

import pytest

from devkit_spec.features.delivery.usecases.native_handoff import HandoffPreview
from devkit_spec.features.proposals.models.approval import schema


@pytest.mark.parametrize("setup", [None, 'just init && echo "evidence"'])
@pytest.mark.parametrize("effort", ["low", "medium", "high"])
def test_handoff_message_and_schema_parity(setup, effort):
    preview = HandoffPreview(
        Path("/repository"),
        "idea",
        "sha",
        "main",
        "/worktree",
        setup,
        "digest",
        "title\nverbatim",
        "summary unchanged",
        "Plan 한국어 and English",
        effort,
        "shared://exact-report",
    )
    en, ko = preview.message("en"), preview.message("ko")
    for evidence in (preview.title, preview.summary, preview.report_uri, str(preview.root), preview.worktree):
        assert json.dumps(evidence, ensure_ascii=False) in en
        assert json.dumps(evidence, ensure_ascii=False) in ko
    assert preview.plan not in en and preview.plan not in ko
    for value in ("low", "medium", "high", "dev_effort"):
        assert value in en and value in ko
    assert "Final merge requires its own approval" in en and "최종 병합에는 별도 승인" in ko

    # A client omitting all field metadata still receives complete effort/approval semantics in message.
    def canonical(value):
        return (
            {k: canonical(v) for k, v in value.items() if k not in {"title", "description"}}
            if isinstance(value, dict)
            else value
        )

    assert canonical(schema(effort, "en")) == canonical(schema(effort, "ko"))
    assert schema(effort, "ko")["properties"]["approve"]["default"] is False


@pytest.mark.parametrize("language", ["en", "ko"])
@pytest.mark.parametrize("case", ["accept", "false", "decline", "cancel", "malformed", "unavailable", "stale"])
def test_handoff_language_does_not_change_authority(tmp_path, monkeypatch, language, case):
    import asyncio

    from devkit_core.base.mcp import ConfirmationReply
    from devkit_dist.features.host.models.errors import HostConfirmationError

    from devkit_spec.base.errors import HandoffReplyError, HandoffStaleError
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase

    (tmp_path / ".devkit").mkdir()
    local = tmp_path / ".devkit/config.local.toml"
    local.write_text(f'[presentation]\nlanguage="{language}"\n')
    preview = HandoffPreview(
        tmp_path, "idea", "sha", "main", "/worktree", None, "digest", "title", "", "plan", "medium"
    )
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.prepare", lambda *args: preview)
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.validate", lambda *args: None)
    service = HandoffUseCase(tmp_path)
    executed = []

    def execute(current, effort):
        if case == "stale":
            raise HandoffStaleError("fixture changed scope")
        executed.append((current, effort))
        return {"status": "fixture-only"}

    monkeypatch.setattr(service, "_execute", execute)

    async def confirm(message, requested):
        assert message == preview.message(language)
        assert requested == schema("medium", language)
        assert "low" in message and "medium" in message and "high" in message
        local.write_text('[presentation]\nlanguage="en"\n')
        assert message == preview.message(language)
        if case == "unavailable":
            raise HostConfirmationError("fixture missing capability")
        return ConfirmationReply(
            case if case in {"decline", "cancel"} else "accept",
            {"approve": case != "false", "activity_effort": "translated" if case == "malformed" else "low"},
        )

    error = {"unavailable": HostConfirmationError, "malformed": HandoffReplyError, "stale": HandoffStaleError}.get(case)
    if error:
        with pytest.raises(error):
            asyncio.run(service.execute("idea", "shared://fixture", confirm))
    else:
        result = asyncio.run(service.execute("idea", "shared://fixture", confirm))
        assert (
            result["status"]
            == {"accept": "fixture-only", "false": "not_approved", "decline": "declined", "cancel": "cancelled"}[case]
        )
    assert bool(executed) == (case == "accept")
