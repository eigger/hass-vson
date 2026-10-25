<!-- hass-standards:header:start -->
# hass-vson

A Home Assistant custom integration for Vson WP6003 Bluetooth air quality sensors.

**English** | [한국어](README.ko.md)

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-vson?style=flat)](https://github.com/eigger/hass-vson/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#installation)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.1.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-vson/tests.yml?branch=master&style=flat&label=Tests)](https://github.com/eigger/hass-vson/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-vson/validate.yml?branch=master&style=flat&label=Validate)](https://github.com/eigger/hass-vson/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-vson?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-vson/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-vson/releases)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

Vson BLE Sensor Home Assistant Integration


## Supported Models
- WP6003

## Installation

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-vson&category=integration)
<!-- hass-standards:installation:end -->
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

<!-- hass-standards:support:start -->
## Support

- [Issues](https://github.com/eigger/hass-vson/issues): Report bugs or request features.
- [Discussions](https://github.com/eigger/hass-vson/discussions): Ask questions and share your experience.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## License

Released under the [MIT License](LICENSE).
<!-- hass-standards:license:end -->
