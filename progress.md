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


### Later owner confirmation — custom image displayed

Owner first saw our image with the vendor clock over it, then briefly saw the factory background despite the app retaining the custom selection, then saw our image again with the clock overlay. Our custom picture is therefore owner-confirmed on the real watch through GFit's photo-background path. Persistence/selection behavior remains uncertain. No direct Linux resource transfer was performed. This establishes appearance customization, not custom executable UI or interactive navigation. Next investigation: stock `.sty` / `.view` layout and native control bindings.


### Style/view follow-up and cleanup

The narrow RU30 decoder also completely decodes watch6.view (151x180) and watch131.view (146x184), with both record/image CRCs verified. Visual inspection shows static face previews (analog hands and a digital date/time respectively). Thus these .view examples are preview images, not executable layout code. Reference AC701 UI headers define separate clock/text/picture/layout controls and event handlers, but the exact .sty disk layout has not been validated against them; no style fields have been patched. The temporary artwork server timed out and its firewall rule is absent on verification. Public own-artwork PNG remains available in GitHub assets.


## 2026-10-13 — Native firmware route prioritized

Owner explicitly prefers a native app/UI through normal firmware update; background and notification demonstrations do not satisfy that goal. Offline lab now reproduces original firmware byte-exactly through both code-image paths and builds a CRC-consistent equal-length branding fixture in both app images. Fixture changes 46 stored bytes; no new app behavior or device acceptance is claimed. Nested bootloader/key/config and every non-code outer payload were preserved. Negative tests reject corrupted outer payload and stale nested CRC after outer-only repair. Seven embedded native updaters, including both BLE helpers, decode completely with header/decoded-data CRCs verified. Sixteen unit tests passed. Source/tool pins, hashes, optional-metadata limits and next boundaries recorded in docs/firmware-update-lab.md. No DFU command, update handoff, firmware transfer or image exploit was sent to the watch. Actual UI patch, boot-policy tracing and recovery remain unresolved.


## 2026-10-13 — native architecture pass

Added stock-hash-guarded runtime ELF mapping, conservative code indexing and read-only style inventory. Confirmed next-instruction-relative PI32v2 calls with a compiled fixture; resolved 148 updater direct ROM calls and documented 174 unresolved indirect calls. Recorded two exact UI function matches and native loader correlation. Public architecture notes link evidence and open gaps. Validation: 21 unit tests pass; real nine-file style inventory validates 131 header/table checks and reports the unresolved data mismatch. Device untouched.


## 2026-10-13 — installation proof reprioritized

Owner explicitly authorized firmware load testing and requested exclusive focus on proving modified-code deployment. Native UI research paused. Started narrowly scoped proxy on 192.168.1.97:8899, selecting SHA256-verified unchanged stock firmware for initial download interception. Added a temporary LAN-only firewall rule tagged mero-watch-load-test. Requested phone proxy/trust setup and restoration-page observation; no upgrade action or watch transfer yet. Next: verify app download path and metadata checks, then controlled identifiable modified build. Recovery after a failed boot remains unverified and was disclosed before authorization.

Firewall correction: iptables INPUT ACCEPT did not establish reachability; an independent inet firewalld input hook remained. Added runtime firewalld rich rule permitting TCP 8899 only from current phone IPv4 192.168.1.84 with a 3600-second expiry. Earlier single-layer firewall assessment was incomplete.

Modified download handoff prepared: selected the prevalidated both-image branding fixture SHA256 a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7; MD5 2fd0d033055a4e897e8dbd5e83b2b0db. Verified decrypt/re-encrypt of the real restoration metadata with exactly its fileMd5 changed and every other decoded field preserved. Key material loaded only from ignored inspected app disassembly, never logged. Restarted proxy selecting this artifact; waiting for refreshed Detect and subsequent owner update action.

Owner instructed to press Upgrade Now after refreshed detection. Observed POST /abroad/awsd/ota/piddownload and proxy HTTP 200 response containing 18,760,384 bytes of the modified fixture with SHA256 a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7. This establishes app download handoff only; watch transfer, acceptance and boot are still pending owner observation. Sanitized event journal retained privately at captures/firmware-work/load-test-events.jsonl.

Owner reports GFit Pro shows transfer progress without an error so far. This is owner-reported transfer initiation, not yet accepted installation or boot confirmation.

Owner-reported transfer checkpoint: 40%, slow but continuing, no error reported. No host BLE operation was initiated while the phone owns the update connection.

Owner-reported transfer checkpoint: 60%, continuing. Installation/boot result remains pending.

Owner reports transfer finished; watch displays Chinese text, loading dots and an identifier; GFit Pro says waiting for upgrade. No identifier retained. This is an intermediate device update state, not a confirmed success or boot. Owner instructed to keep power/app/connection unchanged.

Owner-reported updater display address F9:F3:71:D9:79:12, versus previously observed normal BLE/EDR F9:F3:71:D9:79:11. Treat as a distinct update-mode candidate, not an overwritten normal address. Owner reports repeated Chinese message/loading cycles, then further apparent progress; success and normal reboot still unconfirmed.

Owner reports GFit Pro OTA update timeout after completed transfer; phone Bluetooth shows Apple Watch connecting and is no longer connected. Normal boot and modified marker are NOT confirmed. Possible update-mode reconnection failure is a hypothesis; no claim of signature rejection or successful flash. Started passive scan for normal ...:11 and displayed updater ...:12; no power cycle/reset instructed.

Observed passive BLE: F9:F3:71:D9:79:12 advertised local name Apple Watch, RSSI -78 dBm, no service UUIDs in advertisement, manufacturer-data ID 1494 (0x05d6). This is live host evidence of the alternate updater address; manufacturer ID alone does not identify/authenticate hardware. Requested owner force-close phone app before a read-only service inventory.

Owner photograph /home/zacmero/Downloads/photo_2026-10-13_23-43-37.jpg shows Chinese 等待连接 (waiting for connection) and 地址 (address), explicitly F9:F3:71:D9:79:12. Dots are a waiting indicator; apparent progress is not verified flash progress. This narrows the current failure to update-mode connection/handoff; application acceptance/rejection remains unproven. No IMEI is displayed in this photo. Read-only connect at nearby RSSI -58 also timed out.

Controller trace updater-retry-private.btsnoop positively shows HCI Create Connection (0x01/0x0005) to F9:F3:71:D9:79:12, BR/EDR address type, then Connect Complete Page Timeout (0x04). This is Classic paging, not LE Create Connection or GATT validation. The host retry failure must not be attributed to firmware acceptance/signatures. Investigating explicit LE bearer selection. Raw trace remains private.

Temporarily enabled BlueZ experimental APIs through /run/systemd/system/bluetooth.service.d/mero-watch-load-test.conf and restarted host Bluetooth service; existing pairing database was preserved, watch remained powered. Installed client bearer setter previously failed UnknownProperty, so explicit LE connection requires checking daemon API availability. Runtime override must be removed after experiment.

Explicit Adapter1.ConnectDevice with AddressType=public succeeded after experimental API activation (dbus-fast raised unexpected output signature o despite the daemon returning the created path). Verified Device1 Connected=true, LE.Connected=true, BREDR.Connected=false, unpaired, services GAP1800 and AE00. The alternate-address updater is reachable over LE; Generic Device1.Connect had attempted Classic instead. No flash command sent by host yet.

Updater LE authentication succeeded using the previously validated private helper. Source-derived GetFileInfoOffset E1 replied offset 64, length 66. This confirms an authenticated, responsive normal RCSP OTA endpoint at ...:12; initiating E2 file eligibility check with only the requested bytes from the hash-guarded modified fixture. No E3/flash-entry sent yet.

## 2026-10-14 — direct host continuation

Owner photo 23:58:50 shows 请尝试使用升级软件手动触发升级 (please try using upgrade software to manually trigger upgrade), plus updater ...:12 address. E2 eligibility response for the modified artifact was 00. Implemented bounded device-driven E5 range server from pinned RCSP reference, with E8 acknowledgements and E6 result checks; only success permits E7 reboot. 27 tests pass in proxy environment, including packet reassembly and range bounds. Under existing explicit firmware-load authorization, launched direct host --flash continuation using the exact validated modified artifact. Final acceptance and boot remain pending.

Direct E3 was accepted with a four-byte zero payload, and owner reports file-transfer screen. Host initially aborted because it incorrectly required a one-byte E3 result; corrected to inspect the first status byte as the reference SDK does. No file blocks were served before that abort. Started a resume listener on the existing link without authentication reset, E1/E2 or E3; awaiting device pulls. This implementation error is recorded separately from device rejection.

Resume attempt could not continue: link became disconnected before status query; fresh connect to updater timed out. Subsequent passive scan found ONLY normal F9:F3:71:D9:79:11, name Apple Watch, RSSI -54, with normal manufacturer-data format (no JLOTA marker). Thus updater address disappeared and the normal application-mode advertisement returned; actual UI/boot confirmation requested from owner. No host E5 payload blocks have been served.

Owner clarifies watch UI still says File transfer despite ...:11 normal-format advertisement; do not interpret address return as confirmed application boot. Phone Bluetooth remains off. Normal-address informational/eligibility probe is underway.

Normal ...:11 E1 returns disabled mark (0,0); pinned SDK reference explicitly requires E2 payload 00 in this case. Added that behavior and bounded-range regression test. Normal ...:11 E2 accepted (00), E3 sent with corrected first-byte acknowledgement handling, and device began E5 pulls. Observed first served block: offset 0, 512 bytes of the exact modified fixture. This is the first confirmed host-to-device file payload transfer; 28 tests pass. Owner still sees file-transfer screen.

Owner confirms direct computer OTA is the preferred route from now on. Active transfer serves the MODIFIED fixture (not stock), SHA256 a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7. Phone Bluetooth remains off; GFit Pro/proxy is not carrying this host BLE transfer. Added an observation-only second AE02 subscriber that acts only if the device returns E6=80: sends source-derived 0B payload 00 01 on the still-open link, waits for peripheral disconnect, reconnects ...:12 explicitly over LE, confirms target-info mandatory-loader flag and performs E3-only second pass (no repeated E1/E2). This preserves the SDK handoff that the earlier phone attempt did not complete. No final success/boot claim yet.

At UTC 03:32, replaced the auxiliary GATT subscriber with passive D-Bus observation: after the second StartNotify client was added, request delivery appeared duplicated and effective progress slowed. The passive observer does not call StartNotify during file serving; it acquires a subscription only on the device EOF signal (or E6=80) to preserve the handoff link. Only the auxiliary process was interrupted; primary file serving stayed running. 30 tests pass, including the observed four-byte E3 acknowledgement and mandatory-loader gate.

UTC 03:42:55: first-stage E6 result80 (loader staged), 4,672 served blocks, 18,700,191 response bytes including repeated ranges; final announced loader payload57,059 bytes. Passive observer took notification subscription at EOF, sent0B payload0001; reply01. Peripheral disconnected itself, then direct LE reconnect to ...:12 authenticated and target-info mandatory-loader flag confirmed. UTC03:43:10: E3-only second stage began (no E1/E2); four-byte zero ack accepted; E5 pulls started. E8 announced1,302,528 bytes. Owner photo00:43:51 shows red 升级中，请不要断电 (upgrading, do not cut power), green18% progress. This is live second-stage firmware programming, not just phone download or eligibility. Final status/normal boot remains pending.

UTC03:45:10: second-stage E6 returned00 success after334 served blocks /1,309,024 response bytes (announced payload1,302,528). Host sent E7 payload00; device acknowledged with four-byte zero payload. Direct host updater process exited0. Owner reports watch reached100% then turned off. Instructed normal power-on; application boot and marker visibility still pending. This establishes device-reported acceptance of the modified package and completed programming, not yet confirmed normal execution.

Owner confirms normal boot after completed second-stage success and E7 ack. About still displays Apple Watch; post-flash advertisement also names Apple Watch at normal ...:11. The patched app literal is not proven to drive that displayed name. Do not claim visible Mero Agent behavior. Verified outcome: device-reported programming success for modified code-image payload plus owner-confirmed normal boot. Next verification must target a traced observable name/version field; current literal was an unverified packaging marker.

## 2026-10-14 — fresh computer-only stock update

Owner authorized a fresh stock update from a normally booted watch. Original package size/hash verified unchanged; protected recovery copy retained. At UTC04:30:18 the normal-address authenticated E1/E2 probe accepted the stock package (mark offset/length 0/0). At UTC04:30:32 Linux initiated E3 and served device-requested blocks; E8 announced 15,878,656 bytes. Owner independently confirmed the watch entered transfer mode without GFit Pro. This establishes computer-only update entry; full programming and normal boot remain pending. Private sanitized journals: fresh-stock-probe-events.jsonl, fresh-stock-transfer-events.jsonl, fresh-stock-handoff-events.jsonl under captures/firmware-work. Passive handoff observer is active for the two-stage transition. Initial explicit ConnectDevice returned Error.Failed although LE was already connected; the existing LE connection authenticated successfully.

### Fresh stock update: completed programming

**Observed (2026-10-14):** Starting from normally booted firmware, Linux initiated the full stock update without a GFit Pro update session. Owner confirmed entry into transfer mode. UTC04:59:18 first-stage E6 returned80 after3,998 served blocks /15,939,487 response bytes (includes package framing and requested ranges; not a flash readback). The passive observer subscribed at EOF, sent0B payload0001, received01, and observed the peripheral disconnect itself. Direct public-LE reconnect to updater address ...:12 succeeded; target-info mandatory-loader mode was confirmed at04:59:33. E3-only pass two announced1,302,528 bytes. UTC05:01:52 final E6 returned00 after334 blocks /1,309,024 response bytes; E7 reboot received00000000 acknowledgement. Handoff process exited0. Total computer-initiated sequence took about31 minutes20 seconds. Owner reports power-off and is performing normal power-on; normal boot confirmation is pending.

This establishes direct computer-only update entry, both transfer stages, loader handoff and device-reported programming success. It does not establish arbitrary patched firmware compatibility, flash readback or recovery from every failed boot. The original stock package and independent read-only recovery copy remain unchanged.

### Fresh stock update: normal boot confirmed

**Owner-reported (2026-10-14):** After the completed computer-only stock update and normal power-on, the watch returned to its normal clock/menu. The complete fresh-start route is therefore demonstrated on this device: Linux authentication/eligibility, update entry from normal firmware, first-stage file serving, device-driven loader relink, second-stage firmware programming, success acknowledgement and normal boot. GFit Pro was not required for this update sequence. This test installed the original stock package, not the prepared mero-watch marker candidate.

**Observed post-boot:** Linux reports Connected=true and ServicesResolved=true at normal address ...:11. AE01/AE02 are present, and a live GAP Device Name read returned Apple Watch. The stock application data connection is functional after the fresh update. A redundant explicit ConnectDevice call returned Error.Failed despite the established working LE connection; use the live connection state and successful GATT operation rather than that error alone.

## 2026-10-14 — native style CRC interpretation resolved

**Observed offline:** Re-running scripts/native_style_inventory.py across all nine stock .sty files under the private resource-bundles directory validates all 131 window-header CRCs, all 131 relocation-table CRCs, and all 131 window-data CRCs when each relocation word is masked to its lower 17 bits for the CRC calculation. Original tagged bytes are preserved; the inventory does not write files. All non-null normalized targets fall inside their window. This supersedes the earlier unresolved 130/131 raw-data CRC mismatch, without replacing that historical observation. Pointer tags and normalized-target validity are now reported explicitly. The tagged-pointer test also checks that corruption of a lower pointer bit invalidates the normalized CRC.

This resolves a data-integrity interpretation gap, not the full native control ABI, resource writer, event ownership, or custom application execution. Reference SDK pointer/page decoding differences remain to be reconciled.

Owner approved the next mission recorded in docs/mission-2026-10-15.md: preserve connectivity/settings and existing controls, prove a native panel and custom handler, then live agent data, commands, mero-shell and separately tested phone/ntfy integration. No new flash experiment occurred in this planning checkpoint. The branding fixture generator now emits mero-watch plus a null byte; its prepared private artifact is not installed.

Checkpoint validation: all 30 unit tests passed without skips in the optional capture/tool environment; all 9 stock styles /131 windows independently rechecked for header, table and normalized data CRCs and in-window pointer targets. Git whitespace checks passed. Raw/vendor firmware and authentication material remain excluded from Git.

## 2026-10-14 UTC21 — native C panel experiment resumed

Owner reports fully charged watch and authorizes proceeding with the approved mission now. Added docs/possible-apps.md with the requested local audio-to-text / meeting and class notes idea, separated from offloaded transcription and kept as a later branch. Native graph parser traverses all131 windows /3,074 controls with sibling-aware relocation handling. Source-correlated handler table has697 records and two duplicate IDs; duplicates are not treated as unused space. Three additional complete UI helper matches and the actual element lookup / Music text setter / redraw path are documented in docs/native-panel-probe.md.

Own C probe compiles to58 bytes, fitting a traced routine exactly. Candidate contains only three bounded application changes in both images: own compiled routine, a redirected Music initialization diagnostic call, and mero-watch marker literal. Candidate SHA2567fb622c7bd5ca1fa23f9547f445751e0ddd00b467cfc9eb895a3d598c67b8040; 18,760,384 bytes;164 stored byte changes; non-code outer payloads unchanged and both banks independently validated. All35 tests pass. This is a temporary Music text-area execution probe, not the finished native agent screen; media control handlers and settings remain unchanged. Native appearance and creation timing still require observation.

The previous runtime experimental BlueZ override was absent. Recreated the same temporary override and restarted the host daemon; pairing records preserved. At UTC21:50:41 the normal LE connection authenticated and E1/E2 accepted the candidate. A passive handoff observer was ready at21:51:21; Linux started the primary update at21:51:26. Private native-probe eligibility, transfer and handoff journals remain under ignored captures/firmware-work. No execution/boot success claim is made while the transfer is active.
