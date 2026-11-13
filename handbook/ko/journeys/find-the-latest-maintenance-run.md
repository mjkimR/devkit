---
sources:
  CAP-DLV-maintenance-history: null
  UC-find-the-latest-maintenance-run: null
title: 최신 유지보수 실행 찾기
translated_from: en/journeys/find-the-latest-maintenance-run.md@988fdb1dd957bc37
---

# 최신 유지보수 실행 찾기

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
- [유지보수 실행 기록하기](record-a-maintenance-run.md)
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

이전에 게시한 보고서나 이후 통합 결과가 필요할 때 유지보수 이력(maintenance history)을 사용합니다.
근거를 고르기 전에 플레이북과 저장소를 확인합니다.

```bash
uv run devkit maintenance history list --playbook <playbook> --limit 20
uv run devkit maintenance history get --run-id <run-id> --file report.md
```

list는 최신 연도부터 읽고 마지막 추가 기록을 합치며 대체된 실행은 기본적으로 제외합니다.
`--source-sha`, `--outcome`으로 좁히거나 `--include-superseded`로 대체된 실행도 포함합니다.
소스 SHA(source SHA)는 시작 때 검사한 HEAD이며 `inspected_tree`가 수정 콘텐츠까지 식별합니다.

실행과 파일을 고릅니다. get의 기본 파일은 `record.json`입니다.
`HISTORY_FILE`은 임의 바이트를 보존하도록 base64 콘텐츠를 반환합니다.
조회는 로컬 Git ref를 fetch하거나 체크아웃·근거를 변경하지 않습니다.

이력 브랜치가 없으면 알림과 빈 목록을 반환합니다. 실행·파일이 없으면 `HISTORY_RUN_MISSING`입니다.
호출 제한은 `retry_after`를 포함한 `HISTORY_DEFERRED`를 반환하므로 나중에 재시도합니다.
이력 부재를 이전 유지보수 성공이나 저장소가 깨끗하다는 뜻으로 해석하지 않습니다.
수집·게시는 [유지보수 실행 기록하기](record-a-maintenance-run.md)를 참고하십시오.

## 출처

- [UC-find-the-latest-maintenance-run](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-find-the-latest-maintenance-run.md) (영어 원문)
- [CAP-DLV-maintenance-history](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-maintenance-history.md) (영어 원문)
