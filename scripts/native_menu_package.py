"""Stock-only offline resource experiment; preserves both stock code banks.

Uses the pinned backend only for its inspected crypto and container reader.
No Bluetooth operations; package contains private vendor material.
"""
import argparse
import binascii
import contextlib
import hashlib
import io
from pathlib import Path
import struct

from .ufw_lab import load_backend, checked_parse, ORIGINAL_SHA256, BANKS

RESOURCE_SHA256 = "5f1b405ea728c735d885913aef695647824a36ed95e120e8b885dba8384dd2e3"
BUNDLE_SHA256 = "4927e21c0d2834cc188387c6e5111e7026ab7b62d618283fc58bc03487da3d9c"
RESOURCE_LENGTH = 15878656


def crc(data):
    return binascii.crc_hqx(data, 0)


def check_jlfs(data, header, start, size):
    if crc(data[header + 2:header + 32]) != struct.unpack_from("<H", data, header)[0]:
        raise ValueError("JLFS header CRC mismatch")
    if crc(data[start:start + size]) != struct.unpack_from("<H", data, header + 2)[0]:
        raise ValueError("JLFS data CRC mismatch")


def update_jlfs(data, header, start, size):
    struct.pack_into("<H", data, header + 2, crc(data[start:start + size]))
    struct.pack_into("<H", data, header, crc(data[header + 2:header + 32]))


def bundle_locations(resources):
    found = []
    for offset in range(0x7000, 0x8000, 32):
        record = resources[offset:offset + 32]
        if not record[0]:
            break
        if record[:11] == b"JL         ":
            found.append(record)
    if len(found) != 1:
        raise ValueError("expected exactly one JL root entry")
    record = found[0]
    size = struct.unpack_from("<I", record, 28)[0]
    cluster = struct.unpack_from("<H", record, 26)[0]
    seen, chunks, locations = set(), [], []
    while cluster < 0xfff8:
        if not 2 <= cluster < 4096 or cluster in seen:
            raise ValueError("invalid resource allocation chain")
        seen.add(cluster)
        start = 0x8000 + (cluster - 2) * 4096
        length = min(4096, size - sum(map(len, chunks)))
        if length <= 0 or start + length > len(resources):
            raise ValueError("invalid bundle extent")
        chunks.append(resources[start:start + length])
        locations.append((start, length))
        cluster = struct.unpack_from("<H", resources, 0x4000 + 2 * cluster)[0]
    bundle = b"".join(chunks)
    if len(bundle) != size:
        raise ValueError("truncated bundle")
    return bundle, locations


def build(raw, backend):
    from .native_menu_logo import replace
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("input must be protected original package")
    with contextlib.redirect_stdout(io.StringIO()):
        layout = checked_parse(backend, raw, BANKS[0])
        checked_parse(backend, raw, BANKS[1])
    entry = next(e for e in layout.entries if e.name == "res.bin")
    container = bytearray(raw[entry.eoffset:entry.eoffset + entry.esize])
    if len(container) != RESOURCE_LENGTH + 64:
        raise ValueError("resource container size mismatch")
    check_jlfs(container, 0, 32, len(container) - 32)
    check_jlfs(container, 32, 64, RESOURCE_LENGTH)
    resources = bytearray(container[64:])
    backend.jl_sfc_cipher(resources, 0, len(resources), 0, layout.chipkey)
    if hashlib.sha256(resources).hexdigest() != RESOURCE_SHA256:
        raise ValueError("resource decryption mismatch")
    inverse = bytearray(resources)
    backend.jl_sfc_cipher(inverse, 0, len(inverse), 0, layout.chipkey)
    if inverse != container[64:]:
        raise ValueError("resource cipher roundtrip failed")
    bundle, locations = bundle_locations(resources)
    if hashlib.sha256(bundle).hexdigest() != BUNDLE_SHA256:
        raise ValueError("JL bundle differs from inspected original")
    check_jlfs(bundle, 0, 32, len(bundle) - 32)
    check_jlfs(bundle, 96, 298352, 5891959)
    patched, image, used = replace(bundle[298352:298352 + 5891959])
    modified = bytearray(bundle)
    modified[298352:298352 + len(patched)] = patched
    update_jlfs(modified, 96, 298352, len(patched))
    update_jlfs(modified, 0, 32, len(modified) - 32)
    check_jlfs(modified, 96, 298352, len(patched))
    check_jlfs(modified, 0, 32, len(modified) - 32)
    offset = 0
    for start, size in locations:
        resources[start:start + size] = modified[offset:offset + size]
        offset += size
    if bundle_locations(resources)[0] != modified:
        raise ValueError("resource allocation writeback failed")
    encrypted = bytearray(resources)
    backend.jl_sfc_cipher(encrypted, 0, len(encrypted), 0, layout.chipkey)
    check = bytearray(encrypted)
    backend.jl_sfc_cipher(check, 0, len(check), 0, layout.chipkey)
    if check != resources:
        raise ValueError("modified resource cipher roundtrip failed")
    container[64:] = encrypted
    update_jlfs(container, 32, 64, RESOURCE_LENGTH)
    update_jlfs(container, 0, 32, len(container) - 32)
    check_jlfs(container, 32, 64, RESOURCE_LENGTH)
    check_jlfs(container, 0, 32, len(container) - 32)
    output = bytearray(raw)
    output[entry.eoffset:entry.eoffset + entry.esize] = container
    entries = bytearray()
    for other in layout.entries:
        header = bytearray(other.plain_header)
        if other.index == entry.index:
            struct.pack_into("<H", header, 4, crc(container))
        backend.jl_enc_cipher(header, 0, len(header), 0xffff)
        entries.extend(header)
    header = bytearray(layout.header_plain)
    struct.pack_into("<H", header, 2, crc(entries))
    struct.pack_into("<H", header, 0, crc(header[2:64]))
    backend.jl_enc_cipher(header, 0, len(header), 0xffff)
    output[:64] = header
    output[64:64 + len(entries)] = entries
    if len(output) != len(raw):
        raise ValueError("package size changed")
    with contextlib.redirect_stdout(io.StringIO()):
        for bank in BANKS:
            checked_parse(backend, bytes(output), bank)
    for other in layout.entries:
        if other.name != "res.bin" and output[other.eoffset:other.eoffset + other.esize] != raw[other.eoffset:other.eoffset + other.esize]:
            raise ValueError("non-resource payload changed")
    return bytes(output), image, used


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stock", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("preview", type=Path)
    parser.add_argument("--backend", type=Path, required=True)
    parser.add_argument("--crypto-path", type=Path, required=True)
    args = parser.parse_args()
    backend = load_backend(args.backend, args.crypto_path)
    package, image, used = build(args.stock.read_bytes(), backend)
    with args.output.open("xb") as file:
        file.write(package)
    args.output.chmod(0o600)
    image.save(args.preview)
    print(f"Verified stock-code/menu-logo package; image bytes {used}; SHA256 {hashlib.sha256(package).hexdigest()}")
