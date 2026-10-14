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
