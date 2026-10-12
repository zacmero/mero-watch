# BLE/GATT protocol notebook

**Status:** partial identification; raw observation only. Last updated 2026-10-12.

## Observed GATT surface (LightBlue, 2025-12-09)

```text
Service AE00
├── Characteristic AE01  [write-without-response]
└── Characteristic AE02  [notify]
```

LightBlue displayed *short* UUID labels. Re-discover and record their **full 128-bit UUIDs** via BlueZ/Bleak; do not assume a particular base UUID before doing so.

### Known notification example

```text
FEDCBA80FF0000A65FF61000000000641137EF
```

Earlier AE02 notifications reportedly began `FEDCBA80`. Treat the complete sample as **uninterpreted binary**, with no invented header, length, checksum, timestamp, operation or payload field.

Useful initial analyses: count lengths, compare prefixes/suffixes across repeated idle traces, diff paired/unpaired and static/moving states, test for repeated framing and entropy; use captured samples, not conjectural command injection.

## Experiment registry

| ID | Task | Risk | State |
| --- | --- | --- | --- |
| BLE-001 | Scan and record advertisement + current BLE address/type | Read-only | Pending 2026 repeat |
| BLE-002 | Enumerate complete service/characteristic UUIDs and properties | Read-only | Pending 2026 repeat |
| BLE-003 | Subscribe to AE02; repeat historical notification capture | Read-only | Pending |
| BLE-004 | Record GFit Pro traffic through permitted local host/app diagnostics | Observation | Pending |
| BLE-005 | Correlate *explicit watch actions* with notified data | Read-only | Pending |
| BLE-006 | Document and test decoded benign commands only after evidence and rollback plan | Write risk | Blocked until protocol validation |

## Suggested structured log

For each capture include:

```text
date_utc: YYYY-MM-DDTHH:MM:SSZ
host: mero-machine or other device
os_kernel:
adapter_vendor_product:
bleak_version:
watch_firmware_screen:
watch_bluetooth_name:
watch_address_type:
watch_address: <redacted in public logs>
connection_state: app_connected | app_disconnected
gatt_full_uuid:
event: advertise | notify | read | timeout | disconnect
bytes_hex: <scrub private content before commit>
context: idle | raise_wrist | press_button | app_action | etc.
observation:
interpretation: untested hypothesis only
```

Keep private captures locally under `captures/` (ignored by Git). Commit only manually sanitized fixtures with clear provenance and expected checksum/packet lengths.

## Protocol investigation principles

1. **Reproduce** old AE00/AE01/AE02 findings with current gear.
2. Identify whether permissions demand authentication, bonding or an app handshake.
3. Establish framing empirically using many captures and controls.
4. Distinguish BLE GATT from Bluetooth Classic call/audio profiles.
5. Only after decoding and confirming benign traffic, design a minimal bridge; avoid writes related to DFU, factory reset or security settings.
6. If GFit Pro uses OTA, inspect downloaded firmware metadata **offline** before any firmware transfer.

No confirmed firmware update URLs, vendor documentation or exploit methods are currently part of the evidence.
