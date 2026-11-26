// Box.asm - Nand to Tetris Capstone, Part C
// Roll no: 2501730484
// Personal number K = 84
//
// Box starts at row 84 (left edge, column 0).
// Height = 20 rows: rows 84 through 103 inclusive.
// Width = 16 * ((84 mod 4) + 1) = 16 pixels = 1 screen word.
// First address = SCREEN + (32 * 84) = SCREEN + 2688.
//
// While a key is pressed, each row's first word is filled with 0xFFFF.
// When no key is pressed, those same words are cleared to 0.

(LOOP)
    // Check keyboard. Any non-zero value means a key is pressed.
    @KBD
    D=M
    @PRESSED
    D;JNE

    // No key: choose white (zero) to erase the box.
    @color
    M=0
    @DRAW
    0;JMP

(PRESSED)
    // Key pressed: choose black (all bits set).
    @color
    M=-1

(DRAW)
    // addr = SCREEN + 32*84 = SCREEN + 2688
    @SCREEN
    D=A
    @2688
    D=D+A
    @addr
    M=D

    // count = 20 rows
    @20
    D=A
    @count
    M=D

(ROW)
    // Draw one 16-pixel word at the left edge of this row.
    @color
    D=M
    @addr
    A=M
    M=D

    // Advance 32 words to the next screen row.
    @32
    D=A
    @addr
    M=D+M

    // count-- ; repeat until all 20 rows are drawn.
    @count
    M=M-1
    D=M
    @ROW
    D;JGT

    // Keep checking the keyboard continuously.
    @LOOP
    0;JMP
