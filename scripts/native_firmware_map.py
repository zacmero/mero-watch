#!/usr/bin/env python3
"""Offline ELF wrappers using startup-observed mappings of the exact watch app.

ELF wrappers are analysis artifacts, not installable firmware. No original
instruction is changed. Updater bases supplied by the caller remain hypotheses.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

FLASH_BASE = 0x06000120
APP_SHA256 = "9117eea8ff2f1694a16d57f16850100692c2ff8bfc3b66bfd8ede9c76c0e5ae4"
DATA_SOURCE, DATA_DEST, DATA_SIZE = 0x06117798, 0x00104840, 18972
CODE_SOURCE, CODE_DEST, CODE_SIZE = 0x0611c1b4, 0x0011d960, 37580
BSS_BASE, BSS_SIZE = 0x00109260, 83712


def runtime_address(file_offset):
    if not 0 <= file_offset < CODE_SOURCE - FLASH_BASE + CODE_SIZE:
        raise ValueError("Offset outside inspected app")
    if file_offset < DATA_SOURCE - FLASH_BASE:
        return FLASH_BASE + file_offset
    if file_offset < CODE_SOURCE - FLASH_BASE:
        return DATA_DEST + file_offset - (DATA_SOURCE - FLASH_BASE)
    return CODE_DEST + file_offset - (CODE_SOURCE - FLASH_BASE)


def elf32(sections, entry):
    """sections: (name, address, bytes or None, flags, memory_size)."""
    names = b"\0" + b"".join(name.encode() + b"\0" for name, *_ in sections) + b".shstrtab\0"
    name_offsets = {}
    position = 1
    for name, *_ in sections:
        name_offsets[name] = position
        position += len(name) + 1
    names_name = position
    data = bytearray(256)
    headers = [(0,) * 10]
    for name, address, payload, flags, size in sections:
        offset = len(data)
        if payload is not None:
            if len(payload) != size:
                raise ValueError("Section size mismatch")
            data.extend(payload)
        headers.append((name_offsets[name], 8 if payload is None else 1, flags,
                        address, offset, size, 0, 0, 4, 0))
    names_offset = len(data)
    data.extend(names)
    headers.append((names_name, 3, 0, 0, names_offset, len(names), 0, 0, 1, 0))
    data.extend(bytes(-len(data) % 4))
    section_offset = len(data)
    for header in headers:
        data.extend(struct.pack("<10I", *header))
    identity = b"\x7fELF\x01\x01\x01" + bytes(9)
    # Machine 241 / flags 0 match the inspected PI32v2 reference and app wrapper.
    data[:52] = struct.pack("<16sHHIIIIIHHHHHH", identity, 2, 241, 1, entry, 0,
                            section_offset, 0, 52, 0, 0, 40, len(headers), len(headers) - 1)
    return bytes(data)


def map_app(payload):
    if hashlib.sha256(payload).hexdigest() != APP_SHA256:
        raise ValueError("Application differs from exact inspected stock bytes")
    data_offset, code_offset = DATA_SOURCE - FLASH_BASE, CODE_SOURCE - FLASH_BASE
    if DATA_SOURCE + DATA_SIZE != CODE_SOURCE or code_offset + CODE_SIZE != len(payload):
        raise ValueError("Startup copy partition does not cover application")
    return elf32([
        (".flash", FLASH_BASE, payload[:data_offset], 6, data_offset),
        (".ram_data", DATA_DEST, payload[data_offset:code_offset], 3, DATA_SIZE),
        (".ram_code", CODE_DEST, payload[code_offset:], 6, CODE_SIZE),
        (".bss", BSS_BASE, None, 3, BSS_SIZE),
    ], FLASH_BASE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("app", "single"))
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), help="Analysis base for single-image wrapper")
    args = parser.parse_args()
    payload = args.input.read_bytes()
    if args.kind == "app":
        output = map_app(payload)
    else:
        if args.base is None:
            parser.error("single-image analysis requires --base")
        output = elf32([(".text", args.base, payload, 6, len(payload))], args.base)
    import os
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(output)
    print(json.dumps({"kind": args.kind, "input_bytes": len(payload), "elf_bytes": len(output),
                      "device_execution": "not_performed"}))


if __name__ == "__main__":
    main()
