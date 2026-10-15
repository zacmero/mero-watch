"""Host lifecycle/command tests; these do not prove the watch's UI ABI."""
import ctypes
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = r'''
#include <stdlib.h>
#include <string.h>
typedef unsigned int u32;
static unsigned char elements[7][208];
static int allocations, fail_alloc, redraws, menus;
static u32 window;
void *mero_ui_alloc(u32 size) {
    if (fail_alloc) return 0;
    void *p = calloc(1, size); if (p) ++allocations; return p;
}
void mero_ui_free(void *p) { if (p) { --allocations; free(p); } }
int mero_ui_text(void *e, const char *code, const char *text, int n, int mode) {
    if (strcmp(code, "ascii") || mode || n < 0 || n > 63) abort();
    *(const char **)((unsigned char *)e + 112) = text; return 0;
}
void *mero_ui_element(u32 id) {
    if ((id & ~0x3ffu) != ((119u << 17) | 0x3000u) || (id & 0x3ffu) > 6) return 0;
    return elements[id & 0x3ffu];
}
int mero_ui_redraw(void *e) { (void)e; return ++redraws; }
int mero_ui_window(u32 id) { window = id; return 0; }
int mero_ui_menu(void) { return ++menus; }
void *test_element(int index) {
    *(u32 *)(elements[index] + 4) = (119u << 17) | 0x3000u | index;
    return elements[index];
}
const char *test_text(int index) { return *(const char **)(elements[index] + 112); }
int test_allocations(void) { return allocations; }
int test_redraws(void) { return redraws; }
int test_menus(void) { return menus; }
u32 test_window(void) { return window; }
void test_fail(int value) { fail_alloc = value; }
'''


@unittest.skipUnless(shutil.which('cc'), 'host C compiler unavailable')
class NativeShellTest(unittest.TestCase):
    def test_readout_refresh_back_and_release(self):
        libc = ctypes.CDLL(None, use_errno=True)
        libc.mmap.restype = ctypes.c_void_p
        address = libc.mmap(ctypes.c_void_p(0x100000), 0x20000, 3, 0x100022, -1, 0)
        if address != 0x100000:
            self.skipTest('synthetic low-address RAM mapping unavailable')
        try:
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                (folder / 'fixture.c').write_text(FIXTURE)
                subprocess.run(['cc', '-shared', '-fPIC', '-O2',
                    str(ROOT / 'native/mero_shell.c'), str(ROOT / 'native/mero_specs.c'),
                    str(folder / 'fixture.c'), '-o', str(folder / 'shell.so')], check=True, capture_output=True)
                lib = ctypes.CDLL(str(folder / 'shell.so'))
                lib.test_element.restype = ctypes.c_void_p
                lib.test_text.restype = ctypes.c_char_p
                lib.mero_shell_text_change.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
                lib.mero_shell_touch.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint)]
                lib.mero_menu_touch.argtypes = lib.mero_shell_touch.argtypes
                ctypes.c_ushort.from_address(0x10f38c).value = 100
                ctypes.c_ushort.from_address(0x10f38e).value = 110
                ctypes.c_uint.from_address(0x10b300).value = 900
                ctypes.c_uint.from_address(0x10b2fc).value = 600
                ram = ctypes.string_at(address, 0x20000)
                elements = [lib.test_element(index) for index in range(7)]
                for element in elements:
                    self.assertEqual(lib.mero_shell_text_change(element, 1, None), 0)
                self.assertEqual(lib.test_allocations(), 7)
                self.assertEqual([lib.test_text(i) for i in range(7)], [
                    b'mero-shell', b'free heap: 900 B', b'low heap: 600 B',
                    b'physical pool: 1280 B', b'ISA: PI32v2/r3', b'Refresh', b'Back'])
                self.assertEqual(ctypes.string_at(address, 0x20000), ram)
                down, up = (ctypes.c_uint * 1)(0), (ctypes.c_uint * 1)(7)
                self.assertEqual(lib.mero_shell_touch(elements[5], down), 0)
                ctypes.c_uint.from_address(0x10b300).value = 850
                self.assertEqual(lib.mero_shell_touch(elements[5], up), 1)
                self.assertEqual(lib.test_text(1), b'free heap: 850 B')
                self.assertEqual(lib.test_redraws(), 5)
                ctypes.c_uint.from_address(0x10b2fc).value = 1000
                lib.mero_shell_touch(elements[5], up)
                self.assertEqual(lib.test_text(1), b'free heap: unavailable')
                self.assertEqual(lib.mero_shell_touch(elements[6], up), 1)
                self.assertEqual(lib.test_menus(), 1)
                self.assertEqual(lib.mero_menu_touch(None, up), 1)
                self.assertEqual(lib.test_window(), (119 << 17) | 0x800 | 119)
                for element in elements:
                    lib.mero_shell_text_change(element, 10, None)
                self.assertEqual(lib.test_allocations(), 0)
                self.assertIsNone(lib.test_text(0))
                lib.test_fail(1)
                lib.mero_shell_text_change(elements[0], 1, None)
                self.assertIsNone(lib.test_text(0))
                lib.mero_shell_text_change(elements[0], 10, None)
                self.assertEqual(lib.test_allocations(), 0)
        finally:
            libc.munmap(ctypes.c_void_p(address), 0x20000)
