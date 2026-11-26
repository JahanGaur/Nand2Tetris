# Nand to Tetris Capstone: Make the Computer Draw a Box

**Roll no.:** 2501730484  
**Personal number:** K = 84  
**Box:** starts at row 84, is 20 rows tall, and is 16 pixels wide (one 16-bit screen word), from the left edge.  
**Assembler extra feature (K mod 3 = 0):** save user-defined labels and variables with their resolved addresses in `symbols.txt`.

## Files

| File | Part | Purpose |
|---|---|---|
| `CPU.hdl`, `Memory.hdl`, `Computer.hdl` | A | Hack CPU, memory map, and complete computer |
| `assembler.py` | B | Two-pass Hack assembler; generates `.hack` and `symbols.txt` |
| `Box.asm` / `Box.hack` | C | Personalized keyboard-controlled box program and machine code |
| `verify_box.py` | Optional check | Small simulator to check the box's screen-memory footprint |
| `Test/` | B | Add, Max, Rect, and Pong assembly test programs |
| `screenshots/` | Report | Existing screenshots from the supplied project; replace/retake as needed for your own run |

## Run

From this directory:

```bash
python assembler.py Box.asm
python verify_box.py Box.hack 84
```

The assembler writes `Box.hack` and `symbols.txt` in this directory. To assemble the supplied tests:

```bash
python assembler.py Test/Add.asm
python assembler.py Test/Max.asm
python assembler.py Test/Rect.asm
python assembler.py Test/Pong.asm
```

## Box calculation

- Screen base address: `SCREEN = 16384`
- One screen row: 32 words
- Starting row offset: `32 * 84 = 2688` words
- First screen word: `16384 + 2688 = 19072`
- Height: 20 rows (84–103)
- Width: 1 word = 16 pixels

The program polls `KBD`. If the keyboard memory-mapped value is non-zero, it writes `-1` to the first word of each of the 20 rows. Otherwise it writes `0` to those same words, erasing the box.

## Part A testing

Open the NAND2Tetris Web IDE, load the corresponding Project 5 chips, and run the official tests (`CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, and `ComputerRect.tst`). Keep screenshots of your own test runs in `screenshots/`. The HDL files in this folder are the supplied implementation; verify them in your environment before claiming a pass.

## Report reminder

Include your name, roll number, K, the calculated box dimensions, screenshots from your own official tests, a screenshot of the box while a key is held, and one paragraph explaining a mistake you fixed. Do not submit screenshots belonging to another student as your own evidence.
