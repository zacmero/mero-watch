# Device dossier — Mero Watch artifact

**Record created:** 2026-10-12  
**Physical condition:** working and operational as of 2026-10-12, per owner.  
**Classification:** unidentified Apple Watch Ultra-styled **clone**, not an authenticated Apple Watch.

## Evidence ledger

| Evidence | Value | Classification | Provenance / caution |
| --- | --- | --- | --- |
| Rescued device | Discarded-electronics find | Owner-reported | Historical conversation, 2025-12-09 |
| Model marking | `A2859` | Observed/reported marking | May be copied/spoofed; not hardware identity |
| Firmware/software version | `v1001` | Reported marking | Need exact screen/photo and software build |
| Companion app | `GFit Pro` | Owner-reported functional app | Prior pairing established |
| Bluetooth name | `Apple Watch` | Previously observed | Cosmetic advertised name only |
| BLE address | `F9:F3:71:D9:79:11` | Previously observed | Session-dependent; public identifier, handle carefully |
| Service | `AE00` | Observed by LightBlue | Shortened 16-bit UUID display; canonical 128-bit encoding still to verify |
| GATT write characteristic | `AE01`, write-without-response | Observed by LightBlue | Do **not** send speculative bytes |
| GATT notify characteristic | `AE02`, notify | Observed by LightBlue | Was seen delivering data |
| Example BLE payload | `FEDCBA80FF0000A65FF61000000000641137EF` | Historical captured notification | Encoding, framing, CRC and semantics **unknown** |
| Additional labels | IMEI, CMIT, GB/T, MAC | Owner-reported from box/info | Actual numbers not archived; regulatory claims not verified |
| Computer | ArchMerOS/Arch Linux | Owner's lab | Earlier Bleak experiment on Linux |
| Current computer Bluetooth | TP-Link UB5A `2357:0604` (available) | From broader lab records | **Not yet verified with the watch** |
| Prior Linux blocker | `hci0 removed`; adapter/controller reset; Bleak timeout | Historical observed error | The underlying cause is unconfirmed |

## Identification hypotheses — NOT established facts

- **T800/T900 family:** possible marketing/product family based on appearance, but no board, SoC, retail listing, Bluetooth manufacturer data or update image yet identifies it.
- **Jieli AC695X:** earlier candidate chipset, unsubstantiated.
- **Realtek RTL8762C:** earlier candidate chipset, unsubstantiated.
- **Operating system:** unknown. Might be vendor RTOS / bare-metal firmware. There is **no evidence of a Linux shell**.
- **Firmware installability:** unknown. A vendor OTA implementation does not imply unrestricted code execution or unlockability.
- **BLE audio/voice:** unknown; classic Bluetooth audio profiles and BLE command channels might be separate, and a microphone is not necessarily accessible through GATT.

The marking `A2859` and advertised name `Apple Watch` must **not** be used to select Apple firmware or Apple procedures.

## Open questions

1. Physical board markings, SoC/package identifiers, flash part, power circuitry?
2. Which BLE address(es), address type, appearance and manufacturer/service data are advertised now?
3. Exact complete GATT service/characteristic UUIDs, properties and permissions?
4. Is `AE02` a streaming notification channel? Does it only emit after app authentication/init commands?
5. What is the packet framing (start bytes `FE DC BA 80`?), payload length, checksum and message type?
6. How is the watch paired? Does its app use BLE only or also Bluetooth Classic?
7. Is the firmware available from the companion app or vendor endpoints? What is its archive/container format?
8. Are there UART/SWD/test pads and an independently readable external SPI flash?
9. What is the minimum functioning wrist-agent interface (notifications / buttons / watch-to-PC controls), even if code execution is impossible?

## Preservation and handling

- **Record before changing:** all screens and firmware fields; hardware photos; working app connection; adapter and phone versions.
- **Prefer observation:** advertise/scan → service enumeration → notify subscription → traffic capture → packet correlation.
- **Keep mobile app state reproducible.** Disconnect app before independent host connections if the watch allows only one central.
- **No blind protocol writes** and **no speculative OTA**. Investigate update data offline first.
- **No disassembly** until photographs and a recoverability assessment are documented.
- Device identity and captures can contain sensitive identifiers. Avoid committing IMEIs, unredacted personal notifications, pairing keys and full private BLE traces into this **public** repository.

## Physical inventory to collect next

Photos of front/rear, strap removed if safe, packaging labels, setup/about/version screens; charger type; display resolution only if measured; case dimensions only if measured; phone app version; output of `lsusb`, `bluetoothctl list`, scanner advertisement and GATT enumeration. None of these new data has been collected yet in this repo.

## Verified host/connection observations — 2026-10-12

Live checks at 21:32–21:35 UTC confirmed TP-Link USB `2357:0604`, a powered/unblocked `hci0`, kernel `7.1.8-arch1-3` and BlueZ `5.87`. The historical watch address/name was observed advertising again. One Bleak connection returned `Connected: True` with zero GATT services; attempts before and after timed out without observed controller disappearance. AE00/AE01/AE02 have not yet been reverified. See the dated [protocol investigation record](protocol-notes.md) for commands, provenance and limits. This append updates the earlier collection status without replacing historical observations.

At 21:44:14 UTC, an interactive BlueZ connection in the owner-described normal Bluetooth mode was verified with `Connected=true`, `ServicesResolved=true` and an audio media transport. The Linux audio card's active profile was `a2dp-sink`. No companion app was used. Zero GATT services/characteristics were exposed in that inventory; AE02 and microphone access remain unverified.

## Device findings consolidated — 2026-10-12 session

**Later-session update:** read-only modification research found a watch AVRCP input node and media-control interface, then a subsequent disconnect and `br-connection-key-missing` on reconnect. Earlier stability remains a dated observation; the last state in the later session was disconnected. The owner reports Siri voice interaction without a health app and supplied a pairing JSON descriptor naming BLE/EDR at the historical address. These reports and RCSP-family source comparisons are appended below and in the protocol notebook.

### Verified observations

- The historical address and `Apple Watch` name were discovered again on the current Linux host. Sample RSSI values ranged from −80 to −50 dBm. These readings establish reception, not the cause of earlier timeouts.
- BlueZ reported the watch address type as `public`. This is a host-reported property, not authenticated manufacturer identity or a guarantee that the address never changes.
- The successful normal-mode connection was paired and bonded, with services resolved. Seven samples spanning 30 seconds remained connected; an independent check after closing the Bluetooth client also remained connected. No companion app was required for this connection.
- BlueZ exposed the following device/profile UUIDs. Their presence is not proof that each function works; they were not all exercised:

| BlueZ label | Full UUID |
| --- | --- |
| Serial Port | `00001101-0000-1000-8000-00805f9b34fb` |
| Audio Sink | `0000110b-0000-1000-8000-00805f9b34fb` |
| A/V Remote Control Target | `0000110c-0000-1000-8000-00805f9b34fb` |
| A/V Remote Control | `0000110e-0000-1000-8000-00805f9b34fb` |
| Handsfree | `0000111e-0000-1000-8000-00805f9b34fb` |
| Human Interface Device | `00001124-0000-1000-8000-00805f9b34fb` |
| PnP Information | `00001200-0000-1000-8000-00805f9b34fb` |
| Vendor specific | `fe010000-1234-5678-abcd-00805f9b34fb` |

- The host created an idle media transport with UUID `0000110a-0000-1000-8000-00805f9b34fb` and codec value `0`. The audio card had active profile `a2dp-sink`. Playback, calls and microphone capture were not attempted.
- BlueZ showed manufacturer-data key `0x05d6` and modalias `bluetooth:v05D6p000Ad0240`. These are reported protocol identifiers; no manufacturer or chipset attribution was validated. Payload semantics remain unknown.
- The normal-mode inventory contained zero BlueZ GATT services and characteristics. The vendor-specific UUID above was a device UUID, not an enumerated GATT service. Historical AE00/AE01/AE02 were not rediscovered in this session.

### Owner-reported mode and phone behavior

- A watch pairing mode asks the user to download a health app for phone connection.
- The owner can connect the watch to an iPhone without that app and sees two connections. Their identities and transports were not independently inventoried.
- The owner calls the successful setting normal Bluetooth mode. Clicking its normal Bluetooth icon changes it to a “B...” icon with dots; exact icon meanings and whether the control represents mode, power or connection status remain unknown.
- The phone was disconnected for the computer retry. The owner subsequently confirmed that the computer connection was stable.

### Limits and next evidence

The normal Bluetooth connection is verified; persistent BLE notifications, serial data, HID input, microphone access, shell access and agent control are not. App initialization requirements and a separate BLE identity remain hypotheses. A QR/app prompt does not prove that the app is technically mandatory for all device functions.

The current adapter did not reproduce the historical controller-removal failure. Earlier intermittent attempts have no confirmed packet-level root cause: proximity, phone competition, watch setting changes and host connection handling were not isolated. Raw HCI monitoring was blocked by host permissions. Preserve the working normal-mode connection and investigate the BLE channel separately when its identity is established.

## Modification-research evidence — later 2026-10-12 session

- **Observed:** BlueZ exposed media-control and input interfaces; Linux created `Apple Watch (AVRCP)`. Actual key events were not captured, and host capabilities do not prove each advertised key can be generated by the watch.
- **Owner-reported:** app-free phone pairing and Siri voice interaction work. Linux microphone capture, a wake-word mechanism and audio playback remain untested.
- **Owner correction:** the current prompt is generic “Health App”; exact companion app identity is unknown. GFit Pro remains the historical recollection, not a verified current download identity.
- **Owner-supplied descriptor:** QR JSON has same-address `bleAddr`/`edrAddr`, `connectWay=0`, `name=Apple Watch`, `pid=76`, `vid=4750`. These are unauthenticated protocol fields; their full semantics are unknown.
- **Hypothesis with new source support:** Jieli/RCSP-related protocol is plausible because official vendor docs/source use the historical UUID family, packet boundary markers and similar QR fields. Exact chip, firmware SDK target, authentication and command semantics remain unknown. The prior AC695X/RTL8762C suggestions are not promoted to hardware facts.
- **Later observed blocker:** normal reconnect returned `br-connection-key-missing` and remote termination; explicit LE connection was unavailable through the installed daemon/device API. No bond reset or unexplained write was attempted.

The owner prioritizes agent status and short commands. [Modification options](modification-options.md) distinguishes host bridges, voice, metadata/notification display, watch faces and actual native firmware/UI replacement, with evidence and prerequisites for each.


2026-10-12 follow-up: BLE AE00/AE01/AE02 rediscovered after standard pairing repair; Classic A2DP/AVRCP connected alongside GATT. Watch-only evtest verified KEY_PLAYCD (200) and KEY_PAUSECD (201), press/release. Owner reports computer music control and watch app access. One AE02 notification captured; semantics unknown. Microphone, camera shutter and agent commands remain untested. See docs/protocol-notes.md for dated evidence and official mobile-app candidates; no Linux health app identified.


## Owner firmware screenshots and app confirmation — 2026-10-12

Observed in owner-supplied app screenshots: current/latest firmware **1.0.0.4**; restoration screen **pid:76 version:1004 type:0**. This is the latest app-visible version evidence, while the older reported v1001 marking remains historical. Owner confirms GFit Pro and reports App Store release 1.4.5; recalls a previous firmware update with uncertainty. The manual URL selects watch_type=ultra2, a tutorial category rather than hardware identity.

Offline Android GFit Pro 1.4.5 inspection found Jieli RCSP/OTA libraries and a PID-based firmware lookup. This strengthens the protocol lead without identifying the watch MCU. The vendor metadata query rejected unauthenticated research requests with code 422, Token error or expired; no matching device firmware image was obtained. OS/shell access and custom screen output remain unverified. See [firmware research](gfit-firmware-research.md) for sources, artifact hashes, display options and next steps.
