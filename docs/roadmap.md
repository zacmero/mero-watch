# Research roadmap and deliverables

North star: **turn a working, unidentified watch into an understood and potentially programmable interface** without sacrificing the only working specimen.

## Phase 0 — Baseline preservation

- Photograph device, charger, box/label and all version/diagnostic screens.
- Verify companion app still works; record app version and watch UI capabilities.
- Note Linux kernel, BlueZ version, Bluetooth adapter model, USB topology.
- Define safe reset/recovery path before any high-risk operations.

**Exit:** a repeatable pre-experiment baseline and no device disruption.

## Phase 1 — BLE reconnaissance (BLE-001–003)

- `bluetoothctl` scan: identify advertisements and changes when app connects.
- `btmon`: independently observe host controller behavior.
- Bleak scan + service inventory; record full UUIDs, property lists.
- Subscribe to existing notify characteristics; verify whether AE02 still emits `FEDCBA80...`.
- Triage Linux instability: USB resets vs authorization/bonding vs competing central.

**Exit:** successful repeatable connection **or** documented failure path with logs, with the watch unharmed.

## Phase 2 — Decode protocol (BLE-004–006)

- Capture *authorized* GFit Pro/app interactions or local test-device Bluetooth diagnostics.
- Compare idle vs button presses, screen actions, sync triggers, notifications, app initiated features.
- Group packets by length and prefix; test frames, payload positions, counters and possible checksum offline.
- Build unit tests around sanitized, collected packet examples.
- Start with a *proven benign* command only after packet semantics and safety are clear.

**Exit:** at least one reproducible decoded message or known safe external function.

## Phase 3 — Firmware and hardware archaeology (FW-001, SYS-001)

- Read available vendor update metadata / app resources **offline**.
- Determine SoC family through manufacturer data, files, signed headers, board markings and references.
- Characterize boot chain, possible RTOS, RAM/flash, and any diagnostic interface.
- Assess external flash clipping/UART/SWD with power and voltage safety, *only if justified*.
- Investigate whether any shell/native apps are even architecturally possible; an MCU with RTOS may not provide a shell.

**Exit:** evidence-backed hardware/firmware profile; clear go/no-go for custom software.

## Phase 4 — Mero wrist companion (AGENT-001)

Candidate architecture:

```text
Watch <---BLE---> Arch Linux / bridge <---authenticated API---> Mero agents
```

Progressive, evidence-driven milestones:

1. PC→watch benign status message/alert (only if write commands are proven).
2. Watch→PC event or input (only if packets/buttons accessible).
3. Agent skill/CLI for short commands and responses.
4. Optional voice transport if microphone/audio streams are actually exposed.

**Exit:** one working, documented end-to-end feature. Do not promise audio/voice without proof.

## Decision gates

| Gate | Proceed if… | Otherwise… |
| --- | --- | --- |
| G1 | Stable GATT reconnection possible | Fix adapter, host stack and pairing without writing to watch |
| G2 | Notification packet format can be reproduced | Focus on capture quality and baseline; do not guess opcodes |
| G3 | Safe command semantics verified | Remain observation-only; use external phone/app integration where feasible |
| G4 | Firmware architecture and recovery identified | Do **not** flash; native code execution is an optional outcome |
| G5 | Watch can relay user inputs and/or outputs | Deploy minimal useful bridge; treat unsupported capabilities as closed research branches |

## Tracking conventions

- Experiment IDs: `BLE-001`, `FW-001`, `SYS-001`, `AGENT-001`.
- Each completed experiment should record **setup, command, raw observable evidence, interpretation, negative results, next hypothesis**.
- Maintain provenance tags: **observed**, **owner-reported**, **inferred**, **untested**.
- Keep this roadmap aligned with open GitHub issues; update the dossier only when an interpretation becomes evidence-backed.
