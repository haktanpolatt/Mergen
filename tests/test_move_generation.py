"""
Test suite for move generation correctness.

Tests various positions to ensure legal move generation is correct.
"""

import unittest
import chess
from Interface import get_best_move_from_c


class TestMoveGeneration(unittest.TestCase):
    """Test move generation in various positions."""
    
    def test_starting_position_legal_moves(self):
        """Test that starting position has 20 legal moves."""
        board = chess.Board()
        legal_moves = list(board.legal_moves)
        self.assertEqual(len(legal_moves), 20, "Starting position should have 20 legal moves")
    
    def test_no_illegal_moves(self):
        """Test that engine doesn't suggest illegal moves."""
        test_positions = [
            chess.Board(),  # Starting position
            chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"),  # After e4
            chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq e6 0 3"),  # After e4 e5 Nf3
        ]
        
        for board in test_positions:
            move_uci = get_best_move_from_c(board.fen(), depth=2)
            move = chess.Move.from_uci(move_uci)
            self.assertIn(move, board.legal_moves, 
                         f"Move {move_uci} should be legal in position {board.fen()}")
    
    def test_checkmate_detection(self):
        """Test that engine detects checkmate positions."""
        # Fool's mate
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        self.assertTrue(board.is_checkmate(), "Should detect fool's mate checkmate")
    
    def test_stalemate_detection(self):
        """Test stalemate detection."""
        # Stalemate position - black king has no legal moves but not in check
        board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertTrue(board.is_stalemate(), "Should detect stalemate")
    
    def test_castling_availability(self):
        """Test castling rights detection."""
        # Italian Game position where white can castle kingside
        board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
        
        # King to g1 (castling)
        castling_move = chess.Move.from_uci("e1g1")
        self.assertIn(castling_move, board.legal_moves, "Kingside castling should be legal")
    
    def test_en_passant_capture(self):
        """Test en passant capture detection."""
        # Set up position with en passant
        board = chess.Board("rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3")
        
        # e5xf6 en passant
        en_passant = chess.Move.from_uci("e5f6")
        self.assertIn(en_passant, board.legal_moves, "En passant should be legal")
    
    def test_promotion_moves(self):
        """Test pawn promotion move generation."""
        # White pawn about to promote
        board = chess.Board("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        
        legal_moves = list(board.legal_moves)
        promotion_moves = [m for m in legal_moves if m.promotion]
        
        # Should have 4 promotion options (Q, R, B, N)
        self.assertEqual(len(promotion_moves), 4, 
                        "Should have 4 promotion options for pawn on 7th rank")


class TestPerftPositions(unittest.TestCase):
    """Test move generation with PERFT positions."""
    
    def count_nodes(self, board, depth):
        """Count leaf nodes at given depth (perft)."""
        if depth == 0:
            return 1
        
        nodes = 0
        for move in board.legal_moves:
            board.push(move)
            nodes += self.count_nodes(board, depth - 1)
            board.pop()
        return nodes
    
    def test_perft_starting_position_depth_1(self):
        """PERFT test: starting position, depth 1."""
        board = chess.Board()
        nodes = self.count_nodes(board, 1)
        self.assertEqual(nodes, 20, "Depth 1 from start should be 20")
    
    def test_perft_starting_position_depth_2(self):
        """PERFT test: starting position, depth 2."""
        board = chess.Board()
        nodes = self.count_nodes(board, 2)
        self.assertEqual(nodes, 400, "Depth 2 from start should be 400")
    
    def test_perft_kiwipete_depth_1(self):
        """PERFT test: Kiwipete position, depth 1."""
        # Famous PERFT test position
        board = chess.Board("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
        nodes = self.count_nodes(board, 1)
        self.assertEqual(nodes, 48, "Kiwipete depth 1 should be 48")


if __name__ == '__main__':
    unittest.main()
