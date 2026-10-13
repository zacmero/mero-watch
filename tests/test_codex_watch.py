from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from scripts.codex_watch import RolloutStatus, content
from scripts.watch_notifications import message_frame, WatchNotifications


class CodexWatchTests(unittest.TestCase):
    def test_incremental_events_ignore_text_and_wait_for_complete_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            def event(kind):
                return json.dumps({"type": "event_msg", "timestamp": datetime.now(timezone.utc).isoformat(),
                                   "payload": {"type": kind, "message": "private text"}}).encode()
            path.write_bytes(event("task_started") + b"\n" + event("agent_message") + b"\n")
            reader = RolloutStatus(path)
            self.assertEqual(reader.read(), "working")
            complete = event("task_complete")
            with path.open("ab") as stream:
                stream.write(complete[:20])
            self.assertEqual(reader.read(), "working")
            with path.open("ab") as stream:
                stream.write(complete[20:] + b"\n")
            self.assertEqual(reader.read(), "done")
            self.assertNotIn("private text", content("Agent", reader.read()))
            path.write_bytes(b"")
            self.assertEqual(reader.read(), "unknown")

    def test_old_working_event_is_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text(json.dumps({"type": "event_msg", "timestamp": "2020-01-01T00:00:00Z",
                                       "payload": {"type": "task_started"}}) + "\n")
            self.assertEqual(RolloutStatus(path).read(), "stale")

    def test_notification_envelope_and_limits(self):
        packet = message_frame(23, "Mero Codex", "Codex | Agent | working", datetime(2026, 10, 13))
        self.assertEqual(packet[:5], bytes.fromhex("fedcbac0a1"))
        self.assertEqual(int.from_bytes(packet[5:7], "big"), len(packet) - 8)
        self.assertEqual(packet[7:11], bytes([23, 2, 0, 0]))
        self.assertEqual(packet[-1], 239)
        with self.assertRaises(ValueError):
            message_frame(1, "a" * 37, "short")
        with self.assertRaises(ValueError):
            message_frame(1, "short", "a" * 230)

    def test_fragmented_reply_matches_opcode_and_sequence(self):
        import asyncio
        class Value:
            def __init__(self, value): self.value = value
        async def check():
            sender = WatchNotifications("00:00:00:00:00:00", None)
            future = asyncio.get_running_loop().create_future()
            sender.pending[(161, 23)] = future
            packet = bytes.fromhex("fedcba00a1000400170201ef")
            sender.changed("org.bluez.GattCharacteristic1", {"Value": Value(packet[:5])}, [])
            self.assertFalse(future.done())
            sender.changed("org.bluez.GattCharacteristic1", {"Value": Value(packet[5:])}, [])
            self.assertEqual(await future, (0, b"\x02\x01"))
        asyncio.run(check())
