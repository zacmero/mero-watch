"""Authorized RCSP updater continuation; no vendor keys or firmware bundled.

E1/E2 eligibility and E3/E5/E8/E6/E7 flow correlated with the pinned
ElectronicCats reference at d1204a478e2a80a5c9fbce85eaca264e7b2cc468,
tools/qix-ble/qix_ble/rcsp_ota.py. --flash is explicit; default only probes.
Requires an already established LE connection to the updater, not Classic.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
from scripts.watch_notifications import WatchNotifications, frame


async def connect_le(address):
    """Explicit public-LE bearer observed in this watch's updater advertisement.

    Raw D-Bus call handles the daemon's ConnectDevice reply signature correctly.
    Requires BlueZ experimental APIs; preserves pairing records.
    """
    from dbus_fast import BusType, Message, MessageType, Variant
    from dbus_fast.aio import MessageBus
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    path = "/org/bluez/hci0"
    node = await bus.introspect("org.bluez", path)
    adapter = bus.get_proxy_object("org.bluez", path, node).get_interface("org.bluez.Adapter1")
    await adapter.call_set_discovery_filter({"Transport": Variant("s", "le")})
    await adapter.call_start_discovery()
    try:
        await asyncio.sleep(3)
        reply = await asyncio.wait_for(bus.call(Message(
            destination="org.bluez", path=path, interface="org.bluez.Adapter1",
            member="ConnectDevice", signature="a{sv}", body=[{
                "Address": Variant("s", address), "AddressType": Variant("s", "public")}])) , 25)
        if reply.message_type == MessageType.ERROR:
            raise RuntimeError("Explicit LE connect failed: " + str(reply.error_name))
        await asyncio.sleep(2)
    finally:
        await adapter.call_stop_discovery()
        bus.disconnect()


async def mandatory_loader(link):
    """Reference SDK pass-two gate: target-info TLV type 9, byte zero."""
    data = await link.request(frame(3, link.next_sequence(), b"\xff\xff\xff\xff\0"))
    i = 0
    while i + 2 <= len(data):
        length = data[i]
        if not length or i + 1 + length > len(data):
            break
        if data[i + 1] == 9:
            return length >= 2 and data[i + 2] == 1
        i += length + 1
    return False


async def handoff(args, firmware, emit):
    """Observe pass one without resetting auth or answering its file pulls.

    A second notify subscriber keeps the still-open link available when the
    serving process completes. Only E6=80 activates the SDK's 0B relink step.
    """
    from dbus_fast import Message, MessageType
    async with Updater(args.address, args.auth_helper, resume=True, passive=True) as link:
        emit("handoff_observer_ready")
        while True:
            opcode, _, payload = await asyncio.wait_for(link.incoming.get(), 1800)
            if opcode == 0xe5 and payload[:6] == bytes(6) and not link.listening:
                # Only take a GATT subscription once the device signals EOF.
                # Multiple StartNotify clients duplicated BlueZ broadcasts.
                await link.notification.call_start_notify()
                link.listening = True
                emit("handoff_subscription_at_eof")
            if opcode != 0xe6:
                continue
            if not payload or payload[0] != 128:
                emit("handoff_not_required", status=payload.hex())
                return
            emit("loader_staged")
            if not link.listening:
                await link.notification.call_start_notify()
                link.listening = True
            answer = await link.request(frame(0x0b, link.next_sequence(), b"\0\x01"))
            emit("advertisement_relink_selected", reply=answer.hex())
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                path = "/org/bluez/hci0/dev_" + args.address.replace(":", "_")
                reply = await link.bus.call(Message(destination="org.bluez", path=path,
                    interface="org.freedesktop.DBus.Properties", member="Get",
                    signature="ss", body=["org.bluez.Device1", "Connected"]))
                if reply.message_type == MessageType.ERROR or not reply.body[0].value:
                    emit("peripheral_disconnected_for_relink")
                    break
                await asyncio.sleep(0.25)
            else:
                raise TimeoutError("device did not perform the expected relink; no host disconnect forced")
            break
    await asyncio.sleep(2)
    await connect_le(args.bootloader_address)
    async with Updater(args.bootloader_address, args.auth_helper) as link:
        if not await mandatory_loader(link):
            raise RuntimeError("target-info does not identify mandatory loader mode; refusing pass two")
        emit("pass_two_loader_confirmed", address=args.bootloader_address)
        # Pinned SDK reference flash_pass2 explicitly sends E3 only; no E1/E2.
        status = await link.flash(firmware, emit)
        if not status or status[0] != 0:
            raise RuntimeError("pass-two status " + status.hex() + "; no reboot requested")
        emit("pass_two_success_reboot_requested")
        try:
            reply = await link.request(frame(0xe7, link.next_sequence(), b"\0"))
            emit("reboot_ack", status=reply.hex())
        except Exception as exc:
            emit("reboot_reply_unconfirmed", error=type(exc).__name__)


def response(opcode, sequence, payload=b""):
    body = bytes([0, sequence]) + payload
    return b"\xfe\xdc\xba\0" + bytes([opcode]) + len(body).to_bytes(2, "big") + body + b"\xef"


def requested_block(parameters, firmware):
    if len(parameters) < 6:
        raise ValueError("truncated E5 request")
    offset = int.from_bytes(parameters[:4], "big")
    size = int.from_bytes(parameters[4:6], "big")
    if offset == size == 0:
        return offset, b"", True
    if not size or size > 65533 or offset + size > len(firmware):
        raise ValueError("E5 range outside selected firmware")
    return offset, firmware[offset:offset + size], False


def file_mark(offset, length, firmware):
    # Reference SDK disables the mark in normal mode using (0,0); E2 still
    # requires one zero byte. Bootloader mode on this device requests (64,66).
    if offset == length == 0:
        return b"\0"
    if not 0 < length <= 512 or offset + length > len(firmware):
        raise ValueError("E1 mark outside selected firmware")
    return firmware[offset:offset + length]


class Updater(WatchNotifications):
    def __init__(self, address, auth_helper, resume=False, passive=False):
        super().__init__(address, auth_helper, authenticate=not resume, subscribe=not passive)
        self.incoming = asyncio.Queue()
        self.ota_buffer = bytearray()
        self.fragment = 20

    def changed(self, interface, values, invalidated):
        super().changed(interface, values, invalidated)
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in values:
            return
        data = bytes(values["Value"].value)
        if (len(data) == 17 and data[0] in (0, 1)) or data == b"\x02pass":
            return
        self.ota_buffer.extend(data)
        while self.ota_buffer:
            start = self.ota_buffer.find(b"\xfe\xdc\xba")
            if start < 0:
                self.ota_buffer[:] = self.ota_buffer[-2:]
                return
            del self.ota_buffer[:start]
            if len(self.ota_buffer) < 7:
                return
            length = int.from_bytes(self.ota_buffer[5:7], "big")
            if length > 4096:
                del self.ota_buffer[:3]
                continue
            end = length + 8
            if len(self.ota_buffer) < end:
                return
            packet = bytes(self.ota_buffer[:end])
            del self.ota_buffer[:end]
            if packet[-1] != 239:
                continue
            if packet[3] & 128 and length >= 1:
                self.incoming.put_nowait((packet[4], packet[7], packet[8:-1]))
            elif packet[3] == 0 and packet[4] in (0xe3, 0xe6) and length >= 2:
                self.incoming.put_nowait((packet[4], packet[8], packet[9:-1]))

    async def write(self, data):
        for offset in range(0, len(data), self.fragment):
            await super().write(data[offset:offset + self.fragment])

    async def __aenter__(self):
        await super().__aenter__()
        try:
            mtu = (await self.properties.call_get("org.bluez.GattCharacteristic1", "MTU")).value
            if 23 <= mtu <= 517:
                self.fragment = mtu - 3
        except Exception:
            pass
        return self

    async def probe(self, firmware):
        mark = await self.request(frame(0xe1, self.next_sequence(), b""))
        if len(mark) != 6:
            raise ValueError("invalid E1 response")
        offset = int.from_bytes(mark[:4], "big")
        length = int.from_bytes(mark[4:], "big")
        answer = await self.request(frame(0xe2, self.next_sequence(), file_mark(offset, length, firmware)))
        if not answer or answer[0] != 0:
            raise RuntimeError("E2 rejected file: " + answer.hex())
        return offset, length

    async def flash(self, firmware, emit, enter=True):
        if enter:
            await self.write(frame(0xe3, self.next_sequence(), b""))
        emit("flash_entry_sent" if enter else "resume_waiting", fragment_bytes=self.fragment)
        blocks = total = 0
        tick = time.monotonic()
        deadline = tick + 1800
        while time.monotonic() < deadline:
            try:
                opcode, sequence, parameters = await asyncio.wait_for(self.incoming.get(), 60)
            except asyncio.TimeoutError:
                status = await self.request(frame(0xe6, self.next_sequence(), b""))
                emit("idle_status", status=status.hex(), blocks=blocks, bytes_served=total)
                return status
            if opcode == 0xe5:
                offset, payload, done = requested_block(parameters, firmware)
                await self.write(response(opcode, sequence, payload))
                if done:
                    status = await self.request(frame(0xe6, self.next_sequence(), b""))
                    emit("transfer_done_status", status=status.hex(), blocks=blocks, bytes_served=total)
                    return status
                blocks += 1
                total += len(payload)
                if blocks == 1 or time.monotonic() - tick >= 10:
                    emit("serving", blocks=blocks, bytes_served=total, last_offset=offset)
                    tick = time.monotonic()
            elif opcode == 0xe8:
                await self.write(response(opcode, sequence))
                emit("content_size", bytes=int.from_bytes(parameters[:4], "big"))
            elif opcode == 0xe3:
                emit("flash_entry_ack", status=parameters.hex())
                if not parameters or parameters[0] != 0:
                    raise RuntimeError("E3 rejected update mode")
            elif opcode == 0xe6:
                emit("device_status", status=parameters.hex(), blocks=blocks, bytes_served=total)
                return parameters
            else:
                emit("ignored_device_command", opcode=opcode)
        raise TimeoutError("overall OTA deadline reached")


async def run(args):
    firmware = args.firmware.read_bytes()
    digest = hashlib.sha256(firmware).hexdigest()
    allowed = {"5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145",
               "a687b219ec0cf3415a3b9961036103e3cafcf4cf5bf9e5011df063fc369ce0b7",
               "7fb622c7bd5ca1fa23f9547f445751e0ddd00b467cfc9eb895a3d598c67b8040"}
    if digest != args.sha256 or digest not in allowed:
        raise ValueError("firmware not one of the explicitly validated experiment artifacts")

    def emit(event, **fields):
        record = dict(utc=datetime.now(timezone.utc).isoformat(), event=event, **fields)
        args.log.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(args.log, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(fd, "a") as out:
            out.write(json.dumps(record) + "\n")
        print(json.dumps(record), flush=True)

    emit("selected", sha256=digest, bytes=len(firmware), address=args.address)
    if args.handoff:
        await handoff(args, firmware, emit)
        return
    if args.connect_le:
        await connect_le(args.address)
        emit("explicit_le_connected")
    async with Updater(args.address, args.auth_helper, resume=args.resume) as link:
        if not args.resume:
            offset, length = await link.probe(firmware)
            emit("eligible", mark_offset=offset, mark_length=length)
        if args.flash:
            status = await link.flash(firmware, emit, enter=not args.resume)
            if status and status[0] == 0:
                emit("reboot_requested")
                try:
                    reply = await link.request(frame(0xe7, link.next_sequence(), b"\0"))
                    emit("reboot_ack", status=reply.hex())
                except Exception as exc:
                    # Reboot can disconnect before its reply; boot still needs verification.
                    emit("reboot_reply_unconfirmed", error=type(exc).__name__)
            else:
                raise RuntimeError("OTA final status " + status.hex() + "; no reboot requested")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", required=True)
    parser.add_argument("--auth-helper", type=Path, required=True)
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--flash", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Continue the existing authenticated OTA connection without reset/probe/E3")
    parser.add_argument("--connect-le", action="store_true", help="Establish explicit LE through experimental BlueZ Adapter1.ConnectDevice")
    parser.add_argument("--handoff", action="store_true", help="Observe active pass one and handle E6=80 relink, then E3-only pass two")
    parser.add_argument("--bootloader-address", default="F9:F3:71:D9:79:12")
    args = parser.parse_args()
    if args.resume and not args.flash:
        parser.error("--resume requires --flash")
    if args.handoff and not args.flash:
        parser.error("--handoff requires --flash")
    asyncio.run(run(args))
