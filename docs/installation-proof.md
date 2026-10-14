# Modified firmware installation experiment

## 2026-10-13 — authorized normal-updater test

The owner explicitly authorized loading modified firmware and prioritized proving
deployment over further UI reconstruction. Earlier offline-only scope does not
describe this experiment. No hardware recovery path has yet been demonstrated;
that limitation was disclosed before authorization.

### Selected artifact

Both application images have the equal-length `Apple Watch` → `Mero Agent!`
branding fixture. Runtime visibility of that string remains unverified. The
bootloader, package geometry, configurations and non-code payloads are unchanged.
Offline repacking/integrity evidence is in [the update lab](firmware-update-lab.md).

Size: 18,760,384 bytes. SHA-256:
`a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7`.
MD5: `2fd0d033055a4e897e8dbd5e83b2b0db`.
The binary remains private under ignored captures.

### Handoff mechanism

`scripts/firmware_download_proxy.py` runs in the retained mitmproxy environment.
It replaces only the observed vendor POST `/abroad/awsd/ota/piddownload` with
the explicitly selected, SHA-256-guarded local file. The phone still uses
GFit Pro's normal Bluetooth updater.

The optional restoration response rewrite is restricted to
`/abroad/awsd/ota/userUpgradeOta`. Its encrypted envelope uses an RSA-wrapped
AES key and AES/ECB/PKCS padding as implemented in the inspected app. The key
material is read from private app disassembly and is never embedded or logged
in repository code. The decoded PID, version and original MD5 must match the
captured stock build. Only `fileMd5` changes; the AES key envelope, version,
URL, size, name and all other decoded metadata remain unchanged.

The rewrite was tested against the real captured response by decrypting its
result and comparing every metadata field. Three synthetic tests independently
check exact field preservation, rejection of another PID and preservation of
an error response. All 24 tests pass in the optional proxy environment.

### Connection correction

An iptables INPUT allow rule did not establish reachability: an independent
`inet firewalld` hook filtered the traffic. A runtime firewalld rule now permits
the phone's current IPv4 to TCP 8899, expiring after 3600 seconds. Safari and
the vendor detection request subsequently reached the proxy. This corrects
the incomplete earlier single-layer firewall check.

### Evidence checkpoint

- Owner-reported: Detect Now succeeded and offered Upgrade Now after connection
  correction. Detection was refreshed after selecting the modified package.
- Observed: after the owner was instructed to press Upgrade Now, GFit Pro
  requested the exact download route; the proxy supplied HTTP 200 with the
  modified artifact's verified size and SHA-256.
- Owner-reported: the app began showing transfer progress with no error so far.
- Pending: completed transfer, device acceptance, reboot and observable marker.
- Pending: normal restoration of stock; failed-boot recovery remains unverified.

Download handoff and transfer initiation do not establish execution. A successful
update and reboot establish stronger acceptance evidence; a visible changed
marker is needed to positively identify modified application execution. If the
marker is not visible, record that result rather than calling the native app
installation proven.

Owner reports transfer finished; watch displays Chinese text, loading dots and an identifier; GFit Pro says waiting for upgrade. No identifier retained. This is an intermediate device update state, not a confirmed success or boot. Owner instructed to keep power/app/connection unchanged.

Owner-reported updater display address F9:F3:71:D9:79:12, versus previously observed normal BLE/EDR F9:F3:71:D9:79:11. Treat as a distinct update-mode candidate, not an overwritten normal address. Owner reports repeated Chinese message/loading cycles, then further apparent progress; success and normal reboot still unconfirmed.

Owner reports GFit Pro OTA update timeout after completed transfer; phone Bluetooth shows Apple Watch connecting and is no longer connected. Normal boot and modified marker are NOT confirmed. Possible update-mode reconnection failure is a hypothesis; no claim of signature rejection or successful flash. Started passive scan for normal ...:11 and displayed updater ...:12; no power cycle/reset instructed.

Observed passive BLE: F9:F3:71:D9:79:12 advertised local name Apple Watch, RSSI -78 dBm, no service UUIDs in advertisement, manufacturer-data ID 1494 (0x05d6). This is live host evidence of the alternate updater address; manufacturer ID alone does not identify/authenticate hardware. Requested owner force-close phone app before a read-only service inventory.

Owner photograph /home/zacmero/Downloads/photo_2026-10-13_23-43-37.jpg shows Chinese 等待连接 (waiting for connection) and 地址 (address), explicitly F9:F3:71:D9:79:12. Dots are a waiting indicator; apparent progress is not verified flash progress. This narrows the current failure to update-mode connection/handoff; application acceptance/rejection remains unproven. No IMEI is displayed in this photo. Read-only connect at nearby RSSI -58 also timed out.

Controller trace updater-retry-private.btsnoop positively shows HCI Create Connection (0x01/0x0005) to F9:F3:71:D9:79:12, BR/EDR address type, then Connect Complete Page Timeout (0x04). This is Classic paging, not LE Create Connection or GATT validation. The host retry failure must not be attributed to firmware acceptance/signatures. Investigating explicit LE bearer selection. Raw trace remains private.

Temporarily enabled BlueZ experimental APIs through /run/systemd/system/bluetooth.service.d/mero-watch-load-test.conf and restarted host Bluetooth service; existing pairing database was preserved, watch remained powered. Installed client bearer setter previously failed UnknownProperty, so explicit LE connection requires checking daemon API availability. Runtime override must be removed after experiment.

Explicit Adapter1.ConnectDevice with AddressType=public succeeded after experimental API activation (dbus-fast raised unexpected output signature o despite the daemon returning the created path). Verified Device1 Connected=true, LE.Connected=true, BREDR.Connected=false, unpaired, services GAP1800 and AE00. The alternate-address updater is reachable over LE; Generic Device1.Connect had attempted Classic instead. No flash command sent by host yet.

Updater LE authentication succeeded using the previously validated private helper. Source-derived GetFileInfoOffset E1 replied offset 64, length 66. This confirms an authenticated, responsive normal RCSP OTA endpoint at ...:12; initiating E2 file eligibility check with only the requested bytes from the hash-guarded modified fixture. No E3/flash-entry sent yet.

## 2026-10-14 — direct host continuation

Owner photo 23:58:50 shows 请尝试使用升级软件手动触发升级 (please try using upgrade software to manually trigger upgrade), plus updater ...:12 address. E2 eligibility response for the modified artifact was 00. Implemented bounded device-driven E5 range server from pinned RCSP reference, with E8 acknowledgements and E6 result checks; only success permits E7 reboot. 27 tests pass in proxy environment, including packet reassembly and range bounds. Under existing explicit firmware-load authorization, launched direct host --flash continuation using the exact validated modified artifact. Final acceptance and boot remain pending.

Direct E3 was accepted with a four-byte zero payload, and owner reports file-transfer screen. Host initially aborted because it incorrectly required a one-byte E3 result; corrected to inspect the first status byte as the reference SDK does. No file blocks were served before that abort. Started a resume listener on the existing link without authentication reset, E1/E2 or E3; awaiting device pulls. This implementation error is recorded separately from device rejection.

Resume attempt could not continue: link became disconnected before status query; fresh connect to updater timed out. Subsequent passive scan found ONLY normal F9:F3:71:D9:79:11, name Apple Watch, RSSI -54, with normal manufacturer-data format (no JLOTA marker). Thus updater address disappeared and the normal application-mode advertisement returned; actual UI/boot confirmation requested from owner. No host E5 payload blocks have been served.

Owner clarifies watch UI still says File transfer despite ...:11 normal-format advertisement; do not interpret address return as confirmed application boot. Phone Bluetooth remains off. Normal-address informational/eligibility probe is underway.

Normal ...:11 E1 returns disabled mark (0,0); pinned SDK reference explicitly requires E2 payload 00 in this case. Added that behavior and bounded-range regression test. Normal ...:11 E2 accepted (00), E3 sent with corrected first-byte acknowledgement handling, and device began E5 pulls. Observed first served block: offset 0, 512 bytes of the exact modified fixture. This is the first confirmed host-to-device file payload transfer; 28 tests pass. Owner still sees file-transfer screen.

Owner confirms direct computer OTA is the preferred route from now on. Active transfer serves the MODIFIED fixture (not stock), SHA256 a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7. Phone Bluetooth remains off; GFit Pro/proxy is not carrying this host BLE transfer. Added an observation-only second AE02 subscriber that acts only if the device returns E6=80: sends source-derived 0B payload 00 01 on the still-open link, waits for peripheral disconnect, reconnects ...:12 explicitly over LE, confirms target-info mandatory-loader flag and performs E3-only second pass (no repeated E1/E2). This preserves the SDK handoff that the earlier phone attempt did not complete. No final success/boot claim yet.

At UTC 03:32, replaced the auxiliary GATT subscriber with passive D-Bus observation: after the second StartNotify client was added, request delivery appeared duplicated and effective progress slowed. The passive observer does not call StartNotify during file serving; it acquires a subscription only on the device EOF signal (or E6=80) to preserve the handoff link. Only the auxiliary process was interrupted; primary file serving stayed running. 30 tests pass, including the observed four-byte E3 acknowledgement and mandatory-loader gate.

UTC 03:42:55: first-stage E6 result80 (loader staged), 4,672 served blocks, 18,700,191 response bytes including repeated ranges; final announced loader payload57,059 bytes. Passive observer took notification subscription at EOF, sent0B payload0001; reply01. Peripheral disconnected itself, then direct LE reconnect to ...:12 authenticated and target-info mandatory-loader flag confirmed. UTC03:43:10: E3-only second stage began (no E1/E2); four-byte zero ack accepted; E5 pulls started. E8 announced1,302,528 bytes. Owner photo00:43:51 shows red 升级中，请不要断电 (upgrading, do not cut power), green18% progress. This is live second-stage firmware programming, not just phone download or eligibility. Final status/normal boot remains pending.

UTC03:45:10: second-stage E6 returned00 success after334 served blocks /1,309,024 response bytes (announced payload1,302,528). Host sent E7 payload00; device acknowledged with four-byte zero payload. Direct host updater process exited0. Owner reports watch reached100% then turned off. Instructed normal power-on; application boot and marker visibility still pending. This establishes device-reported acceptance of the modified package and completed programming, not yet confirmed normal execution.


## 2026-10-14 — confirmed outcome and protected original

Owner confirms normal boot after device-reported second-stage success and acknowledged reboot. About and normal advertisement still show Apple Watch; the modified app literal was not a traced About-name field. Owner accepts deployment proof and selects mero-watch as firmware/build identifier going forward. A new offline mero-watch marker candidate was independently repacked/checked (SHA256 57cb7fcaca447abd79733351d68e743fa4deff87988dba4eeb731a44b8bef210), not installed.

Complete original vendor UFW was rehashed and is unchanged: 18,760,384 bytes, SHA256 5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145, MD5 550f4fcf32916da3a2dbb77c9510ee3e. Retained capture copy is owner-read-only. A second independently verified, owner-read-only copy and private manifest are in /home/zacmero/.local/share/mero-watch/recovery/ (directory mode0700). This is the full vendor code/bootloader/resource package, not a physical flash or user-state dump. It provides a stock restore source if the updater is reachable; arbitrary failed-boot/hardware recovery is not guaranteed. The phone download proxy was stopped after direct OTA succeeded. Experimental BlueZ runtime override remains enabled for the continuing direct-updater work.

### Fresh stock update: completed programming

**Observed (2026-10-14):** Starting from normally booted firmware, Linux initiated the full stock update without a GFit Pro update session. Owner confirmed entry into transfer mode. UTC04:59:18 first-stage E6 returned80 after3,998 served blocks /15,939,487 response bytes (includes package framing and requested ranges; not a flash readback). The passive observer subscribed at EOF, sent0B payload0001, received01, and observed the peripheral disconnect itself. Direct public-LE reconnect to updater address ...:12 succeeded; target-info mandatory-loader mode was confirmed at04:59:33. E3-only pass two announced1,302,528 bytes. UTC05:01:52 final E6 returned00 after334 blocks /1,309,024 response bytes; E7 reboot received00000000 acknowledgement. Handoff process exited0. Total computer-initiated sequence took about31 minutes20 seconds. Owner reports power-off and is performing normal power-on; normal boot confirmation is pending.

This establishes direct computer-only update entry, both transfer stages, loader handoff and device-reported programming success. It does not establish arbitrary patched firmware compatibility, flash readback or recovery from every failed boot. The original stock package and independent read-only recovery copy remain unchanged.

### Fresh stock update: normal boot confirmed

**Owner-reported (2026-10-14):** After the completed computer-only stock update and normal power-on, the watch returned to its normal clock/menu. The complete fresh-start route is therefore demonstrated on this device: Linux authentication/eligibility, update entry from normal firmware, first-stage file serving, device-driven loader relink, second-stage firmware programming, success acknowledgement and normal boot. GFit Pro was not required for this update sequence. This test installed the original stock package, not the prepared mero-watch marker candidate.
