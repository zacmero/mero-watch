# Custom screen investigation — 2026-10-13

## Verified screen and connection data

The authenticated informational `GetExternalFlashMsgCmd` (opcode 214 / D6, no command parameters) returned 28 bytes. Opcode and response layout were traced in the exact GFit Pro 1.4.5 Android APK. Its `ExternalFlashMsgResponse.parse` uses Java ByteBuffer's default big-endian fields. No file creation, transfer, deletion, activation, or firmware command occurred.

SDK-decoded device reports:

| Field | Value |
| --- | --- |
| Screen width / height | 240 / 296 pixels |
| External flash size | 16,777,216 bytes (16 MiB) |
| FAT size | 16,777,216 bytes |
| System / system status | 1 / 0; semantics not established |
| Watch version code | 0 |
| Block size / cluster | 256 / 16; units not independently verified |
| Match version string | `W002` |
| External-flash receive MTU | 256 |

These are protocol reports, not physical chip measurements. This receive MTU belongs to the external-flash response; the earlier general RCSP capability MTUs were 272/540.

Before this query, BlueZ Device1 said Connected=true while MediaControl1 said Connected=false and no watch input device was present. Standard Connect returned success without restoring media. Explicit connection of the watch's advertised HID (1124), A2DP sink (110B), and AVRCP (110E) profiles succeeded. MediaControl1 became true and `Apple Watch (AVRCP)` reappeared as input event15. No experimental daemon override or bond deletion was used in this repair.

After repair, a `Mero link test` text received the same transport status 0 / application parameters [2,1], with MediaControl still true afterward. **Owner-reported:** Bluetooth icon lit, message present, no popup or vibration. Thus missing media connectivity alone does not explain that test's display behavior. The prior Codex message is also now owner-confirmed in Messages; lack of vibration on that earlier delivery was uncertain.

## Available routes

1. **Custom face/background:** GFit's actual WatchManager calls `enableCustomWatchBg` and maintains a custom background FAT path. The official SDK example retrieves actual screen dimensions from external-flash metadata, chooses chip-specific BMP conversion, transfers the file, then activates it. This establishes an app-side route to investigate, not successful custom-image installation on this watch. A bitmap is not a programmable agent dashboard; repeatedly overwriting flash to imitate a live screen is not the proposed design. See [official CustomDialManager source](https://github.com/Jieli-Tech/Android-JL_Health/blob/main/code/app/HealthAide_V1.1.0_SDK_V1.14.0/app/src/main/java/com/jieli/healthaide/tool/customdial/CustomDialManager.java).
2. **Resource modification:** The downloaded build contains separately extractable main UI and face bundles with `.sty`, `.view`, `.res`, `.str` and `.json` files. RU30 resource encoding remains unsupported by the old RU2 parser. The small face JSON files are project metadata, not demonstrated executable applications. A faithful offline decode/re-encode is needed before proposing any replacement resource.
3. **Native custom UI:** A persistent agent screen, new navigation and custom touch commands likely require native application changes unless further evidence reveals a suitable programmable resource interface. Preserve the original board/display/Bluetooth implementation where possible. Exact LCD/touch drivers, RAM/overlay mapping, update validation and recovery remain unresolved. Related custom Jieli badge firmware targets AC707N/BR35, whereas this build indicates AC701/BR28; badge binaries are not compatible firmware evidence for this device. See the [badge project's documented hardware and custom GUI](https://github.com/ElectronicCats/jieli-ble-badge-research).

The mirrored APK's architecture split contains `lib/arm64-v8a/libjl_bmp_convert.so`; the public Java converter API alone does not supply a demonstrated native Linux encoder. The [SDK FAQ](https://doc.zh-jieli.com/Apps/Android/health/en-us/master/Other/question_answer.html) documents custom-background failures including device freezes, so format/dimensions must be verified before a transfer experiment.

## Proposed next work

The [240 × 296 screen concept](mockups/agent-screen.svg) is an offline design, not installed or interactive watch software. The intended native panel shows agent state and computer connectivity, with Agents / Host / Actions navigation. Buttons are proposed capabilities, not demonstrated ones.

First reproduce a stock face's resource format offline and verify a round trip without changing its decoded contents. Then prepare one compatible custom face file, with its exact destination, size and restoration plan for owner review before any transfer. A static face tests appearance and resource compatibility; a live dashboard needs an established RAM-backed update/render path. In parallel, resolve native UI entry points and board/memory layout before constructing a modified application. Firmware installation still requires a verified recovery plan and explicit approval.


## 2026-10-13 — Custom background codec and real resource candidate

BGP_B131/BGP_C131 now positively identified and decoded as single-image RU30 resources. Both stock images decode completely to 240x296. Pixel-preserving re-encoding verified; compression bytes differ. Inspected GFit ARM64 converter exports br28_png_to_res; bounded offline emulation reproduces its wrapped resource output. Public narrow Python codec, independently emulated converter oracle and 13 passing tests added. Native-generated own-artwork candidate assets/mero-screen-test.res is 27,993 bytes, SHA256 e5159492a76ffeea541c3c583860b3b1c920e0d6ad9e9ec62861b03c718e89e6. Native/Python comparison matches three small fixtures exactly; full candidate compression grouping differs but pixels agree. Candidate uses native output. See docs/ru30-background-format.md.

Owner rechecked GFit Pro and successfully selected/uploaded an owner photo, correcting the earlier tentative vendor-only recollection. Our PNG was served through a LAN-only directory containing generated artwork, with a ten-minute server/firewall expiry. Phone HTTP retrieval was observed; display confirmation pending. No resource, activation, OTA or firmware command was sent by the computer. The background is a static appearance test; live status and touch/menu replacement remain separate native-UI work.
