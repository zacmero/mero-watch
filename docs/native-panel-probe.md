# First native C UI probe — 2026-10-14

## Scope and current status

The owner resumed the approved mission and reports the watch fully charged. The first bounded execution test temporarily uses the Music screen's text area. It is not the finished agent application, counter, or custom UI mode. Media touch handlers, settings, the Bluetooth stack, loader, and resource files are preserved. The probe temporarily substitutes a lyric-text path and one initialization diagnostic call; normal lyric behavior is not preserved in that path during this experiment.

**Observed offline:** The candidate builds and validates in both application images. Device execution and visible output are untested at this checkpoint. No new device firmware transfer has started yet.

## Control and handler mapping

The read-only `scripts/native_control_tree.py` traverses all nine stock styles, 131 windows and 3,074 controls. Child records are contiguous siblings; nested child groups are reached through tagged pointers rather than a contiguous preorder walk. Bounds, repeated/cyclic nodes, overlapping records, relocation presence, and style CRCs are checked. Type names correlate with the pinned SDK; device record lengths remain authoritative. Across all nine styles, the graph contains 871 text controls and 664 picture controls, alongside the other control types.

Five source-correlated `ui_style_info` triples at application file offsets 1,133,116 through 1,133,175 reference the name `JL` and the same handler span `0x06114b98`–`0x06117728`. The span holds 697 16-byte records shaped as ID, touch, key, and change callback pointers. Every non-null callback points into an inspected flash-code or copied-RAM-code range. 634 candidate records match IDs in the parsed main control graph. Two IDs have duplicate entries (`0x04000800`, `0x00381400`); their runtime selection behavior is not proven, and neither is treated as unused code space.

Additional complete instruction matches from optimized reference UI IR are `get_rect_cover` (124 bytes, `0x0610e684`), `in_rect` (40 bytes, `0x0600d7de`), and `get_element_by_id` (36 bytes, `0x0600de38`). The native wrapper at `0x0600de5c` calls the matched tree walker with root `0x0010ce28`; its missing-element diagnostic independently identifies its purpose. These are analysis observations, not a running-device debugger result.

The Music window is native window 10. Its registration and callback refer to `music_mode_onchange`, `music_mode_release`, and `show_lyric` diagnostics. Text control ID `0x00143002` exists in that window. Native text paths store attributes at widget offset 112, rather than the reference SDK's offset 72. Reference widget structures must not be copied blindly.

## Probe bindings and bounded patch

Application file SHA-256 is `9117eea8ff2f1694a16d57f16850100692c2ff8bfc3b66bfd8ede9c76c0e5ae4`. Its file-offset-to-flash mapping begins at `0x06000120`; the broader flash image base is distinct. The patch builder accepts only that exact original application and the inspected compiled code hash.

| Binding | Address | Evidence |
| --- | --- | --- |
| Element lookup wrapper | `0x0600de5c` | Calls exact matched tree walker; native root and diagnostic traced |
| Text setter | `0x0603aeac` | Actual Music caller and five-argument register/stack path; stores format, text, length, cursor and mode |
| Redraw | `0x0600e8ea` | Both actual Music text paths invoke it after the visibility-bit check |
| Text format literal | `0x0608451f` | Original application contains `text\0` at the resolved address |
| Marker literal | `0x06084ed4` | Original `Apple Watch` literal becomes equal-length `mero-watch\0` |

Investigator-authored [C source](../native/mero_panel_probe.c) and [linker bindings](../native/mero_panel_probe.ld) compile to exactly 58 bytes with the inspected PI32v2/r3 toolchain. The probe looks up the Music text widget, returns safely if absent, sets a ten-byte marker through the actual setter, and redraws if visible. Mode 2 follows an observed native setter caller; its full text-encoding semantics are not claimed. The marker is ASCII and its appearance must be checked on the watch.

The code occupies the complete 58-byte original routine at `0x0603f01a`–`0x0603f054`. Original routine SHA-256 is `8150090421d37d82c3a06f038aa6666a2119ecbc3ccf6608e837c3e98d0894d6`. Its two observed direct callers ignore the returned value. The adjacent function is unchanged.

At `0x0603f178`, replace only the six-byte Music initialization diagnostic call with a six-byte relative call to the probe. The original call bytes are `80ff0e5f0800`; the existing saved-register frame remains in place. The marker literal is the third and final application patch range. No arbitrary code cave, duplicate handler entry, or guessed RAM allocation is used.

Compiled code SHA-256: `dda5c95217e10d0a1d281c2c15e41a5b3afeb92dcb0613fc0780614edc8a61ea`. Candidate UFW SHA-256: `7fb622c7bd5ca1fa23f9547f445751e0ddd00b467cfc9eb895a3d598c67b8040`; 18,760,384 bytes; 164 stored bytes differ from stock. Both application images contain only the specified application changes, all checked CRC layers validate, package size is unchanged, and every non-code outer payload remains byte-identical.

## Hardware success criteria

After the established two-stage Linux update, confirm normal boot and reconnect the data and media links. Open Music and look for the marker in its text area. A visible marker produced through this traced hook establishes execution of our newly compiled native code. Lack of a marker does not by itself establish failed installation: widget creation timing, selected Music mode, and text rendering still require observation. Check playback controls and basic settings independently. Then move toward a separate native panel, an observable custom action, and live agent data; this probe does not claim those capabilities.

The protected stock package remains the restore source while the loader is reachable. This experiment does not prove arbitrary custom-code compatibility or hardware recovery from every failure. Private firmware, IR, disassembly and build artifacts remain outside public Git history.

### Target visibility finding during transfer

**Observed offline:** The target text widget is a descendant of lyric layout0x00140c02. Its serialized CSS invisible byte is1 at startup; the text widget itself has invisible byte0. The text rectangle is (834,1690,8334,1014) in the native serialized coordinate units. Thus the post-boot test must include the Music lyric/text view; absence on the main playback screen is inconclusive. This candidate does not change the original layout visibility or geometry.

### Application growth boundary

**Observed offline:** In the first code bank, app.bin starts at file offset37,152 and has1,200,992 bytes; its end1,238,144 equals cfg_tool.bin data offset. There is no gap between these declared file payloads. The bank contains later tone, UI upgrade, P11, configuration and EQ payloads, plus virtual VM/BTIF/EXIF entries. File sizes/positions alone do not establish spare executable capacity. Larger code would require deliberately rebuilding the application/container layout and validating preserved content, addressing and physical update bounds; this probe does not do that.

### Deployment started

At UTC21:50:41, the authenticated normal-address eligibility check accepted this candidate. The passive observer was ready at21:51:21; primary Linux transfer began at21:51:26 and announced15,878,656 resource bytes. Runtime experimental BlueZ host configuration was restored after an UnknownMethod failure caused by its absent temporary override. The owner-reported full charge and prior firmware-experiment authorization apply. Device programming, normal boot and visible native execution remain pending.
