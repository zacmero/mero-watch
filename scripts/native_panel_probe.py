"""Exact-stock, bounded patches for the first compiled native C UI probe."""
import hashlib
if __package__:
    from .native_firmware_map import APP_SHA256, FLASH_BASE
else:
    from native_firmware_map import APP_SHA256, FLASH_BASE


ENTRY = 0x0603f01a
HOOK = 0x0603f178
MARKER = 0x06084ed4
CODE_SHA256 = "dda5c95217e10d0a1d281c2c15e41a5b3afeb92dcb0613fc0780614edc8a61ea"
SLOT_SHA256 = "8150090421d37d82c3a06f038aa6666a2119ecbc3ccf6608e837c3e98d0894d6"
OLD_HOOK = bytes.fromhex("80ff0e5f0800")


def checked_code(code):
    if len(code) != 58 or hashlib.sha256(code).hexdigest() != CODE_SHA256:
        raise ValueError("native probe is not the inspected 58-byte compiled artifact")
    return code


def hook_call():
    # Observed six-byte PI32v2 call: signed LE displacement from next PC.
    return OLD_HOOK[:2] + (ENTRY - HOOK - 6).to_bytes(4, "little", signed=True)


def patches(app, code):
    checked_code(code)
    if hashlib.sha256(app).hexdigest() != APP_SHA256:
        raise ValueError("native probe requires exact inspected stock application")
    offset = ENTRY - FLASH_BASE
    if hashlib.sha256(app[offset:offset + 58]).hexdigest() != SLOT_SHA256:
        raise ValueError("native function boundary or original bytes differ")
    if app[HOOK - FLASH_BASE:HOOK - FLASH_BASE + 6] != OLD_HOOK:
        raise ValueError("Music initialization diagnostic call differs")
    if app[MARKER - FLASH_BASE:MARKER - FLASH_BASE + 11] != b"Apple Watch":
        raise ValueError("marker literal differs at the traced application address")
    return [(offset, code), (HOOK - FLASH_BASE, hook_call()),
            (MARKER - FLASH_BASE, b"mero-watch\0")]
