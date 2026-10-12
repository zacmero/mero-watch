# Agent instructions for mero-watch

This project is a **hardware archaeology** investigation of a *working* Apple Watch Ultra-style **clone** owned by Zac Mero. Protect the device first.

## Evidence discipline

- Separate **observed** (packet/log/photo), **owner-reported** (prior description), **hypothesized** (potential chipset/protocol), and **untested**.
- The only previously observed BLE service data: `AE00` service, `AE01` write-without-response, `AE02` notify, and notification sample `FEDCBA80FF0000A65FF61000000000641137EF`. Their semantic meaning is unknown.
- `A2859`, `v1001`, and Bluetooth name `Apple Watch` are **displayed identifiers**, not an authenticated manufacturer identity.
- T800/T900, Jieli AC695X and Realtek RTL8762C are candidate theories, not validated hardware.
- Do not fabricate byte offsets, message types, CRC algorithms, manufacturer identifiers, update URLs or shell commands.

## Safe default scope

- Allowed: passive scans, service inventory, notification listening, log analysis, offline app/firmware inspection, and reversible host configuration.
- Ask before: sending unexplained GATT writes, firmware/DFU commands, destructive app resets, opening the watch, applying voltage to pads, programming flash.
- Prioritize `btmon`/kernel evidence if a USB HCI controller disappears.
- Don't claim a Linux/Android/RTOS shell exists without positive evidence.
- Assume this is a **public** repository: no secrets, pairing keys, real IMEI, unredacted private notifications, personal health traces or raw confidential capture dumps.
- Never overwrite historical observations; append dated investigation records with provenance.

## Immediate next experiment

`BLE-001`: use current Arch Linux adapter to scan, inventory complete GATT UUIDs and attempt **read-only** notification capture. Cross-check AE00/AE01/AE02 and earlier controller reset failures. File findings in `docs/protocol-notes.md`, update `docs/device-dossier.md` only with verified evidence.

## Goal

Deliver an optional Linux BLE bridge to Mero agents after the watch's real capabilities become clear. Native firmware/voice/shell features are research branches, not guaranteed milestones.
