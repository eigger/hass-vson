<!-- hass-standards:header:start -->
# Vson BLE for Home Assistant

Vson WP6003 Bluetooth 공기질 센서를 위한 Home Assistant 커스텀 통합입니다.

[English](README.md) | **한국어**

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-vson?style=flat)](https://github.com/eigger/hass-vson/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#설치)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.1.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-vson/tests.yml?branch=master&style=flat&label=Tests)](https://github.com/eigger/hass-vson/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-vson/validate.yml?branch=master&style=flat&label=Validate)](https://github.com/eigger/hass-vson/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-vson?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-vson/latest/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-vson/releases)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

<a name="지원-모델"></a>

## 지원 기기
- WP6003

## 요구사항

- **Home Assistant:** 2025.1.0 이상.
- **Bluetooth:** 연결 가능한 Bluetooth 어댑터 또는 프록시.
- **기기:** Vson WP6003.

## 설치

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-vson&category=integration)
<!-- hass-standards:installation:end -->

1. 위 배지를 클릭해 마켓플레이스에서 저장소를 엽니다.
2. 저장소를 직접 추가하려면 **설정 → 마켓플레이스 → 링크에서 추가**에서 <https://github.com/eigger/hass-vson>을 입력합니다. 안내가 표시되면 GitHub 계정을 연결합니다.
3. **설치**를 선택합니다. 재시작 안내가 표시되면 Home Assistant를 재시작합니다. 설치가 끝나면 [설정](#설정)으로 이동합니다.

## 설정

**설정 → 기기 및 서비스**에서 발견된 센서를 설정하거나 **통합 추가 → Vson**을 선택해 센서를 고릅니다.

## Bluetooth 및 진단

원격 연결은 [Bluetooth proxy 설정 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md)를 따르세요. 전원, 다른 앱의 연결 점유, 시간 제한, 실패 단계와 로그는 [WP6003 문제 해결](docs/troubleshooting.ko.md)을 확인하세요.

기본 측정 주기는 300초이며 통합 옵션에서 30~86400초로 설정할 수 있습니다. 매 폴링 후 연결을 닫습니다. 연결, 폴링 시간, 통신 문제, 마지막 오류, 오류 횟수, 마지막 실패 진단 센서를 제공합니다. 실패 정보에는 단계, 추정 원인과 가능한 연결 경로 정보가 포함됩니다. 이후 폴링에 성공해도 실패 이력은 유지되며 항목을 다시 로드하거나 재시작하면 초기화됩니다. 기존 연결·폴링 시간 엔티티 ID는 유지합니다.

전송·알림 처리·보고는 공용 blesession을 사용합니다. 자동 테스트는 실제 HA와 모의 BLE 전송을 사용하며 실제 WP6003·로컬 어댑터·proxy 검증은 별도로 필요합니다.

## 참고 자료

- [WP6003-air-box (saso5)](https://github.com/saso5/saso5.github.io/tree/master/WP6003-air-box)
- [xiaomi_ble](https://github.com/home-assistant/core/tree/dev/homeassistant/components/xiaomi_ble)
- [xiaomi-ble](https://github.com/Bluetooth-Devices/xiaomi-ble.git)

<!-- hass-standards:support:start -->
## 지원

- [Issues](https://github.com/eigger/hass-vson/issues): 버그를 신고하거나 기능을 요청하세요.
- [Discussions](https://github.com/eigger/hass-vson/discussions): 질문하고 사용 경험을 공유하세요.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## 라이선스

[MIT License](LICENSE) 라이선스로 배포됩니다.
<!-- hass-standards:license:end -->
