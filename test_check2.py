#!/usr/bin/env python3
"""
Test that engine properly responds to check
"""

import chess
from Interface import get_best_move_from_c

def test_engine_in_check():
    """Test that engine makes legal moves when in check"""
    
    print("=" * 60)
    print("Testing Engine Response to Check")
    print("=" * 60)
    
    # Test: Black (engine) is in check and must respond
    print("\n[Test] Black king in check - engine MUST get out of check")
    print("White queen on f3 attacks black king on e8")
    
    # Position: Black king in check from white queen
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/5Q2/PPPPPPPP/RNB1KBNR b KQkq - 0 1")
    print(board)
    print(f"\nIs black in check? {board.is_check()}")
    print(f"Black has {board.legal_moves.count()} legal moves")
    
    # List legal moves
    legal_moves_list = list(board.legal_moves)
    print(f"Legal moves: {[m.uci() for m in legal_moves_list]}")
    
    # Get engine's move
    fen = board.fen()
    engine_move_uci = get_best_move_from_c(fen, depth=4)
    print(f"\nEngine wants to play: {engine_move_uci}")
    
    # Check if it's legal
    try:
        engine_move = chess.Move.from_uci(engine_move_uci)
        if engine_move in board.legal_moves:
            print("✓ Engine move is LEGAL - correctly handles check!")
            board.push(engine_move)
            print(f"After engine's move, still in check? {board.is_check()}")
            print("\nBoard after move:")
            print(board)
        else:
            print("✗ ERROR: Engine move is ILLEGAL - ignores check!")
            print(f"   Engine tried: {engine_move_uci}")
            print(f"   But legal moves are: {[m.uci() for m in legal_moves_list]}")
    except Exception as e:
        print(f"✗ ERROR: Invalid move format: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Another check position
    print("\n[Test 2] Black in check from rook")
    board = chess.Board("r3k3/8/8/8/8/8/8/4K2R b K - 0 1")
    print(board)
    print(f"Is black in check? {board.is_check()}")
    print(f"Black has {board.legal_moves.count()} legal moves")
    
    legal_moves_list = list(board.legal_moves)
    print(f"Legal moves: {[m.uci() for m in legal_moves_list]}")
    
    fen = board.fen()
    engine_move_uci = get_best_move_from_c(fen, depth=4)
    print(f"\nEngine wants to play: {engine_move_uci}")
    
    try:
        engine_move = chess.Move.from_uci(engine_move_uci)
        if engine_move in board.legal_moves:
            print("✓ Engine move is LEGAL")
            board.push(engine_move)
            print(f"After move, still in check? {board.is_check()}")
        else:
            print("✗ ERROR: Engine move is ILLEGAL")
    except Exception as e:
        print(f"✗ ERROR: {e}")

if __name__ == "__main__":
    test_engine_in_check()
