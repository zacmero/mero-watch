"""Offline inventory of SDK-correlated native style headers; never writes files.

Stock data CRCs match after masking relocated pointer words to their lower
17 bits. Tagged bytes are preserved; this inventory never modifies files.
"""
import argparse
import binascii
import json
from pathlib import Path
import struct


def inventory(data):
    if len(data) < 24:
        raise ValueError("truncated style header")
    count = data[17]
    if 24 + count * 20 > len(data):
        raise ValueError("truncated window directory")
    windows = []
    for i in range(count):
        h = 24 + i * 20
        offset, length, table, table_len, crc_data, crc_table, crc_head = struct.unpack_from(
            "<IIIHHHH", data, h)
        if offset + length > len(data) or table + table_len > len(data):
            raise ValueError("window or pointer table outside file")
        if table_len % 2:
            raise ValueError("odd pointer table length")
        relocations = list(struct.unpack_from("<" + "H" * (table_len // 2), data, table))
        if any(p + 4 > length for p in relocations):
            raise ValueError("relocation outside window")
        crc = lambda b: binascii.crc_hqx(b, 0)
        normalized = bytearray(data[offset:offset + length])
        tags = set()
        targets_valid = True
        for p in relocations:
            word = struct.unpack_from("<I", normalized, p)[0]
            if word:
                tags.add(word >> 17)
                targets_valid &= (word & 0x1ffff) < length
            struct.pack_into("<I", normalized, p, word & 0x1ffff)
        windows.append(dict(index=i, offset=offset, length=length,
                            pointer_table_offset=table, pointer_table_length=table_len,
                            relocations=relocations,
                            header_crc_matches=crc(data[h:h + 14]) == crc_head,
                            table_crc_matches=crc(data[table:table + table_len]) == crc_table,
                            normalized_data_crc_matches=crc(normalized) == crc_data,
                            pointer_tags=sorted(tags), pointer_targets_in_window=targets_valid,
                            reference_data_crc_matches=crc(data[offset:offset + length]) == crc_data))
    return dict(type=data[16], window_count=count,
                property_length=struct.unpack_from("<H", data, 18)[0],
                rotation=data[20], windows=windows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    print(json.dumps(inventory(args.file.read_bytes()), indent=2))
