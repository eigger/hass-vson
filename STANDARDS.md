# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/v1.1.1
- 참조 커밋 SHA: 9876b521d401071345a13bd508f43d220852c77b
- Standards release: v1.1.1
- Resolved standards SHA: 9876b521d401071345a13bd508f43d220852c77b

This is a targeted application for blesession, diagnostic entities, shared HA test infrastructure, reusable test/validation workflows, and bilingual Bluetooth guidance. It is not a claim of full repository standards adoption. Existing HA minimum `2025.1.0`, sensor unique IDs are preserved; the release version is 1.4.0. No exceptions have been approved or invented.

The implementation reuses blesession `0.9.0` for connection ownership, notifications, bounded writes/disconnects, attempt serialization, trace vocabulary, radio facts and retained session reports. WP6003 commands, packet parsing, timing policy and HA entities remain integration responsibilities. No new cross-repository library abstraction or edits to other integrations are needed for this change.

Both reusable workflows are pinned to the reviewed standards SHA. The root HA test fixture and domain fixture guidance come from the central templates. Existing parser, sensor, import and config/options regressions were retained or converted to actual HA tests under `tests/components/vson/`; the fake `homeassistant.*` modules were removed.

See [verification evidence](ADOPTION_CHECKLIST.md). Full metadata/category review, managed README/badge adoption, automated dependency maintenance, central adoption-status updates, remote CI and physical hardware validation are not claimed by this scoped change. The central status table was not modified because this task's changes are confined to hass-vson.

## Earlier ZIP packaging adoption

The previously adopted release workflow and its reviewed SHA remain unchanged. Historical record follows.

# Scoped standards adoption
- Previously reviewed standards SHA: `fd4162c0b93fbe8e109f99c787773ae09ba157e1`
- Standard: https://github.com/eigger/hass-repo-standards/tree/fd4162c0b93fbe8e109f99c787773ae09ba157e1

Only HACS ZIP release packaging and README badges are adopted in this change. Existing code, support minimum, dependencies, documentation body and CI are preserved. Full standards adoption and real HA verification remain outside this change.


## 2026-10-23 ZIP release and Downloads update

Base commit: `a095f96d18863c76e02f7b5c195fff66ce6987f9`. HACS remains Custom. `hacs.json` now selects `vson.zip`; publishing the next release builds and attaches that integration ZIP through the pinned central action. Analytics Usage is replaced by Downloads. The archive contains tracked integration files at its root. No existing release/tag/assets are modified.

Implementation and review: root; generated release caller reuses the independently reviewed central ZIP contract. Support minimum, manifest, code, dependencies, README body and prior adoption exceptions are preserved. Verification evidence is recorded in ADOPTION_CHECKLIST.md; this scoped update does not establish full standards compliance.

## 2026-10-25 중앙 검사기 갱신

- 검토한 중앙 main: `1863343638014adb8a4001afc8fddc1a27dc500f` (git ls-remote 확인). 이전 기본 기준 `4fa557eaa7142b87a6cae8b09c249cf50c3865c6`의 채택 이력은 위 기록을 보존합니다.
- 모든 중앙 workflow/action pin과 reusable workflow의 standards-ref를 같은 검토 SHA로 맞춥니다. HACS-04는 actions/*의 full SHA 고정을 유지하면서 SHA 값 차이를 허용합니다.
- Validate에 중앙 템플릿의 무조건 실행 standards job을 추가합니다. 기존 HACS/Hassfest와 HA test job 이름·입력은 보존하며, 기본 브랜치를 사용하는 중앙 실행 조건을 적용합니다.
- 통합 코드·런타임 의존성·지원 최소·배포 버전은 이번 변경 대상이 아닙니다. 기존 채택 범위를 전체 완료로 바꾸지 않으며 실제 검증 결과와 남은 항목은 ADOPTION_CHECKLIST.md의 같은 날짜 기록을 참조합니다.


### 2026-10-25 Standards 파일·표시 이름 분리

- 기존 Validate의 중앙 검사 job을 `standards.yml`로 옮기고 workflow/job 표시 이름을 `Standards`로 줄였습니다. Validate의 HACS/Hassfest, 검사 항목·통과 기준·실행 단계·조건·권한은 유지합니다.
- 위치 인식과 중앙 명명 안내를 맞춘 검토 소스: `ca740d88b32fa5dcbc94c41fce2908450c76ed50` ([중앙 PR #24](https://github.com/eigger/hass-repo-standards/pull/24), 현재 이 PR의 의존 변경). 이전 기준 `1863343638014adb8a4001afc8fddc1a27dc500f`의 검증 이력은 앞 기록으로 보존합니다. 모든 중앙 pin·standards-ref는 같은 새 검토 소스로 맞춥니다.

## 2026-10-25 중앙 immutable release 참조 전환

- 사용자 요청에 따라 현재 중앙 참조를 immutable `v1.0.0` / resolved SHA `44349ee5621eea5d80e5c427f7a2435d2c2491bb`로 전환했습니다. 중앙 workflow/action caller는 exact release tag를, `standards-ref`는 resolved full SHA를 사용합니다.
- 범위는 중앙 참조·기록 정합화뿐입니다. 기존 지원 최소, 통합 버전, manifest, 런타임 요구사항, 구현, 테스트와 CI의 caller-owned 설정은 보존했습니다.
- 과거 SHA·검증·예외 기록은 역사적 증거로 보존합니다. 이번 변경은 generated reference-only 범위이므로 GOV-05 자체 검토이며 PR CI/병합은 대기 상태입니다.
