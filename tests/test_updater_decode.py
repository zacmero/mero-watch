import binascii
import struct
import unittest
from scripts.decode_jieli_updater import decode, decode_block


class UpdaterDecodeTests(unittest.TestCase):
    def test_terminal_match_can_reference_previous_chunk(self):
        self.assertEqual(decode_block(b"\x30ABC", 3, b""), b"ABC")
        self.assertEqual(decode_block(b"\0\x03\0", 4, b"ABC"), b"ABCA")

    def test_invalid_match_and_truncated_length_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Match extent"):
            decode_block(b"\0\x01\0", 4, b"")
        with self.assertRaisesRegex(ValueError, "length extension"):
            decode_block(b"\xf0", 4, b"")

    def test_container_checks_both_crc_layers(self):
        plain = b"ABCABCA"
        header = struct.pack("<HHIII16s", 0, binascii.crc_hqx(plain, 0), 7, 0, 0, b"test.bin")
        header = struct.pack("<H", binascii.crc_hqx(header[2:], 0)) + header[2:]
        payload = struct.pack("<II", 4, 3) + b"\x30ABC" + struct.pack("<II", 3, 4) + b"\0\x03\0"
        output, summary = decode(header + payload)
        self.assertEqual(output, plain)
        self.assertEqual(summary["chunks"], 2)
        damaged = bytearray(header + payload)
        damaged[41] = ord("D")
        with self.assertRaisesRegex(ValueError, "Decoded updater CRC"):
            decode(damaged)
        damaged[0] ^= 1
        with self.assertRaisesRegex(ValueError, "header CRC"):
            decode(damaged)
