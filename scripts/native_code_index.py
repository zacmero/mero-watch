#!/usr/bin/env python3
"""Offline PI32v2 call/literal index, with conservative straight-line tracking.

References are analysis candidates, not a recovered complete call graph.
Direct calls use next-PC-relative semantics verified with a linked fixture.
"""
import argparse
import bisect
import json
from pathlib import Path
import re
if __package__:
    from .native_firmware_map import FLASH_BASE, runtime_address
else:
    from native_firmware_map import FLASH_BASE, runtime_address

INSTRUCTION = re.compile(r"^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\s*(.*)")


def instructions(text):
    for line in text.splitlines():
        match = INSTRUCTION.match(line)
        if match:
            yield (int(match[1], 16), len(match[2].split()), match[3].strip())


def direct_call(address, size, operation):
    match = re.fullmatch(r"call (-?\d+)", operation)
    return address + size + int(match[1]) if match else None


def index(text, payload, base, app, pattern):
    labels = {}
    for match in re.finditer(rb"[ -~]{6,}", payload):
        label = match.group().decode("ascii")
        if not pattern.search(label):
            continue
        addresses = [FLASH_BASE + match.start(), runtime_address(match.start())] if app else [base + match.start()]
        for address in set(addresses):
            labels[address] = label
    rows = list(instructions(text))
    calls = [{"source": address, "target": target} for address, size, operation in rows
             if (target := direct_call(address, size, operation)) is not None]
    starts = sorted({address for address, _, operation in rows
                     if operation.startswith("[--sp]") and "rets" in operation})
    references, registers = [], {}
    previous_end = None
    for address, size, operation in rows:
        if address != previous_end or (operation.startswith("[--sp]") and "rets" in operation):
            registers.clear()
        previous_end = address + size
        literal = re.fullmatch(r"r(\d+) = (-?\d+)", operation)
        addition = re.fullmatch(r"r(\d+) = r(\d+) \+ (-?\d+)", operation)
        register_addition = re.fullmatch(r"r(\d+) = r(\d+) \+ r(\d+)", operation)
        paired_assignment = re.match(r"r(\d+)_r(\d+) =", operation)
        copy = re.fullmatch(r"r(\d+) = r(\d+)", operation)
        assignment = re.match(r"r(\d+) (?:=|\+=|-=|\*=)", operation)
        register = None
        value = None
        if literal:
            register, value = int(literal[1]), int(literal[2])
        elif addition:
            register = int(addition[1])
            if int(addition[2]) in registers:
                value = registers[int(addition[2])] + int(addition[3])
        elif register_addition:
            register = int(register_addition[1])
            left, right = int(register_addition[2]), int(register_addition[3])
            if left in registers and right in registers:
                value = registers[left] + registers[right]
        elif copy:
            register = int(copy[1])
            value = registers.get(int(copy[2]))
        elif assignment:
            register = int(assignment[1])
        if register is not None:
            registers.pop(register, None)
            if value is not None:
                registers[register] = value
                if value in labels:
                    i = bisect.bisect_right(starts, address)
                    references.append({"instruction": address, "register": register,
                                       "string_address": value, "text": labels[value],
                                       "nearest_prologue_candidate": starts[i - 1] if i else None})
        if paired_assignment:
            registers.pop(int(paired_assignment[1]), None)
            registers.pop(int(paired_assignment[2]), None)
        for incremented in re.findall(r"r(\d+)(?:\+\+|--)", operation):
            registers.pop(int(incremented), None)
        if operation.startswith("call"):
            # r4-r12 callee preservation is used only as an ABI-based hypothesis.
            registers = {r: value for r, value in registers.items() if 4 <= r <= 12}
        if "goto" in operation or operation.startswith("if ") or operation == "rts" or "{pc" in operation:
            registers.clear()
    return {"instructions": len(rows), "calls": calls, "string_references": references,
            "limits": "Linear constant candidates; indirect calls/control flow/ABI not fully recovered"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disassembly", type=Path)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=FLASH_BASE)
    parser.add_argument("--app", action="store_true")
    parser.add_argument("--match", default=r"(?i)ui_|style|layout|draw|touch|crc|verify|flash\.bin|uboot|signature")
    args = parser.parse_args()
    result = index(args.disassembly.read_text(), args.binary.read_bytes(), args.base,
                   args.app, re.compile(args.match))
    import os
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({"instructions": result["instructions"], "direct_calls": len(result["calls"]),
                      "literal_reference_candidates": len(result["string_references"])}))


if __name__ == "__main__":
    main()
