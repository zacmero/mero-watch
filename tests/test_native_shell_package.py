import struct
import unittest

from scripts.native_shell_package import (APP_BASE, CALLBACK_END, CALLBACK_START,
                                         MODULE_BASE, module_bytes, build)


class NativeShellPackageTests(unittest.TestCase):
    def test_preserve_factory_handlers_and_callback_field_order(self):
        app = bytearray(CALLBACK_END - APP_BASE)
        factory = bytes(range(256)) * 43 + bytes(range(144))
        self.assertEqual(len(factory), 697 * 16)
        app[CALLBACK_START - APP_BASE:] = factory
        symbols = dict(mero_shell_text_change=0x100, mero_shell_touch=0x200,
                       mero_menu_touch=0x300, mero_menu_text_change=0x400)
        module, begin, end = module_bytes(app, b'abc', symbols)
        self.assertEqual(begin, MODULE_BASE + 4)
        self.assertEqual(end - begin, 710 * 16)
        self.assertEqual(module[4:4 + len(factory)], factory)
        records = list(struct.iter_unpack('<4I', module[4 + len(factory):]))
        self.assertEqual(records[0], ((119 << 17) | 0x3000, 0, 0, 0x100))
        self.assertEqual(records[5][1:], (0x200, 0, 0x100))
        self.assertEqual(records[7][1:], (0x300, 0, 0))
        self.assertEqual(records[8][1:], (0, 0, 0x400))

    def test_reject_nonstock_before_parsing_or_modifying(self):
        with self.assertRaisesRegex(ValueError, 'protected original'):
            build(b'not stock', b'', {}, None)
