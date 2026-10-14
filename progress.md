# Research progress — 2026-10-12

- Began research into watch modification and Linux agent integration.
- Read existing dossier, protocol notes and roadmap; preserved uncommitted work.
- Verified the normal Bluetooth connection remains connected.
- Asked for first desired function and exact app-download identity. Owner selected agent status and short commands.
- Built-in web search failed before returning results; investigating an alternative tool.

## Research pass completed

- Alternative web connector and direct official GitHub retrieval provided vendor/host API sources. External repository-index searches timed out with 504; no matching firmware or app binary was obtained.
- Observed watch AVRCP input and media-control interfaces; actual button events remain uncaptured because event-node access was denied and the connection subsequently dropped.
- Owner supplied QR pairing JSON and clarified the generic Health App prompt and Siri interaction. Recorded reports without assuming universal app compatibility or a confirmed wake mechanism.
- Compared historical packet boundaries and UUIDs with official Jieli SDK definitions; recorded a stronger RCSP-family hypothesis without assigning offsets, decoding commands or identifying the chip.
- A normal reconnect returned a missing Classic key/remote disconnect; explicit LE route was unavailable. No bonds, watch firmware or persistent bearer settings were changed.
- Chose installed evtest/PipeWire tools for next experiments rather than creating redundant probes.
- Added docs/modification-options.md and updated README, dossier, protocol notes and roadmap. Documented six modification paths and concrete input/voice/BLE/firmware identification experiments.
- Verified git diff whitespace and local documentation link targets. No firmware modification or live agent function is claimed.


2026-10-12 follow-up: BLE AE00/AE01/AE02 rediscovered after standard pairing repair; Classic A2DP/AVRCP connected alongside GATT. Watch-only evtest verified KEY_PLAYCD (200) and KEY_PAUSECD (201), press/release. Owner reports computer music control and watch app access. One AE02 notification captured; semantics unknown. Microphone, camera shutter and agent commands remain untested. See docs/protocol-notes.md for dated evidence and official mobile-app candidates; no Linux health app identified.

2026-10-12 firmware research pass: inspected owner screenshots; confirmed 1.0.0.4 / PID76 / 1004 / type0. Inspected vendor manual/website assets and offline Android GFit Pro 1.4.5 plus separate vendor GSFit APK. Identified Jieli RCSP/OTA/authentication libraries and actual firmware lookup routes. Metadata rejected with code422; no exact image acquired. Reviewed official text/resource APIs, independent authentication/UFW tools, Jieli Ghidra support and ReverseEngineerAnything. Main priorities corrected to OS access/custom display. Report created at docs/gfit-firmware-research.md; raw binaries and crypto material remain ignored/private. No watch writes or updates.

Report verification: all repository-local Markdown targets resolve; git diff --check passes; downloaded APKs and crypto disassembly confirmed ignored. Ready to publish documentation-only milestone. Exact firmware acquisition and custom display/OS experiments remain pending.

Temporary iPhone capture prepared: isolated mitmproxy 12.2.3/Python3.13 environment; LAN proxy running, onboarding page and vendor HTTPS verified locally. TLS inspection restricted to gssdfit.com/jieliapp.com; only firmware routes saved, authorization/cookie headers omitted. Private CA/captures confirmed git-ignored. Waiting for owner to configure iPhone proxy/certificate and open normal firmware version page; no firmware/update command sent. Proxy cleanup pending.

Phone could not reach proxy onboarding. Local listener/page remained healthy; firewalld public zone on LAN interface did not allow 8899. Added runtime rich rule limited to home IPv4 subnet and capture TCP port, expires automatically after 30 minutes. Owner phone connectivity verification pending; firewall rule and proxy cleanup required after capture.

Phone TCP connections now observed on proxy; owner confirms phone LAN IP typo. mitm.it displayed upstream nonproxy page, possibly HTTPS bypass by vendor-only TLS filter. Dedicated public-certificate setup HTTP server started; only landing page/certificate routes served, private key path verified404. Temporary 8898 firewall rule restricted to phone IP; cleanup pending.

Owner reports certificate downloaded, installed and trusted; a typed URL error was corrected. Proxy listener and phone connections verified. Owner instructed to open normal app firmware/version page, stopping at restoration if no normal page exists. Firmware response capture still pending; vendor route/TLS failure diagnostics enabled without retaining unrelated response bodies.

2026-10-12 capture milestone: trusted owner iPhone session produced normal-check code1024 and restoration metadata code200. Decoded matching PID76/version1004/type0 metadata; retrieved update1004.ufw on computer via documented download API, 18,760,384 bytes, vendor MD5 matched. Offline reviewed/guarded jl-misctools unpacking identified JL701N package label and BR28 board_7012AF_J1 build clues. Both flash images yielded matching component files; large resource payload separated for later format analysis. No firmware transferred to watch. Public report/dossier/protocol notes updated; crypto/raw data/artifacts remain ignored.

Capture cleanup complete on host: both listeners stopped, both runtime firewall rules removed, absence verified. Owner reports proxy off and trust disabled, retaining profile/setup for future analysis. Main OS/custom-display objective continues with offline AC701/BR28 architecture/resource analysis; native shell and custom app loading remain unproven.

2026-10-13 offline build pass: repository-import searches again failed504; direct pinned GitHub source retrieval used. Inspected comparable AC701/BR28 compiler/linker/OS configuration and vendor PI32v2 toolchain; compiled own fixture and disassembled unchanged watch code. Corrected app base with string-pointer correlations. Matched five SDK kernel routines exactly, supporting uC/OS-II-derived OS. Decrypted resource image, verified/extracted 13 filesystem files and 11 JLFS bundles. Traced GFit notification serializer and native command161 subtype dispatcher; live display/authentication still pending. Created docs/build-analysis.md and appended evidence records. No firmware/watch writes; analysis artifacts and package-derived key remain private.


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
