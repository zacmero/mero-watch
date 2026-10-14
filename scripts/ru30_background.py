#!/usr/bin/env python3
"""Offline codec for the single-image RU30 backgrounds observed on this watch.

Validated layout: BGP_B131/BGP_C131 and GFit's BR28 converter output.
This handles alpha + RGB565 RLE backgrounds, not arbitrary face/UI bundles.
It performs no Bluetooth operations. Pillow is needed only for the CLI.
"""
import argparse
import binascii
from pathlib import Path
import struct

PREFIX = bytes.fromhex("525533300003010001000000000000000000000018000000")
SECTIONS = struct.pack("<IHHIIHHI", 48, 1, 84, 0, 60, 1, 80, 0)
TEXT_RECORD = struct.pack("<III", 256, 80, 1024)
IMAGE_OFFSET = 1104
IMAGE_ID_FLAGS = 0x30010000


def encode_row(pixels):
    result = bytearray()
    i = 0
    while i < len(pixels):
        count = 1
        while count < 127 and i + count < len(pixels) and pixels[i + count] == pixels[i]:
            count += 1
        if count >= 2:
            result.append(128 | count)
            result.extend(pixels[i])
            i += count
        else:
            start = i
            i += 1
            while i - start < 127 and i < len(pixels):
                if i + 1 < len(pixels) and pixels[i] == pixels[i + 1]:
                    break
                i += 1
            result.append(i - start)
            result.extend(b"".join(pixels[start:i]))
    return bytes(result)


def decode_row(data, width):
    pixels = []
    position = 0
    while position < len(data):
        tag = data[position]
        position += 1
        count = tag & 127
        needed = 3 if tag & 128 else count * 3
        if count == 0 or position + needed > len(data) or len(pixels) + count > width:
            raise ValueError("Invalid or oversized RLE run")
        if tag & 128:
            pixels.extend([data[position:position + 3]] * count)
        else:
            pixels.extend(data[i:i + 3] for i in range(position, position + needed, 3))
        position += needed
    if len(pixels) != width:
        raise ValueError("RLE row does not match image width")
    return pixels


def encode(width, height, rgba):
    if not 1 <= width <= 1024 or not 1 <= height <= 1024 or len(rgba) != width * height * 4:
        raise ValueError("Invalid dimensions or RGBA byte length")
    rows = []
    for y in range(height):
        pixels = []
        for i in range(y * width * 4, (y + 1) * width * 4, 4):
            red, green, blue, alpha = rgba[i:i + 4]
            color = (red >> 3) << 11 | (green >> 2) << 5 | blue >> 3
            pixels.append(bytes([alpha, color >> 8, color & 255]))
        rows.append(encode_row(pixels))
    offset = height * 4
    table = bytearray()
    for row in rows:
        if offset >= 1 << 21 or len(row) >= 1 << 11:
            raise ValueError("Image exceeds observed packed-row field limits")
        table.extend(struct.pack("<I", offset | len(row) << 21))
        offset += len(row)
    blob = bytes(table) + b"".join(rows)
    record = struct.pack("<HHIHHII", 0, binascii.crc_hqx(blob, 0), IMAGE_ID_FLAGS,
                         width, height, len(blob), IMAGE_OFFSET)
    record = struct.pack("<H", binascii.crc_hqx(record[2:], 0)) + record[2:]
    return PREFIX + SECTIONS + TEXT_RECORD + record + bytes(1024) + blob


def decode(resource):
    if len(resource) < IMAGE_OFFSET or resource[:24] != PREFIX or resource[24:48] != SECTIONS:
        raise ValueError("Unsupported RU30 background layout")
    if resource[48:60] != TEXT_RECORD:
        raise ValueError("Unsupported string record")
    header_crc, data_crc, flags, width, height, length, offset = struct.unpack_from(
        "<HHIHHII", resource, 60)
    if flags != IMAGE_ID_FLAGS or offset != IMAGE_OFFSET:
        raise ValueError("Unsupported picture format")
    if not 1 <= width <= 1024 or not 1 <= height <= 1024 or length < height * 4:
        raise ValueError("Invalid dimensions or image length")
    if offset + length != len(resource):
        raise ValueError("Image extent mismatch")
    blob = resource[offset:]
    if (header_crc != binascii.crc_hqx(resource[62:80], 0)
            or data_crc != binascii.crc_hqx(blob, 0)):
        raise ValueError("Background checksum mismatch")
    rgba = bytearray()
    for y in range(height):
        packed = struct.unpack_from("<I", blob, y * 4)[0]
        start, size = packed & 0x1fffff, packed >> 21
        if start < height * 4 or start + size > length:
            raise ValueError("Row extent outside image")
        for alpha, high, low in decode_row(blob[start:start + size], width):
            color = high << 8 | low
            red, green, blue = color >> 11, color >> 5 & 63, color & 31
            rgba.extend((red << 3 | red >> 2, green << 2 | green >> 4,
                         blue << 3 | blue >> 2, alpha))
    return width, height, bytes(rgba)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("encode", "decode"))
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    from PIL import Image
    if args.action == "encode":
        with Image.open(args.input) as image:
            image = image.convert("RGBA")
            data = encode(image.width, image.height, image.tobytes())
        args.output.write_bytes(data)
    else:
        width, height, rgba = decode(args.input.read_bytes())
        Image.frombytes("RGBA", (width, height), rgba).save(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
