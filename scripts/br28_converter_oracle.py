#!/usr/bin/env python3
"""Offline AArch64 emulation of the inspected GFit BR28 image converter.

Needs Pillow, pyelftools and Unicorn, and the locally extracted vendor library.
Only the image routine executes; no Android, Bluetooth, network or host file
imports are emulated. Unsupported imports and relocation types fail closed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as registers

BASE, TLS, STACK, HEAP, STUB = 0x1000000, 0x2000000, 0x3000000, 0x4000000, 0x9000000
EXIT = STUB + 0xfff0
XREGS = [getattr(registers, f"UC_ARM64_REG_X{i}") for i in range(6)]


class Converter:
    def __init__(self, library):
        self.machine = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        for address, size in ((BASE, 0x100000), (TLS, 0x1000), (STACK, 0x100000),
                              (HEAP, 0x4000000), (STUB, 0x10000)):
            self.machine.mem_map(address, size)
        self.machine.reg_write(registers.UC_ARM64_REG_TPIDR_EL0, TLS)
        self.heap_position = HEAP
        self.stubs, self.symbols = {}, {}
        with Path(library).open("rb") as stream:
            elf = ELFFile(stream)
            if elf["e_machine"] != "EM_AARCH64":
                raise ValueError("Expected inspected AArch64 converter library")
            symbols = elf.get_section_by_name(".dynsym")
            for segment in elf.iter_segments():
                if segment["p_type"] == "PT_LOAD":
                    if segment["p_vaddr"] + segment["p_memsz"] > 0x100000:
                        raise ValueError("Library exceeds emulated mapping")
                    self.machine.mem_write(BASE + segment["p_vaddr"], segment.data())
            for symbol in symbols.iter_symbols():
                if symbol["st_shndx"] != "SHN_UNDEF":
                    self.symbols[symbol.name] = BASE + symbol["st_value"]
            imported = {}
            for section in (".rela.dyn", ".rela.plt"):
                for relocation in elf.get_section_by_name(section).iter_relocations():
                    kind, addend = relocation["r_info_type"], relocation["r_addend"]
                    if kind == 1027:  # R_AARCH64_RELATIVE
                        value = BASE + addend
                    elif kind in (257, 1025, 1026):  # ABS64, GLOB_DAT, JUMP_SLOT
                        symbol = symbols.get_symbol(relocation["r_info_sym"])
                        if symbol["st_shndx"] != "SHN_UNDEF":
                            value = BASE + symbol["st_value"] + addend
                        else:
                            if symbol.name not in imported:
                                address = STUB + len(imported) * 16
                                if address >= EXIT:
                                    raise ValueError("Too many import stubs")
                                imported[symbol.name] = address
                                self.stubs[address] = symbol.name
                            value = imported[symbol.name] + addend
                    else:
                        raise ValueError(f"Unsupported relocation {kind}")
                    self.machine.mem_write(BASE + relocation["r_offset"], struct.pack("<Q", value))
        self.machine.hook_add(UC_HOOK_CODE, self.import_call, begin=STUB, end=STUB + 0xffff)

    def allocate(self, size):
        pointer = self.heap_position
        self.heap_position += max(16, (size + 15) & ~15)
        if self.heap_position >= HEAP + 0x4000000:
            raise ValueError("Emulated heap exhausted")
        return pointer

    def import_call(self, machine, address, instruction_size, userdata):
        if address == EXIT:
            return
        name = self.stubs.get(address)
        args = [machine.reg_read(register) for register in XREGS[:4]]
        if name == "malloc":
            result = self.allocate(args[0])
        elif name == "calloc":
            result = self.allocate(args[0] * args[1])
            machine.mem_write(result, bytes(args[0] * args[1]))
        elif name == "free":
            result = 0
        elif name in ("memcpy", "memmove", "__memcpy_chk", "__memmove_chk"):
            machine.mem_write(args[0], bytes(machine.mem_read(args[1], args[2])))
            result = args[0]
        elif name in ("memset", "__memset_chk"):
            machine.mem_write(args[0], bytes([args[1] & 255]) * args[2])
            result = args[0]
        elif name in ("__android_log_print", "__android_log_write"):
            result = 0
        else:
            raise ValueError(f"Unsupported native import {name}")
        machine.reg_write(XREGS[0], result)
        machine.reg_write(registers.UC_ARM64_REG_PC, machine.reg_read(registers.UC_ARM64_REG_LR))

    def call(self, *arguments):
        self.machine.reg_write(registers.UC_ARM64_REG_SP, STACK + 0xff000)
        self.machine.reg_write(registers.UC_ARM64_REG_LR, EXIT)
        for register, argument in zip(XREGS, arguments):
            self.machine.reg_write(register, argument)
        self.machine.emu_start(self.symbols["br28_png_to_res"], EXIT,
                               timeout=30_000_000, count=30_000_000)
        if self.machine.reg_read(registers.UC_ARM64_REG_PC) != EXIT:
            raise ValueError("Native converter exceeded emulation budget")
        return self.machine.reg_read(XREGS[0]) & 0xffffffff

    def encode(self, image):
        image = image.convert("RGBA")
        if not 1 <= image.width <= 1024 or not 1 <= image.height <= 1024:
            raise ValueError("Image dimensions exceed offline test bounds")
        bgra = image.tobytes("raw", "BGRA")
        source = self.allocate(len(bgra))
        self.machine.mem_write(source, bgra)
        size = self.call(source, image.width, image.height, 1, 0)
        if not 0 < size < 4_000_000:
            raise ValueError("Unexpected native output size")
        output = self.allocate(size)
        actual = self.call(source, image.width, image.height, 1, output)
        if actual != size:
            raise ValueError("Native sizing and writing calls disagree")
        return bytes(self.machine.mem_read(output, size))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    from PIL import Image
    with Image.open(args.input) as image:
        resource = Converter(args.library).encode(image)
    # Independently verify the generated container/checksums before saving.
    from ru30_background import decode
    decode(resource)
    args.output.write_bytes(resource)
    print(json.dumps({"bytes": len(resource), "sha256": hashlib.sha256(resource).hexdigest()}))


if __name__ == "__main__":
    main()
