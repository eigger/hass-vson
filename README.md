# hass-vson

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-vson?style=flat)](https://github.com/eigger/hass-vson/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#installation)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.1.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-vson/tests.yml?branch=master&style=flat&label=Tests)](https://github.com/eigger/hass-vson/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-vson/validate.yml?branch=master&style=flat&label=Validate)](https://github.com/eigger/hass-vson/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-vson?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-vson/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-vson/releases)
<!-- hass-standards:badges:end -->
Vson BLE Sensor Home Assistant Integration

**English** | [한국어](README.ko.md)

## 💬 Feedback & Support

🐞 Found a bug? Let us know via an [Issue](https://github.com/eigger/hass-vson/issues).  
💡 Have a question or suggestion? Join the [Discussion](https://github.com/eigger/hass-vson/discussions)!

## Supported Models
- WP6003

## Installation
1. Install this integration with HACS (adding repository required), or copy the contents of this
repository into the `custom_components/vson` directory.
2. Restart Home Assistant.
  
## Bluetooth and diagnostics

For remote connections, follow the [Bluetooth proxy setup guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md). See [WP6003 troubleshooting](docs/troubleshooting.md) for power, competing connections, timing, failure stages and logging.

Measurements are polled every 300 seconds by default; configure 30–86400 seconds in the integration options. Connections close after each poll. Diagnostics include Connection, Poll duration, Communication problem, Last error, Error count and Last failure. Failure details include stage, likely cause and available radio facts; history survives a successful subsequent poll and resets on entry reload/restart. The existing Connection and Poll duration entity IDs are preserved.

This integration uses shared blesession transport, notification handling and reports. It requires Home Assistant 2025.1.0 or newer. Automated tests use real HA with simulated BLE transport; physical WP6003/local adapter/proxy validation is still needed.

## References
- [WP6003-air-box (saso5)](https://github.com/saso5/saso5.github.io/tree/master/WP6003-air-box)
- [xiaomi_ble](https://github.com/home-assistant/core/tree/dev/homeassistant/components/xiaomi_ble)
- [xiaomi-ble](https://github.com/Bluetooth-Devices/xiaomi-ble.git)
