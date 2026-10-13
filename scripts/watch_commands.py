#!/usr/bin/env python3
"""Custom host commands from verified watch keys, with explicit synthetic replay.

Only KEY_PLAYCD / KEY_PAUSECD press events are mapped. Identify performs a
standard GATT Device Name read; this does not send RCSP, OTA or firmware data.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import socket
import struct
import sys

KEY_COMMANDS = {200: "status", 201: "identify"}
INPUT_EVENT = struct.Struct("@llHHI")
DEVICE_NAME = "00002a00-0000-1000-8000-00805f9b34fb"


def command_for_event(event_type, code, value):
    return KEY_COMMANDS.get(code) if event_type == 1 and value == 1 else None


def input_commands(stream):
    while record := stream.read(INPUT_EVENT.size):
        if len(record) != INPUT_EVENT.size:
            raise ValueError("Truncated Linux input_event record")
        _, _, event_type, code, value = INPUT_EVENT.unpack(record)
        command = command_for_event(event_type, code, value)
        if command:
            yield command


async def identify(address):
    from dbus_fast import BusType
    from dbus_fast.aio import MessageBus

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    try:
        node = await bus.introspect("org.bluez", "/")
        manager = bus.get_proxy_object("org.bluez", "/", node).get_interface(
            "org.freedesktop.DBus.ObjectManager")
        objects = await manager.call_get_managed_objects()
        device_path = next((path for path, interfaces in objects.items()
            if "org.bluez.Device1" in interfaces
            and interfaces["org.bluez.Device1"]["Address"].value.upper() == address.upper()), None)
        if device_path is None:
            raise RuntimeError("Watch is not present in BlueZ; discover/connect its LE bearer first")
        for path, interfaces in objects.items():
            char = interfaces.get("org.bluez.GattCharacteristic1")
            if path.startswith(device_path + "/") and char and char["UUID"].value == DEVICE_NAME:
                node = await bus.introspect("org.bluez", path)
                proxy = bus.get_proxy_object("org.bluez", path, node).get_interface(
                    "org.bluez.GattCharacteristic1")
                value = await asyncio.wait_for(proxy.call_read_value({}), timeout=10)
                return {"address": address.upper(), "name": bytes(value).decode("utf-8", "replace")}
        raise RuntimeError("Device Name characteristic unavailable; media-only connection is insufficient")
    finally:
        bus.disconnect()


async def execute(command, address=None):
    if command == "status":
        return {"host": socket.gethostname(),
            "uptime_seconds": float(Path("/proc/uptime").read_text().split()[0]),
            "load_average": list(os.getloadavg())}
    if command == "identify":
        if not address:
            raise ValueError("identify requires --address")
        return await identify(address)
    raise ValueError("Unsupported command")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--action", choices=["status", "identify"])
    group.add_argument("--simulate", choices=["play", "pause"], nargs="+")
    group.add_argument("--input", type=Path, help="Linux event device or recorded input_event file; no input grab")
    parser.add_argument("--address", help="Watch Bluetooth address for identify")
    args = parser.parse_args()
    stream = None
    try:
        source = "direct"
        if args.simulate:
            source = "synthetic"
            actions = (command_for_event(1, 200 if key == "play" else 201, 1) for key in args.simulate)
        elif args.input:
            source = "input_stream"
            stream = args.input.open("rb")
            actions = input_commands(stream)
        else:
            actions = [args.action]
        for command in actions:
            result = asyncio.run(execute(command, args.address))
            print(json.dumps({"source": source, "command": command, "result": result}), flush=True)
    except (OSError, RuntimeError, ValueError, ImportError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        if stream:
            stream.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
