# Native firmware / normal-update investigation — 2026-10-13

## Scope and current result

Owner prefers a real native application and replacement UI through the normal firmware-update path. The background/notification demonstrations do not provide that functionality. This pass establishes an **offline packaging and updater-analysis workflow**, not a working custom application or an approved installation.

No watch connection, unexplained GATT write, updater entry command, malformed image transfer, OTA transaction or flash operation occurred during this pass. All generated firmware files remain in ignored private captures because package-derived key material is present.

## Verified packaging workflow

Original UFW: 18,760,384 bytes, SHA-256 `5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145`. Both code-image entries (`flash.bin`, `flash2.bin`) parse into matching 1,200,992-byte application contents. The first also contains its compressed `uboot.boot`; geometry differences between the images remain preserved.

The [upstream repacker](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/d1204a478e2a80a5c9fbce85eaca264e7b2cc468/tools/ufw-repack/repack_ufw.py) targets BR35/AC707N. Its code was inspected and pinned by SHA-256 `30a9162fa46e1c486f4310e70070cd18cc5ef7122622010ed12617f26b7a973c`; its applicability here was tested rather than assumed. Our `scripts/ufw_lab.py` selects code entries by observed bank name and adapts the raw UFW to its parser through a discarded synthetic prefix. It verifies the actual UFW and nested integrity layers independently of the backend's permissive parser. No synthetic wrapper is retained in the output.

**Observed:** Untouched repacking through either code-image path reproduces the original package byte-for-byte. An offline, equal-length `Apple Watch` → `Mero Agent!` string fixture at application offset 544,180 was then repacked into both images. The resulting package remains 18,760,384 bytes and differs in 46 stored bytes, including data and integrity fields. Fixture SHA-256: `a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7`. This is a packaging experiment; the string's actual runtime effect is untested and it adds no agent feature.

Checks passed for UFW header CRC, stored encrypted entry-table CRC, critical outer code/resource/updater payload CRCs, and application-directory parent/application/config-tool JLFS header/data CRCs. The nested `uboot.boot`, `key_mac` and `isd_config.ini` bytes remained unchanged in both images. All non-code outer payloads—including `ota.bin`, resources and configuration—remained byte-identical. The original source hash is unchanged.

**Negative tests:** A flipped code-payload byte is rejected by the outer payload check. Recomputing only the outer CRC layers still leaves an invalid nested application-parent CRC, which the checker rejects. This guards against a superficially valid container hiding stale inner integrity fields.

**Limit:** Several optional metadata entries do not match a simple CRC16 of their stored bytes even in the untouched original. Their precise checksum/encoding semantics remain unresolved; this pass preserves them exactly. The checker does not claim universal validation of every package type or bootloader acceptance policy.

## Updater payloads decoded

The unchanged `ota.bin` contains eight CRC-verified embedded entries: `uart_update.bin`, `uart_user.bin`, `edr_ota2.bin`, `usb_update2.bin`, `sd_update2.bin`, `ble_ota.bin`, `ble_app_ota.bin`, and `nor_ota.bin`.

Seven have an additional 32-byte compressed-updater header. Their chunk stream is LZ4-style, carries history across chunks, and permits a terminal match. Standard independent-block decoding rejected it. A bounded linked-history decoder, `scripts/decode_jieli_updater.py`, successfully reconstructs all seven with both header and complete decoded-data CRCs verified:

| Updater | Decoded bytes | Chunks |
| --- | ---: | ---: |
| BLE | 44,096 | 11 |
| BLE application updater | 63,872 | 16 |
| USB | 19,840 | 5 |
| UART user updater | 14,496 | 4 |
| SD | 17,824 | 5 |
| NOR | 13,440 | 4 |
| EDR | 36,512 | 9 |

The two BLE headers have address field `0x00177000`; runtime mapping/entry behavior is not yet independently established. These decoded native bytes permit inspection of the actual updater code. Merely including USB/UART loader binaries does **not** establish accessible watch pads, working recovery entry or a recoverable failed flash.

## What is still required for a native agent screen

1. Trace updater checks, ROM calls and normal-update selection/handoff. A CRC-consistent repack is not proof that authentication/signature/version restrictions permit it. Absence of readable signature-related strings is not proof of an unsigned boot chain.
2. Resolve application section/RAM-copy mapping and a native UI entry point. Build an actual agent panel and runtime input/data handlers; the branding fixture is not that application.
3. Establish restoration and recovery on this exact board. The device advertises no double backup, so the second code image in the package is not rollback evidence. Physical inspection or recovery-entry experiments need separate owner authorization when prepared concretely.
4. Prepare the meaningful application patch, independently validate it, and review the complete installation/recovery procedure before any update transfer.

The image/executable route remains secondary. Scanning this application's strings found no `dlopen`, `load_module`, `rt_module`, Lua/Wasm/ELF markers; that weak negative result does not rule out code loading or decoder bugs. No image-decoder exploit has been demonstrated or sent to the watch. The firmware path now has stronger direct evidence and is the active branch.

## Reproduce the offline tests

The pinned upstream backend and inspected jltech source must be obtained separately; neither vendor firmware nor private keys are distributed. Use a fresh output path under ignored captures:

```bash
rtk proxy .venv/bin/python scripts/ufw_lab.py roundtrip ORIGINAL.ufw captures/roundtrip.ufw \
  --backend /private/pinned/repack_ufw.py --crypto-path /private/jl-misctools/firmware
rtk proxy .venv/bin/python scripts/ufw_lab.py branding-fixture ORIGINAL.ufw captures/fixture.ufw \
  --backend /private/pinned/repack_ufw.py --crypto-path /private/jl-misctools/firmware
rtk proxy .venv/bin/python scripts/decode_jieli_updater.py BLE_PAYLOAD.bin captures/ble-decoded.bin
```

The lab only accepts the exact original firmware hash and refuses existing output paths. Sixteen unit tests passed, plus real-package round trips, both-image mutation validation, seven updater decodes and the two negative package tests.
