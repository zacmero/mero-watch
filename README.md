# mero-watch ⌚🔬

Native UI and firmware research on Zac Mero’s working Apple Watch Ultra-style clone.
The goal is a useful Mero wrist interface with its own diagnostic screen and agent controls.

## Current achievements

| Area | Established result |
|---|---|
| Computer connection | BLE data and Classic media/control connections demonstrated without GFit Pro; watch play/pause controls worked on Linux. |
| Stock firmware | Matching PID76 firmware 1.0.0.4 acquired, inspected and protected in two read-only private copies. |
| Direct updates | Linux can enter OTA from normal firmware, serve both stages, reconnect to the loader and complete programming without the phone app. Stock updates returned to normal boot. |
| Visible firmware modification | Owner verified the Calculator icon changed to an M, the CALC label remained, and tapping it still opened Calculator. |
| Executable architecture | PI32v2/r3 disassembly and compilation established. Package/build evidence identifies the Jieli JL701N / BR28 family; exact physical SoC identity remains unauthenticated. |
| Kernel evidence | Exact helper-code matches strongly support a Jieli uC/OS-II-derived RTOS. Exact kernel version is unproved. |
| Resource architecture | Native control trees, image resources, event registrations and the 37-entry menu dispatch table are mapped. |

The original vendor package is 18,760,384 bytes, SHA-256
`5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145`.
Firmware, package-derived key material and confidential captures remain outside Git.
The preserved package is an OTA recovery artifact, not a physical flash/NVRAM dump;
recovery from every possible failed boot has not been established.

## Active work: a separate mero-shell

Add an independent main-menu launcher and native diagnostic window while retaining
existing apps. First commands: read allocator statistics, refresh the display and
return to the menu. Later work includes live agent status and short machine commands.

The firmware’s own diagnostic code exposes current free heap, its low-water mark
and allocator-region size. A read-only C binding compiles for PI32v2/r3 and passes
synthetic RAM tests. An additional window/control-tree candidate passes offline
integrity checks. **The new entry, live diagnostic screen and authored native C
execution have not yet been demonstrated on the watch.**

The earlier Music lyric-text probe had no owner-accessible test view and did not
prove execution. Notifications reached the watch inbox, but popup/vibration behavior
did not meet the intended interface. The visible M-icon experiment proves resource
control; it does not by itself establish a new native application or OS shell.

A general-purpose/POSIX shell and Linux are not observed. `mero-shell` means our
own diagnostic UI and command console on the existing firmware.

## Investigation records

- [Visible menu modification and launch architecture](docs/native-menu-launch.md)
- [Computer-only OTA](docs/direct-ota.md) and [installation evidence](docs/installation-proof.md)
- [Approved native mission](docs/mission-2026-10-15.md)
- [Native architecture](docs/native-architecture.md) and [build analysis](docs/build-analysis.md)
- [Device dossier](docs/device-dossier.md) and [Bluetooth protocol notebook](docs/protocol-notes.md)
- [Firmware acquisition and vendor-app research](docs/gfit-firmware-research.md)
- [Possible applications](docs/possible-apps.md), including meeting/class audio-to-text and a later exercise-menu alternative
- [Lab playbook](docs/lab-playbook.md) and [agent instructions](AGENTS.md)

## Historical stages

The [previous README](docs/history/readme-before-native-shell-2026-10-15.md) preserves
the initial unknown-chipset/missing-firmware stages verbatim. Dated investigation
records retain their original observations; use the current achievement table for
project status. The [2025 archive](docs/2025-investigation.md) records the earlier
LightBlue/Bleak work and adapter failures.

Tracking: [protocol work](https://github.com/zacmero/mero-watch/issues/2),
[native firmware/system access](https://github.com/zacmero/mero-watch/issues/3),
[Mero wrist interface](https://github.com/zacmero/mero-watch/issues/4).

## Working rules

Preserve the working device, distinguish observed and owner-reported results from
inferences, and validate bounded firmware candidates before transfer. Keep original
firmware protected. Do not publish pairing keys, real IMEI, private notifications,
health traces or confidential raw captures. See AGENTS.md before running experiments.
