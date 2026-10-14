import struct
import unittest
from scripts.native_control_tree import control_tree


class ControlTreeTests(unittest.TestCase):
    def fixture(self):
        data = bytearray(108)
        for offset, kind, children, size in [(0, 2, 2, 0), (28, 3, 1, 28),
                                              (56, 12, 0, 28), (84, 7, 0, 24)]:
            data[offset:offset + 4] = bytes([kind, children, 0, size])
        struct.pack_into("<I", data, 24, 0x0400001c)
        struct.pack_into("<I", data, 52, 0x04000054)
        return data

    def test_siblings_precede_nested_children_and_tags_are_preserved(self):
        data = self.fixture()
        original = bytes(data)
        root = control_tree(data, [24, 52])
        self.assertEqual([c["offset"] for c in root["children"]], [28, 56])
        self.assertEqual(root["children"][0]["children"][0]["offset"], 84)
        self.assertEqual(bytes(data), original)

    def test_cycles_and_unrelocated_children_are_rejected(self):
        with self.assertRaises(ValueError):
            control_tree(self.fixture(), [24])
        data = self.fixture()
        struct.pack_into("<I", data, 52, 0x0400001c)
        with self.assertRaises(ValueError):
            control_tree(data, [24, 52])
