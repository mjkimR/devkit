---
sources:
  CAP-DIST-content-packages: null
  CAP-DIST-in-repo-bundles: null
  CAP-DIST-sync-and-transactions: null
  CAP-DIST-workspace-ownership: null
  UC-snapshot-bundle-sources: null
title: 번들 소스를 로컬로 도입하고 갱신하기
translated_from: en/journeys/snapshot-bundle-sources.md@ecca4d7d9a74c1ff
---

# 번들 소스를 로컬로 도입하고 갱신하기

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

번들 소스 스냅샷(Bundle source snapshot)은 지원되는 콘텐츠 제공자 전체를 별도 로컬 패키지로 보존합니다. 원래 번들 버전·자원 바이트·실행 모드·라이선스를 경로 없는 출처 정보와 함께 유지합니다. 런타임·명령 제공자나 지원하지 않는 동적 의존 범위는 쓰기 전에 거부합니다.

```sh
uv run devkit bundle snapshot SOURCE --to tools/local-content --package local-content
uv run devkit bundle refresh tools/local-content --source SOURCE
uv run devkit bundle refresh tools/local-content --source SOURCE --expect CURRENT --candidate REVIEWED
```

첫 번째 refresh 명령은 쓰기 없이 변경을 미리 보여 줍니다. 현재·후보 다이제스트와 후속 작업을 검토한 뒤 두 ID를 모두 전달해 교체합니다. 직접 편집이나 오래된 검토 ID가 있으면 `BUNDLE_SNAPSHOT_CONFLICT`로 거부하고 편집을 보존합니다.

실제 소유 의존 그룹에서 원본 제공자 전체를 교체하고 별도 editable 래퍼를 설치한 뒤 일반 sync를 실행합니다. 직접 원본 의존이 없으면 직접 제거를 건너뛰고 전이 의존을 따로 해결합니다. 패키지 메타데이터가 바뀌면 재설치하고 제거된 선택 번들은 명시적으로 해제합니다. 스냅샷 생성·갱신 명령은 이 작업을 안내하며 대신 실행하지 않습니다.

소스·출처 정보·의도한 부트스트랩 변경을 커밋합니다. 소비자 수정은 프로젝트 오버라이드(Project override)에 둡니다. 런타임·빌드 전제 조건을 갖춘 새 클론은 비공개 원본 접근 없이 선택 소스를 재현할 수 있습니다.

## 출처

- [UC-snapshot-bundle-sources](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/distribution/UC-snapshot-bundle-sources.md) (영어 원문)
- [CAP-DIST-in-repo-bundles](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md) (영어 원문)
- [CAP-DIST-content-packages](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)
- [CAP-DIST-workspace-ownership](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md) (영어 원문)
- [CAP-DIST-sync-and-transactions](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)
