---
sources:
  CAP-DLV-maintenance-history: null
  UC-record-a-maintenance-run: null
title: 유지보수 실행 기록하기
translated_from: en/journeys/record-a-maintenance-run.md@6fc3381b7fda3bfe
---

# 유지보수 실행 기록하기

<!-- handbook:provenance -->
> 소스 커밋 `a6e769c5721d` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](assess-test-management.md)
- [필요한 명령 진입점 설계하기](design-command-entrypoints.md)
- [아이디어 발굴하고 구체화하기](discover-and-refine-an-idea.md)
- [개발에서 통합까지 진행하기](drive-development-to-integration.md)
- [격리된 명령 실행하기](execute-an-isolated-command.md)
- [설계 문제 탐색하기](explore-a-design-problem.md)
- [최신 유지보수 실행 찾기](find-the-latest-maintenance-run.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [선택한 외부 에이전트 자산 가져오기](import-third-party-agent-assets.md)
- [인터페이스와 사용 흐름 개선하기](improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [제안 계획 후 넘기기](plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [결정 대체 관계 읽기](read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [아이디어 조사와 로드맵 구체화하기](research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
- [번들 소스를 로컬로 도입하고 갱신하기](snapshot-bundle-sources.md)
- [선택한 느린 작업 빠르게 하기](speed-up-selected-slow-operations.md)
- [어드바이저리](../areas/advisory.md)
- [에이전트 우선 CLI 도구 키트](../areas/cli.md)
- [협업](../areas/collaboration.md)
- [컴팩트 명령 출력](../areas/compact.md)
- [전달](../areas/delivery.md)
- [배포](../areas/distribution.md)
- [문서](../areas/documents.md)
- [커밋 게이트](../areas/gate.md)
- [생성 파일](../areas/generated.md)
- [거버넌스 규칙](../areas/governance.md)
- [하네스](../areas/harness.md)
- [호스트](../areas/host.md)
- [통합](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [검색](../areas/search.md)
- [추적성](../areas/traceability.md)
- [뷰어](../areas/viewer.md)
- [워크트리](../areas/worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

유지보수 이력(maintenance history)은 유지보수 플레이북과 함께 명시적으로 요청하는 동반 작업입니다.
명령 설치나 플레이북 호출만으로 수집을 시작하거나 반복 제안하지 않습니다.
기본 플레이북의 보고서와 완료 절차는 독립적으로 유지됩니다.

## 수집과 동결

유지보수 범위, 보고서 경로와 로컬 실행 디렉터리를 정한 뒤 명령을 사용합니다.

```text
uv run devkit maintenance history start --playbook <playbook> --scope <scope> --into <run-dir> --report <report>
uv run devkit maintenance history finish --run <run-dir> --outcome completed
```

start는 HEAD, 수정 경로, 검사한 콘텐츠 트리와 수정 diff digest를 기록하면서 실제 index·ref와 실행 디렉터리 밖의 파일을 보존합니다.
보고서를 작성·검증하고 `finish --file <path>`로 추가 근거를 등록한 뒤 검사한 바이트를 동결합니다.
인식된 비밀 정보는 `HISTORY_SECRET_FOUND`로 완료를 거부합니다.
검사한 콘텐츠가 바뀌면 `HISTORY_RUN_DRIFTED`가 근거 재검증을 요구합니다.

## 별도로 게시하기

자격 증명 없는 저장소와 전용 이력 브랜치를 선택하고 승인합니다.
대상 설정은 입력만 제공하며 `init`, `publish`, `update`는 각각 명시적 `--authority`가 필요합니다.
`uv run devkit maintenance history publish --run <run-dir> --authority <authority>`로 기록과 보고서를 게시합니다.
동결한 추가 근거는 반복 가능한 `--file`로 선택합니다.

게시 과정은 선택 파일·정규 기록·연도별 인덱스 항목을 강제하지 않는 ref 갱신으로 한 번에 공개합니다.
브랜치가 없으면 별도로 승인된 초기화가 필요하고 외부 브랜치 루트는 거부합니다.
응답이 유실되면 원래 바이트로 같은 작업에서 상태를 확인합니다. 원격 기록이 일치하면 재전송 없이 원래 게시를 확인합니다.
동결한 근거가 바뀌면 새 실행이 필요합니다.

실행 결과(completed, failed, interrupted)와 게시 상태(pending, published, failed, unknown)는 별개입니다.
이후 통합 상태 변경은 승인된 `update --integration-state <state>` 추가 기록으로 남기며 게시된 근거를 고치지 않습니다.
[최신 유지보수 실행 찾기](find-the-latest-maintenance-run.md)를 참고하십시오.

## 출처

- [UC-record-a-maintenance-run](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-record-a-maintenance-run.md) (영어 원문)
- [CAP-DLV-maintenance-history](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-maintenance-history.md) (영어 원문)
