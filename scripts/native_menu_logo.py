"""Offline bounded replacement of the observed Calculator menu icon.

Produces a resource file only, not an installable firmware package. Requires
Pillow for the investigator-authored vector-like logo rasterization.
"""
import argparse
import binascii
import hashlib
from pathlib import Path
import struct

from PIL import Image, ImageDraw

if __package__:
    from .ru30_background import encode_row, decode_row
else:
    from ru30_background import encode_row, decode_row

STOCK_SHA256 = "52ec6f8d3849962b6bccf910fea0d77e6ac7e847abfbff1cdcac88e6b7117c0f"
ALIASES = (158820, 377948, 5848101)
PAYLOAD = 213454
CAPACITY = 2658


def logo():
    image = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((1, 1, 48, 48), fill=(0, 192, 224, 255))
    draw.line([(13, 35), (13, 15), (25, 28), (37, 15), (37, 35)],
              fill=(255, 255, 255, 255), width=5)
    return image


def replace(resource):
    if hashlib.sha256(resource).hexdigest() != STOCK_SHA256:
        raise ValueError("unrecognized resource; fixed bounds are stock-specific")
    image = logo()
    rows = []
    for y in range(50):
        pixels = []
        for x in range(50):
            r, g, b, a = image.getpixel((x, y))
            color = (r >> 3) << 11 | (g >> 2) << 5 | b >> 3
            pixels.append(bytes((a, color >> 8, color & 255)))
        rows.append((pixels, encode_row(pixels)))
    offset = 200
    table = bytearray()
    data = bytearray()
    for pixels, row in rows:
        if decode_row(row, 50) != pixels:
            raise ValueError("logo row roundtrip failed")
        table.extend(struct.pack("<I", offset | len(row) << 21))
        data.extend(row)
        offset += len(row)
    if offset > CAPACITY:
        raise ValueError("logo exceeds existing image capacity")
    payload = bytes(table + data).ljust(CAPACITY, b"\0")
    output = bytearray(resource)
    original_payload = resource[PAYLOAD:PAYLOAD + CAPACITY]
    for header in ALIASES:
        hc, dc, flags, width, height, length, start = struct.unpack_from(
            "<HHIHHII", resource, header)
        if (flags, width, height, length, start) != (0x30160000, 50, 50, CAPACITY, PAYLOAD):
            raise ValueError("icon descriptor differs from observation")
        if hc != binascii.crc_hqx(resource[header + 2:header + 20], 0) or dc != binascii.crc_hqx(original_payload, 0):
            raise ValueError("original icon checksum mismatch")
        struct.pack_into("<H", output, header + 2, binascii.crc_hqx(payload, 0))
        struct.pack_into("<H", output, header, binascii.crc_hqx(output[header + 2:header + 20], 0))
    output[PAYLOAD:PAYLOAD + CAPACITY] = payload
    allowed = set(range(PAYLOAD, PAYLOAD + CAPACITY))
    for header in ALIASES:
        allowed.update(range(header, header + 4))
    if len(output) != len(resource) or any(a != b and i not in allowed
            for i, (a, b) in enumerate(zip(resource, output))):
        raise ValueError("unexpected resource change")
    return bytes(output), image, offset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resource", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("preview", type=Path)
    args = parser.parse_args()
    patched, image, used = replace(args.resource.read_bytes())
    with args.output.open("xb") as file:
        file.write(patched)
    args.output.chmod(0o600)
    image.save(args.preview)
    print(f"Verified logo: {used}/{CAPACITY} bytes; three menu aliases; resource only")
