import unittest
from scripts.native_panel_probe import checked_code, hook_call, patches, ENTRY, HOOK


class NativeProbeTests(unittest.TestCase):
    def test_compiled_artifact_damage_and_wrong_size_are_rejected(self):
        code = bytes.fromhex(
            "7404e29fc0ff02301400beea1a77041604524022c1ff1f45080602f1b5198020"
            "432a4016bfea35df50ee400220ea04404016beea4d7c02815404")
        self.assertEqual(checked_code(code), code)
        with self.assertRaises(ValueError):
            checked_code(code[:-1])
        with self.assertRaises(ValueError):
            checked_code(bytes([code[0] ^ 1]) + code[1:])
        with self.assertRaises(ValueError):
            patches(b"unverified application", code)

    def test_hook_retains_width_and_calls_exact_compiled_entry(self):
        call = hook_call()
        self.assertEqual(len(call), 6)
        self.assertEqual(call[:2], b"\x80\xff")
        self.assertEqual(HOOK + 6 + int.from_bytes(call[2:], "little", signed=True), ENTRY)
