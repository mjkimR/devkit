"""Domain-owned English/Korean approval copy, independent of approval authority."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devkit_agt.features.integration.models.contracts import IntegrationRequest


def confirmation_message(request: IntegrationRequest, language: str) -> str:
    def t(en: str, ko: str) -> str:
        return ko if language == "ko" else en

    def display(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    def brief(value: str, limit: int = 1500) -> str:
        return display(value if len(value) <= limit else value[:limit] + t("… [truncated]", "… [잘림]"))

    plan = request.context.finish
    branch, target = display(plan.branch), display(plan.target_branch)
    if request.repository:
        repo = display(request.repository.selector)
        title = (
            t(
                f"Approve pull request cleanup of {branch}, already merged into {repo} {target}?",
                f"{branch}의 pull request 정리를 승인하시겠습니까? 이 브랜치는 이미 {repo} {target}에 병합되었습니다.",
            )
            if plan.already_merged
            else t(
                f"Approve pull request integration of {branch} into {repo} {target} with a merge commit?",
                f"병합 커밋으로 {branch}을(를) {repo} {target}에 통합하는 pull request 작업을 승인하시겠습니까?",
            )
        )
        operation = (
            t(
                f"PR {request.pr_number} is already merged. Fetch target; fast-forward local target; perform the selected cleanup below.",
                f"PR {request.pr_number}은(는) 이미 병합되었습니다. 대상을 fetch하고 로컬 대상을 fast-forward한 뒤 아래에서 선택한 정리를 수행합니다.",
            )
            if plan.already_merged
            else t(
                f"Push source; {'use PR ' + str(request.pr_number) if request.pr_number else 'create PR'}; merge; fetch; fast-forward local target.",
                f"소스를 push하고 {'PR ' + str(request.pr_number) + ' 사용' if request.pr_number else 'PR 생성'}, 병합, fetch, 로컬 대상 fast-forward를 수행합니다.",
            )
        )
        caveat = (
            t(
                "Checked landing evidence was not recorded in this process. Cleanup reports INTEGRATION_LANDED_UNCHECKED (not-recorded); run the landed-target check after cleanup.",
                "이 프로세스에 병합 결과 검증 증거가 기록되지 않았습니다. 정리 시 INTEGRATION_LANDED_UNCHECKED (not-recorded)를 보고합니다. 정리 후 병합된 대상 검사를 실행하세요.",
            )
            if plan.already_merged
            else t(
                "Merge runs now only when required checks and reviews pass; otherwise resume later on the unchanged checked target. A frequently advancing target may prevent this route from ever merging. A target commit landing after the last check can merge without devkit checks; this is reported and does not stop cleanup.",
                "필수 검사와 검토를 통과한 경우에만 지금 병합합니다. 그렇지 않으면 검사한 대상이 변경되지 않은 상태에서 나중에 재개하세요. 대상이 자주 변경되면 이 경로로는 끝내 병합하지 못할 수 있습니다. 마지막 검사 후 대상에 추가된 커밋은 devkit 검사 없이 병합될 수 있으며, 이 경우 이를 보고하되 정리는 중단하지 않습니다.",
            )
        )
        path = display(plan.path) if plan.worktree_identity else t("no", "아니요")
        return "\n".join(
            [
                title,
                t(
                    f"Source: {plan.source_sha}; confirmation target: {plan.target_sha}",
                    f"소스: {plan.source_sha}; 승인 시점 대상: {plan.target_sha}",
                ),
                operation,
                t(
                    f"Remove worktree: {path}; delete local and remote source branches: {plan.delete_branch} (remote lease {plan.source_sha}).",
                    f"worktree 삭제: {path}; 로컬 및 원격 소스 브랜치 삭제: {plan.delete_branch} (원격 lease {plan.source_sha}).",
                ),
                t("Additional cleanup: ", "추가 정리: ")
                + display(json.dumps([asdict(scope) for scope in request.cleanup])),
                t(
                    f"GitHub automatic branch deletion: {request.repository.delete_on_merge}; when enabled the platform can delete the remote branch regardless of devkit delete_branch policy.",
                    f"GitHub 자동 브랜치 삭제: {request.repository.delete_on_merge}; 활성화된 경우 플랫폼은 devkit delete_branch 정책과 관계없이 원격 브랜치를 삭제할 수 있습니다.",
                ),
                caveat,
                t("Unverified platform rules: ", "검증되지 않은 플랫폼 규칙: ")
                + display(str(request.unverified_rules)),
                t(
                    f"Result check: {display(request.readiness.disclosure)}; landed-target check after cleanup: {display(request.readiness.landed_check)}",
                    f"결과 검사: {display(request.readiness.disclosure)}; 정리 후 병합된 대상 검사: {display(request.readiness.landed_check)}",
                ),
                t(
                    "A host timeout can leave execution running; inspect worktree and Git/PR state before recovery.",
                    "호스트 시간 초과 후에도 실행이 계속될 수 있습니다. 복구 전에 worktree와 Git/PR 상태를 확인하세요.",
                ),
            ]
        )
    if plan.already_merged:
        title = t(
            f"Approve cleanup of {branch}, already merged into {target}?",
            f"{branch}의 정리를 승인하시겠습니까? 이 브랜치는 이미 {target}에 병합되었습니다.",
        )
    elif plan.merge_method == "no-ff":
        title = t(
            f"Approve local integration of {branch} into {target} with a merge commit?",
            f"병합 커밋으로 {branch}을(를) {target}에 로컬 통합하도록 승인하시겠습니까?",
        )
    else:
        title = t(
            f"Approve local integration of {branch} into {target} by fast-forward?",
            f"fast-forward로 {branch}을(를) {target}에 로컬 통합하도록 승인하시겠습니까?",
        )
    lines = [title]
    evidence = {item.code: item.value for item in request.readiness.evidence}
    for code, en, ko in (
        ("TASK_TITLE", "Work", "작업"),
        ("TASK_SUMMARY", "Goal", "목표"),
        ("RESULT_SUMMARY", "Completed work", "완료된 작업"),
    ):
        if evidence.get(code):
            lines.append(f"{t(en, ko)}: {brief(evidence[code])}")
    if plan.already_merged:
        lines.append(
            t(
                "The branch is already merged into the target: nothing is merged; only the cleanup below runs.",
                "브랜치가 이미 대상에 병합되어 있습니다. 추가 병합 없이 아래 정리만 실행합니다.",
            )
        )
    elif plan.merge_method == "no-ff":
        lines += [
            t(
                f"Later commits on the target are merged in without another confirmation only if the merge is clean, the integration policy is unchanged and readiness provider {display(request.provider)} passes again on the merged result; otherwise nothing changes on the target.",
                f"대상에 나중에 추가된 커밋은 충돌 없이 병합할 수 있고, 통합 정책이 변경되지 않았으며, 준비 상태 제공자 {display(request.provider)}가 병합 결과를 다시 통과시킨 경우에만 추가 승인 없이 함께 병합합니다. 그렇지 않으면 대상은 변경되지 않습니다.",
            ),
            t("Result check: ", "결과 검사: ") + display(request.readiness.disclosure),
        ]
    else:
        lines.append(
            t(
                "The target advances to the verified source commit (fast-forward); if the target moved, nothing changes on the target.",
                "대상을 검증된 소스 커밋으로 fast-forward합니다. 대상이 이동했다면 대상은 변경되지 않습니다.",
            )
        )
    lines += [
        "",
        t("Repository: ", "저장소: ") + display(plan.base),
        t("Task: ", "작업: ") + display(request.context.task.id),
        t("Source: ", "소스: ") + f"{branch} @ {plan.source_sha}",
        t(f"Target: {target} @ {plan.target_sha} (at confirmation)", f"대상: {target} @ {plan.target_sha} (승인 시점)"),
        t("Remove worktree: ", "worktree 삭제: ")
        + (display(plan.path) if plan.worktree_identity is not None else t("no", "아니요")),
        t("Delete local branch: ", "로컬 브랜치 삭제: ") + (branch if plan.delete_branch else t("no", "아니요")),
        t("Additional cleanup:", "추가 정리:"),
    ]
    targets = [
        f"- {display(scope.extension)}: {display(target.kind)} {display(target.identity)}"
        for scope in request.cleanup
        for target in scope.targets
    ]
    lines.extend(targets or [t("- none", "- 없음")])
    lines += [
        "",
        t(
            "Approve only if this work and the cleanup above are ready.",
            "이 작업과 위 정리가 준비된 경우에만 승인하세요.",
        ),
        t(
            "No fetch, push, remote deletion or PR operations.",
            "fetch, push, 원격 삭제 또는 PR 작업은 수행하지 않습니다.",
        ),
    ]
    return "\n".join(lines)
