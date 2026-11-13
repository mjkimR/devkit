---
sources:
  CAP-VIEW-repository-viewer: null
  UC-read-decision-supersession: null
title: 결정 대체 관계 읽기
translated_from: en/journeys/read-decision-supersession.md@eb1026cb39a885b2
---

# 결정 대체 관계 읽기

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

Read 또는 렌더링된 Files에서 ADR을 열면 머리말 아래에 Supersedes와 Superseded by가 표시됩니다. 전체 대체는 이전 결정의 상태와 상호 메타데이터를 따르며 나머지는 부분 대체와 작성된 조항 범위를 보여줍니다.

확인된 결정 링크는 같은 뷰어에서 따라갑니다. 없거나 모호한 ID는 링크 없이 표시하고 범위 누락도 명시합니다. PADR은 Proposed supersession과 해당 Planning 출처를 보여주며 적용된 ADR의 역방향 관계에는 포함되지 않습니다.

인덱싱이나 일부 읽기가 끝나지 않아도 본문은 읽을 수 있습니다. 불완전한 결과에는 실패한 경로와 Reload relations가 표시됩니다. 불완전한 빈 목록은 역방향 관계가 없다는 증거가 아닙니다. 출처나 브랜치를 바꾸면 이전 컨텍스트 결과를 버립니다. 읽기는 저장소 파일을 변경하지 않습니다.

## 출처

- [UC-read-decision-supersession](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/viewer/UC-read-decision-supersession.md) (영어 원문)
- [CAP-VIEW-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/viewer/CAP-VIEW-repository-viewer.md) (영어 원문)
