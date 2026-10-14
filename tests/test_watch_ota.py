import unittest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from scripts.watch_ota import response, requested_block, Updater, file_mark, mandatory_loader
from scripts.watch_notifications import frame


class UpdaterTests(unittest.TestCase):
    def test_disabled_mark_uses_sdk_zero_byte_and_other_ranges_are_checked(self):
        self.assertEqual(file_mark(0, 0, b"abcd"), b"\0")
        self.assertEqual(file_mark(1, 2, b"abcd"), b"bc")
        with self.assertRaises(ValueError):
            file_mark(3, 2, b"abcd")

    def test_reply_has_status_then_sequence_and_exact_length(self):
        self.assertEqual(response(0xe5, 7, b"ab"), bytes.fromhex("fedcba00e5000400076162ef"))

    def test_device_ranges_are_bounded_and_done_is_distinct(self):
        self.assertEqual(requested_block(bytes.fromhex("000000010002"), b"abcd"), (1, b"bc", False))
        self.assertEqual(requested_block(bytes(6), b"abcd"), (0, b"", True))
        with self.assertRaises(ValueError):
            requested_block(bytes.fromhex("000000030002"), b"abcd")

    def test_fragmented_and_combined_device_commands_are_reassembled(self):
        updater = Updater("test", "unused")
        first = frame(0xe5, 8, bytes.fromhex("000000010002"))
        second = frame(0xe8, 9, bytes.fromhex("00000004"))
        for data in (first[:4], first[4:] + second):
            updater.changed("org.bluez.GattCharacteristic1", {"Value": SimpleNamespace(value=data)}, [])
        self.assertEqual(updater.incoming.get_nowait(), (0xe5, 8, bytes.fromhex("000000010002")))
        self.assertEqual(updater.incoming.get_nowait(), (0xe8, 9, bytes.fromhex("00000004")))


class UpdaterFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_four_byte_entry_ack_does_not_abort_before_done(self):
        updater = Updater("test", "unused")
        updater.write = AsyncMock()
        updater.request = AsyncMock(return_value=b"\0")
        updater.incoming.put_nowait((0xe3, 1, bytes(4)))
        updater.incoming.put_nowait((0xe5, 2, bytes(6)))
        events = []
        result = await updater.flash(b"abcd", lambda event, **fields: events.append(event))
        self.assertEqual(result, b"\0")
        self.assertIn("flash_entry_ack", events)
        self.assertIn("transfer_done_status", events)
        self.assertEqual(updater.write.await_count, 2)

    async def test_loader_gate_requires_actual_mandatory_flag(self):
        link = SimpleNamespace(request=AsyncMock(return_value=b"\2\11\1"), next_sequence=lambda: 1)
        self.assertTrue(await mandatory_loader(link))
        link.request.return_value = b"\2\11\0"
        self.assertFalse(await mandatory_loader(link))
        link.request.return_value = b"\5\11\1"
        self.assertFalse(await mandatory_loader(link))
