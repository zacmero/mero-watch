# Modification research findings — 2026-10-12

## Baseline

Observed: Linux still reports the watch connected and bonded. Normal mode has an audio transport and lists audio, remote-control, serial and HID UUIDs. Earlier inventory found zero GATT services. Advertised profiles do not establish functional input, serial protocol or native app support.

Owner priority: agent status and short commands. Exact companion app package/QR URL is requested and not yet supplied. Prior GFit Pro name remains owner-reported.

## Research record

Primary-source investigation and read-only host capability results will be recorded here, then consolidated into docs/modification-options.md.

## New local capability observation

Native `evtest`, `wpctl`, `pw-record`, `pw-play` and `pactl` are installed. Use native tools for the first event/audio experiment rather than add a custom listener. The watch-specific event node requires additional read permission; no unrelated keyboard events should be captured.

BlueZ exposed `MediaControl1.Connected=true` and `Input1`. `/proc/bus/input/devices` contained `Apple Watch (AVRCP)` with keyboard/event handlers. This creates a possible host input route, but no actual button event was captured. The event node was not readable by the current user. No `/dev/rfcomm*` nodes or relevant local APKs were found in the repo/Downloads top level.

Input nodes are transient: the initially observed event14 sysfs path disappeared before key decoding. Capability inspection must locate the device by name on each run. This does not itself establish a controller reset.

## App identity lead

Official Google Play listing: [GFit Pro](https://play.google.com/store/apps/details?id=com.app.cy.GFit), package `com.app.cy.GFit`, developer Shenzhen Guangsu Shidai Technology Co., Ltd. Official iPhone listing: [GFit Pro](https://apps.apple.com/us/app/gfit-pro/id1672924696). Both describe watch notifications/device management. Neither listing proves compatibility with this specimen or custom native app support. Exact owner QR/app identity remains pending. No APK or firmware was downloaded.

## SDK research lead

Source-grounded conclusion: official RCSP uses the same boundary constants and AE00 service family. The QR parser source also reads the same `edrAddr`/`name` fields. Together these support a Jieli/RCSP-family hypothesis more strongly than the prior appearance-only chipset guesses. No exact chip, firmware build, supported SDK, authentication sequence or writable command is identified.

Jieli's official [iOS SDK import documentation](https://github.com/Jieli-Tech/iOS-JL_Bluetooth/blob/main/docs/html/Development/import_desc.html) and [CoreBluetooth demo](https://github.com/Jieli-Tech/ios-bt-demo/blob/main/UsingCoreBluetoothClassic/README_en.md) use AE00/AE01/AE02. This is a protocol-family lead, not identification of this watch or its exact SoC. Other unrelated devices also use those UUIDs. Investigate packet framing in official source before proposing any commands.

## Connection state caveat

Explicit bearer experiment: local `bluetoothctl help` exposes `menu le` and `connect DEVICE`, but the attempted LE connection reported `org.bluez.Bearer.LE1 is not available` for the watch. No GATT objects appeared. CLI feature availability does not establish that the daemon/device supports this route. No persistent bearer preference was changed; no undocumented bytes, pairing reset or firmware command was sent. The diagnostic client was closed normally.

One normal reconnect returned `org.bluez.Error.Failed br-connection-key-missing` followed by `org.bluez.Reason.Remote, Connection terminated by remote user`. Kernel records since the previous stable session contained no matching controller-reset entries. Owner reports neither reconnecting to the phone nor changing watch mode since the stable connection. Cause remains unknown; do not blame either action. No bond removal, reset or repair pairing was attempted.

During later read-only research the AVRCP input disappeared and BlueZ reported `Connected=no`. No watch command or deliberate disconnect was sent in this research. The cause and timing are unknown; the earlier measured stability window and owner report remain historical evidence, not proof of indefinite stability.

## Owner clarification

The QR code opens a nonexistent page, and the owner cannot identify the download app name. Prior GFit Pro compatibility is historical owner evidence; the current QR destination is requested for identification. A dead download page is not evidence that the watch accepts custom firmware or apps.

The owner subsequently supplied JSON from the QR interaction rather than a URL. Fields: `bleAddr` and `edrAddr` both equal the already documented historical watch address, `connectWay=0`, `name=Apple Watch`, `pid=76`, `vid=4750`. Treat this as an owner-supplied pairing descriptor; no URL was established. Field names suggest both BLE and EDR addressing, but their exact semantics and manufacturer attribution require source validation. These identifiers are not authenticated hardware identity.

## Architecture sources

Official Jieli [health SDK](https://github.com/Jieli-Tech/iOS-JL_Health/blob/main/README_EN.md) provides a documented host integration research route, not a watch application installer. [BlueZ Media API](https://bluez.readthedocs.io/en/latest/media-api/) and [MPRIS Player API](https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html) provide standard host media/control interfaces to investigate for a host-side agent facade. Exact watch rendering and button delivery remain untested.

## Offline packet comparison

Direct official header retrieval independently confirmed RCSP boundary constants in [JL_rcsp_packet.h](https://github.com/Jieli-Tech/fw-AC63_BT_SDK/blob/master/include_lib/btstack/third_party/rcsp/JL_rcsp_packet.h). Jieli's [QRScanVC.m](https://github.com/Jieli-Tech/iOS-JL_Health/blob/main/code/JL_Health/JieliJianKang/%E8%AE%BE%E5%A4%87%E7%95%8C%E9%9D%A2/%E6%89%AB%E4%B8%80%E6%89%AB/QRScanVC.m) parses `edrAddr` and `name` from scanned JSON. This adds an independent format resemblance to the protocol-family lead; not all of the owner's QR fields were validated in that source.

Owner correction: the watch prompt says generic “Health App”; the exact compatible companion app is unknown. The owner reports pairing and activating Siri through watch voice interaction without a health app. This establishes owner-reported phone functionality, not a Linux microphone capture, wake-word mechanism or confirmed agent integration.


The historical sample is 19 bytes, begins `FE DC BA`, and ends `EF`. Directly retrieved official [RCSP documentation](https://doc.zh-jieli.com/SDKWiki/master/Jieli-Tech/fw-AC63_BT_SDK/9-third-party-integrations/9.1-jl-rcsp.html) describes the same boundary tags. This supports an RCSP-family hypothesis, not a decoded packet or exact SoC identity. Its payload, opcode, flags, length and authentication meaning remain unknown. No bytes were transmitted. Official source headers are being checked to ground this comparison independently of search snippets.


2026-10-12 follow-up: BLE AE00/AE01/AE02 rediscovered after standard pairing repair; Classic A2DP/AVRCP connected alongside GATT. Watch-only evtest verified KEY_PLAYCD (200) and KEY_PAUSECD (201), press/release. Owner reports computer music control and watch app access. One AE02 notification captured; semantics unknown. Microphone, camera shutter and agent commands remain untested. See docs/protocol-notes.md for dated evidence and official mobile-app candidates; no Linux health app identified.

2026-10-12 screenshot evidence: photo_2026-10-12_20-57-06.jpg shows Firmware Restoration, current/latest 1.0.0.4; photo_2026-10-12_20-57-07.jpg shows pid:76 version:1004 type:0 and restoration warnings. Owner confirms GFit Pro and reports a possible previous firmware update. Manual URL uses awsfile.gssdfit.com, watch_type=ultra2 and Square watch. Photos remain outside public repository.

Manual assets retrieved: index.26091567.js and enVideo chunk d6c9a1a1 expose hardcoded Bilibili tutorial IDs, not firmware URLs. Official GFit privacy JavaScript states manufacturer supplies firmware and GFit supplies upgrade path. Primary domain gssdfit.com responds with Nuxt application; offline inspection ongoing.

Primary SDK source evidence: Android-JL_Health NotificationHelper calls WatchManager.pushMessageInfo with NotificationMsg title/content; UpgradeViewModel queries online OTA using device PID/UID and accepts .ufw/.buf or update ZIP. This does not establish this specimen's commands or firmware. ElectronicCats/jieli-ble-badge-research publishes AC707N badge custom firmware and build/dump documentation for different hardware; useful tooling, not compatible firmware. Vendor current QR points to GS Fit landing page, with a vendor-hosted GSFit APK (different app identity from owner-confirmed GFit Pro).

GFit Pro Android offline artifact identified as com.app.cy.GFit 1.4.5 (42), mirrored XAPK; APK SHA-256 37aa539669470c402bd064fd252c7daccb90548be8170c3af63b2be2498192b7. Vendor-hosted GSFit APK saved separately. Neither executed/installed. GFit contains Jieli RCSP and OTA libraries, upgrade state machine, OTA metadata via POST ota/pidVersion (PID/version/MAC/optional userId) and download via ota/piddownload on vendor AWS application base. No bundled .ufw/.fw image found. Query wrapper is app-specific AES/RSA; no crypto keys, user tokens or raw app binaries will be committed.
