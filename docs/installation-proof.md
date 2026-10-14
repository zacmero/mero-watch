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
