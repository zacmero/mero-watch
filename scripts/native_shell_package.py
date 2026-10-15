"""Stock-pinned offline native-shell package builder. No device operations.

Appends code inside declared PRCT capacity, retains factory callbacks and apps,
and extends only the JL resource allocation. Device execution remains untested.
"""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess

from .ufw_lab import ORIGINAL_SHA256, BANKS, load_backend, checked_parse, repack, app_bytes
from .native_menu_package import crc, check_jlfs, update_jlfs, bundle_locations, RESOURCE_SHA256, BUNDLE_SHA256
from .native_shell_style import build as build_style, MENU_PAGES, SHELL_PAGE

MODULE_BASE = 0x0613d6dc
CALLBACK_START = 0x06114b98
CALLBACK_END = 0x06117728
STYLE_INFO = 0x06114b5c
APP_BASE = 0x06000120
FLASH_CAPACITY = 16777216  # Device-reported external resource/FAT capacity.


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def root_files(data):
    result = {}
    for offset in range(0x7000, 0x8000, 32):
        record = data[offset:offset + 32]
        if not record[0]:
            break
        cluster = struct.unpack_from('<H', record, 26)[0]
        size = struct.unpack_from('<I', record, 28)[0]
        chain, payload = [], bytearray()
        while cluster < 0xfff8:
            if not 2 <= cluster < 4096 or cluster in chain:
                raise ValueError('invalid FAT chain')
            chain.append(cluster)
            start = 0x8000 + (cluster - 2) * 4096
            payload.extend(data[start:start + min(4096, size - len(payload))])
            cluster = struct.unpack_from('<H', data, 0x4000 + 2 * cluster)[0]
        if len(payload) != size:
            raise ValueError('truncated root file')
        result[bytes(record[:11])] = (offset, chain, bytes(payload))
    return result


def resource_container(raw, layout, backend):
    from .native_shell_resources import build as build_images
    entry = next(e for e in layout.entries if e.name == 'res.bin')
    original = raw[entry.eoffset:entry.eoffset + entry.esize]
    check_jlfs(original, 0, 32, len(original) - 32)
    check_jlfs(original, 32, 64, len(original) - 64)
    data = bytearray(original[64:])
    backend.jl_sfc_cipher(data, 0, len(data), 0, layout.chipkey)
    if hashlib.sha256(data).hexdigest() != RESOURCE_SHA256:
        raise ValueError('unexpected resource plaintext')
    old_files = root_files(data)
    root_offset, chain, bundle = old_files[b'JL         ']
    if hashlib.sha256(bundle).hexdigest() != BUNDLE_SHA256:
        raise ValueError('unexpected JL bundle')
    parts = []
    for offset in (32, 64, 96, 128):
        header = bytearray(bundle[offset:offset + 32])
        start, size = struct.unpack_from('<II', header, 4)
        check_jlfs(bundle, offset, start, size)
        payload = bundle[start:start + size]
        if offset == 64:
            payload = build_style(payload)
        elif offset == 96:
            payload = build_images(payload)
        parts.append((header, payload))
    output = bytearray(bundle[:160])
    for index, (header, payload) in enumerate(parts):
        output.extend(b'\xff' * (-len(output) % 16))
        start = len(output)
        output.extend(payload)
        struct.pack_into('<II', header, 4, start, len(payload))
        output[32 + index * 32:64 + index * 32] = header
        update_jlfs(output, 32 + index * 32, start, len(payload))
        check_jlfs(output, 32 + index * 32, start, len(payload))
    struct.pack_into('<I', output, 8, len(output))
    update_jlfs(output, 0, 32, len(output) - 32)
    check_jlfs(output, 0, 32, len(output) - 32)
    needed = align(len(output), 4096) // 4096
    used = {c for _, existing, _ in old_files.values() for c in existing}
    free = [c for c in range(2, 4096) if c not in used and struct.unpack_from('<H', data, 0x4000 + 2 * c)[0] == 0]
    if needed < len(chain) or needed - len(chain) > len(free):
        raise ValueError('unexpected resource allocation size')
    chain = chain + free[:needed - len(chain)]
    length = max(len(data), max(0x8000 + (c - 1) * 4096 for c in chain))
    if length > FLASH_CAPACITY:
        raise ValueError('resource capacity exceeded')
    data.extend(b'\xff' * (length - len(data)))
    for index, cluster in enumerate(chain):
        struct.pack_into('<H', data, 0x4000 + 2 * cluster, chain[index + 1] if index + 1 < len(chain) else 0xffff)
        start = 0x8000 + (cluster - 2) * 4096
        chunk = output[index * 4096:(index + 1) * 4096]
        data[start:start + 4096] = chunk + b'\xff' * (4096 - len(chunk))
    struct.pack_into('<I', data, root_offset + 28, len(output))
    new_files = root_files(data)
    if new_files.keys() != old_files.keys() or bundle_locations(data)[0] != output:
        raise ValueError('resource tree changed unexpectedly')
    for name, (_, old_chain, payload) in old_files.items():
        if name != b'JL         ' and new_files[name][1:] != (old_chain, payload):
            raise ValueError('factory resource changed')
    encrypted = bytearray(data)
    backend.jl_sfc_cipher(encrypted, 0, len(encrypted), 0, layout.chipkey)
    inverse = bytearray(encrypted)
    backend.jl_sfc_cipher(inverse, 0, len(inverse), 0, layout.chipkey)
    if inverse != data:
        raise ValueError('resource cipher roundtrip failed')
    container = bytearray(original[:64]) + encrypted
    struct.pack_into('<I', container, 8, len(container))
    struct.pack_into('<I', container, 40, len(container) - 64)
    update_jlfs(container, 32, 64, len(container) - 64)
    update_jlfs(container, 0, 32, len(container) - 32)
    return bytes(container)


def module_bytes(app, code, symbols):
    table = bytearray(app[CALLBACK_START - APP_BASE:CALLBACK_END - APP_BASE])
    if len(table) != 697 * 16:
        raise ValueError('factory handler count changed')
    for row in range(7):
        table.extend(struct.pack('<4I', (SHELL_PAGE << 17) | 0x3000 | row,
                                 symbols['mero_shell_touch'] if row in (5, 6) else 0,
                                 0, symbols['mero_shell_text_change']))
    for page in MENU_PAGES:
        table.extend(struct.pack('<4I', (page << 17) | 0xffe, symbols['mero_menu_touch'], 0, 0))
        table.extend(struct.pack('<4I', (page << 17) | 0x33fe, 0, 0, symbols['mero_menu_text_change']))
    prefix = code + bytes(-len(code) % 4)
    start = MODULE_BASE + len(prefix)
    return prefix + table, start, start + len(table)


def append_bank(layout, module, backend):
    data = bytearray(layout.flash_bin_plain)
    last = next(e for e in layout.jlfs_app_dir if e.name == 'eq_cfg_hw.bin')
    end = last.data_offset + last.data_size
    if 0x06000000 + end + 32 - layout.app_dir_appbase != MODULE_BASE or last.eindex != 1:
        raise ValueError('unexpected append geometry')
    prct = next(e for e in layout.jlfs_app_dir if e.name == 'PRCT')
    vm = next(e for e in layout.jlfs_app_dir if e.name == 'VM')
    if prct.data_offset + prct.data_size != vm.data_offset:
        raise ValueError('partition boundary mismatch')
    original_tail = bytes(data[-8:])
    data = data[:end]
    struct.pack_into('<H', data, last.hdr_off + 14, 0)
    struct.pack_into('<H', data, last.hdr_off, crc(data[last.hdr_off + 2:last.hdr_off + 32]))
    # Every observed SFC root entry starts its data32 bytes after its header.
    # The backend parser hardcodes this and would silently accept a bad eoff.
    header = bytearray(struct.pack('<HHIIBBH16s', 0, crc(module), 32, len(module) + 32, 0x82, 0, 1, b'mero_shell.bin'))
    struct.pack_into('<H', header, 0, crc(header[2:]))
    data.extend(header + module)
    sfc_end = len(data)
    length = max(len(layout.flash_bin_plain), align(sfc_end + 8, 512))
    if length - layout.app_dir_appbase > prct.data_size:
        raise ValueError('native module exceeds PRCT partition capacity')
    data.extend(b'\xff' * (length - len(data) - 8))
    data.extend(original_tail)
    backend.jl_enc_cipher(data, 0, 32, 0xffff)
    for entry in layout.jlfs_top:
        backend.jl_enc_cipher(data, entry.hdr_off, 32, 0xffff)
    backend.jl_sfc_cipher(data, layout.app_dir_appbase, sfc_end - layout.app_dir_appbase,
                          layout.app_dir_appbase, layout.chipkey)
    return bytes(data)


def outer(raw, layout, replacements, backend):
    output = bytearray(raw[:min(e.eoffset for e in layout.entries)])
    cursor, headers = len(output), bytearray()
    for entry in layout.entries:
        if entry.eoffset < cursor:
            raise ValueError('overlapping outer payloads')
        output.extend(raw[cursor:entry.eoffset])
        payload = replacements.get(entry.name, raw[entry.eoffset:entry.eoffset + entry.esize])
        header = bytearray(entry.plain_header)
        struct.pack_into('<H', header, 4, crc(payload))
        struct.pack_into('<II', header, 8, len(output), len(payload))
        output.extend(payload)
        cursor = entry.eoffset + entry.esize
        backend.jl_enc_cipher(header, 0, len(header), 0xffff)
        headers.extend(header)
    output.extend(raw[cursor:])
    header = bytearray(layout.header_plain)
    struct.pack_into('<I', header, 4, len(output))
    struct.pack_into('<H', header, 2, crc(headers))
    struct.pack_into('<H', header, 0, crc(header[2:]))
    backend.jl_enc_cipher(header, 0, len(header), 0xffff)
    output[:64] = header
    output[64:64 + len(headers)] = headers
    return bytes(output)


def build(raw, code, symbols, backend):
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('input must be protected original firmware')
    layout = checked_parse(backend, raw, BANKS[0])
    app = app_bytes(layout)
    module, begin, end = module_bytes(app, code, symbols)
    changes = [(STYLE_INFO - APP_BASE + index * 12 + 4, struct.pack('<II', begin, end)) for index in range(5)]
    patched = raw
    for bank in BANKS:
        current = checked_parse(backend, patched, bank)
        if app_bytes(current) != app:
            raise ValueError('stock app banks differ')
        patched = repack(backend, current, [('app.bin', offset, value) for offset, value in changes])
    replacements = {'res.bin': resource_container(raw, layout, backend)}
    expected = bytearray(app)
    for offset, value in changes:
        expected[offset:offset + len(value)] = value
    for bank in BANKS:
        current = checked_parse(backend, patched, bank)
        replacements[bank] = append_bank(current, module, backend)
    result = outer(raw, layout, replacements, backend)
    for bank in BANKS:
        verified = checked_parse(backend, result, bank)
        if app_bytes(verified) != expected:
            raise ValueError('unexpected original application mutation')
        own = next(e for e in verified.jlfs_app_dir if e.name == 'mero_shell.bin')
        if own.eoff != 32 or own.esize != own.data_size + 32:
            raise ValueError('native root file offset/size contract invalid')
        check_jlfs(verified.flash_bin_plain, own.hdr_off, own.data_offset, own.data_size)
        if verified.flash_bin_plain[own.data_offset:own.data_offset + own.data_size] != module:
            raise ValueError('appended module readback failed')
        old = checked_parse(backend, raw, bank)
        for entry in old.jlfs_app_dir:
            if entry.name not in ('app.bin', 'app_area_head', 'PRCT'):
                match = next(e for e in verified.jlfs_app_dir if e.name == entry.name)
                if (entry.data_offset, entry.data_size) != (match.data_offset, match.data_size):
                    raise ValueError('factory flash layout moved')
                if old.flash_bin_plain[entry.data_offset:entry.data_offset + entry.data_size] != verified.flash_bin_plain[match.data_offset:match.data_offset + match.data_size]:
                    raise ValueError('factory flash payload changed: ' + entry.name)
    for entry in verified.entries:
        if entry.name not in replacements:
            original = next(e for e in layout.entries if e.name == entry.name)
            if result[entry.eoffset:entry.eoffset + entry.esize] != raw[original.eoffset:original.eoffset + original.esize]:
                raise ValueError('unrelated outer payload changed')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('stock', 'code', 'elf', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--nm', required=True)
    parser.add_argument('--backend', required=True, type=Path)
    parser.add_argument('--crypto-path', required=True, type=Path)
    args = parser.parse_args()
    symbols = {parts[2]: int(parts[0], 16) for line in subprocess.check_output([args.nm, str(args.elf)], text=True).splitlines()
               if len(parts := line.split()) == 3 and parts[1] == 'T'}
    code = args.code.read_bytes()
    if not 0 < len(code) < 4096 or any(not MODULE_BASE <= symbols[name] < MODULE_BASE + len(code) for name in
            ('mero_shell_text_change', 'mero_shell_touch', 'mero_menu_touch', 'mero_menu_text_change')):
        raise ValueError('native code/symbol bounds invalid')
    backend = load_backend(args.backend, args.crypto_path)
    with contextlib.redirect_stdout(io.StringIO()):
        package = build(args.stock.read_bytes(), code, symbols, backend)
    with args.output.open('xb') as stream:
        stream.write(package)
    args.output.chmod(0o600)
    print(json.dumps({'bytes': len(package), 'sha256': hashlib.sha256(package).hexdigest(),
                      'code_sha256': hashlib.sha256(code).hexdigest(), 'symbols': symbols,
                      'device_execution': 'untested'}))


if __name__ == '__main__':
    main()
