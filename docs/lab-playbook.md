# Arch Linux lab playbook (non-destructive)

This workflow is for **the owner's own watch** on **ArchMerOS / Arch Linux**. All default steps are read-only or notification subscription. Never paste pairing keys, private notifications or raw health data into public issues.

## 1 — Confirm host and adapter

```bash
uname -r
bluetoothctl --version
lsusb
rfkill list bluetooth
systemctl status bluetooth --no-pager
bluetoothctl list
```

The broader lab inventory includes a **TP-Link UB5A USB Bluetooth adapter** (USB VID:PID `2357:0604`). Confirm with `lsusb` rather than presuming it is the connected `hci0`. In December 2025 a different/unreliable Bluetooth USB controller reset mid-connection (`hci0 removed`) and Bleak timed out.

If needed:

```bash
sudo pacman -S --needed bluez bluez-utils python
sudo systemctl enable --now bluetooth
sudo rfkill unblock bluetooth
```

Avoid making disruptive resets as the first diagnostic step. Record system journal messages when the controller disappears.

## 2 — Advertise-only discovery

Put the watch near the adapter. If the GFit Pro phone connection monopolizes BLE, disconnect temporarily through normal UI; avoid unpairing/resetting the watch.

```bash
bluetoothctl
# interactive:
list
power on
scan on
# observe Apple Watch or other device IDs; stop after 10-20 seconds:
scan off
devices
info <WATCH_ADDRESS>
quit
```

The previously seen `F9:F3:71:D9:79:11` is a historical reference, **not** a guaranteed stable address. BLE address randomization or distinct Bluetooth Classic/BLE addresses may apply.

## 3 — Run the Python read-only probe

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/ble_probe.py scan --seconds 15
python scripts/ble_probe.py inspect --address '<CURRENT_BLE_ADDRESS>'
python scripts/ble_probe.py listen --address '<CURRENT_BLE_ADDRESS>' --seconds 30
```

`scan` lists advertisements. `inspect` establishes a BLE connection and enumerates services/characteristics, without writing to them. `listen` subscribes only to the historical `AE02` match by default; if the canonical UUID differs, use `--uuid '<FULL_CHARACTERISTIC_UUID>'`. Use `--all-notify` only when interested in all available notify channels.

To preserve **private** local output:

```bash
mkdir -p captures
python scripts/ble_probe.py listen --address '<CURRENT_BLE_ADDRESS>' --seconds 30 | tee captures/ble-001-local.log
```

`captures/` is Git-ignored. Sanitize data before copying observations to documentation.

## 4 — Independently observe controller state

Open a second terminal before an attempt:

```bash
sudo btmon
```

In another terminal:

```bash
sudo journalctl -fu bluetooth
# or for kernel USB/HCI resets:
sudo journalctl -kf
```

Stop collectors after experiment. The old `hci0 removed` event distinguishes a host/controller transport failure from a BLE service handshake problem.

## 5 — Troubleshooting decision tree

- **No advertised device:** verify power/visibility, Bluetooth radio and whether the phone app currently holds a connection. Try a passive scan before changing bonds.
- **Scan works; connection times out:** check competing phone connection, kernel HCI resets, BlueZ logs and adapter stability. Record whether `hci0` disappears.
- **Services lack AE00:** verify that the BLE address belongs to the same watch, confirm full UUID list, avoid assuming prior UUIDs persist across firmware versions.
- **AE02 subscribes but no packets:** maybe an app initialization/authentication handshake is needed; do not guess bytes to AE01. Correlate with safe manual on-watch actions, document negative result.
- **HCI controller repeatedly vanishes:** try USB port/topology investigation and known-good adapter, then inspect `dmesg`/journal; do not accuse the watch protocol before stabilizing transport.
- **Only non-BLE audio device appears:** watch may advertise a second separate BLE identity; scan and inventory both.

## 6 — Firmware research gate

Before any firmware procedure: archive original app version/update manifest; examine packages and update blobs **offline**; identify chip/platform; establish rollback and voltage constraints. Never deliver an unknown `AE01` packet, reflash blindly, or force bootloader entry on the only functioning specimen.

## Template: outcome

```text
ID: BLE-001
Date/time + UTC offset:
Operator:
Host / kernel:
Controller / lsusb / BlueZ / Bleak versions:
Phone app connection state:
Advertised name and address type:
Full service UUIDs and characteristic properties:
Exact non-destructive commands:
Result and logs saved in captures/:
Hypothesis supported / falsified:
Next safe test:
```
