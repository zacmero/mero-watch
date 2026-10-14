# Main-menu launch investigation — 2026-10-14

## Correction to the first probe

Owner-reported: Music works as a phone playback controller, with no accessible
lyrics/text screen. No visible change was reported after the native probe. Its
hidden lyric layout was therefore a poor verification target. Successful OTA
programming does not prove execution of our C code. Do not repeat that test.

## Observed stock binary path

All addresses below refer to the exact stock app SHA-256 checked by
`scripts/native_menu_inventory.py`; the app file maps at `0x06000120`.

* Dispatcher `0x0603e320` reads the selected grid child ID. Its search loop at
  `0x0603e3ac`–`0x0603e3d0` checks 37 records with a 32-byte stride.
* Table starts at `0x0609a990`. The three control-ID columns correlate with JL
  style windows 7, 3 and 118. Their grid IDs are `0x000e1400`, `0x00061400`
  and `0x00ec1400`, respectively.
* Each record contains three menu layout IDs, two observed zero words, a
  target window ID, an optional callback and the menu ordinal. The callback
  receives a pointer to the target-window value on the stack and can prevent
  the subsequent launch if it returns zero.
* `0x0603e3de` loads the target; `0x0603e3e6` loads the optional callback;
  `0x0603e3f4` calls it indirectly. The post-callback path passes the target
  to `0x060006ba`, then `0x0602f2e4` and `0x0602e384`. These are observed
  call targets; their full names and semantics are not yet established.
* Grid touch callback `0x0603e80e` reaches the dispatcher at `0x0603e836`.
  Both windows 3 and 7 register that touch callback, key callback
  `0x0603e83c` and change callback `0x0603eab0`. Window 118 instead registers
  touch `0x0603e432`, key `0x0603e5d0`, change `0x0603e656`.
* For example, entry 10 targets Music window ID `0x0014080a`, whose change
  callback is `0x0603f15c`. This correlates the menu table with the previously
  traced screen; it does not validate the lyric probe.

Menu label controls in the inspected styles have source `none`, code `strpic`
and a referenced string-image list. Window 3's first text control
`0x00063000` has list count 1 and resource index 5. Its adjacent picture control
has an empty serialized image list, so its actual displayed icon requires
tracing runtime assignment. Do not assume that copying that empty list copies
the visible logo.

Native apps here are linked code plus serialized controls, image/string
resources and registered event callbacks. The observed menu does not launch a
standalone executable file. A duplicate menu row alone is not a new app: it
would still launch the original target and could conflict with fixed counts.

## Next bounded proof

Use an existing, reachable menu entry and retain its launch path. Trace its
visible label/icon resource assignment and its visible screen initialization.
Then change a small visible asset or widget in that exact path, with an offline
preview and byte-range verification before spending another OTA cycle.
Replacing a resource proves resource control; showing investigator-authored
content through a traced callback proves native code execution. Record these
as separate milestones. Only after that should we duplicate the app's control
tree/registration and introduce a distinct Mero entry.

No new package has been flashed during this investigation. Whole menu cloning,
new resource IDs and additional code capacity remain untested.

## Visible menu resource experiment prepared

Decoded all 37 images in window 3's menu image table. Every image descriptor
and payload CRC passed. Resource 22 is visibly a calculator icon. Windows 3,
7 and 118 each reference its same 50×50 payload at JL.res offset 213454,
length 2658; their descriptor offsets are 158820, 377948 and 5848101.
This identifies the displayed resource, not yet the calculator's code-window ID.

`scripts/native_menu_logo.py` creates an investigator-authored cyan circle with
a white M. Its encoded payload uses 1254 bytes of the original 2658-byte extent;
the remainder is zero padding outside the referenced row data. Row decode
roundtrips pass; only that payload and the three descriptor CRC pairs change.
Dimensions, IDs, offsets and resource size remain identical.

`scripts/native_menu_package.py` rebuilds this resource experiment starting from
the protected original firmware. It verifies the original encrypted-resource
roundtrip, the JL allocation chain and original bundle hashes, repairs the JL.res
leaf and JL parent CRCs, scatters the same-size bundle back into its original
clusters, encrypts resources, and repairs inner-resource and UFW CRCs. Both stock
code banks and every other outer payload remain byte-identical. Thus it also
removes the earlier hidden Music probe when installed; it adds no new C code.

Prepared private package SHA-256:
`6741c87b7dfe98d7724b3b59b39af2fdbed3ab72537f2b827ba77e14a4a01bf1`.
Size remains 18,760,384 bytes. This is an installable offline-validated candidate,
not a confirmed on-watch result. Seeing the changed Calculator icon would prove
control of a visible native menu asset. It would not prove a new app or execution
of investigator-authored C.
