#!/usr/bin/env python3
"""
Debug check handling in C engine
"""

import chess
import ctypes
import os

# Load the C library
lib_path = os.path.abspath("Source/C/Engine.so")
lib = ctypes.CDLL(lib_path)

# Set up function prototypes
lib.find_best_move_from_fen.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.find_best_move_from_fen.restype = ctypes.c_char_p

def debug_check_position():
    """Debug a specific check position"""
    
    # Position where black is in check from rook
    board = chess.Board("r3k2r/8/8/8/8/8/8/4R3 b kq - 0 1")
    print("Position:")
    print(board)
    print(f"\nIs black in check? {board.is_check()}")
    print(f"Legal moves according to python-chess:")
    for move in board.legal_moves:
        print(f"  {move.uci()}")
    
    # Get what C engine thinks
    fen = board.fen()
    print(f"\nFEN: {fen}")
    
    c_move = lib.find_best_move_from_fen(fen.encode(), 3)
    c_move_str = c_move.decode()
    
    print(f"\nC engine suggests: {c_move_str}")
    
    # Is it legal?
    try:
        move = chess.Move.from_uci(c_move_str)
        if move in board.legal_moves:
            print("✓ Move is legal!")
        else:
            print("✗ Move is ILLEGAL!")
            print("\nThe C engine generated an illegal move.")
            print("This means generate_legal_moves() in C is not working correctly.")
    except:
        print("✗ Invalid move format")

if __name__ == "__main__":
    debug_check_position()
