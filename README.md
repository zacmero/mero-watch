# mero-watch ⌚🔬

**Mero Computer Archaeology — rescued smartwatch reverse engineering**

A living investigation of Zac Mero's working Apple Watch Ultra-style **clone**: identify its real hardware, document its Bluetooth protocol, test non-destructive control from Arch Linux, and see whether it can become a minimalist interface for Mero agents.

> **Status — 2026-10-12:** Watch is charged, fully operational, and available for experiments. The chipset, firmware update format, CPU/RTOS, and prospects for a native shell or custom firmware are **not yet known**.

**Verified Linux connection, 2026-10-12:** the owner-described normal Bluetooth mode connects without GFit Pro. BlueZ resolved its services and the Linux audio system selected `a2dp-sink`; the connection survived closing `bluetoothctl`. Seven checks over 30 seconds confirmed connection state, and the owner subsequently reported it stable. Audio playback and microphone operation have not been tested. This mode exposed zero GATT services, so the historical AE00/AE02 channel is still unverified on Linux. See the [normal-mode connection procedure](docs/lab-playbook.md#normal-bluetooth-connection-without-the-phone-app) and [dated findings](docs/protocol-notes.md#2026-10-12--normal-mode-connection-without-companion-app-from-2142-utc).

## Known device facts (and their limits)

| Field | Evidence / status |
| --- | --- |
| Origin | Rescued from discarded electronics (owner report) |
| Form factor | Apple Watch Ultra-style clone; **not authenticated as an Apple product** |
| Model marking | `A2859`, reported on packaging/device; not a trusted hardware identification |
| Firmware marking | `v1001`, reported; firmware provenance unknown |
| Companion app | **GFit Pro**, used for pairing |
| Bluetooth advertised/displayed name | `Apple Watch` in earlier tests; not proof of Apple hardware |
| BLE service | `AE00` (observed with LightBlue in December 2025) |
| BLE write characteristic | `AE01` — **write without response** (observed) |
| BLE notify characteristic | `AE02` — **notify** (observed) |
| Address seen in previous session | `F9:F3:71:D9:79:11` (may change or be randomized) |
| Notification prefix | `FEDCBA80...` (observed, not yet decoded) |
| Additional markings | IMEI, CMIT, GB/T and MAC appeared on packaging/info screens; **values and authenticity not verified** |
| Processor/OS | **Unknown**. Jieli AC695X / Realtek RTL8762C were preliminary guesses only. |

**Important:** The watch already yielded genuine BLE clues in 2025. This is not a from-scratch protocol project; our blocker then was an unreliable Linux Bluetooth adapter, not a complete lack of device communications.

## Repository map

- [Modification options](docs/modification-options.md) — practical routes to agent status/commands, voice, protocol bridges and native firmware; latest connection limitation and next experiments

- [Device dossier](docs/device-dossier.md) — known facts, hypotheses, unknowns, preservation rules
- [2025 investigation archive](docs/2025-investigation.md) — prior LightBlue/Bleak tests and observed packet data
- [BLE protocol notebook](docs/protocol-notes.md) — GATT structure, packet observations, experiments
- [Roadmap](docs/roadmap.md) — staged plan, evidence gates, definition of done
- [Lab playbook](docs/lab-playbook.md) — Arch/BlueZ setup, safe probing, troubleshooting
- [`scripts/ble_probe.py`](scripts/ble_probe.py) — optional read-only scan / inspect / notification listener
- [`AGENTS.md`](AGENTS.md) — instructions for future human or AI contributors

## Quick start — Arch Linux

First check the adapter and discover the watch:

```bash
sudo pacman -S --needed bluez bluez-utils python
sudo systemctl enable --now bluetooth
bluetoothctl list
bluetoothctl
# in the interactive shell:
power on
scan on
# stop scanning when found; note device name and address
```

For a reproducible **read-only** Python GATT investigation:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/ble_probe.py scan --seconds 12
python scripts/ble_probe.py inspect --address <WATCH_ADDRESS>
python scripts/ble_probe.py listen --address <WATCH_ADDRESS> --seconds 20
```

The listener only subscribes to **existing notify characteristics**; it does not send undocumented commands or firmware.

> The old Linux attempt used `~/watch_hack/venv` and `~/watch_hack/watch_listen.py`. It timed out when the previous USB Bluetooth controller reset (`hci0 removed`). Those files have **not** been recovered or copied here; this repo supplies fresh, minimal tools instead.

## Mission and sequencing

1. **BLE-001 — Reconnect and capture baseline:** advertise/scan, inspect GATT, reproduce `AE00/AE01/AE02`, capture notified packets.
2. **BLE-002 — Decode protocol:** inspect traffic from the authorized GFit Pro pairing; correlate known user actions with packets; maintain byte-level hypotheses.
3. **FW-001 — Identify firmware/hardware:** investigate lawful update manifests and images *offline* before attempting any writes; identify chipset, SDK, bootloader, RTOS if possible.
4. **SYS-001 — Evaluate local execution:** assess UART, SWD, diagnostic interfaces, update path, shell possibilities without assuming Linux exists.
5. **AGENT-001 — Build a wrist bridge:** experiment with safe watch↔Arch↔Mero-agent interactions; microphone/audio features depend on actual protocol support.

## Operating principles

- Preserve the working watch: **no blind GATT writes, OTA updates, flashing, or teardown** without a recovery plan.
- Tag statements **observed / reported / hypothesis / untested**; do not present clone identifiers as manufacturer specifications.
- Capture timestamps, adapter model, address type, firmware version, command and outcome.
- Do not commit secrets, pairing keys, private notification contents, full unredacted personal health/activity data, or raw traffic dumps containing private information.
- The repository is **public**. The historical BLE address is published for reproducibility but may be a privacy-sensitive device identifier; avoid publishing future persistent identifiers or IMEIs by default.

Created as a research record on **2026-10-12**, drawing on the owner's **2025-12-09–10** experiments and current plans.
