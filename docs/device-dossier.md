# Device dossier — Mero Watch artifact

**Record created:** 2026-10-12  
**Physical condition:** working and operational as of 2026-10-12, per owner.  
**Classification:** unidentified Apple Watch Ultra-styled **clone**, not an authenticated Apple Watch.

## Evidence ledger

| Evidence | Value | Classification | Provenance / caution |
| --- | --- | --- | --- |
| Rescued device | Discarded-electronics find | Owner-reported | Historical conversation, 2025-12-09 |
| Model marking | `A2859` | Observed/reported marking | May be copied/spoofed; not hardware identity |
| Firmware/software version | `v1001` | Reported marking | Need exact screen/photo and software build |
| Companion app | `GFit Pro` | Owner-reported functional app | Prior pairing established |
| Bluetooth name | `Apple Watch` | Previously observed | Cosmetic advertised name only |
| BLE address | `F9:F3:71:D9:79:11` | Previously observed | Session-dependent; public identifier, handle carefully |
| Service | `AE00` | Observed by LightBlue | Shortened 16-bit UUID display; canonical 128-bit encoding still to verify |
| GATT write characteristic | `AE01`, write-without-response | Observed by LightBlue | Do **not** send speculative bytes |
| GATT notify characteristic | `AE02`, notify | Observed by LightBlue | Was seen delivering data |
| Example BLE payload | `FEDCBA80FF0000A65FF61000000000641137EF` | Historical captured notification | Encoding, framing, CRC and semantics **unknown** |
| Additional labels | IMEI, CMIT, GB/T, MAC | Owner-reported from box/info | Actual numbers not archived; regulatory claims not verified |
| Computer | ArchMerOS/Arch Linux | Owner's lab | Earlier Bleak experiment on Linux |
| Current computer Bluetooth | TP-Link UB5A `2357:0604` (available) | From broader lab records | **Not yet verified with the watch** |
| Prior Linux blocker | `hci0 removed`; adapter/controller reset; Bleak timeout | Historical observed error | The underlying cause is unconfirmed |

## Identification hypotheses — NOT established facts

- **T800/T900 family:** possible marketing/product family based on appearance, but no board, SoC, retail listing, Bluetooth manufacturer data or update image yet identifies it.
- **Jieli AC695X:** earlier candidate chipset, unsubstantiated.
- **Realtek RTL8762C:** earlier candidate chipset, unsubstantiated.
- **Operating system:** unknown. Might be vendor RTOS / bare-metal firmware. There is **no evidence of a Linux shell**.
- **Firmware installability:** unknown. A vendor OTA implementation does not imply unrestricted code execution or unlockability.
- **BLE audio/voice:** unknown; classic Bluetooth audio profiles and BLE command channels might be separate, and a microphone is not necessarily accessible through GATT.

The marking `A2859` and advertised name `Apple Watch` must **not** be used to select Apple firmware or Apple procedures.

## Open questions

1. Physical board markings, SoC/package identifiers, flash part, power circuitry?
2. Which BLE address(es), address type, appearance and manufacturer/service data are advertised now?
3. Exact complete GATT service/characteristic UUIDs, properties and permissions?
4. Is `AE02` a streaming notification channel? Does it only emit after app authentication/init commands?
5. What is the packet framing (start bytes `FE DC BA 80`?), payload length, checksum and message type?
6. How is the watch paired? Does its app use BLE only or also Bluetooth Classic?
7. Is the firmware available from the companion app or vendor endpoints? What is its archive/container format?
8. Are there UART/SWD/test pads and an independently readable external SPI flash?
9. What is the minimum functioning wrist-agent interface (notifications / buttons / watch-to-PC controls), even if code execution is impossible?

## Preservation and handling

- **Record before changing:** all screens and firmware fields; hardware photos; working app connection; adapter and phone versions.
- **Prefer observation:** advertise/scan → service enumeration → notify subscription → traffic capture → packet correlation.
- **Keep mobile app state reproducible.** Disconnect app before independent host connections if the watch allows only one central.
- **No blind protocol writes** and **no speculative OTA**. Investigate update data offline first.
- **No disassembly** until photographs and a recoverability assessment are documented.
- Device identity and captures can contain sensitive identifiers. Avoid committing IMEIs, unredacted personal notifications, pairing keys and full private BLE traces into this **public** repository.

## Physical inventory to collect next

Photos of front/rear, strap removed if safe, packaging labels, setup/about/version screens; charger type; display resolution only if measured; case dimensions only if measured; phone app version; output of `lsusb`, `bluetoothctl list`, scanner advertisement and GATT enumeration. None of these new data has been collected yet in this repo.
