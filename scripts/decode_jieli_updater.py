#!/usr/bin/env python3
"""Decode inspected Jieli updater chunks offline, with header/decoded CRC checks.

The observed LZ4-style chunks share history and permit a terminal match.
This performs no loader activation or device operation.
"""
import argparse
import binascii
import json
from pathlib import Path
import struct


def decode_block(encoded, expected, history):
    output = bytearray(history)
    base, position = len(output), 0

    def extended(value):
        nonlocal position
        if value == 15:
            while True:
                if position >= len(encoded):
                    raise ValueError("Truncated length extension")
                extra = encoded[position]
                position += 1
                value += extra
                if extra != 255:
                    break
        return value

    while position < len(encoded):
        token = encoded[position]
        position += 1
        literals = extended(token >> 4)
        if position + literals > len(encoded) or len(output) + literals > base + expected:
            raise ValueError("Literal extent exceeds input/output")
        output.extend(encoded[position:position + literals])
        position += literals
        if position == len(encoded):
            break
        if position + 2 > len(encoded):
            raise ValueError("Truncated match offset")
        distance = int.from_bytes(encoded[position:position + 2], "little")
        position += 2
        count = extended(token & 15) + 4
        if not distance or distance > len(output) or len(output) + count > base + expected:
            raise ValueError("Match extent exceeds history/output")
        for _ in range(count):
            output.append(output[-distance])
    if len(output) - base != expected:
        raise ValueError("Decoded chunk length mismatch")
    return bytes(output[base:])


def decode(data):
    if len(data) < 32 or len(data) > 16_000_000:
        raise ValueError("Unsupported updater extent")
    hcrc, dcrc, expected, address_field, reserved, name = struct.unpack_from("<HHIII16s", data)
    if binascii.crc_hqx(data[2:32], 0) != hcrc:
        raise ValueError("Updater header CRC mismatch")
    if not 0 < expected <= 10_000_000:
        raise ValueError("Decoded updater exceeds lab bounds")
    position, chunks = 32, 0
    output = bytearray()
    while len(output) < expected:
        if position + 8 > len(data):
            raise ValueError("Truncated chunk header")
        compressed, plain = struct.unpack_from("<II", data, position)
        position += 8
        if (not 0 < compressed <= len(data) - position or not 0 < plain <= 4096
                or len(output) + plain > expected):
            raise ValueError("Invalid chunk bounds")
        output.extend(decode_block(data[position:position + compressed], plain, output))
        position += compressed
        chunks += 1
    if binascii.crc_hqx(output, 0) != dcrc:
        raise ValueError("Decoded updater CRC mismatch")
    return bytes(output), {"name": name.split(b"\0")[0].decode("ascii", "replace"),
                           "decoded_bytes": len(output), "chunks": chunks,
                           "address_field": address_field, "reserved_field": reserved,
                           "trailer_bytes": len(data) - position,
                           "header_crc_valid": True, "decoded_crc_valid": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output, summary = decode(args.input.read_bytes())
    import os
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(output)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
