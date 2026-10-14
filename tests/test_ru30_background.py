import binascii
import hashlib
import struct
import unittest
from scripts.ru30_background import decode, encode


class BackgroundTests(unittest.TestCase):
    def test_matches_independently_emulated_vendor_flat_fixture(self):
        resource = encode(4, 4, bytes([18, 20, 24, 255]) * 16)
        self.assertEqual(hashlib.sha256(resource).hexdigest(),
                         "662a7dabbde697c5fdd457c1c69a577c33763ee46a5045e3211111a0396ae584")
        self.assertEqual(decode(resource), (4, 4, bytes([16, 20, 24, 255]) * 16))

    def test_alpha_and_long_runs_survive_rgb565_roundtrip(self):
        rgba = bytes([255, 0, 0, 0]) * 130 + bytes([0, 255, 0, 128]) * 130
        self.assertEqual(decode(encode(260, 1, rgba)), (260, 1, rgba))

    def test_checksum_damage_is_rejected(self):
        resource = bytearray(encode(2, 2, bytes([0, 0, 0, 255]) * 4))
        resource[-1] ^= 1
        with self.assertRaisesRegex(ValueError, "checksum"):
            decode(resource)

    def test_row_outside_payload_is_rejected_even_with_valid_checksums(self):
        resource = bytearray(encode(2, 2, bytes([0, 0, 0, 255]) * 4))
        struct.pack_into("<I", resource, 1104, 0x1fffff)
        struct.pack_into("<H", resource, 62, binascii.crc_hqx(resource[1104:], 0))
        struct.pack_into("<H", resource, 60, binascii.crc_hqx(resource[62:80], 0))
        with self.assertRaisesRegex(ValueError, "extent"):
            decode(resource)

    def test_other_resource_types_are_not_silently_accepted(self):
        resource = bytearray(encode(1, 1, bytes([0, 0, 0, 255])))
        resource[67] = 0x20
        with self.assertRaisesRegex(ValueError, "format"):
            decode(resource)
