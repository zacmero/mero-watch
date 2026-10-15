# Separate native mero-shell — 2026-10-15

Status: first device installation rejected at the end of pass two with E6 `04`.
The pinned reference calls this "bad update file"; exact rejected field is not
yet identified. Native code execution and the new screen are NOT proved.

## Candidate and provenance

Built exclusively from the protected PID76 1.0.0.4 original, not the prior Music
probe or Calculator icon package. Private candidate is 18,813,120 bytes, SHA256
`850a2fc80ae17972b09af770d13ad2c4f15a76dcbad8ba9d31615838fced13b4`.
Own PI32v2/r3 code is 704 bytes, SHA256
`0360a6e4299828169d2e3fcc5a429e8b0537d46ecd503cb7c2dad68a50e4f8cb`.
Vendor firmware and key material remain private and ignored by Git.

## Independent launcher and window

JL.sty has 119 original windows; 131 was the total across all nine bundles.
The new window is page119, bringing JL to120. Three observed menu variants
(pages3,7,118) retain their original control IDs and fixed grids. A separate
footer occupies the bottom15% of their viewport, with its own M icon and Mero
caption. Factory Calculator resources and handlers are restored from stock.
The fixed37-entry factory app dispatch table is unchanged.

Seven new text widgets show mero-shell, free heap, low heap, physical pool,
PI32v2/r3 architecture, Refresh and Back. These are a diagnostic console, not
a POSIX shell. Refresh reads the counters documented in
[system-spec clues](native-system-specs.md); Back uses the existing menu path.
No CPU frequency or total physical RAM is inferred from the heap values.

Each text widget allocates its own68-byte state at its native INIT callback,
after attributes exist. RELEASE clears the attribute pointer and frees only
its owned state. No factory widget structure is copied from an unrelated SDK.
Touch-up7 invokes commands; other touch events do not.

## Code and callback storage

Appended module starts at mapped address `0x0613d6dc` in both bank layouts.
It follows the last existing root file (`eq_cfg_hw.bin`) as a new JLFS leaf
`mero_shell.bin`. Its payload contains code, alignment and a callback table.
The complete697 original16-byte records remain in original order, followed
by13 own records. Native record order is ID, touch, key, change. Five existing
JL style descriptors point to this merged table; their names are unchanged.
All other original app bytes, functions and callback records are retained.

The original last file loses only its terminal marker and gets a new header
CRC; its payload stays exact. Existing file offsets and VM/BTIF/EXIF partition
descriptors remain unchanged. Appended bytes must fit declared PRCT capacity.
Opaque final eight bank bytes are preserved. Execution/read mapping of this
appended region is the remaining device experiment, not an offline proof.

## Resource preservation

JL directory grows by one window. New M bitmap is resource39; page118 already
has resource38, which is retained. Every original bitmap payload is unchanged.
New page aliases the existing About resource context. ASCII font behavior on
the new page still requires device observation; the STR dictionary is unchanged.

The JL bundle is rebuilt with validated absolute JLFS child offsets. The FAT
keeps all original JL clusters and extends the chain using free clusters only.
All12 other root files keep their chains and payloads. Resource plaintext grows
to15,908,864 bytes, below the device-reported16,777,216-byte capacity. This is a
reported capacity, not a physical flash measurement.

## Validation and launch

All38 host tests pass, including callback-field order, original-record retention,
allocation/release/refresh/navigation behavior and rejection of nonstock input.
Independent candidate decrypt validates120 control trees and1,925 image records,
plus inner/outer CRCs. Both stock recovery copies match the original SHA256 and
remain0400. Factory application changes are limited to style table pointers.

The direct OTA observer was ready at2026-10-15 00:23:29 UTC before primary start.
Private journals: `native-shell-transfer-events.jsonl` and
`native-shell-handoff-events.jsonl` under ignored captures/firmware-work.
Completion, boot and owner observations will be appended rather than assumed.

## First attempt rejected — 00:54 UTC

Pass one returned E6 `80` at00:52:24,4005 served blocks/15,969,695 response bytes.
Loader relink and mandatory-mode check succeeded. Pass two announced1,312,768
bytes and returned E6 `04` at00:54:39 after344 blocks/1,319,264 response bytes.
No E7 reboot was sent. Owner reports the Chinese waiting-for-connection screen;
host reconnected and positively confirmed mandatory-loader mode.

Offline CRC/decrypt checks did not establish updater acceptance of bank growth
or the extra root JLFS file. Those layout changes are suspects, not an identified
cause. Candidate removed from updater allowlist to prevent accidental reuse.
At00:56:19 Linux started E3-only recovery using the protected original package;
E1/E2 are deliberately skipped in confirmed mandatory-loader mode. Recovery
result and normal boot remain pending. Previously transferred resource changes
may remain: loader-only stock code recovery is not a full resource rollback.

### Recovery and first concrete format defect

Stock-code recovery returned E6 `00` at00:59:22 UTC; E7 acknowledged00000000.
Owner normal-boot confirmation remains pending. Recovery reused the existing
LE connection after redundant ConnectDevice calls failed despite Connected=yes.

Post-failure comparison found an actual builder defect: all observed root SFC
entries encode data offset32, but the new leaf encoded0. The backend parser
hardcodes header+32, so its successful decrypt/CRC check failed to catch this
incorrect serialized field. Corrected builder to32 and added an explicit
contract check. This is a plausible explanation of E6 `04`, not proof of the
loader's precise failing branch; no corrected package has been installed yet.
