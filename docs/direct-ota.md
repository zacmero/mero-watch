# Direct computer OTA — installation test

## Scope and status (2026-10-14)

The owner selected the custom Linux BLE updater as the primary deployment route.
The current modified-firmware transfer is active. Full installation, normal
boot and marker visibility are not yet confirmed. This is an authorized hardware
experiment, not a general-purpose production flasher.

Selected package SHA-256:
`a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7`.
Both application images contain the equal-length branding modification. The
bootloader, keys, configuration and resource payload are preserved. Originals,
modified binaries, auth helper, raw traces and event journal stay private.

## Observed connection and protocol

Normal address: `F9:F3:71:D9:79:11`. Alternate updater address, confirmed by owner
photos and host advertisements: `F9:F3:71:D9:79:12`.

The updater advertises the observed manufacturer payload prefix `41544f4c4a`
(`ATOLJ`, reversed JLOTA) and a reference to the original address. HCI confirms
connectable/scannable legacy LE advertisements with **public** address type.
The nearby RSSI was approximately −58 dBm.

Generic BlueZ Connect incorrectly attempted Classic paging to the updater,
which timed out. Enabling the daemon's experimental APIs exposed
Adapter1.ConnectDevice; an explicit AddressType=public call established **LE**.
Confirmed services: GAP1800 and AE00. Existing normal-address pairing keys were
preserved. A runtime systemd override currently enables the API; it must be
tracked/removed when no longer required. The initial wrapper's introspection
expected an empty reply despite the daemon returning an object path; the direct
tool uses a raw D-Bus message to handle the real reply.

Authenticated AE01/AE02 RCSP is responsive at both addresses. Auth secrets and
GetTargetInfo's potentially sensitive fields are neither printed nor committed.

| Operation | Observed or source-backed behavior |
| --- | --- |
| E1 file-info request | Updater `…:12` returned offset64/length66; normal `…:11` returned 0/0 |
| E2 eligibility | Modified file's updater mark was accepted (00); normal disabled-mark path accepted the SDK's single zero byte |
| E3 update entry | Updater acknowledgement contained four zero bytes; status is its first byte, not its payload length |
| E5 device-driven file pulls | Active normal-address transfer requests ranges; host returns exact bytes from immutable selected file |
| E8 content size | Active stage announced 15,878,656 bytes, matching the resource payload size |
| E6 final result | Not yet received for the active transfer |
| E7 reboot | Only sent after updater result success; boot must still be independently checked |

The initial host E3 handler wrongly required one result byte and stopped before
serving data; this was corrected to the reference's first-byte status rule.
Its interrupted resume disconnected. Address `…:11` returned, but the owner
still saw the file-transfer UI: address format alone was not boot proof.
The corrected normal-address transfer now serves E5 data and the owner confirms
visible progress. Do not confuse the earlier spinner with this confirmed progress.

## Conditional second stage

The pinned [reference RCSP updater](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/d1204a478e2a80a5c9fbce85eaca264e7b2cc468/tools/qix-ble/qix_ble/rcsp_ota.py)
defines E6=80 as loader-staged, requiring a second stage. Its sequence is:

1. Send 0B payload `00 01` on the **still-open authenticated connection**.
2. Wait for the peripheral to disconnect itself; do not force host disconnect.
3. Reconnect explicitly over LE to the loader.
4. Confirm target-info TLV type9 says mandatory-loader mode.
5. Send **E3 only** and serve file pulls. Do not repeat E1/E2 during this stage.
6. Check E6, and request E7 only on success.

An observation-only second notification subscriber is active to preserve the
open link if the main process reaches result80. It does not answer the primary
process's file requests or reset authentication. It performs the conditional
sequence only if result80 arrives. This handoff is reference-backed and prepared;
it is not yet observed as completed on this watch.

## Tools and logs

`scripts/watch_ota.py` defaults to eligibility-only. `--flash` is explicit and
only the two previously validated stock/modified hashes are accepted. File
ranges are bounded, replies are fragmented to the negotiated ATT limit, and
unknown device commands are ignored. `--resume` does not reset authentication.
`--handoff` observes an already active transfer and implements the conditional
second stage. Do not run two ordinary serving processes on the same connection.

Current sanitized journal:
`captures/firmware-work/host-ota-modified-events.jsonl`.
It records selected hash, source range/count summaries, status and handoff events;
it does not store credentials, health data or raw auth/device-info packets.

The active run began at UTC 03:14:09. Host transfer performance observed so far
is roughly 10–11 KB/s. Bytes served count responses, potentially including
repeated requests; it is not a claim of unique bytes programmed or final success.
The active transfer has a 30-minute overall deadline. No computer-side firmware
readback or failed-boot physical recovery procedure is established.

At UTC 03:32, replaced the auxiliary GATT subscriber with passive D-Bus observation: after the second StartNotify client was added, request delivery appeared duplicated and effective progress slowed. The passive observer does not call StartNotify during file serving; it acquires a subscription only on the device EOF signal (or E6=80) to preserve the handoff link. Only the auxiliary process was interrupted; primary file serving stayed running. 30 tests pass, including the observed four-byte E3 acknowledgement and mandatory-loader gate.

After replacing the second StartNotify client with passive observation, the private journal shows consecutive range offsets advancing by the full bytes served again (e.g. 106,496 bytes over one reporting interval), restoring about 10–11 KB/s effective range progression. This supports the duplicate-notification diagnosis. Current hardware transfer remains active; no final status/boot claim.
