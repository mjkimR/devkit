import pytest

from devkit_spec.base.errors import HandoffReplyError
from devkit_spec.features.delivery.usecases.native_handoff import HandoffPreview, HandoffUseCase


@pytest.mark.parametrize(
    ("policy", "effort", "authority"), [("ask", "low", "host-conversation"), ("auto", "medium", "policy")]
)
def test_handoff_cli_uses_host_or_retained_policy_authority(tmp_path, monkeypatch, policy, effort, authority):
    preview = HandoffPreview(
        tmp_path,
        "idea",
        "sha",
        "main",
        "/worktree",
        None,
        "digest",
        "title",
        "summary",
        "plan",
        "medium",
        "shared://fixture",
    )
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.prepare", lambda *args: preview)
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.validate", lambda *args: None)
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.approval_policy", lambda *_args: policy)
    executed = []
    service = HandoffUseCase(tmp_path)
    monkeypatch.setattr(
        service,
        "_execute",
        lambda current, selected: executed.append((current, selected)) or {"status": "handed_off"},
    )

    result = service.execute("idea", "shared://fixture", effort)
    assert result["authority"] == authority
    assert result["status"] == "handed_off"
    assert executed == [(preview, effort)]


def test_automatic_handoff_uses_the_declared_effort(tmp_path, monkeypatch):
    preview = HandoffPreview(tmp_path, "idea", "sha", "main", "/worktree", None, "digest", "title", "", "plan", "high")
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.prepare", lambda *args: preview)
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.validate", lambda *args: None)
    monkeypatch.setattr("devkit_spec.features.delivery.usecases.native_handoff.approval_policy", lambda *_args: "auto")
    with pytest.raises(HandoffReplyError):
        HandoffUseCase(tmp_path).execute("idea", "shared://fixture", "medium")
