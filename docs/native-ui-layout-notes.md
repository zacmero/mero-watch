# Native face layout investigation — 2026-10-13

The owned watch has displayed our custom picture with its vendor clock overlay. This establishes background replacement, not a replacement clock/menu implementation. Owner also observed a temporary factory-background fallback before the custom picture returned; cause remains unresolved.

## Observed artifact anchors

- `watch6.view` decodes as a static 151 × 180 analog-face preview; `watch131.view` as a static 146 × 184 digital-face preview. Both use the same alpha/RGB565 RU30 image variant supported by the new codec and pass header/payload CRC checks. They are preview bitmaps in these inspected files, not executable layouts.
- `watch131.json` has compatibility `version_id: W002`, matching the actual device's external-flash response. Its project UUID is metadata, not executable code or authenticated hardware identity.
- `watch131.sty` is 760 bytes. ASCII `date` is at byte 276; `week0` at byte 376. The 16 bytes immediately preceding each resemble native UI control headers: `[10,0,1,100,0,255,255,255,1,40,0,4,192,1,0,4]` and `[8,0,1,52,0,255,255,255,0,32,0,4,112,1,0,4]` respectively. Exact field interpretation remains unverified.

## Reference source and limits

The pinned reference AC701 SDK defines separate clock, number, text, picture and layout controls, with element/control event handlers. Its UI time/number/text structures contain short source labels and control headers, making the stock `.sty` strings useful anchors for further parsing. See [control.h](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/include_lib/system/ui/ui/control.h), [ui_core.h](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/include_lib/system/ui/ui/ui_core.h), and [layout.h](https://github.com/UWINGS-KUNYI/ac701n_soundbox/blob/f8eeea1ebecacb84d20f04515773528ad5616c1a/sdk/include_lib/system/ui/ui/layout.h).

**Hypothesized:** The string-bearing records bind native date/week displays. The header similarity is useful evidence, but this reference SDK does not establish the clone's exact serialized ABI. Candidate CSS-pointer interpretations did not produce an obvious matching CSS structure. Simple CRC16/CRC32 guesses for the style header also did not validate. Do not patch a presumed invisibility bit, pointer or checksum based on these guesses.

## Next boundary

Identify the actual style loader and control-record traversal in the downloaded native application, validate lengths/relocations against multiple stock faces, and resolve how IDs bind native handlers. Then construct and independently parse a modified face bundle that removes the stock clock and adds the desired presentation. Touch/agent commands and live data need demonstrated native callbacks and a runtime update route. No `.sty` modification, face-bundle transfer or firmware patch has been attempted.

The direct Linux transfer branch is separate: the SDK has FatFsWatch/RcspWatch implementations, a TransferTask and explicit custom-background activation builders. Destination selection, transaction completion and restoration still need verification before computer-originated resource writes.


## 2026-10-13 — native loader and runtime follow-up

Full dated architecture record: [native architecture](native-architecture.md). It covers the source-correlated screen loader, exact UI helper matches and all 131 stock window directory/table CRC checks. Stock data CRC interpretation remains unresolved for 130 windows; no modified layout was uploaded.

## 2026-10-14 — native style CRC interpretation resolved

**Observed offline:** Re-running scripts/native_style_inventory.py across all nine stock .sty files under the private resource-bundles directory validates all 131 window-header CRCs, all 131 relocation-table CRCs, and all 131 window-data CRCs when each relocation word is masked to its lower 17 bits for the CRC calculation. Original tagged bytes are preserved; the inventory does not write files. All non-null normalized targets fall inside their window. This supersedes the earlier unresolved 130/131 raw-data CRC mismatch, without replacing that historical observation. Pointer tags and normalized-target validity are now reported explicitly. The tagged-pointer test also checks that corruption of a lower pointer bit invalidates the normalized CRC.

This resolves a data-integrity interpretation gap, not the full native control ABI, resource writer, event ownership, or custom application execution. Reference SDK pointer/page decoding differences remain to be reconciled.
