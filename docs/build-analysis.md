# PID76 firmware build analysis — 2026-10-13

This is offline analysis of the matching vendor `update1004.ufw`, not a physical flash dump. No firmware code was executed, and no Bluetooth command or update was sent to the watch during this pass. Earlier artifact provenance is in [the firmware acquisition report](gfit-firmware-research.md#2026-10-12-owner-session-capture-and-matching-firmware-acquired).

## What the build establishes

| Finding | Evidence and confidence |
| --- | --- |
| Jieli AC701/BR28 family | Observed UFW label `JL701N`, `board_7012AF_J1` application source-path suffix, and AC701 boot UI path; physical chip marking still unverified |
| PI32v2 instruction set, `r3` target | Comparable BR28 SDK compiler flags plus coherent decoding with the vendor toolchain and matching kernel routines; strong support |
| Application load address `0x06000120` | Package entry point and 1,247 exact string-start address correlations; observed/calculated, replacing an initial `0x06000100` analysis hypothesis |
| Jieli uC/OS-II-derived kernel | Five exact function-byte matches to a comparison SDK configured with `CONFIG_UCOS_ENABLE`; strongly supported inference, not an identified OS version |
| Extractable UI/watchface resources | Resource image decrypted, 13 file allocation chains verified, main UI and seven face bundles parsed |
| Existing custom-text route | GFit Pro SDK message serialization and RCSP `0xA1` command traced; corresponding firmware dispatcher identified; live compatibility/authentication still untested |
| Native shell or independently installable apps | Not established |

## Application and disassembly

`app.bin` is 1,200,992 bytes; SHA-256 `9117eea8ff2f1694a16d57f16850100692c2ff8bfc3b66bfd8ede9c76c0e5ae4`.

The comparison source is [UWINGS-KUNYI/ac701n_soundbox at f8eeea1](https://github.com/UWINGS-KUNYI/ac701n_soundbox/tree/f8eeea1ebecacb84d20f04515773528ad5616c1a). It is another AC701/BR28 SDK build, **not the watch's source tree**. Its [Makefile](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/Makefile) specifies `-target pi32v2`, `-mcpu=r3` and `CONFIG_UCOS_ENABLE`. Its [linker script](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/cpu/br28/sdk.ld) places code at `0x06000100`; the watch's extracted application starts 32 bytes later.

The [vendor Linux toolchain endpoint](https://pkgman.jieliapp.com/s/linux-toolchain) supplied `jieli-linux-toolchains-20260730.1`, an LLVM 4.0.1 fork supporting PI32, PI32v2 and Q32S. The downloaded archive was 26,027,508 bytes, SHA-256 `a1545cddbc451a06bac43eb5cd96d831470c42a97c5c0b1f98879a20fc7647bd`. It was extracted under ignored captures, without a global installation.

A small, investigator-authored C function compiled and disassembled successfully as PI32v2/r3. That fixture established the tool's ELF machine identifier and instruction syntax. A separate analysis-only ELF wrapper then exposed the watch's unchanged application bytes to the disassembler. The wrapper is not firmware and must not be treated as a flashable image.

An initial wrapper used the comparison SDK's code origin. Correlating immediate pointer loads with extracted string starts identified `0x06000120` instead, consistent with the package entry point. The corrected analysis-image range is `0x06000120`–`0x06125480`, with the latter address exclusive. Disassembly includes stack operations, calls, conditional dispatch and string-address references. This linear wrapper does not model sections copied to RAM or overlays: later image addresses are not automatically running-device addresses. Mixed code/data and indirect calls still require manual interpretation; a raw disassembler does not recover a trustworthy complete call graph.

[ghidra-jieli](https://github.com/kagaimiq/ghidra-jieli) was inspected as a further tooling candidate. Its PI32v2 implementation describes itself as very early stage. Ghidra/Java were not present and were not installed in this pass; the vendor objdump performed the disassembly. Successful decoding does not establish a debugger connection to the running watch.

## Kernel identification

The comparison [SDK ELF](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/cpu/br28/tools/sdk.elf) contains function symbols. Its SHA-256 is `68fabab7824443eeb4cefde26e5a525fde4a66ba43dae99a2929e5eff2447f9f`. Its symbol sizes and section mappings were read offline, and complete function byte sequences were searched in the watch application.

| Reference function | Bytes matched exactly | Linear analysis-image address |
| --- | ---: | --- |
| `OS_EventTO` | 54 | `0x0611F8B0` |
| `OS_EventTaskWait` | 46 | `0x0611F756` |
| `OS_InsertListHead` | 16 | `0x0611F746` |
| `OS_RemoveList` | 18 | `0x0611F6A4` |
| `os_sem_create` | 24 | `0x061201F4` |

**Observed:** these complete sequences match byte for byte. The two short list routines alone would be weak identification evidence; the event routines, semaphore wrapper, clustered addresses and SDK configuration make the combined result substantially stronger. The SDK's [OS type header](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/include_lib/system/os/os_type.h) selects `ucos_ii.h` under `CONFIG_UCOS_ENABLE` and has a separate FreeRTOS configuration.

The reference ELF places these five routines in its SRAM code region (`0x0011....`), not its flash text region. The watch offsets above locate their stored bytes; its RAM-copy layout and runtime function addresses remain to be reconstructed. They must not be used as debugger breakpoints without that reconstruction.

**Inference:** this watch build very likely uses Jieli's uC/OS-II-derived kernel/port. A precise kernel version, complete task list and runtime privileges have not been recovered. This evidence supersedes the earlier absence of any RTOS identification; it does not establish an interactive OS shell or an application installation service.

## Resource image and filesystem

The outer `res.bin` contains `new_res.bin`. Applying the inspected jl-misctools SFC transform with package-derived key material and resource-relative addressing produced a coherent plaintext image. The key remains private and is not reproduced here. Decrypted image: 15,878,656 bytes, SHA-256 `5f1b405ea728c735d885913aef695647824a36ed95e120e8b885dba8384dd2e3`.

The first 16 KiB decode to erased `0xFF` padding. A FAT16-style allocation table begins at `0x4000`; 32-byte root directory records begin at `0x7000`; file cluster data begins at `0x8000`, using 4,096-byte clusters. These offsets were checked against all 13 root entries, their allocation chains, file lengths and bundle headers. Each chain terminates at `0xFFFF` and has exactly the cluster count required by its declared file length. The final resource image omits some unused padding after the last file; all declared file bytes are present.

This is an observed raw layout, not a verified standard mountable FAT volume: no normal BIOS parameter block was found in the examined prefix. The extractor follows the checked allocation table rather than assuming files are contiguous.

| Root file | Bytes | Parsed contents |
| --- | ---: | --- |
| `JL` | 11,094,096 | Main UI: `index.idx`, `JL.sty`, `JL.res`, `JL.str` |
| `SIDEBAR` | 725,008 | Sidebar style, resources, strings and table |
| `WATCH121` | 217,776 | Face style, resources, strings, preview and project metadata |
| `WATCH128` | 326,880 | Same bundle structure |
| `WATCH107` | 105,184 | Same bundle structure |
| `WATCH179` | 384,384 | Same bundle structure |
| `WATCH125` | 123,152 | Same bundle structure |
| `WATCH131` | 385,184 | Same bundle structure |
| `WATCH6` | 23,456 | Same bundle structure |
| `BGP_B131` | 121,042 | Preserved; not accepted as a JLFS bundle by this parser |
| `BGP_C131` | 108,507 | Preserved; format unresolved |
| `FONT` | 2,199,312 | `F_ASCII.PIX`, `F_UNIC_ALL.PIX`, `ascii.res`, index |
| `LOGO` | 6,080 | Index and `logo.view` |

Eleven files parsed as JLFS bundles with bounded subfile offsets. The two background files are not asserted to be corrupt merely because the JLFS parser rejected them. Resource/preview files start with `RU30`; the available `ru2unpack` tool handles an older resource format and was not blindly applied to them. Styles, image encoding, strings and preview rendering remain to be decoded.

The watchface `.json` files inspected are 89-byte project/version metadata, not application source. For example, they contain `prj_uuid` and `version_id`. File extensions alone do not imply JavaScript, a general JSON UI interpreter or executable app loading. No display resolution is claimed from partially decoded preview headers.

## Text reception and the Linux status route

The offline Android GFit Pro 1.4.5 APK contains a concrete notification path:

`NotificationHelper.checkAndHandleNotification` → `WatchBase.pushMessageInfo` → `SyncMessageTask` → `MessageInfo` / `PushInfoDataToDeviceCmd` → RCSP transport.

`WatchBase.pushMessageInfo` checks that RCSP initialization has completed. `SyncMessageTask` includes both command-push and small-file implementations, so the capability-dependent path must be established before selecting a transport.

**Observed in APK bytecode:** `PushInfoDataToDeviceCmd` constructs command ID `161` (`0xA1`). Its message subtype uses type `2`, version `0`, followed by a one-byte message sequence and serialized message information. `MessageInfo` supplies length/type/value records with these type IDs:

| Type ID | Field | Observed constructor limit |
| --- | --- | --- |
| `0` | Packed timestamp | Four bytes, using `time2Int` and big-endian conversion |
| `1` | App/package name | 31 encoded bytes |
| `2` | Notification flag | One byte |
| `3` | Title | 36 encoded bytes |
| `4` | Content | 424 encoded bytes |

These constants come from inspected constructors and serialization code, not guessed packet offsets. `getData` converts strings to bytes and limits their byte length. The timestamp is a calendar-field encoding using a year offset from 2010, **not raw Unix time**. Inspected `packLTVPacket2` and integer helpers use a two-byte big-endian length equal to type-plus-value bytes, followed by the type and value. Complete timestamp packing, frame construction, fragmentation and authentication behavior still need validated reproduction before a live packet. The table is not a ready-to-send command.

**Observed in firmware disassembly:** a dispatcher at `0x060262E0` compares its command value with `161`. The branch leads to the region at `0x060269EA`, which references the string `smartbox_data_function_set`, reads a subtype while advancing past two envelope bytes, and dispatches through a subtype-indexed callback table. This agrees with the app's type/version envelope. The type-2 callback and complete message storage/rendering chain are not yet fully mapped.

Other mapped code references include the ANCS message-add diagnostic at `0x06022A74`, the RCSP event-buffer diagnostic at `0x0601806C`, and watch-card file access at `0x0602D716`. The image also contains Apple ANCS service/application strings and watch background-management functions. These support existing notification and resource paths; individual strings can survive from shared libraries and are not sufficient proof that every feature is enabled.

**Practical implication:** a custom Linux bridge can target the existing notification display path for agent status, with firmware replacement as a separate research branch. The actual watch must still be tested for RCSP initialization, authentication and supported message mode. AE00/AE01/AE02 UUIDs and an old notification sample alone do not establish the whole transport protocol. No speculative write was performed.

## What this means for modification

1. **Computer information:** first reproduce the SDK's initialization and one explained synthetic text notification, after offline frame validation. This is the shortest evidenced route to status on the current UI.
2. **Custom screens:** decode RU30/style resources and trace supported face/background transfer. Extractable bundles establish content access, not automatic compatibility with a newly constructed bundle.
3. **Native firmware changes:** use the PI32v2/r3 and BR28 board evidence to identify compatible SDK components. Reproducing `board_7012AF_J1` peripheral configuration, image integrity/update behavior and recovery remains necessary before considering a flash experiment.

The build provides real code and UI access for offline reverse engineering. It does not yet provide a running-device debugger, terminal, source reconstruction, arbitrary app loader or demonstrated safe custom firmware. Private analysis files and hashes are retained under ignored captures; only these public-safe findings are published.
