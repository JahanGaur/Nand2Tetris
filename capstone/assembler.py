#!/usr/bin/env python3
"""
Hack Assembler (Nand to Tetris, Capstone Part B)
Usage:  python assembler.py Prog.asm        ->  writes Prog.hack
Personalized extra feature (K mod 3 == 0): write every user-defined label
and variable, with its resolved address, to symbols.txt beside the input file.
All errors are reported; no .hack file is written if any error is found.
"""
import os
import re
import sys

# ---------- tables ----------
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
PREDEFINED = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
              "SCREEN": 16384, "KBD": 24576}
PREDEFINED.update({f"R{i}": i for i in range(16)})
SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


class AsmError(Exception):
    """A problem with one source line."""


def clean(line):
    """Remove comments and every whitespace character."""
    return re.sub(r"\s+", "", line.split("//", 1)[0])


def comp_bits(text):
    if text in COMP:
        return COMP[text]
    # accept the commutative spellings: A+D, M+D, A&D, M|D ...
    for op in "+&|":
        if op in text:
            left, _, right = text.partition(op)
            swapped = right + op + left
            if swapped in COMP:
                return COMP[swapped]
    raise AsmError(f"unknown computation '{text}'")


def dest_bits(text):
    if text == "":
        return "000"
    if any(c not in "ADM" for c in text) or len(set(text)) != len(text):
        raise AsmError(f"unknown destination '{text}'")
    return ("1" if "A" in text else "0") + ("1" if "D" in text else "0") + ("1" if "M" in text else "0")


def jump_bits(text):
    if text not in JUMP:
        raise AsmError(f"unknown jump '{text}'")
    return JUMP[text]


def encode_c(code):
    dest, comp, jump = "", code, ""
    if "=" in code:
        dest, _, comp = code.partition("=")
    if ";" in comp:
        comp, _, jump = comp.partition(";")
    if comp == "":
        raise AsmError("missing computation")
    return "111" + comp_bits(comp) + dest_bits(dest) + jump_bits(jump)


def encode_a(code, symbols, state):
    body = code[1:]
    if body == "":
        raise AsmError("'@' has no address or symbol")
    if body.isdigit():
        value = int(body)
        if value > 32767:
            raise AsmError(f"address {value} is too big (max 32767)")
    elif SYMBOL_RE.match(body):
        if body not in symbols:               # new variable
            symbols[body] = state["next_var"]
            state["next_var"] += 1
        value = symbols[body]
    else:
        raise AsmError(f"'{body}' is not a valid number or symbol")
    return format(value, "016b")


def assemble(lines):
    """Returns (hack_lines, errors). errors is a list of 'Line N: ...' strings."""
    errors, symbols = [], dict(PREDEFINED)
    user_labels = {}            # user-defined labels only
    user_variables = {}         # variables allocated during second pass

    # ---------- first reading: find labels ----------
    instructions = []          # (line_number, text)
    for number, raw in enumerate(lines, start=1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith("("):
            if not text.endswith(")") or not SYMBOL_RE.match(text[1:-1]):
                errors.append(f"Line {number}: invalid label '{text}'")
                continue
            name = text[1:-1]
            if name in symbols:
                errors.append(f"Line {number}: label '{name}' is already defined")
                continue
            symbols[name] = len(instructions)
            user_labels[name] = len(instructions)
        else:
            instructions.append((number, text))

    # ---------- second reading: translate ----------
    state, output = {"next_var": 16}, []
    for number, text in instructions:
        try:
            if text.startswith("@") and len(text) > 1:
                symbol = text[1:]
                was_new = (not symbol.isdigit() and SYMBOL_RE.match(symbol)
                           and symbol not in symbols)
                machine_code = encode_a(text, symbols, state)
                if was_new:
                    user_variables[symbol] = symbols[symbol]
                output.append(machine_code)
            else:
                output.append(encode_c(text))
        except AsmError as why:
            errors.append(f"Line {number}: invalid instruction '{text}' - {why}")
    errors.sort(key=lambda e: int(e.split()[1].rstrip(":")))   # show in line order
    symbol_entries = []
    symbol_entries.extend(("LABEL", name, address)
                          for name, address in user_labels.items())
    symbol_entries.extend(("VARIABLE", name, address)
                          for name, address in user_variables.items())
    symbol_entries.sort(key=lambda item: (item[2], item[0], item[1]))
    return output, errors, symbol_entries


def main():
    if len(sys.argv) != 2 or not sys.argv[1].lower().endswith(".asm"):
        print("Usage: python assembler.py <file.asm>")
        return 2
    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as why:
        print(f"Cannot read '{path}': {why.strerror}")
        return 2

    hack, errors, symbol_entries = assemble(lines)
    if errors:
        for message in errors:
            print(message)
        print(f"Assembly failed: {len(errors)} error(s). No .hack file written.")
        return 1

    out_path = path[:-4] + ".hack"
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(hack) + "\n")
    symbols_path = os.path.join(os.path.dirname(path), "symbols.txt")
    with open(symbols_path, "w", encoding="utf-8") as f:
        f.write("# Type\tSymbol\tAddress\n")
        for kind, name, address in symbol_entries:
            f.write(f"{kind}\t{name}\t{address}\n")
    print(f"OK: {len(hack)} instructions written to {out_path}")
    print(f"OK: {len(symbol_entries)} labels/variables written to {symbols_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
