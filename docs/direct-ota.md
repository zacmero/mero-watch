# Direct computer OTA — installation test

## Latest result — 2026-10-14, UTC05:01

A fresh stock update was initiated directly from normal firmware by Linux, without a GFit Pro update session. Both stages and the device-driven loader relink completed. The watch returned final E6 `00` success and acknowledged reboot; the owner confirmed normal boot after power-on. The dated entries below preserve the earlier experiment states and are superseded by this result where indicated.

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

UTC 03:42:55: first-stage E6 result80 (loader staged), 4,672 served blocks, 18,700,191 response bytes including repeated ranges; final announced loader payload57,059 bytes. Passive observer took notification subscription at EOF, sent0B payload0001; reply01. Peripheral disconnected itself, then direct LE reconnect to ...:12 authenticated and target-info mandatory-loader flag confirmed. UTC03:43:10: E3-only second stage began (no E1/E2); four-byte zero ack accepted; E5 pulls started. E8 announced1,302,528 bytes. Owner photo00:43:51 shows red 升级中，请不要断电 (upgrading, do not cut power), green18% progress. This is live second-stage firmware programming, not just phone download or eligibility. Final status/normal boot remains pending.

UTC03:45:10: second-stage E6 returned00 success after334 served blocks /1,309,024 response bytes (announced payload1,302,528). Host sent E7 payload00; device acknowledged with four-byte zero payload. Direct host updater process exited0. Owner reports watch reached100% then turned off. Instructed normal power-on; application boot and marker visibility still pending. This establishes device-reported acceptance of the modified package and completed programming, not yet confirmed normal execution.

## 2026-10-14 — fresh computer-only stock update

Owner authorized a fresh stock update from a normally booted watch. Original package size/hash verified unchanged; protected recovery copy retained. At UTC04:30:18 the normal-address authenticated E1/E2 probe accepted the stock package (mark offset/length 0/0). At UTC04:30:32 Linux initiated E3 and served device-requested blocks; E8 announced 15,878,656 bytes. Owner independently confirmed the watch entered transfer mode without GFit Pro. This establishes computer-only update entry; full programming and normal boot remain pending. Private sanitized journals: fresh-stock-probe-events.jsonl, fresh-stock-transfer-events.jsonl, fresh-stock-handoff-events.jsonl under captures/firmware-work. Passive handoff observer is active for the two-stage transition. Initial explicit ConnectDevice returned Error.Failed although LE was already connected; the existing LE connection authenticated successfully.

### Update entry packet

Observed fresh normal-boot entry uses authenticated RCSP E1/E2 eligibility followed by E3 with an empty parameter body. For sequence 01, the implementation emits `FE DC BA C0 E3 00 01 01 EF` through AE01; AE02 carries device requests/replies. This is an existing firmware protocol command, not injected executable code. The sequence byte varies; this example is not a standalone unauthenticated unlock packet.

### Fresh stock update procedure used in this experiment

The following commands use the locally retained stock package and private authentication helper. Neither is distributed in the public repository. Keep the watch powered nearby and prevent the phone from competing for its BLE connection. The normal-address LE connection must expose AE01/AE02; a media-only connection is insufficient. The current host uses the recorded runtime BlueZ experimental override.

First perform eligibility-only authentication and probing:

```bash
rtk proxy .venv/bin/python -m scripts.watch_ota \
  --address F9:F3:71:D9:79:11 \
  --auth-helper captures/command-mapping/private_auth_helper.py \
  --firmware captures/gfit-capture/downloaded-update1004.ufw \
  --sha256 5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145 \
  --log captures/firmware-work/fresh-stock-probe-events.jsonl
```

If no LE connection exists, the tool's `--connect-le` option requests one explicitly. In this experiment that option returned `org.bluez.Error.Failed` while LE was already connected; using the existing connection succeeded. Do not interpret that host error alone as firmware rejection.

After eligibility succeeds, start the passive handoff observer in one terminal. Use the same arguments as above, change the log to `fresh-stock-handoff-events.jsonl`, and add `--flash --handoff`. Wait for `handoff_observer_ready`. Then start the primary process in another terminal with the same arguments, log `fresh-stock-transfer-events.jsonl`, and `--flash` only.

The primary process serves pass one. An E6 result `80` means loader staging rather than final failure; the observer then performs the device-driven relink and second pass. Confirm the observer's final E6 `00` result and verify normal boot independently. Do not restart or interrupt a live update merely because the primary process exits on result `80`.

This procedure is currently a hardware experiment on this particular watch, not a general-purpose flasher. Only the explicitly validated package hashes are accepted. A newly modified package needs offline validation and explicit admission before use.

### Fresh stock update: completed programming

**Observed (2026-10-14):** Starting from normally booted firmware, Linux initiated the full stock update without a GFit Pro update session. Owner confirmed entry into transfer mode. UTC04:59:18 first-stage E6 returned80 after3,998 served blocks /15,939,487 response bytes (includes package framing and requested ranges; not a flash readback). The passive observer subscribed at EOF, sent0B payload0001, received01, and observed the peripheral disconnect itself. Direct public-LE reconnect to updater address ...:12 succeeded; target-info mandatory-loader mode was confirmed at04:59:33. E3-only pass two announced1,302,528 bytes. UTC05:01:52 final E6 returned00 after334 blocks /1,309,024 response bytes; E7 reboot received00000000 acknowledgement. Handoff process exited0. Total computer-initiated sequence took about31 minutes20 seconds. Owner reports power-off and is performing normal power-on; normal boot confirmation is pending.

This establishes direct computer-only update entry, both transfer stages, loader handoff and device-reported programming success. It does not establish arbitrary patched firmware compatibility, flash readback or recovery from every failed boot. The original stock package and independent read-only recovery copy remain unchanged.

### Fresh stock update: normal boot confirmed

**Owner-reported (2026-10-14):** After the completed computer-only stock update and normal power-on, the watch returned to its normal clock/menu. The complete fresh-start route is therefore demonstrated on this device: Linux authentication/eligibility, update entry from normal firmware, first-stage file serving, device-driven loader relink, second-stage firmware programming, success acknowledgement and normal boot. GFit Pro was not required for this update sequence. This test installed the original stock package, not the prepared mero-watch marker candidate.

**Observed post-boot:** Linux reports Connected=true and ServicesResolved=true at normal address ...:11. AE01/AE02 are present, and a live GAP Device Name read returned Apple Watch. The stock application data connection is functional after the fresh update. A redundant explicit ConnectDevice call returned Error.Failed despite the established working LE connection; use the live connection state and successful GATT operation rather than that error alone.
