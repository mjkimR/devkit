---
sources:
  CAP-DLV-test-management: null
  UC-assess-test-management: null
title: 선택한 테스트 스위트 평가하기
translated_from: en/journeys/assess-test-management.md@37e80d8c601014fe
---

# 선택한 테스트 스위트 평가하기

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

`maintenance/test-management` 플레이북을 명시적으로 실행해 선택한 테스트 스위트(test suite)의 구성을 평가합니다. 먼저 `maintenance:testing` 또는 `maintenance:all`을 선택하고 동기화합니다.

1. 테스트 경로와 평가할 질문을 정합니다. 에이전트는 코드·픽스처·스크립트·CI를 읽고 저장소에서 알 수 없는 선호만 묻습니다.
2. 필수 명령, 수집 전제 조건, 자원 격리와 측정 비용을 확인합니다. 자원 안전성이 불명확하면 해당 명령을 실행하지 않습니다.
3. 커버리지·지연·실패 발견 시점의 절충을 비교합니다. 독립 실행은 실제로 따로 실행 가능한 그룹이 있어야 하며 디렉터리 이름만으로 판단하지 않습니다.
4. 구체적인 권고와 변경 후보를 한 번에 검토하고 결정합니다. 현 구성을 유지하는 권고도 가능합니다.
5. 결정된 변경은 저장소 워크플로로 진행하고 남은 검사와 결과 수집 작업을 보고합니다.

실행 요청은 평가 권한만 부여하며, 설정 편집 권한은 포함하지 않습니다. 실행 시작, 이전 커밋의 실행 결과, 정리 성공은 필수 테스트 통과 증거가 아닙니다. 대기 중인 증거에는 정확한 리비전·명령·다음 수집 작업을 남깁니다.

## 출처

- [UC-assess-test-management](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-assess-test-management.md) (영어 원문)
- [CAP-DLV-test-management](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-test-management.md) (영어 원문)
