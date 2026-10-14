"""Read-only control graph for the observed stock native style format.

Child records are contiguous siblings, not contiguous preorder subtrees.
Names correlate with the pinned SDK; device record lengths are authoritative.
"""
import argparse
import json
from pathlib import Path
import struct
if __package__:
    from .native_style_inventory import inventory
else:
    from native_style_inventory import inventory


TYPES = {2: "window", 3: "layout", 4: "layer", 5: "grid", 7: "button",
         8: "picture", 10: "time", 12: "text", 15: "number",
         20: "progress", 22: "multiprogress", 24: "watch",
         28: "slider", 33: "vertical_slider"}


def control_tree(payload, relocations):
    relocations = set(relocations)
    seen = set()
    spans = []

    def walk(offset, depth):
        if depth > 100 or offset in seen or offset + 16 > len(payload):
            raise ValueError("invalid, repeated or excessively deep control")
        seen.add(offset)
        kind, count, css_count, size = payload[offset:offset + 4]
        if kind == 2 and size == 0:
            size = 28
        if size < 16 or size % 4 or offset + size > len(payload):
            raise ValueError("invalid control record length")
        end = offset + size
        if any(offset < stop and start < end for start, stop in spans):
            raise ValueError("overlapping control records")
        spans.append((offset, end))
        record = dict(offset=offset, size=size, type=kind,
                      sdk_type=TYPES.get(kind, "unidentified"),
                      id=struct.unpack_from("<I", payload, offset + 8)[0],
                      css_count=css_count, children=[])
        if kind in (8, 10, 12, 15, 20, 22, 24) and size >= 24:
            label = payload[offset + 16:offset + 24].split(b"\0", 1)[0]
            if label and all(32 <= value < 127 for value in label):
                record["inline_label"] = label.decode("ascii")
        if count:
            if size < 20 or end - 4 not in relocations:
                raise ValueError("child pointer absent from relocation table")
            child = struct.unpack_from("<I", payload, end - 4)[0] & 0x1ffff
            if not child:
                raise ValueError("null child pointer")
            for _ in range(count):
                item, child = walk(child, depth + 1)
                record["children"].append(item)
        return record, end

    return walk(0, 0)[0]


def trees(data):
    result = []
    for window in inventory(data)["windows"]:
        if not all(window[key] for key in ("header_crc_matches", "table_crc_matches",
                                           "normalized_data_crc_matches",
                                           "pointer_targets_in_window")):
            raise ValueError("style integrity or pointer validation failed")
        start = window["offset"]
        result.append(dict(index=window["index"], root=control_tree(
            data[start:start + window["length"]], window["relocations"])))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    print(json.dumps(trees(args.file.read_bytes()), indent=2))
