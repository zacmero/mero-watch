# Native architecture investigation

## 2026-10-13 — offline runtime, updater and UI reconstruction

Scope: immutable inspection of the captured PID 76 / firmware 1.0.0.4 build.
No updater activation, resource upload or modified firmware installation occurred
in this pass. This document complements [build analysis](build-analysis.md),
[update lab](firmware-update-lab.md) and [UI notes](native-ui-layout-notes.md).

### Evidence and provenance

Observed stock `app.bin`: 1,200,992 bytes, SHA-256
`9117eea8ff2f1694a16d57f16850100692c2ff8bfc3b66bfd8ede9c76c0e5ae4`.
Original UFW SHA-256:
`5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145`.
Raw firmware, disassembly, library objects and capture output remain private in
ignored `captures/`; they are not public repository dependencies.

Reference SDK: [UWINGS-KUNYI/ac701n_soundbox at f8eeea1](https://github.com/UWINGS-KUNYI/ac701n_soundbox/tree/f8eeea1ebecacb84d20f04515773528ad5616c1a).
Relevant files are `sdk/cpu/br28/maskrom_stubs.ld`, UI headers and
`sdk/apps/common/ui/interface/ui_resources_manager.c`. This is a reference build,
not proof of the clone's complete source or hardware revision.

### Runtime memory

Startup instructions establish the following copy/zero operations. These are
statically derived runtime addresses, not live debugger measurements.

| Region | ROM source | RAM destination | Bytes |
| --- | --- | --- | --- |
| Initialized data | `0x06117798` | `0x00104840` | 18,972 |
| Zeroed BSS | — | `0x00109260` | 83,712 |
| Copied executable code | `0x0611c1b4` | `0x0011d960` | 37,580 |

Flash image base is `0x06000000`; analysis entry is `0x06000120`.
Startup stack values are `0x00103840`. The two ROM copy spans are contiguous;
the copied code ends at the end of `app.bin`. The analysis ELF preserves bytes
and represents BSS without adding payload. `scripts/native_firmware_map.py`
implements this mapping with an exact-stock hash guard.

Earlier exact uC/OS-II-derived byte matches now map to RAM: `OS_EventTO`
`0x0012105c`, `OS_EventTaskWait` `0x00120f02`, `OS_InsertListHead`
`0x00120ef2`, `OS_RemoveList` `0x00120e50`, and `os_sem_create`
`0x001219a0`. These matches do not establish a kernel version or shell.

A compiled and linked PI32v2/r3 fixture confirms direct relative call targets
use instruction address + instruction byte length + printed displacement.
`scripts/native_code_index.py` applies that rule. Its string tracking is linear
and conservative; nearest prologues are candidates, not authenticated symbols.

### Update acceptance path

Decoded `ble_app_ota.bin` is 63,872 bytes. Its analysis base `0x00177000`
is corroborated by startup clearing BSS at `0x00186980`, exactly code end.
This is not evidence of a working recovery connection.

All 148 external direct calls resolve against the reference ROM stub table:
46 memcpy, 38 memcmp, 19 memset, 16 watchdog clear, 14 CRC16, six strlen,
five strcmp, two strncmp, one flash power-on and one reset.
There are also 174 indirect calls whose targets remain unresolved.
ROM CRC16 is `0x0001fdd0`; SHA-256/ECC ROM entry points exist in the reference
but were not observed as direct calls in this updater. Indirect calls and later
boot validation remain gaps; this does **not** prove unsigned firmware acceptance.

At updater `0x0017897c`, CRC16 is called over 62 bytes starting two bytes into
a header, compared with its leading 16-bit value. Subsequent code reads an
entry count at header offset eight and uses an 80-byte entry stride. This
correlates strongly with the captured 64-byte UFW header and entry directory,
and links the offline repacker's header check to actual updater instructions.
Other CRC sites cover 14, 30, 78 and variable lengths; their complete record
semantics remain unresolved. No rollback or recovery procedure is established.

### Native UI architecture

Two reference UI functions match complete stock instruction bytes:
`ui_core_remove_element` at `0x0600dc84` (16 bytes) and
`ui_core_set_element_css` at `0x0606c914` (178 bytes).
Reference prototypes take an element pointer, with the latter accepting a CSS
structure. Real element instances, ownership and execution context are not yet
mapped; these are not callable host commands.

The downloaded UI archives contain LLVM bitcode. Vendor clang produces readable
IR exposing text, time, number, layout, window and drawing APIs. The existence
of those reference APIs does not establish their addresses in this firmware.
The native `ui_style_vm_init` diagnostic points to candidate `0x0600d17e`.
Candidate `0x06061500` correlates with reference `jlui_load_window`, including
the UI-file diagnostic, retry loop and 20-byte window directory stride.
This loader correlation is not a complete exact-byte function match.

Reference loader format:

- File header: 16 reserved bytes, type byte, window-count byte, 16-bit property
  length, rotation byte and three reserved bytes; total 24 bytes.
- Each 20-byte window entry: three 32-bit fields (file offset, window length,
  pointer-table file offset), then four 16-bit fields (pointer-table byte length,
  data CRC, table CRC, header CRC).
- Header CRC covers the first 14 bytes of each window entry. Pointer-table CRC
  covers its indicated byte span. Both use CRC16 polynomial `0x1021`, initial 0.
- The reference loader reads the declared window length, checks its data CRC,
  then reads 16-bit relocation offsets. For each offset, it adds the allocated
  window base to a nonzero 32-bit pointer field within the window.

Observed across nine stock `.sty` files: **131 windows; all 131 header CRCs and
all 131 table CRCs match**, with relocation fields in bounds. Only **one of 131
declared window-data spans** matches the reference data CRC. The file count is
seven WATCH bundles plus SIDEBAR and JL; JL alone contains 119 windows.
Therefore data representation, CRC coverage or loader differences remain open.
Do not silently repair these CRCs or assume SDK layouts are interchangeable.
`scripts/native_style_inventory.py` reports this mismatch without changing files.

### Remaining work toward a real custom screen

1. Explain the stock window-data CRC mismatch and confirm the device's loader
   handling of encoded pointer/data fields.
2. Recover concrete widget structures, screen IDs, event handlers and actual
   text/drawing API entry points; distinguish ROM pointers from RAM instances.
3. Build an offline native-layout fixture with verified structure and validation.
4. Establish boot validation, update activation and a recoverable stock restore
   path before proposing installation of modified executable firmware.

The verified photo/background path still adds the vendor clock overlay. It does
not implement custom native UI, input handlers or an agent application. Neither
an executable disguised as an image nor a usable OS shell has been demonstrated.
