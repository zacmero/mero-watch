# Historical investigation: 9–10 December 2025

Reconstructed from previous owner conversations. This is **not** a verbatim terminal transcript, and files/screenshots from the earlier machine have not been imported.

## 2025-12-09 — first device assessment

- Owner recovered an Apple Watch Ultra-like clone from discarded electronics.
- The box/device displayed `A2859`, `v1001`, and markings including IMEI, CMIT, GB/T.
- It identified itself over Bluetooth as `Apple Watch`.
- The companion application was **GFit Pro** and could pair with the watch.
- The goal was **hacker control, BLE protocol exploration, and programmable functions**, not fitness metrics.
- Family suggestions (T800/T900) and candidate chips (Jieli AC695X, Realtek RTL8762C) were speculative and should never be treated as established.

## 2025-12-09 — iPhone / LightBlue discovery

Using **LightBlue**, the owner connected to the watch and saw:

| UUID in the app | Property | Observation |
| --- | --- | --- |
| `AE00` | Service | A vendor-looking GATT service was present |
| `AE01` | Write without response | Appeared writable; **no specific protocol command was validated** |
| `AE02` | Notify | Generated binary notifications |

A previously recorded BLE address was `F9:F3:71:D9:79:11`.

Notification data was reported with prefix `FEDCBA80...`. A recorded full example was:

```text
FEDCBA80FF0000A65FF61000000000641137EF
```

No byte-by-byte decoding, field labels, command/response mapping, endianness, length interpretation, checksum validation or firmware attribution was confirmed.

**Critical distinction:** an observable `AE01` write characteristic is **not** an invitation to try random values on a working device.

## 2025-12-10 — Arch Linux / Python attempt

Previously used local workspace:

```text
~/watch_hack/
  venv/
  watch_listen.py
```

Historical Linux investigation used **Bleak**. It was unsuccessful due to connection timeouts accompanied by Bluetooth USB/controller instability:

```text
hci0 removed
# controller was deleted/re-added; Bleak connection timed out
```

The earlier dongle was described as unreliable. We **cannot** conclude that Bleak, the watch, the AE00 service, or the pairing protocol was at fault.

No earlier Python source or raw logs were retrieved for this repository. `scripts/ble_probe.py` is a **new implementation**, not a reconstructed copy of `watch_listen.py`.

## 2026-10-12 — resurrection

- Owner confirms watch is **fully working and operational**.
- New research home is `zacmero/mero-watch`.
- The current lab has a TP-Link UB5A Bluetooth adapter available, though compatibility with this watch is **untested**.
- Plan: restore read-only Bluetooth observations first, then characterize packet protocol, identify firmware/SoC, assess shell/diagnostic potential, and potentially integrate with the Mero agent ecosystem.

## What previous testing did NOT establish

- SoC/chip vendor, memory size, MCU architecture, RTOS, source SDK
- Shell or firmware flashing capabilities
- Confirmed interpretation of any BLE packet or writable command
- Verified official UUID namespace expansion
- A successful end-to-end Linux connection on the current adapter
- A reliable way to pull firmware or control the microphone

Future findings should go into timestamped investigation notes with commands, host/adapter models and raw evidence references.
