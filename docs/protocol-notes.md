# BLE/GATT protocol notebook

**Status:** partial identification; raw observation only. Last updated 2026-10-12.

## Observed GATT surface (LightBlue, 2025-12-09)

```text
Service AE00
├── Characteristic AE01  [write-without-response]
└── Characteristic AE02  [notify]
```

LightBlue displayed *short* UUID labels. Re-discover and record their **full 128-bit UUIDs** via BlueZ/Bleak; do not assume a particular base UUID before doing so.

### Known notification example

```text
FEDCBA80FF0000A65FF61000000000641137EF
```

Earlier AE02 notifications reportedly began `FEDCBA80`. Treat the complete sample as **uninterpreted binary**, with no invented header, length, checksum, timestamp, operation or payload field.

Useful initial analyses: count lengths, compare prefixes/suffixes across repeated idle traces, diff paired/unpaired and static/moving states, test for repeated framing and entropy; use captured samples, not conjectural command injection.

## Experiment registry

| ID | Task | Risk | State |
| --- | --- | --- | --- |
| BLE-001 | Scan and record advertisement + current BLE address/type | Read-only | 2026-10-12: name/address rediscovered; BlueZ reports public address type; raw advertising/HCI capture still pending |
| BLE-002 | Enumerate complete service/characteristic UUIDs and properties | Read-only | 2026-10-12: normal-mode inventory has zero GATT services; device/profile UUIDs recorded; historical AE00 still unverified |
| BLE-003 | Subscribe to AE02; repeat historical notification capture | Read-only | Pending: no AE02 characteristic found in current mode |
| BLE-004 | Record GFit Pro traffic through permitted local host/app diagnostics | Observation | Pending |
| BLE-005 | Correlate *explicit watch actions* with notified data | Read-only | Pending |
| BLE-006 | Document and test decoded benign commands only after evidence and rollback plan | Write risk | Blocked until protocol validation |

## Suggested structured log

For each capture include:

```text
date_utc: YYYY-MM-DDTHH:MM:SSZ
host: mero-machine or other device
os_kernel:
adapter_vendor_product:
bleak_version:
watch_firmware_screen:
watch_bluetooth_name:
watch_address_type:
watch_address: <redacted in public logs>
connection_state: app_connected | app_disconnected
gatt_full_uuid:
event: advertise | notify | read | timeout | disconnect
bytes_hex: <scrub private content before commit>
context: idle | raise_wrist | press_button | app_action | etc.
observation:
interpretation: untested hypothesis only
```

Keep private captures locally under `captures/` (ignored by Git). Commit only manually sanitized fixtures with clear provenance and expected checksum/packet lengths.

## Protocol investigation principles

1. **Reproduce** old AE00/AE01/AE02 findings with current gear.
2. Identify whether permissions demand authentication, bonding or an app handshake.
3. Establish framing empirically using many captures and controls.
4. Distinguish BLE GATT from Bluetooth Classic call/audio profiles.
5. Only after decoding and confirming benign traffic, design a minimal bridge; avoid writes related to DFU, factory reset or security settings.
6. If GFit Pro uses OTA, inspect downloaded firmware metadata **offline** before any firmware transfer.

No confirmed firmware update URLs, vendor documentation or exploit methods are currently part of the evidence.

## 2026-10-12 — BLE-001 live host diagnosis (21:32–21:37 UTC)

**Provenance:** local commands run by the agent; phone/proximity/mode changes reported by the owner. Raw diagnostic output remains in Git-ignored `captures/`.

### Observed

- Host: kernel `7.1.8-arch1-3`, BlueZ `5.87`. USB inventory confirms TP-Link `2357:0604`; kernel logs associate it with `hci0` and load `rtl8761bu` adapter firmware. This identifies the host adapter, not the watch chipset.
- Bluetooth service is running; controller powered; rfkill reports neither soft nor hard block. No controller removal/reset errors appeared in the inspected current-boot kernel records or during these attempts.
- Bleak was absent from the default Python environment. Created ignored `.venv/` and installed the existing requirements: Bleak `3.0.2`, dbus-fast `5.2.0`.
- `rtk proxy bluetoothctl --timeout 15 scan le` detected the historical watch address at RSSI −80 dBm. A subsequent `rtk proxy .venv/bin/python -u scripts/ble_probe.py scan --seconds 15` detected the same address/name at −50 dBm, without advertised service UUIDs.
- GATT-only probe at 21:32:47 UTC timed out with an empty exception message. No controller disappearance was observed.
- Retry starting at 21:33:37 UTC reported `Connected: True`, but enumerated **zero GATT services**. BlueZ listed serial-port, audio, HID and vendor UUID `fe010000-1234-5678-abcd-00805f9b34fb`; AE00/AE01/AE02 were not verified. BlueZ pairing/bonding state changed from false to true. The probe did not request pairing; the cause of this transition is unknown.
- Repeat starting at 21:34:16 UTC timed out. A subsequent read-only D-Bus inventory showed `Connected=false`, `Paired=true`, `Bonded=true`, `ServicesResolved=false`, and no GATT service/characteristic objects for the watch.
- `rtk proxy timeout 2 btmon` failed with `Failed to bind channel: Operation not permitted`; `rtk proxy sudo -n true` reported that a password is required. No HCI packet capture was obtained.

Local files: `captures/ble-001-20261012-inspect.log` (debug retry), `captures/ble-001-20261012-inspect-repeat.log` (repeat). These are private diagnostics, not public fixtures. The probe disconnects on leaving its context manager, including after successful inventory.

### Owner-reported

The phone was disconnected and the watch moved close to the adapter. The owner also changed the watch's Bluetooth mode and describes a normal Bluetooth icon that changes to a “B...” icon with dots when clicked. The meaning of these icons, selected mode and exact timing relative to attempts are unknown. A status indicator rather than a mode selector has not been ruled out. The owner reports no pairing through Linux settings.

A later scan starting at 21:35:38 UTC still saw the same watch address/name, with RSSI −80 dBm. BlueZ/Bleak also supplied the previously listed profile UUIDs; this does not establish that those UUIDs came from the current advertising packet rather than cached BlueZ properties. One further GATT-only attempt with a 15-second timeout reported `Connected: True`, then the newly added empty-service diagnostic raised `TypeError` because Bleak's collection does not implement `len()`. The diagnostic was corrected to iterate the collection and verified against a real empty `BleakGATTServiceCollection`. Current mode labels and HCI packets remain unavailable, so these attempts are not a controlled comparison between two modes. Additional private logs: `captures/ble-001-20261012-after-mode-scan.log`, `captures/ble-001-20261012-after-mode-inspect.log`.

### Interpretation and next test

The historical `hci0 removed` failure was not reproduced. Better reception and a watch mode change both occurred, so neither is established as the cause of the successful retry. One connection succeeded, but repeatable BLE GATT access remains unverified. The profile list is consistent with a Classic Bluetooth interface being available; it does not establish the meaning of the watch's modes or prove which transport the successful attempt used.

Next: record the exact Bluetooth mode labels/icons and selected setting; compare discovery and GATT inventory under owner-selected modes while holding proximity and phone disconnection constant. Obtain an authorized HCI monitor trace if timeouts persist. Do not guess AE01 commands, remove bonds, or reset the watch.

Final verification starting at 21:37:13 UTC timed out with the corrected diagnostic: `BLE operation failed (TimeoutError): no additional error detail`. Local log: `captures/ble-001-20261012-final-inspect.log`. Syntax, empty-service handling using Bleak's real collection, the empty timeout message path and `git diff --check` passed. Intermittent connection remains unresolved; the successful connection should not be described as stable recovery.

## 2026-10-12 — Normal-mode connection without companion app (from 21:42 UTC)

**Owner-reported:** the phone can make two connections without GFit Pro; the watch is now in its normal Bluetooth mode, and the owner will disconnect the phone for a computer retry. This does not identify the watch's mode icons or the phone's two connection transports.

**Observed:** scan starting at 21:42:45 UTC again discovered the historical watch address/name (RSSI −70 dBm). A bounded one-shot `bluetoothctl connect` briefly showed a connection, then disconnected without observed USB/HCI reset. An interactive `rtk proxy bluetoothctl` session, followed by `default-agent` and `connect` to the freshly discovered address, subsequently established a connection with media endpoints and transport present.

At 21:44:14 UTC, a read-only BlueZ D-Bus inventory verified `Connected=true`, `Paired=true`, `Bonded=true`, `ServicesResolved=true`, zero GATT services/characteristics and one idle media transport (UUID `0000110a-0000-1000-8000-00805f9b34fb`, codec value `0`). `pactl -f json list cards` independently reported the watch's audio card with active profile `a2dp-sink`. No health app, application-command GATT write, bond removal or watch reset was used. Existing bonding was reused; the interactive BlueZ agent was registered as default for this session.

**Interpretation:** a normal Linux audio-profile connection is verified. BLE AE00/AE02, microphone operation and programmable watch control remain unverified. The previous Bleak inventory tool explicitly disconnects on exiting, and is not a persistent normal-mode connection tool. The preceding one-shot disconnection has no packet-level root cause yet; neither phone competition nor the default agent is proven to be the sole cause.

Raw local files: `captures/ble-001-20261012-normal-mode-scan.log` and `captures/ble-001-20261012-normal-mode-stability.log`. Normal-mode connection instructions were added to the lab playbook.

Stability verification: all seven read-only samples from 21:44:33 through 21:45:03 UTC reported `Connected=true` and `ServicesResolved=true`. After `quit` closed the interactive Bluetooth client, an independent check at 21:45:19 UTC still reported paired, bonded and connected. The connection was left active; continued long-term stability and audio playback have not been tested.

**Subsequent owner report:** the computer connection is stable. The owner clarifies that a pairing mode prompts for a health app, while normal Bluetooth mode permits app-free phone connections and shows two connections on the iPhone. These reports do not establish the two transports or the meaning of the “B...” icon. Full observed device/profile UUIDs and the evidence limits are consolidated in the [device dossier](device-dossier.md#device-findings-consolidated--2026-10-12-session).

## 2026-10-12 — Modification research and later connection state (through 22:06 UTC)

**Owner-reported:** first desired application is agent status and short commands. The watch prompt says “Health App”; the owner now cannot identify the exact app and recalls using a generic app. Retain the historical GFit Pro recollection without treating it as a confirmed current QR destination. The watch paired and activated Siri through voice interaction on the iPhone without the health app; the trigger mechanism and Linux microphone operation remain untested.

**Owner-supplied QR content:** JSON contains `bleAddr` and `edrAddr` both equal to the already documented watch address, `connectWay=0`, `name=Apple Watch`, `pid=76`, `vid=4750`. These fields are not authenticated manufacturer/SoC identity. No URL was established from the supplied JSON.

**Observed locally:** while connected, BlueZ had `MediaControl1.Connected=true` and an `Input1` interface. `/proc/bus/input/devices` contained `Apple Watch (AVRCP)` with a keyboard/event handler. Its capability bitmap included media key types, but actual watch button events were not captured. The event node was not readable by the current user. No local RFCOMM node or relevant APK was found in the checked repo/Downloads top level.

Later, the event node disappeared and BlueZ reported disconnected. A conventional reconnect returned `org.bluez.Error.Failed br-connection-key-missing`, followed by `org.bluez.Reason.Remote, Connection terminated by remote user`. The owner reports neither changing watch mode nor reconnecting to the iPhone since the successful computer session. No matching USB/HCI reset entries appeared in the inspected later kernel records. Root cause remains unknown. This later failure does not erase the earlier measured connection and stability window.

The CLI's documented `menu le` / `connect` route returned `org.bluez.Bearer.LE1 is not available` for the watch. No GATT objects appeared. No persistent bearer preference, bonds or watch firmware were changed. The diagnostic client was closed; the last observed connection state was disconnected.

**Offline protocol lead:** the stored sample is 19 bytes and shares `FE DC BA` / `EF` boundaries with [official RCSP definitions](https://github.com/Jieli-Tech/fw-AC63_BT_SDK/blob/master/include_lib/btstack/third_party/rcsp/JL_rcsp_packet.h). Official Jieli Bluetooth docs also use AE00/AE01/AE02, and official health demo source parses scanned `edrAddr`/`name` JSON. This strengthens the Jieli/RCSP-family hypothesis without decoding the watch sample, validating a normal RCSP frame, identifying its SoC or proving OTA compatibility. No packet was transmitted.

See [modification options](modification-options.md) for ranked routes, primary sources and concrete input/voice/BLE/firmware identification experiments. Native `evtest`, `pactl`, `wpctl`, `pw-record` and `pw-play` are installed; no custom event reader is needed for the first test.
