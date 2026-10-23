# hass-vson
Vson BLE 센서 Home Assistant 통합

[English](README.md) | **한국어**

## 💬 피드백 및 지원

🐞 버그는 [Issue](https://github.com/eigger/hass-vson/issues)로 알려주세요.
💡 질문과 제안은 [Discussion](https://github.com/eigger/hass-vson/discussions)을 이용하세요.

## 지원 모델
- WP6003

## 설치
1. HACS에 이 저장소를 추가하여 설치하거나 이 저장소의 통합 파일을 `custom_components/vson` 디렉터리로 복사하세요.
2. Home Assistant를 재시작하세요.

## Bluetooth 및 진단

원격 연결은 [Bluetooth proxy 설정 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md)를 따르세요. 전원, 다른 앱의 연결 점유, 시간 제한, 실패 단계와 로그는 [WP6003 문제 해결](docs/troubleshooting.ko.md)을 확인하세요.

기본 측정 주기는 300초이며 통합 옵션에서 30~86400초로 설정할 수 있습니다. 매 폴링 후 연결을 닫습니다. 연결, 폴링 시간, 통신 문제, 마지막 오류, 오류 횟수, 마지막 실패 진단 센서를 제공합니다. 실패 정보에는 단계, 추정 원인과 가능한 연결 경로 정보가 포함됩니다. 이후 폴링에 성공해도 실패 이력은 유지되며 항목을 다시 로드하거나 재시작하면 초기화됩니다. 기존 연결·폴링 시간 엔티티 ID는 유지합니다.

전송·알림 처리·보고는 공용 blesession을 사용합니다. Home Assistant 2025.1.0 이상이 필요합니다. 자동 테스트는 실제 HA와 모의 BLE 전송을 사용하며 실제 WP6003·로컬 어댑터·proxy 검증은 별도로 필요합니다.

## 참고 자료
- [WP6003-air-box (saso5)](https://github.com/saso5/saso5.github.io/tree/master/WP6003-air-box)
- [xiaomi_ble](https://github.com/home-assistant/core/tree/dev/homeassistant/components/xiaomi_ble)
- [xiaomi-ble](https://github.com/Bluetooth-Devices/xiaomi-ble.git)
