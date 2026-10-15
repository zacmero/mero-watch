# Native system-spec clues — 2026-10-14

The first mero-shell is a custom diagnostic UI/command console. A POSIX shell,
Linux kernel, process model or executable-app installer has not been observed.

## Traced live allocator statistics

Observed stock app SHA-256:
`9117eea8ff2f1694a16d57f16850100692c2ff8bfc3b66bfd8ede9c76c0e5ae4`.
Its routine at `0x060c66f0` logs current free heap, minimum-ever free heap and
"physics memory size". The instruction sequence reads:

| Value | Read |
|---|---|
| Current free heap | 32-bit RAM word `0x0010b300` |
| Minimum-ever free heap | 32-bit RAM word `0x0010b2fc` |
| Allocator region bytes | `(u16[0x0010f38e] - u16[0x0010f38c]) << 7` |

These addresses fall within the startup-observed BSS mapping. The native
`mero_specs.c` readout copies those values without changing device counters.
It rejects reversed/empty bounds and a minimum above current free bytes. Heap
and physical-region counters are logged separately, so no assumed cross-bound
is imposed between them. No on-watch readout has been tested yet.
The region size must not be presented as total physical chip RAM.

## Other firmware clues under analysis

* `version_id` string used by `0x06025578`; its query ABI remains unverified.
* UI-library version and version-string diagnostics exist, but their bindings
  and relationship to the device's displayed firmware version are not proved.
* External-flash initialization `0x06006af8` prints an ID. It also writes GPIO
  and peripheral registers, so do not invoke it merely to read specs. Find a
  cached descriptor/pure getter instead.
* Flash-capacity/read-ID diagnostics and clock-frequency diagnostics exist.
  Strings alone do not identify a callable, read-only API or prove a capacity.
* `ui_sysinfo` is read through VM record 197 and a 248-byte configuration record.
  Its name does not mean it contains CPU/RAM/flash specs.
* `imb_task info dump` concerns image-rendering work, not necessarily RTOS tasks.

## Known build architecture versus measured device specs

Startup-observed segments: 18,972 bytes initialized data, 83,712 bytes BSS and
37,580 bytes copied RAM code. These are linked segment sizes, not total chip
memory. PI32v2/r3 instruction/toolchain compatibility is established; an exact
physical SoC identity remains unauthenticated. Exact kernel-helper matches
support a Jieli uC/OS-II-derived RTOS inference, with version unproved.

The diagnostic screen should distinguish these build observations from live
allocator measurements. New native screen/entry launch is still being built.
