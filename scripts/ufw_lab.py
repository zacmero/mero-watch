#!/usr/bin/env python3
"""Offline lab for this watch's UFW; never connects to or flashes a device.

Uses the pinned, separately obtained upstream repacker and jltech crypto.
Outputs contain package-derived private key material: keep them out of git.
The branding fixture tests packaging only, not custom application execution.
"""
import argparse
import ast
import binascii
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

BANKS = ("flash.bin", "flash2.bin")
ORIGINAL_SHA256 = "5f315a22adada0c7933afa89558b5d1e9be577ede10f9dbc5a53cd82c2c23145"
BACKEND_SHA256 = "30a9162fa46e1c486f4310e70070cd18cc5ef7122622010ed12617f26b7a973c"


def load_backend(path, crypto_path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != BACKEND_SHA256:
        raise ValueError("External repacker differs from the inspected pinned version")
    sys.path.insert(0, str(crypto_path.resolve()))
    spec = importlib.util.spec_from_file_location("mero_inspected_ufw_backend", path)
    backend = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = backend
    spec.loader.exec_module(backend)
    if backend.QIX_HEADER_LEN < 27:
        raise ValueError("Synthetic prefix is too short for wrapper checksum field")
    # The watch package has no Qix prefix; these bytes are always discarded.
    # Avoid a slow CRC calculation for the adapter prefix only.
    backend.crc16_ccitt_false = lambda data: 0
    # The upstream BR35 tool picks etype=0 only. Select by observed bank name
    # instead, without altering any package header or encoded bytes.
    tree = ast.parse(path.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "parse_ufw")
    function.args.args.append(ast.arg(arg="target_bank"))
    function.args.defaults.append(ast.Constant(value="flash.bin"))
    replaced = 0
    for node in ast.walk(function):
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name) and node.test.left.id == "etype"
                and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq)
                and len(node.test.comparators) == 1
                and isinstance(node.test.comparators[0], ast.Constant)
                and node.test.comparators[0].value == 0):
            node.test = ast.Compare(ast.Name("name", ast.Load()), [ast.Eq()],
                                    [ast.Name("target_bank", ast.Load())])
            replaced += 1
    if replaced != 1:
        raise ValueError("Upstream parser selection differs from inspected version")
    module = ast.Module(body=[function], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), backend.__dict__)
    return backend


def checked_parse(backend, raw, bank):
    # Synthetic adapter prefix is discarded on output. This watch has no Qix wrapper.
    prefix = backend.QIX_MAGIC + bytes(backend.QIX_HEADER_LEN - len(backend.QIX_MAGIC))
    layout = backend.parse_ufw(prefix + raw, bank)
    crc = lambda data: binascii.crc_hqx(data, 0)
    header = layout.header_plain
    if crc(header[2:64]) != int.from_bytes(header[:2], "little"):
        raise ValueError("UFW header CRC mismatch")
    if crc(raw[64:64 + layout.numents * 80]) != int.from_bytes(header[2:4], "little"):
        raise ValueError("UFW entry-table CRC mismatch")
    for entry in layout.entries:
        if entry.name in (*BANKS, "res.bin", "ota.bin", "tail.bin"):
            data = raw[entry.eoffset:entry.eoffset + entry.esize]
            if len(data) != entry.esize or crc(data) != entry.edcrc:
                raise ValueError(f"Critical outer payload CRC mismatch: {entry.name}")
    for entry in layout.jlfs_app_dir:
        if entry.name in ("app_area_head", "app.bin", "cfg_tool.bin"):
            h = layout.flash_bin_plain[entry.hdr_off:entry.hdr_off + 32]
            if crc(h[2:]) != int.from_bytes(h[:2], "little"):
                raise ValueError(f"JLFS header CRC mismatch: {entry.name}")
            data = layout.flash_bin_plain[entry.data_offset:entry.data_offset + entry.data_size]
            if len(data) != entry.data_size or crc(data) != entry.data_crc:
                raise ValueError(f"JLFS data CRC mismatch: {entry.name}")
    return layout


def app_bytes(layout):
    entry = next(e for e in layout.jlfs_app_dir if e.name == "app.bin")
    return layout.flash_bin_plain[entry.data_offset:entry.data_offset + entry.data_size]


def repack(backend, layout, patches):
    with contextlib.redirect_stdout(io.StringIO()):
        wrapped = backend.repack(layout, patches)
    return wrapped[backend.QIX_HEADER_LEN:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("roundtrip", "branding-fixture"))
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--backend", type=Path, required=True)
    parser.add_argument("--crypto-path", type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error("Use a new output path; original files are never overwritten")
    raw = args.input.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA256:
        parser.error("Input differs from the exact inspected watch firmware")
    backend = load_backend(args.backend, args.crypto_path)
    layouts = {bank: checked_parse(backend, raw, bank) for bank in BANKS}
    for bank, layout in layouts.items():
        if repack(backend, layout, []) != raw:
            raise ValueError(f"Untouched repack is not byte-exact: {bank}")
    if app_bytes(layouts[BANKS[0]]) != app_bytes(layouts[BANKS[1]]):
        raise ValueError("Original bank application contents differ")
    output = raw
    offset = None
    if args.action == "branding-fixture":
        old, new = b"Apple Watch", b"Mero Agent!"
        app = app_bytes(layouts[BANKS[0]])
        if app.count(old) != 1 or len(old) != len(new):
            raise ValueError("Unique equal-length fixture string not found")
        offset = app.index(old)
        for bank in BANKS:
            layout = checked_parse(backend, output, bank)
            output = repack(backend, layout, [("app.bin", offset, new)])
        for bank in BANKS:
            patched = checked_parse(backend, output, bank)
            expected = app[:offset] + new + app[offset + len(old):]
            if app_bytes(patched) != expected:
                raise ValueError(f"Unexpected application mutation: {bank}")
    # Every non-code outer payload, including the OTA loader/resources/config,
    # must remain byte-identical. Code-bank slot positions and sizes stay fixed.
    for entry in layouts[BANKS[0]].entries:
        if entry.name not in BANKS:
            start, end = entry.eoffset, entry.eoffset + entry.esize
            if raw[start:end] != output[start:end]:
                raise ValueError(f"Unexpected non-code payload change: {entry.name}")
    if len(output) != len(raw):
        raise ValueError("Package size changed")
    # Restrictive creation also prevents an output-path race overwriting a file.
    import os
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(output)
    print(json.dumps({"action": args.action, "bytes": len(output),
                      "sha256": hashlib.sha256(output).hexdigest(),
                      "changed_bytes": sum(a != b for a, b in zip(raw, output)),
                      "application_fixture_offset": offset,
                      "both_banks_checked": True, "non_code_payloads_unchanged": True,
                      "device_acceptance": "untested", "recovery": "unverified"}))


if __name__ == "__main__":
    main()
