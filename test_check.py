#!/usr/bin/env python3
"""
Test script to verify check handling in Mergen engine
"""

import chess
from Interface import get_best_move_from_c, get_eval_from_c

def test_check_detection():
    """Test that the engine detects and responds to check correctly"""
    
    print("=" * 60)
    print("Testing Check Detection and Response")
    print("=" * 60)
    
    # Test 1: Simple check position - White king in check
    print("\n[Test 1] White king in check by Black queen")
    board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 0 1")
    print(board)
    print(f"Is white in check? {board.is_check()}")
    print(f"Legal moves for white: {board.legal_moves.count()}")
    
    # The C engine should only generate legal moves (moves that get out of check)
    fen = board.fen()
    try:
        best_move = get_best_move_from_c(fen, depth=3)
        print(f"Engine suggests: {best_move}")
        move = chess.Move.from_uci(best_move)
        if move in board.legal_moves:
            print("✓ Engine move is legal (gets out of check)")
            board.push(move)
            print(f"After move, white still in check? {board.is_check()}")
        else:
            print("✗ ERROR: Engine suggested illegal move!")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 2: Black king in check
    print("\n[Test 2] Black king in check by White queen")
    board = chess.Board("rnbqkbnr/ppp2ppp/8/3pp3/4P3/5Q2/PPPP1PPP/RNB1KBNR b KQkq - 0 1")
    print(board)
    print(f"Is black in check? {board.is_check()}")
    print(f"Legal moves for black: {board.legal_moves.count()}")
    
    fen = board.fen()
    try:
        best_move = get_best_move_from_c(fen, depth=3)
        print(f"Engine suggests: {best_move}")
        move = chess.Move.from_uci(best_move)
        if move in board.legal_moves:
            print("✓ Engine move is legal (gets out of check)")
            board.push(move)
            print(f"After move, black still in check? {board.is_check()}")
        else:
            print("✗ ERROR: Engine suggested illegal move!")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 3: Pin situation - piece pinned to king
    print("\n[Test 3] Piece pinned to king (cannot move)")
    board = chess.Board("rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
    print(board)
    print(f"Is white in check? {board.is_check()}")
    print(f"Legal moves: {board.legal_moves.count()}")
    
    # Test 4: Position where ignoring check would lose queen
    print("\n[Test 4] Check where queen is threatened")
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 1")
    print(board)
    print(f"Is black in check? {board.is_check()}")
    
    fen = board.fen()
    try:
        best_move = get_best_move_from_c(fen, depth=3)
        print(f"Engine suggests: {best_move}")
        move = chess.Move.from_uci(best_move)
        if move in board.legal_moves:
            print("✓ Engine move is legal")
            board.push(move)
            print(f"After move: {board.fen()}")
        else:
            print("✗ ERROR: Engine suggested illegal move!")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_check_detection()
