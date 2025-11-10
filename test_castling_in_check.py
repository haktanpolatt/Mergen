#!/usr/bin/env python3
"""
Minimal test to isolate the bug
"""

import chess

# Test the exact FEN where the bug occurs
board = chess.Board("r3k2r/8/8/8/8/8/8/4R3 b kq - 0 1")
print("Board:")
print(board)
print(f"\nBlack to move")
print(f"Is black in check? {board.is_check()}")
print(f"\nLegal moves:")
for move in board.legal_moves:
    print(f"  {move.uci()} - {board.san(move)}")

# Now check what's legal
print("\n--- Checking specific moves ---")

# Try e8c8 (queenside castling)
try:
    move = chess.Move.from_uci("e8c8")
    if move in board.legal_moves:
        print("e8c8 (O-O-O): LEGAL")
    else:
        print("e8c8 (O-O-O): ILLEGAL (can't castle while in check!)")
except:
    print("e8c8: Invalid")

# Try e8d8
try:
    move = chess.Move.from_uci("e8d8")
    if move in board.legal_moves:
        print("e8d8: LEGAL")
    else:
        print("e8d8: ILLEGAL")
except:
    print("e8d8: Invalid")
