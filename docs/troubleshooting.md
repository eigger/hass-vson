# WP6003 troubleshooting

[README](../README.md) | [한국어](troubleshooting.ko.md)

## Common troubleshooting

Start with the [common Bluetooth troubleshooting guide](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md) and [Bluetooth proxy setup guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md).

## Device-specific checks

- Supported model: Vson WP6003, advertising as `6003#*` with service `fff0`. No firmware version has been verified in this change.
- Keep the monitor powered and within range of a connectable local adapter or active Bluetooth proxy. No special wake-up sequence is implemented or verified.
- This integration does not configure pairing, bonding or authentication. Close other phone applications or integrations that might hold the monitor's connection.
- Discovery uses passive advertisements. Measurements require a separate active GATT connection: subscribe to `fff4`, write `0xAB` to `fff1`, and receive an 18-byte response. Discovery alone does not prove this exchange works.
- The default polling interval is 300 seconds (configurable from 30 to 86400). Each poll uses one library attempt bounded at 60 seconds, including connection; the connector retains its own connection retry behavior. The response and write each have a 5-second bound. Notification settling (0.5 seconds) and command pacing (0.05 seconds) preserve existing device timing.
- Connections close after each poll, so the Connection entity normally reads disconnected between polls. Local adapters and proxies use HA's Bluetooth routing; neither route has been tested on physical WP6003 hardware for this change.

## Symptoms and actions

| Symptom | Failing stage | Checks | Action |
| --- | --- | --- | --- |
| Monitor not discovered | Discovery / `unreachable` | Power, `6003#*` advertisement, service `fff0`, connectable receiver | Verify Bluetooth setup and move the powered device closer. |
| Advertisements visible but no connection | `connect` | Free proxy slots and other applications holding the device | Release other connections and retry at the next poll. |
| Wrong service or notification subscription fails | `session` / `subscribe` | WP6003 model, GATT service and characteristic properties | Confirm the model; collect a short debug log if it persists. |
| Connection drops or write does not return | `transfer` / `readout` | Proxy availability, reported route, signal, interference | Restore the transport and wait for the next poll. A hung operation is bounded. |
| No response or invalid packet | `transfer` / `readout` | Powered monitor; response must have 18 bytes | Close other applications; report the model/firmware and failure details. |
| Poll succeeds but closing fails | `disconnect_error` attribute | Proxy or adapter health | Inspect the communication problem attributes; the valid measurement is retained. |

## Diagnostics and logs

The device exposes Connection, Poll duration, Communication problem, Last error, Error count and Last failure. Connection means an active GATT session, not advertisement reception. Poll duration includes discovery and cleanup and updates while polling.

Communication problem is unknown until the first completed poll, turns on for a failed poll or cleanup warning, and clears after a clean successful poll. Measurement entities become unavailable after poll failure and recover on success. Last error and Last failure retain the last failed poll after recovery; Error count counts failed polls since entry setup and resets on reload/restart. A cancelled poll is not recorded as a failure. Cleanup warnings appear on Communication problem but do not increment failed-poll counts when measurements succeeded.

Attributes use blesession's shared fields where available: `failed_stage`, `failed_detail`, `likely_cause`, `likely_cause_key`, `error`, stage timings, `via`, `via_type`, `rssi`, and `paths`. When `via_unconfirmed` is true, `via` is the best advertisement receiver, an estimated route rather than a confirmed connection path. Missing route facts are unknown, not evidence of a local connection.

Temporarily enable debug logging for `custom_components.vson` and `blesession` in Home Assistant, reproduce once, then disable debug logging. Collect only that interval. Remove device addresses, scanner names, credentials, tokens and personal data before publishing attributes or logs.

## If the problem persists

Use the existing [Issues](https://github.com/eigger/hass-vson/issues) destination. Include Home Assistant, integration, blesession and ESPHome versions where applicable, monitor/proxy model and revision, firmware, local/proxy connection method, failure time and stage, and reproduction steps. Describe successful and failed attempts separately. Hardware behavior remains unverified by the automated tests.
