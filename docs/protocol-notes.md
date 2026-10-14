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


## 2026-10-12 — restored dual connection and verified media controls

Observed: after the missing-key failure, a standard, owner-authorized Bluetooth pairing repair succeeded. LE discovery exposed three services: 1800 (2A00 read/write), 1801 (2A05 indicate, 2902 descriptor), and AE00 (AE01 write-without-response; AE02 notify with 2902 descriptor). Complete UUIDs use the Bluetooth base `0000XXXX-0000-1000-8000-00805f9b34fb`. This verifies the historical AE00/AE01/AE02 inventory on the current Linux adapter. No AE01 application writes were sent.

Connecting the remote Audio Sink (110B), trusting this watch on the host and connecting AVRCP (110E) restored the Classic media transport alongside the GATT services. BlueZ exposed MediaControl1 connected and an A2DP transport; PipeWire selected a2dp-sink. HFP profiles advertise a microphone source, but microphone recording remains untested. Owner reported that media, camera and other watch apps became accessible after the second connection, and that watch controls started computer music playback. Camera shutter behavior is not yet verified.

A corrected read-only AE02 subscription captured one 18-byte notification at 22:54:02.858143 UTC, beginning FE DC BA and ending EF. Meaning and relationship to button presses remain unknown. Raw payload stays private in ignored captures. The first subscription attempt had an invalid D-Bus match rule and is not evidence of absent notifications. The corrected listener stopped notifications successfully without disconnecting the watch.

A watch-only, nonexclusive `evtest` capture on the then-current `/dev/input/event14` (Apple Watch AVRCP) observed EV_KEY code 200 KEY_PLAYCD and code 201 KEY_PAUSECD, each with values 1 (press) and 0 (release). This is direct evidence for Linux media controls; node numbering is transient. Capture used sudo through its interactive prompt; no credentials are stored in this repository. Agent command mapping and status delivery remain future work.

Official app research: [WearLink](https://play.google.com/store/apps/details?id=com.jieli.healthaide), package com.jieli.healthaide, is Jieli's Android health app; [YiDong Health](https://apps.apple.com/us/app/%E5%AE%9C%E5%8A%A8%E5%81%A5%E5%BA%B7/id1597841052) is its iPhone app. The [official Android health SDK](https://github.com/Jieli-Tech/Android-JL_Health) supplies mobile examples. These are protocol-family candidates, not verified compatible apps for this watch. No native Linux version was identified or installed. Historical GFit/GFit Pro recollection remains owner-reported. The working Linux media connection requires no health app.


## 2026-10-12 — GFit Pro and firmware/display research

Owner prioritizes native OS/firmware access and custom computer information on the watch over button mapping. Firmware screenshots show 1.0.0.4 / PID 76 / version 1004 / type 0. Android GFit Pro 1.4.5 offline inspection found Jieli RCSP, authentication and OTA components. Official SDK provides notification and watch-resource operations; specimen support is untested. Vendor firmware metadata query returned code 422, Token error or expired. Exact image remains unavailable in this research pass. No watch protocol writes or firmware operations were performed. Detailed provenance and findings: [GFit firmware research](gfit-firmware-research.md).

## 2026-10-12 — owner-session firmware metadata and host-only retrieval

Owner-configured iPhone HTTPS capture observed GFit Pro `ota/pidVersion` returning code `1024` (no latest device firmware), and `ota/userUpgradeOta` returning code `200` with encrypted restoration metadata. Client-side decoding yielded PID76/version1004/type0 and `update1004.ufw`. These server API routes are not evidence of a BLE command encoding.

A host-side `ota/piddownload` request with the documented encrypted `fwareUrl` body and live app session headers held in memory downloaded 18,760,384 bytes. Vendor MD5 matched exactly. An earlier 73-byte token-error response was rejected as a firmware artifact. No watch GATT write, OTA transfer or restoration was initiated by the investigator. See [full artifact and container evidence](gfit-firmware-research.md#2026-10-12-owner-session-capture-and-matching-firmware-acquired).

Raw captures, crypto material, certificate files and binaries remain ignored/private. Vendor TLS inspection and certificate-download listeners were stopped; temporary firewall allowances were removed and their absence verified. Owner reports phone proxy off and certificate trust disabled, with the profile retained for potential future analysis.

## 2026-10-13 — offline RCSP message-path evidence

Inspected GFit Pro 1.4.5 Android bytecode: `WatchBase.pushMessageInfo` requires RCSP initialization, and `SyncMessageTask` has command-push and small-file paths. `PushInfoDataToDeviceCmd` uses command ID161 (`0xA1`); message subtype type2/version0 serializes a message sequence and typed timestamp/package/flag/title/content records. Constructor limits are 31/36/424 encoded bytes for package/title/content. Timestamp is calendar-packed, not Unix time. These are app-code observations, not tested specimen packet meanings.

Corrected application mapping (`0x06000120`) exposes a native command161 comparison at `0x060262E0` and `smartbox_data_function_set` dispatcher at `0x060269EA`, with a two-byte envelope and indexed subtype callbacks. Mapping of the type2 rendering callback is pending. Transport framing, authentication and specimen capability selection must be established before using this as a live status sender. No raw byte recipe or unexplained GATT write was sent. Details: [build analysis](build-analysis.md#text-reception-and-the-linux-status-route).


## 2026-10-13 — Automated commands and delivered status text

Provenance: local BlueZ/D-Bus reads, private RCSP captures and offline GFit Pro 1.4.5 SDK bytecode; owner observation of the watch screen. Raw authentication traffic and device auth-key attributes remain in ignored captures, never public documentation.

- **Observed:** Explicit LE-bearer connection restored the AE00/AE01/AE02 data path alongside the media connection. A temporary runtime BlueZ `--experimental` override was removed and the service restarted with its original command. Standard Device Name reads still succeeded after restoration. No bond was removed.
- **Observed:** SDK-compatible challenge/response authentication succeeded. Informational GetTargetInfo replies confirmed PID 76 and firmware 1.0.0.4. Product UID is 18256 (`0x4750`); do not conflate this decoded integer with the owner's QR field `vid:4750`. The four-byte ProductInfo form supplies no explicit manufacturer VID.
- **Observed:** Reported protocol send/receive MTUs are 272/540. SDK-decoded update capability fields advertise double backup=false, need bootloader=true, single-backup OTA way=1. The meaning of way=1 and actual flash/recovery layout remain unverified. Two images inside the update package do not establish rollback support. Small-file transfer support is advertised.
- **Observed transport / owner-reported display:** A source-derived legacy A1 text command was sent with heading `Mero status` and generic computer uptime/load information. Fresh requests received status=0 with response parameters `[2,1]`; the application-level meaning of these parameters is unresolved. On resend, the owner reported vibration and found `Mero status` / online text in the watch's messages, but saw no popup. This demonstrates a usable custom text delivery path; popup policy remains unresolved. Existing Instagram entries may be historical phone messages; their origin was not captured.
- **Observed host test:** `scripts/watch_commands.py` maps verified KEY_PLAYCD (200) press to host status and KEY_PAUSECD (201) press to read-only watch identification. Synthetic replay exercised both actions without watch interaction, including an actual remote Device Name read. Four unit tests cover repeat/release filtering, malformed records and command restrictions. Synthetic tests do not establish a new physical button-to-action end-to-end result. Status is a host snapshot, not yet a Mero agent API integration.
- No firmware/DFU command or update transfer occurred. The authentication reset used was the SDK's volatile session reset, not a factory reset. Notification payloads were source-derived rather than guessed GATT writes.

Next: inspect SDK and native notification display policy before changing flags; build agent-status delivery on the proven text path. Complete offline update-validator, memory-layout and recovery analysis before proposing any modified firmware installation.


## 2026-10-13 — Real Codex status bridge

Implemented scripts/codex_watch.py and scripts/watch_notifications.py. A read-only local Codex rollout source sent `Mero Codex` / `Codex | Agent run | working` for another session with recent events. Observed RCSP transport status 0 and application parameters [2,1]; visual confirmation of this specific message remains pending. A bounded 60-second follow test completed with no further state transition. No terminal control or firmware transfer occurred. Authentication helper/material remain private; public code logs no raw packets or metadata replies. Eight unit tests passed. Herdr was explicitly considered but not accessed because HERDR_ENV was unset. See docs/agent-bridge.md for setup, provenance and limitations.


## 2026-10-13 — Dual-link repair and custom-screen preflight

Owner confirms the Mero Codex message in Messages, without a popup; vibration on that delivery was uncertain. Current inspection found Device1 Connected=true but MediaControl1 Connected=false and no watch input device. Standard Connect alone did not restore media. Explicit advertised HID/A2DP-sink/AVRCP profile connections restored MediaControl and the AVRCP input device. Owner then confirmed the Bluetooth icon lit, but the subsequent Mero link test still produced only a stored message, without popup or vibration. Both-bearer availability alone therefore does not explain that test's behavior.

A source-verified informational GetExternalFlashMsg query returned SDK-decoded screen dimensions 240x296, reported external flash and FAT size 16 MiB each, match version W002 and external-flash receive MTU 256. These are device reports, not physical measurements. Offline custom-face and native UI routes, source provenance, unknowns and the 240x296 screen concept are recorded in docs/custom-screen-research.md. No face/resource transfer, activation, firmware command or flash operation occurred.


## 2026-10-13 — Custom background codec and real resource candidate

BGP_B131/BGP_C131 now positively identified and decoded as single-image RU30 resources. Both stock images decode completely to 240x296. Pixel-preserving re-encoding verified; compression bytes differ. Inspected GFit ARM64 converter exports br28_png_to_res; bounded offline emulation reproduces its wrapped resource output. Public narrow Python codec, independently emulated converter oracle and 13 passing tests added. Native-generated own-artwork candidate assets/mero-screen-test.res is 27,993 bytes, SHA256 e5159492a76ffeea541c3c583860b3b1c920e0d6ad9e9ec62861b03c718e89e6. Native/Python comparison matches three small fixtures exactly; full candidate compression grouping differs but pixels agree. Candidate uses native output. See docs/ru30-background-format.md.

Owner rechecked GFit Pro and successfully selected/uploaded an owner photo, correcting the earlier tentative vendor-only recollection. Our PNG was served through a LAN-only directory containing generated artwork, with a ten-minute server/firewall expiry. Phone HTTP retrieval was observed; display confirmation pending. No resource, activation, OTA or firmware command was sent by the computer. The background is a static appearance test; live status and touch/menu replacement remain separate native-UI work.
