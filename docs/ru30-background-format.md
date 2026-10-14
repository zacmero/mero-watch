# RU30 background format — 2026-10-13

## Evidence

Decoded both stock external-resource backgrounds `BGP_B131` and `BGP_C131` into complete 240 × 296 images. These previously unresolved, non-JLFS files are directly wrapped RU30 images. The general `.res`/`.view` files also use RU30, but this codec supports only the observed single-image background variant.

The exact mirrored GFit Android APK's architecture split contains `libjl_bmp_convert.so`, exporting `br28_png_to_res`. Offline AArch64 emulation established its call arguments: BGRA bytes, width, height, wrap-resource flag and destination pointer. A null destination obtains required size. The emulator executes only this image routine, with bounded memory/instruction budgets and small memory/log import stubs. No JNI UI, Bluetooth or network code executes. ELF relocation types and imported calls outside those inspected fail explicitly.

Three small fixtures produced identical native/Python bytes. The complete screen revealed different valid RLE grouping between the Python encoder and native routine; independent decoding yields identical pixels. The install candidate uses the actual native routine's output, reproduced byte-for-byte by the public emulator. This is **offline resource compatibility evidence**, not proof of device acceptance.

## Observed container

All offsets below apply to the validated single-background layout; they are not a universal RU30 specification.

| Offset | Observed layout |
| --- | --- |
| 0–23 | Fixed `RU30` header, preserved in the codec; remaining field semantics only partially known |
| 24–35 | Section record: offset 48, count 1, type 84 (`T`), final field 0 |
| 36–47 | Section record: offset 60, count 1, type 80 (`P`), final field 0 |
| 48–59 | String record: numeric field 256, storage offset 80, length 1024 |
| 60–79 | Image record: header CRC16, payload CRC16, packed identifier/flags `0x30010000`, width, height, payload length, payload offset |
| 80–1103 | 1024 zero string-storage bytes in the generated variant |
| 1104 onward | Image payload: one little-endian 32-bit row descriptor per row, followed by compressed rows |

Multi-byte container fields are little-endian. The image CRC covers the entire payload. The record CRC covers record bytes 2–19 (including the payload CRC). Both match CRC-16 with polynomial `0x1021`, initial value zero, as implemented by Python `binascii.crc_hqx(data, 0)`. This was checked against both stock files and generated native output; the native converter's 16-entry nibble table also matches that polynomial. The first four record bytes are two CRC16 values, **not a single CRC32**.

Each row descriptor packs a 21-bit payload-relative offset and an 11-bit encoded byte length. Rows decode into alpha byte + big-endian RGB565 value. An RLE control byte with its high bit set repeats one three-byte pixel; otherwise it introduces literal three-byte pixels. The low seven bits give pixel count; zero is rejected. Decode verifies width, extents and both CRCs. RGB565 quantization changes source colors; alpha remains eight bits.

`scripts/ru30_background.py` implements this narrow layout using the standard library; Pillow is needed only for PNG import/export. `scripts/br28_converter_oracle.py` reproduces the inspected vendor routine using optional pyelftools/Unicorn/Pillow dependencies. Neither tool transfers data to the watch.

## Results and transfer boundary

Stock BGP round trips preserve every decoded pixel, but compressed files differ: 121,042 → 112,628 bytes for BGP_B131 and 108,507 → 101,016 bytes for BGP_C131. No original file was overwritten. Our native-generated candidate is 27,993 bytes; provenance/hash is in assets/README.md. Thirteen tests passed, including an independently native-validated golden fixture, alpha/long-run handling, checksum rejection and out-of-bounds rows.

The owner initially recalled vendor-only downloads, then rechecked GFit Pro and successfully uploaded an owner-selected photo to the watch. This proves a photo-background transfer capability on the owned device. Our PNG has been served to the phone for a separate appearance test; its display result is pending at this record's creation.

Offline SDK tracing distinguishes legacy `FatFsWatch` from `RcspWatch`. Modern RcspWatch file creation validates watch-file compatibility and uses a TransferTask plus storage-device handler. WatchBase exposes source-derived custom-background query/activation command builders. The resource-upload state machine, destination selection and restoration procedure still need tracing before a direct Linux transfer is attempted. No SDK transfer or activation command has been sent by the computer.

A background can establish a custom visual appearance. A live agent screen and replacement menu/touch behavior require a runtime rendering path; repeated background-flash rewrites are not the live-update plan.
