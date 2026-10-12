#!/usr/bin/env python3
"""Read-only BLE reconnaissance for mero-watch.

Commands: scan, inspect, listen. No GATT writes, firmware updates or pairing manipulation.
Output may contain unique device identifiers or private data: keep raw logs local.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

try:
    from bleak import BleakClient, BleakScanner
except ImportError as exc:
    raise SystemExit("Bleak is missing. Run: python -m pip install -r requirements.txt") from exc


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_ae02(uuid: str) -> bool:
    """Short UUID in a canonical Bluetooth base UUID, or bare short form."""
    head = uuid.lower().split("-")[0]
    return head == "ae02" or head == "0000ae02"


async def scan(args: argparse.Namespace) -> None:
    print(f"[{timestamp()}] Passive BLE discovery for {args.seconds:.1f}s")
    found = await BleakScanner.discover(timeout=args.seconds, return_adv=True)
    if not found:
        print("No BLE devices discovered.")
        return
    for address, (device, adv) in sorted(found.items()):
        name = adv.local_name or device.name or "(unnamed)"
        services = ", ".join(adv.service_uuids or []) or "(none advertised)"
        print(f"{address} | {name} | RSSI {adv.rssi} | services: {services}")


def show_services(client: BleakClient) -> None:
    for service in client.services:
        print(f"Service {service.uuid} | {service.description}")
        for char in service.characteristics:
            properties = ", ".join(char.properties)
            print(f"  Characteristic {char.uuid} | {properties}")
            for desc in char.descriptors:
                print(f"    Descriptor {desc.uuid}")


async def inspect(args: argparse.Namespace) -> None:
    print(f"[{timestamp()}] Connecting to {args.address} (service discovery only)")
    async with BleakClient(args.address, timeout=args.timeout) as client:
        print("Connected:", client.is_connected)
        show_services(client)


async def listen(args: argparse.Namespace) -> None:
    print(f"[{timestamp()}] Connecting to {args.address} (notifications only)")
    async with BleakClient(args.address, timeout=args.timeout) as client:
        print("Connected:", client.is_connected)
        matching = [
            char for service in client.services for char in service.characteristics
            if "notify" in char.properties
            and (args.all_notify or (char.uuid.lower() == (args.uuid or "").lower() if args.uuid else is_ae02(char.uuid)))
        ]
        if not matching:
            print("No matching notifiable characteristics; nothing was changed.")
            show_services(client)
            return

        def on_notify(sender: object, data: bytearray) -> None:
            uuid = getattr(sender, "uuid", str(sender))
            print(f"[{timestamp()}] {uuid} | {len(data)} bytes | {bytes(data).hex().upper()}", flush=True)

        for char in matching:
            print("Subscribing (CCCD/notify):", char.uuid)
            await client.start_notify(char.uuid, on_notify)
        try:
            await asyncio.sleep(args.seconds)
        finally:
            for char in matching:
                if client.is_connected:
                    await client.stop_notify(char.uuid)
        print("Listening completed.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="read BLE advertisements")
    s.add_argument("--seconds", type=float, default=12)
    s.set_defaults(run=scan)
    for command in ("inspect", "listen"):
        sp = sub.add_parser(command, help="inspect GATT without writes" if command == "inspect" else "receive BLE notifications")
        sp.add_argument("--address", required=True, help="currently observed BLE address")
        sp.add_argument("--timeout", type=float, default=20, help="connection timeout in seconds")
        if command == "listen":
            sp.add_argument("--seconds", type=float, default=20)
            group = sp.add_mutually_exclusive_group()
            group.add_argument("--uuid", help="full notifiable characteristic UUID; default: AE02")
            group.add_argument("--all-notify", action="store_true", help="subscribe to all notify characteristics")
        sp.set_defaults(run=inspect if command == "inspect" else listen)
    return p


if __name__ == "__main__":
    parser = build_parser()
    options = parser.parse_args()
    if options.command != "inspect" and options.seconds <= 0:
        parser.error("--seconds must be positive")
    if getattr(options, "timeout", 1) <= 0:
        parser.error("--timeout must be positive")
    try:
        asyncio.run(options.run(options))
    except (OSError, TimeoutError) as err:
        parser.exit(1, f"BLE operation failed: {err}\nCheck adapter, phone connection, and btmon/journalctl.\n")
    except KeyboardInterrupt:
        parser.exit(130, "Interrupted.\n")
