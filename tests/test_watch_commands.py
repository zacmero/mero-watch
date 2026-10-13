import asyncio
import io
import unittest
from scripts import watch_commands as commands


class WatchCommandTests(unittest.TestCase):
    def test_one_action_per_press_ignores_release_repeat_and_unmapped_events(self):
        records = [(1, 200, 1), (1, 200, 2), (1, 200, 0), (0, 0, 0),
                   (1, 201, 1), (1, 201, 0), (1, 199, 1)]
        data = b"".join(commands.INPUT_EVENT.pack(0, 0, *event) for event in records)
        self.assertEqual(list(commands.input_commands(io.BytesIO(data))), ["status", "identify"])

    def test_truncated_stream_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Truncated"):
            list(commands.input_commands(io.BytesIO(b"\0")))

    def test_identify_requires_explicit_target(self):
        with self.assertRaisesRegex(ValueError, "address"):
            asyncio.run(commands.execute("identify"))

    def test_unmapped_command_cannot_execute(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            asyncio.run(commands.execute("reboot"))


if __name__ == "__main__":
    unittest.main()
