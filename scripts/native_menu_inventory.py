"""Read-only, stock-specific menu-to-window evidence inventory.

Addresses come from the observed PI32v2 dispatcher, not the reference SDK.
This does not add an app or alter firmware.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

APP_SHA256 = "9117eea8ff2f1694a16d57f16850100692c2ff8bfc3b66bfd8ede9c76c0e5ae4"
APP_BASE = 0x06000120
MENU_ADDRESS = 0x0609A990
HANDLERS_BEGIN = 0x06114B98
HANDLERS_END = 0x06117728


def inventory(app):
    if hashlib.sha256(app).hexdigest() != APP_SHA256:
        raise ValueError("unrecognized app; fixed addresses are stock-specific")
    handlers = {}
    for address in range(HANDLERS_BEGIN, HANDLERS_END, 16):
        control, touch, key, change = struct.unpack_from("<4I", app, address - APP_BASE)
        handlers.setdefault(control, []).append(dict(
            record_address=address, touch=touch, key=key, change=change))
    entries = []
    for index in range(37):
        address = MENU_ADDRESS + 32 * index
        fields = struct.unpack_from("<8I", app, address - APP_BASE)
        first, second, reserved1, third, reserved2, window, before, ordinal = fields
        if reserved1 or reserved2 or ordinal != index:
            raise ValueError("menu record differs from observed structure")
        entries.append(dict(index=index, address=address,
            menu_control_ids=[first, second, third], target_window_id=window,
            prelaunch_callback=before, target_handlers=handlers.get(window, []),
            menu_handlers=[handlers.get(control, []) for control in (first, second, third)]))
    return dict(app_sha256=APP_SHA256, dispatcher=0x0603E320,
                entry_size=32, entries=entries,
                limits="Observed dispatcher/table correlation; app names, icon assignment, "
                       "duplicate-handler selection and cloning are not yet validated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", type=Path)
    args = parser.parse_args()
    print(json.dumps(inventory(args.app.read_bytes()), indent=2))
