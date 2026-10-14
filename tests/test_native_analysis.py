import re
import struct
import unittest
from scripts.native_firmware_map import runtime_address, elf32, FLASH_BASE
from scripts.native_code_index import index, direct_call
from scripts.native_style_inventory import inventory
import binascii


class NativeAnalysisTests(unittest.TestCase):
    def test_style_checks_and_relocation_bounds(self):
        data = bytearray(52)
        data[17] = 1
        struct.pack_into("<IIIH", data, 24, 44, 8, 48, 2)
        struct.pack_into("<H", data, 48, 0)
        crc = lambda b: binascii.crc_hqx(b, 0)
        struct.pack_into("<HHH", data, 38, crc(data[44:52]),
                         crc(data[48:50]), crc(data[24:38]))
        window = inventory(data)["windows"][0]
        self.assertTrue(window["reference_data_crc_matches"])
        self.assertTrue(window["header_crc_matches"])
        self.assertTrue(window["table_crc_matches"])
        struct.pack_into("<I", data, 44, 0x04000000)
        tagged = inventory(data)["windows"][0]
        self.assertFalse(tagged["reference_data_crc_matches"])
        self.assertTrue(tagged["normalized_data_crc_matches"])
        self.assertEqual(tagged["pointer_tags"], [512])
        data[44] ^= 1
        self.assertFalse(inventory(data)["windows"][0]["reference_data_crc_matches"])
        self.assertFalse(inventory(data)["windows"][0]["normalized_data_crc_matches"])
        struct.pack_into("<H", data, 48, 6)
        with self.assertRaises(ValueError):
            inventory(data)

    def test_startup_copy_boundaries_and_kernel_runtime(self):
        self.assertEqual(runtime_address(0), FLASH_BASE)
        self.assertEqual(runtime_address(0x06117798 - FLASH_BASE), 0x00104840)
        self.assertEqual(runtime_address(0x0611c1b4 - FLASH_BASE), 0x0011d960)
        self.assertEqual(runtime_address(1179860), 0x001219a0)
        with self.assertRaises(ValueError):
            runtime_address(1200992)

    def test_elf_wrapper_preserves_bytes_and_bss_has_no_payload(self):
        blob = elf32([(".code", 0x1000, b"ABCD", 6, 4),
                      (".bss", 0x2000, None, 3, 100)], 0x1000)
        head = struct.unpack_from("<16sHHIIIIIHHHHHH", blob)
        self.assertEqual(head[2], 241)
        self.assertEqual(head[4], 0x1000)
        first = struct.unpack_from("<10I", blob, head[6] + 40)
        second = struct.unpack_from("<10I", blob, head[6] + 80)
        self.assertEqual(blob[first[4]:first[4] + first[5]], b"ABCD")
        self.assertEqual(second[1], 8)
        self.assertEqual(second[5], 100)

    def test_call_rule_matches_next_instruction_relative_semantics(self):
        self.assertEqual(direct_call(0x1000, 6, "call -10"), 0xffc)
        self.assertIsNone(direct_call(0x1000, 2, "call r2"))

    def test_linear_tracker_drops_values_after_branch_and_compound_write(self):
        text = """1000: c4 ff 00 20 00 00 r4 = 8192
1006: c0 ff 00 00 00 00 r0 = 0
100c: 00 00 r1 = r4 + r0
100e: 00 00 r4 += 1
1010: 00 00 r2 = r4
1012: c4 ff 00 20 00 00 r4 = 8192
1018: 00 00 if (r0 == 0) goto 0
101a: 00 00 r3 = r4
"""
        result = index(text, b"ui_label\0", 8192, False, re.compile("ui_label"))
        self.assertEqual([r["instruction"] for r in result["string_references"]],
                         [0x1000, 0x100c, 0x1012])
