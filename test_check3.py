#!/usr/bin/env python3
"""
Test proper check situations
"""

import chess
from Interface import get_best_move_from_c

def test_real_check():
    """Test with actual check positions"""
    
    print("=" * 60)
    print("Testing Real Check Situations")
    print("=" * 60)
    
    # Test 1: Scholar's mate threat - Black in check
    print("\n[Test 1] Black in check from Queen on f7")
    board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    print(board)
    print(f"Is black in check? {board.is_check()}")
    print(f"Legal moves: {board.legal_moves.count()}")
    
    legal_moves = list(board.legal_moves)
    print(f"Legal moves: {[m.uci() for m in legal_moves]}")
    
    # Engine's response
    fen = board.fen()
    engine_move = get_best_move_from_c(fen, depth=4)
    print(f"\nEngine plays: {engine_move}")
    
    try:
        move = chess.Move.from_uci(engine_move)
        if move in board.legal_moves:
            print("✓ LEGAL move - engine handles check correctly!")
            board.push(move)
            print(f"After move, still in check? {board.is_check()}")
        else:
            print("✗ ILLEGAL move - BUG!")
    except:
        print("✗ Invalid move format")
    
    # Test 2: Simple rook check
    print("\n" + "=" * 60)
    print("[Test 2] Black in check from Rook on e8")
    board = chess.Board("r3k2r/8/8/8/8/8/8/4R3 b kq - 0 1")
    print(board)
    print(f"Is black in check? {board.is_check()}")
    print(f"Legal moves: {board.legal_moves.count()}")
    
    legal_moves = list(board.legal_moves)
    print(f"Legal moves: {[m.uci() for m in legal_moves]}")
    
    fen = board.fen()
    engine_move = get_best_move_from_c(fen, depth=4)
    print(f"\nEngine plays: {engine_move}")
    
    try:
        move = chess.Move.from_uci(engine_move)
        if move in board.legal_moves:
            print("✓ LEGAL move - engine handles check correctly!")
            board.push(move)
            print(f"After move, still in check? {board.is_check()}")
        else:
            print("✗ ILLEGAL move - BUG!")
            print(f"Legal moves were: {[m.uci() for m in legal_moves]}")
    except:
        print("✗ Invalid move format")
    
    # Test 3: Discovered check
    print("\n" + "=" * 60)
    print("[Test 3] Black in discovered check")
    board = chess.Board("4k3/8/8/8/8/3B4/8/4K2R b - - 0 1")
    print(board)
    print(f"Is black in check? {board.is_check()}")
    print(f"Legal moves: {board.legal_moves.count()}")
    
    legal_moves = list(board.legal_moves)
    print(f"Legal moves: {[m.uci() for m in legal_moves]}")
    
    fen = board.fen()
    engine_move = get_best_move_from_c(fen, depth=4)
    print(f"\nEngine plays: {engine_move}")
    
    try:
        move = chess.Move.from_uci(engine_move)
        if move in board.legal_moves:
            print("✓ LEGAL move - engine handles check correctly!")
            board.push(move)
            print(f"After move, still in check? {board.is_check()}")
        else:
            print("✗ ILLEGAL move - BUG!")
    except:
        print("✗ Invalid move format")

if __name__ == "__main__":
    test_real_check()
