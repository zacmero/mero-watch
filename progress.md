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
