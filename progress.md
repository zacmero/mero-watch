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
