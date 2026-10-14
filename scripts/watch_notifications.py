"""Source-derived legacy RCSP text transport; authentication stays local.

The auth helper must expose AuthSession(transport, step_timeout=...). No keys,
raw authentication packets or device-info replies are logged by this module.
"""
import asyncio
from datetime import datetime
import importlib.util
import secrets


def frame(opcode, sequence, parameters):
    body = bytes([sequence]) + parameters
    return b"\xfe\xdc\xba\xc0" + bytes([opcode]) + len(body).to_bytes(2, "big") + body + b"\xef"


def message_frame(sequence, title, content, now=None):
    now = now or datetime.now()
    if not 2010 <= now.year <= 2073:
        raise ValueError("Timestamp outside SDK six-bit year range")
    timestamp = ((now.year - 2010) << 26 | now.month << 22 | now.day << 17
                 | now.hour << 12 | now.minute << 6 | now.second)
    fields = [(0, timestamp.to_bytes(4, "big")), (1, b"org.mero.watch"),
              (2, b"\0"), (3, title.encode("utf-8")), (4, content.encode("utf-8"))]
    if len(fields[3][1]) > 36 or len(fields[4][1]) > 424:
        raise ValueError("Text exceeds source-derived SDK byte limits")
    message = b"".join((len(value) + 1).to_bytes(2, "big") + bytes([tag]) + value
                       for tag, value in fields)
    if len(message) > 240:
        raise ValueError("Only source-verified single-fragment messages are supported")
    return frame(161, sequence, b"\x02\0\0" + message)


class WatchNotifications:
    def __init__(self, address, auth_helper, authenticate=True, subscribe=True):
        self.address = address.upper()
        self.auth_helper = auth_helper
        self.sequence = secrets.randbelow(256)
        self.bus = self.notification = self.properties = None
        self.listening = False
        self.authenticate = authenticate
        self.subscribe = subscribe
        self.auth_queue = asyncio.Queue()
        self.pending = {}
        self.buffer = bytearray()

    def changed(self, interface, values, invalidated):
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in values:
            return
        data = bytes(values["Value"].value)
        if (len(data) == 17 and data[0] in (0, 1)) or data == b"\x02pass":
            self.auth_queue.put_nowait(data)
            return
        self.buffer.extend(data)
        while self.buffer:
            start = self.buffer.find(b"\xfe\xdc\xba")
            if start < 0:
                self.buffer[:] = self.buffer[-2:]
                return
            del self.buffer[:start]
            if len(self.buffer) < 7:
                return
            length = int.from_bytes(self.buffer[5:7], "big")
            if length > 4096:
                del self.buffer[:3]
                continue
            end = 8 + length
            if len(self.buffer) < end:
                return
            if self.buffer[end - 1] != 239:
                del self.buffer[:3]
                continue
            packet = bytes(self.buffer[:end])
            del self.buffer[:end]
            if packet[3] == 0 and length >= 2:
                future = self.pending.get((packet[4], packet[8]))
                if future is not None and not future.done():
                    future.set_result((packet[7], packet[9:-1]))

    async def write(self, data):
        from dbus_fast import Variant
        await asyncio.wait_for(self.writer.call_write_value(
            data, {"type": Variant("s", "command")}), timeout=10)

    async def request(self, packet):
        key = (packet[4], packet[7])
        future = asyncio.get_running_loop().create_future()
        self.pending[key] = future
        try:
            await self.write(packet)
            status, parameters = await asyncio.wait_for(future, timeout=10)
            if status != 0:
                raise RuntimeError(f"RCSP transport status {status}")
            return parameters
        finally:
            self.pending.pop(key, None)

    def next_sequence(self):
        self.sequence = (self.sequence + 1) % 256
        return self.sequence

    async def __aenter__(self):
        from dbus_fast import BusType
        from dbus_fast.aio import MessageBus
        try:
            spec = importlib.util.spec_from_file_location("local_watch_auth", self.auth_helper)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            node = await self.bus.introspect("org.bluez", "/")
            manager = self.bus.get_proxy_object("org.bluez", "/", node).get_interface(
                "org.freedesktop.DBus.ObjectManager")
            objects = await manager.call_get_managed_objects()
            device = next((p for p, i in objects.items() if "org.bluez.Device1" in i
                           and i["org.bluez.Device1"]["Address"].value.upper() == self.address), None)
            if device is None:
                raise RuntimeError("Watch absent from BlueZ; establish its LE connection first")
            chars = {i["org.bluez.GattCharacteristic1"]["UUID"].value: p
                     for p, i in objects.items() if p.startswith(device + "/")
                     and "org.bluez.GattCharacteristic1" in i}
            for short, attribute in (("ae01", "writer"), ("ae02", "notification")):
                path = chars.get(f"0000{short}-0000-1000-8000-00805f9b34fb")
                if path is None:
                    raise RuntimeError("Watch data GATT unavailable; media connection is insufficient")
                node = await self.bus.introspect("org.bluez", path)
                proxy = self.bus.get_proxy_object("org.bluez", path, node)
                setattr(self, attribute, proxy.get_interface("org.bluez.GattCharacteristic1"))
                if attribute == "notification":
                    self.properties = proxy.get_interface("org.freedesktop.DBus.Properties")
            self.properties.on_properties_changed(self.changed)
            if self.subscribe:
                await self.notification.call_start_notify()
                self.listening = True
            if not self.authenticate:
                return self
            loop = asyncio.get_running_loop()
            owner = self

            class Transport:
                def send_to_ae01(self, data):
                    return asyncio.run_coroutine_threadsafe(owner.write(data), loop).result(timeout=12)

                def recv_ae02_raw(self, timeout):
                    return asyncio.run_coroutine_threadsafe(asyncio.wait_for(
                        owner.auth_queue.get(), timeout), loop).result(timeout=timeout + 2)

            # Exact SDK volatile authentication-reset literal; not factory reset/OTA.
            await self.write(bytes.fromhex("fedcbac00600020001ef"))
            await asyncio.sleep(0.05)
            await asyncio.wait_for(asyncio.to_thread(
                module.AuthSession(Transport(), step_timeout=8).do_handshake), timeout=35)
            # Source-derived informational query primes the previously observed path.
            # Response can contain an auth key, so discard it without logging.
            await self.request(frame(3, self.next_sequence(), b"\xff\xff\xff\xff\0"))
            return self
        except BaseException:
            await self.close()
            raise

    async def send(self, title, content):
        parameters = await self.request(message_frame(self.next_sequence(), title, content))
        return {"transport_status": 0, "application_parameters": list(parameters),
                "screen_display": "unconfirmed"}

    async def close(self):
        try:
            if self.listening:
                await asyncio.wait_for(self.notification.call_stop_notify(), timeout=5)
        finally:
            if self.properties is not None:
                self.properties.off_properties_changed(self.changed)
            if self.bus is not None:
                self.bus.disconnect()

    async def __aexit__(self, *args):
        await self.close()
