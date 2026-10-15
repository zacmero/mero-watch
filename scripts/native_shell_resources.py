"""Extend the observed RU30 image directory, retaining every original bitmap.

Adds menu image39 and a resource-page alias for the new shell window. This is
the observed JL.res format only; it is not a general RU30/STR encoder.
"""
import binascii
import hashlib
import struct

from .native_menu_logo import replace, PAYLOAD, CAPACITY, STOCK_SHA256
from .native_shell_style import MENU_PAGES, SHELL_PAGE, MENU_IMAGE_ID


def crc(data):
    return binascii.crc_hqx(data, 0)


def image_records(data):
    count = struct.unpack_from('<I', data, 8)[0]
    for index in range(count):
        identifier, position = struct.unpack_from('<II', data, 16 + index * 8)
        if identifier != index or position + 24 > len(data):
            raise ValueError('unexpected image-page directory')
        table, entries = struct.unpack_from('<IH', data, position + 12)
        if table + entries * 20 > len(data):
            raise ValueError('image table outside file')
        for entry in range(entries):
            header = table + entry * 20
            values = struct.unpack_from('<HHIHHII', data, header)
            hc, dc, flags, width, height, size, start = values
            if start + size > len(data) or hc != crc(data[header + 2:header + 20]) or dc != crc(data[start:start + size]):
                raise ValueError('image descriptor/payload CRC failed')
            yield index, entry, header, values


def build(stock):
    if hashlib.sha256(stock).hexdigest() != STOCK_SHA256:
        raise ValueError('unrecognized image resource')
    if struct.unpack_from('<I', stock, 8)[0] != SHELL_PAGE:
        raise ValueError('unexpected original image page count')
    records = list(image_records(stock))
    old_directory_end = 16 + 8 * SHELL_PAGE
    output = bytearray(stock[:old_directory_end] + bytes(8) + stock[old_directory_end:])
    struct.pack_into('<I', output, 8, SHELL_PAGE + 1)
    for page in range(SHELL_PAGE):
        _, group = struct.unpack_from('<II', stock, 16 + page * 8)
        if group < old_directory_end:
            raise ValueError('unexpected pre-directory group')
        struct.pack_into('<I', output, 20 + page * 8, group + 8)
        if any(struct.unpack_from('<I', stock, group + field)[0] for field in (8, 20)):
            raise ValueError('unrecognized nonzero group reserved field')
        text_table, text_count = struct.unpack_from('<IH', stock, group)
        images, image_count = struct.unpack_from('<IH', stock, group + 12)
        if text_table:
            struct.pack_into('<I', output, group + 8, text_table + 8)
        if images:
            struct.pack_into('<I', output, group + 20, images + 8)
        for index in range(text_count):
            old = text_table + 12 * index
            start, size = struct.unpack_from('<II', stock, old + 4)
            if start < old_directory_end or start + size > len(stock):
                raise ValueError('string-directory extent outside resource')
            struct.pack_into('<I', output, old + 12, start + 8)
    for _, _, header, values in records:
        struct.pack_into('<I', output, header + 8 + 16, values[-1] + 8)
        struct.pack_into('<H', output, header + 8, crc(output[header + 10:header + 28]))

    # Reuse the separately tested investigator-authored image encoding. This
    # appends it as image39; it does not replace Calculator's image22.
    temporary, _, _ = replace(stock)
    picture = temporary[PAYLOAD:PAYLOAD + CAPACITY]
    output.extend(bytes(-len(output) % 4))
    start = len(output)
    output.extend(picture)
    for page in MENU_PAGES:
        group = struct.unpack_from('<I', output, 20 + page * 8)[0]
        table, count = struct.unpack_from('<IH', output, group + 12)
        if count not in (37, 38):
            raise ValueError('unexpected menu image count')
        entries = bytes(output[table:table + count * 20])
        output.extend(bytes(-len(output) % 4))
        target = len(output)
        output.extend(entries)
        for image in range(count + 1, MENU_IMAGE_ID + 1):
            descriptor = bytearray(struct.pack('<HHIHHII', 0, crc(picture), 0x30000000 | image << 16,
                                               50, 50, len(picture), start))
            struct.pack_into('<H', descriptor, 0, crc(descriptor[2:]))
            output.extend(descriptor)
        struct.pack_into('<IH', output, group + 12, target, MENU_IMAGE_ID)
    source_group = struct.unpack_from('<I', output, 20 + 40 * 8)[0]
    alias = bytes(output[source_group:source_group + 24])
    output.extend(bytes(-len(output) % 4))
    target = len(output)
    output.extend(alias)
    struct.pack_into('<II', output, old_directory_end, SHELL_PAGE, target)
    result = bytes(output)
    rebuilt = list(image_records(result))
    lookup = {(page, entry): values for page, entry, _, values in rebuilt}
    for page, entry, _, original in records:
        new = lookup[page, entry]
        if original[2:6] != new[2:6] or stock[original[-1]:original[-1] + original[-2]] != result[new[-1]:new[-1] + new[-2]]:
            raise ValueError('existing bitmap changed')
    return result
