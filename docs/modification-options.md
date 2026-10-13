# Making the watch useful for Mero

**Research date:** 2026-10-12. **Owner priority:** agent status and short commands on the Linux computer.

The first practical target is a Linux bridge using the watch's existing controls and audio. Replacing the built-in watch UI or installing native apps is a separate firmware project whose feasibility is still unknown. No feature removal, firmware update or custom app installation was performed in this investigation.

## What the investigation establishes

**Observed on Linux:** a normal Bluetooth connection resolved services, created an audio transport and selected `a2dp-sink`. BlueZ exposed media-control and input interfaces. Linux created `Apple Watch (AVRCP)` with an event handler. This establishes host interfaces, not actual button delivery, playback or microphone capture. The input capability bitmap includes play/pause, next/previous and volume key types; these are host driver capabilities, not evidence that the watch can generate every listed key.

**Owner-reported:** the watch pairs without a health app and activated Siri through voice interaction on an iPhone. The prompt says “Health App,” and the exact app name is uncertain. The owner previously remembered GFit Pro. The iPhone shows two connections. Whether Siri is triggered by a button, wake phrase or another action has not been established.

**Owner-supplied QR content:** JSON fields `bleAddr` and `edrAddr` both contain the previously documented watch address, `connectWay=0`, `name=Apple Watch`, `pid=76`, `vid=4750`. These are pairing-descriptor fields, not authenticated manufacturer/chip identifiers. No download URL was established from this JSON.

**Current limitation:** later read-only research found the watch disconnected. A normal reconnect reported `br-connection-key-missing` and remote termination; the owner reports no intervening phone connection or mode change. No corresponding controller-reset entries were found. The earlier successful stability window remains valid historical evidence, but current persistent operation requires another pairing diagnosis. No bonds were removed.

The [protocol notebook](protocol-notes.md) preserves the dated tests and exact errors. The [device dossier](device-dossier.md) separates observed identifiers from hardware hypotheses.

## Ranked modification paths

| Path | Useful result | Evidence and next proof | Can remove built-in features? |
| --- | --- | --- | --- |
| 1. Host bridge through existing media controls | Watch button requests agent status or a short predefined command | AVRCP input/media interfaces observed; capture real watch events and map them first | No; reuses existing watch UI |
| 2. Voice bridge through headset functions | Speak a command to Mero and hear a short response | Siri interaction owner-reported; Linux microphone/profile and actual audio must be tested | No; reuses existing audio/assistant UI |
| 3. Host status through media metadata or audio | Show a short status in the watch's music screen, or speak it through its speaker | Audio transport observed; metadata rendering and playback are untested | No; display depends on existing UI |
| 4. Vendor-protocol Linux bridge | Agent alerts, text/status, button events where the protocol supports them | Historical AE00/AE02 plus RCSP-family clues; reconnect/inventory, authentication and benign message semantics still unknown | Usually adapts vendor features; this specimen is unverified |
| 5. Custom watch face/background | A Mero-oriented face or static visual instead of a fitness-oriented face | Vendor SDK documents resource operations; device compatibility and recovery need verification | May change a face; not proof of app execution or menu removal |
| 6. Native firmware/UI replacement | Remove fitness UI and implement a dedicated wrist client | Requires exact platform, board support, original firmware and a proven recovery path | Potentially, if platform and boot chain allow it; currently unknown |

These are research routes, not six supported capabilities. A serial-port UUID alone also does not establish a shell, app loader or documented command channel.

## Protocol and SDK lead: Jieli RCSP

Three independent similarities justify investigating this family:

1. Jieli's official [Bluetooth SDK import documentation](https://github.com/Jieli-Tech/iOS-JL_Bluetooth/blob/main/docs/html/_sources/Development/import_desc.rst.txt) uses AE00/AE01/AE02, matching the historical short UUIDs.
2. Official [RCSP packet definitions](https://github.com/Jieli-Tech/fw-AC63_BT_SDK/blob/master/include_lib/btstack/third_party/rcsp/JL_rcsp_packet.h) use start markers `FE DC BA` and end marker `EF`. The stored watch sample has those boundaries and is 19 bytes long.
3. The official health demo's [QR scanner source](https://github.com/Jieli-Tech/iOS-JL_Health/blob/main/code/JL_Health/JieliJianKang/%E8%AE%BE%E5%A4%87%E7%95%8C%E9%9D%A2/%E6%89%AB%E4%B8%80%E6%89%AB/QRScanVC.m) reads `edrAddr` and `name` from scanned JSON, resembling the owner's descriptor. Not all descriptor fields were validated in that source.

**Hypothesis:** the watch uses a Jieli/RCSP-related protocol. **Not established:** exact SoC, SDK version, packet fields, command IDs, checksum, authentication, or OTA compatibility. Marker/UUID resemblance alone does not validate a normal RCSP frame or authorize replay. No protocol bytes were sent.

The official [Jieli health SDK](https://github.com/Jieli-Tech/iOS-JL_Health) is a concrete source for offline study of device management and resource operations. Its [integration documentation](https://doc.zh-jieli.com/Apps/iOS/health/zh-cn/master/Development/Content/import.html) covers several watch firmware families, so the SDK's existence does not identify this watch. The official [watch development documentation](https://doc.zh-jieli.com/KDocs/master/%E6%89%8B%E8%A1%A8%E7%A9%BF%E6%88%B4%E6%8A%80%E6%9C%AF%E5%BA%94%E7%94%A8%E6%96%87%E6%A1%A3%E5%85%A5%E5%8F%A3%E6%B1%87%E6%80%BB/) provides a firmware/UI research route if the platform is eventually confirmed.

The [Google Play GFit Pro listing](https://play.google.com/store/apps/details?id=com.app.cy.GFit) identifies a possible historical app package, `com.app.cy.GFit`. It is a lead for offline inspection, not a verified app identity for the current QR or proof of a watch app store. Pairing without that app is already demonstrated; health-device commands still require a compatible protocol implementation.

## First end-to-end target

Build toward: **watch input → local bridge → request agent status → short response**.

Use a small explicit set of requests, such as status, repeat response and cancel. Do not turn arbitrary watch input into shell command text. Start by logging events and returning a fixed response; connect real agent actions only after the input mapping is verified. The application runs on Linux, and its output can use verified watch audio or a verified text channel.

The standard host integration surfaces are [Linux input events](https://www.kernel.org/doc/html/latest/input/event-codes.html), the [BlueZ Media API](https://bluez.readthedocs.io/en/latest/media-api/) and the [MPRIS Player interface](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html). A MPRIS facade may let the watch's media controls operate a Linux agent interface. Whether the watch shows track/title metadata is a device experiment, not a guaranteed display channel.

Vendor notification behavior must also be checked by platform. The [official iOS SDK function description](https://doc.zh-jieli.com/Apps/iOS/health/zh-cn/master/Development/Content/function_desc.html) describes ANCS notification delivery. That does not establish a generic AE01 text-push command or a working Linux notification server for this specimen.

## Concrete next experiments

### AGENT-INPUT-001 — Observe watch controls

Prerequisites: restore the normal Bluetooth connection without removing bonds or resetting the watch; disconnect the phone normally; locate the current `Apple Watch (AVRCP)` event node. Event numbers change, so do not reuse the earlier event14 blindly.

`evtest` is already installed. This command lists the input inventory without changing it:

```bash
rtk proxy cat /proc/bus/input/devices
```

In the watch's block, identify its `eventN` handler, then replace the placeholder below with that watch-specific node:

```bash
rtk sudo timeout 30 evtest '<WATCH_EVENT_NODE>'
```

The current user lacked permission to read the observed node, so this bounded capture requires local administrator access. Observe only the watch; do not select a normal keyboard or use exclusive `--grab`. While capturing, use the watch's existing music/remote-control screen and perform one action at a time. Keep raw output local in ignored captures.

Success: repeatable event type/code/value for at least one explicit watch action. No custom watcher is necessary before this succeeds.

### AGENT-VOICE-001 — Verify the Linux voice path

After the connection is restored, inspect the watch's available host audio-card profiles and sources. The current machine already has `pactl`, `wpctl`, `pw-record` and `pw-play`. Choose a supported headset profile only after inspecting its actual name. Use a deliberate short recording of a test phrase and a short playback test; keep recordings private.

Success: microphone audio from this watch is captured on Linux, and a response plays through the watch. Then investigate whether the watch's assistant action emits an observable host event. Siri on the phone does not establish Linux wake-word support.

### BLE-RECONNECT-001 — Identify the control channel

The descriptor names both BLE and EDR at the same address. [BlueZ's generic connection method](https://bluez.readthedocs.io/en/latest/device-api/) chooses between transports for dual-mode devices; a generic connection is insufficient evidence of a usable GATT channel. The installed CLI offered an LE submenu, but its explicit attempt returned `org.bluez.Bearer.LE1 is not available` for this watch. No GATT objects appeared, and no persistent bearer preference was changed.

Next research: inventory current advertising and local BlueZ bearer support; resolve the key error; compare a verified BLE connection with the historical AE00 surface. Listen only after a real notify characteristic appears. Authentication and initialization must be derived from observed traffic or matching SDK source before any command is proposed.

### FW-IDENTIFY-001 — Assess native apps and feature removal

Collect exact nonprivate about/version information and identify compatible vendor source or an original firmware artifact offline. Establish the board, flash layout, update validation and recovery route before designing a firmware replacement. If physical inspection becomes necessary, obtain owner approval before opening the watch. Obtain explicit approval before firmware/DFU commands or flash programming.

Success: an evidence-backed answer about native execution, with a matching build target and recovery method. Until then, Android apps, a Linux shell, arbitrary OTA installation and removal of the original UI are not established capabilities.

## Research limitations

No matching app binary or original firmware was available locally. External repository-index searches failed with HTTP 504; targeted official GitHub source retrieval succeeded. Some documentation pages were inaccessible through the browser connector but could be fetched directly. HCI capture and watch input-node access were blocked by host permissions. No physical opening, firmware transfer, unexplained GATT/serial write or health-app installation was performed.


## Priority correction and new evidence — 2026-10-12

Owner now clarifies that OS access and **custom computer information on the watch display** are the main objectives; button mapping is secondary. BLE/Classic restoration and play/pause verification supersede the earlier connection blocker. Native execution remains unknown.

GFit Pro is owner-confirmed; screenshots show firmware 1.0.0.4, PID 76, version 1004, type 0. Offline app inspection strengthens the Jieli protocol lead and identifies real OTA lookup/download routes. The exact image has not been retrieved because the metadata server rejects the research request. Notification text and compatible watch resources are the strongest source-backed custom-display leads; neither is validated on this specimen yet. [Firmware/display research](gfit-firmware-research.md) records native access prerequisites and the owner-suggested ReverseEngineerAnything tooling.
