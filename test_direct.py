#!/usr/bin/env python3
"""
Direct C library test
"""

import ctypes
import os

lib_path = os.path.abspath("Source/C/Engine.so")
lib = ctypes.CDLL(lib_path)

# Parse FEN and get legal moves count (we'll need to add this function to C)
# For now, just test the best move function

lib.find_best_move_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.find_best_move_from_fen.restype = ctypes.c_char_p

# Test position: Black in check from rook
fen = "r3k2r/8/8/8/8/8/8/4R3 b kq - 0 1"
print(f"Testing FEN: {fen}")
print("Black is in check from white rook on e1")
print("Legal moves should be: e8f8, e8d8, e8f7, e8d7")
print()

result = lib.find_best_move_from_fen(fen.encode(), 3)
move = result.decode()

print(f"C engine returned: {move}")

if move == "e8c8":
    print("BUG: Engine tried to castle while in check!")
elif move in ["e8f8", "e8d8", "e8f7", "e8d7"]:
    print("✓ Move is legal!")
else:
    print(f"Unexpected move: {move}")
