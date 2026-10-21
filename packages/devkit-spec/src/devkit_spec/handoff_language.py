"""Concise handoff disclosure with exact source-bound report identity."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devkit_spec.handoff_mcp import HandoffPreview


def message(preview: HandoffPreview, language: str) -> str:
    def t(en: str, ko: str) -> str:
        return ko if language == "ko" else en

    def show(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    setup = show(preview.setup) if preview.setup else t("none", "없음")
    return "\n".join(
        [
            t("Start Development: ", "Development 시작: ") + show(preview.title),
            t("Goal: ", "목표: ") + show(preview.summary)
            if preview.summary
            else t("Goal: Read the accepted plan.", "목표: 수락된 계획을 읽어주세요."),
            t(
                "Next: create the Development worktree, hand off the accepted plan, then continue implementation.",
                "다음 단계: Development worktree를 만들고 수락된 계획을 인계한 뒤 구현을 계속합니다.",
            ),
            t(
                f"Review and verification level: {preview.effort} recommended by dev_effort (medium when absent).",
                f"검토 및 검증 수준: dev_effort의 권장값은 {preview.effort}입니다(미지정 시 medium).",
            ),
            t(
                "low: self-review. medium: independent initial review. high: repeated independent review.",
                "low: 자체 검토. medium: 독립적인 최초 검토. high: 반복적인 독립 검토.",
            ),
            t(
                "Required checks apply at every level. This selection does not change model reasoning settings.",
                "모든 수준에서 필수 검사를 수행합니다. 이 선택은 모델 추론 설정을 변경하지 않습니다.",
            ),
            t("Review report: ", "검토 보고서: ") + show(preview.report_uri),
            t("Repository: ", "저장소: ") + show(str(preview.root)),
            t("Base: ", "기준: ") + f"{show(preview.base_branch)} @ {preview.head}",
            t("Reuse branch: ", "재사용할 브랜치: ") + show("dev-" + preview.slug)
            if preview.existing
            else t("Create branch: ", "만들 브랜치: ") + show("dev-" + preview.slug),
            t("Completed: worktree creation. Reuse worktree: ", "완료: worktree 생성. 재사용할 worktree: ")
            + show(preview.worktree)
            if preview.existing
            else t("Create worktree: ", "만들 worktree: ") + show(preview.worktree),
            t(
                f"Run configured setup: {setup}; restore locked agent assets.",
                f"설정된 setup 실행: {setup}; 잠긴 에이전트 자산을 복원합니다.",
            ),
            t(
                "Handoff creates the spec bundle and retires the proposal only inside this new worktree.",
                "인계는 이 새 worktree 안에서만 spec 묶음을 만들고 proposal을 정리합니다.",
            ),
            t(
                "This approves starting Development. Final merge requires its own approval.",
                "이 승인은 Development 시작에만 적용됩니다. 최종 병합에는 별도 승인이 필요합니다.",
            ),
        ]
    )


def schema(effort: str, language: str) -> dict:
    korean = language == "ko"
    return {
        "type": "object",
        "properties": {
            "approve": {
                "type": "boolean",
                "title": "이 계획의 Development 시작" if korean else "Start Development of this plan",
                "default": False,
            },
            "activity_effort": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "default": effort,
                "title": "검토 및 검증 수준" if korean else "Review and verification level",
            },
        },
        "required": ["approve", "activity_effort"],
    }
