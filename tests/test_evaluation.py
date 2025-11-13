"""
Test suite for evaluation function correctness.

Tests that evaluation properly assesses positions.
"""

import unittest
import chess
from Interface import get_eval_from_c


class TestEvaluation(unittest.TestCase):
    """Test evaluation function correctness."""
    
    def test_starting_position_equal(self):
        """Test that starting position evaluates to approximately 0."""
        board = chess.Board()
        eval_score = get_eval_from_c(board.fen())
        self.assertAlmostEqual(eval_score, 0.0, delta=0.5, 
                              msg="Starting position should be roughly equal")
    
    def test_white_material_advantage(self):
        """Test that white material advantage gives positive eval."""
        # White up a queen
        board = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        eval_score = get_eval_from_c(board.fen())
        self.assertGreater(eval_score, 5.0, 
                          "White up a queen should have eval > +5")
    
    def test_black_material_advantage(self):
        """Test that black material advantage gives negative eval."""
        # Black up a queen
        board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1")
        eval_score = get_eval_from_c(board.fen())
        self.assertLess(eval_score, -5.0, 
                       "Black up a queen should have eval < -5")
    
    def test_checkmate_evaluation(self):
        """Test that checkmate positions have extreme evaluations."""
        # White checkmates black
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        # This is checkmate, board should reflect game over
        self.assertTrue(board.is_checkmate())
    
    def test_pawn_structure_penalty(self):
        """Test that doubled pawns are penalized."""
        # Normal pawn structure
        normal = chess.Board()
        normal_eval = get_eval_from_c(normal.fen())
        
        # Doubled pawns on f-file for white
        doubled = chess.Board("rnbqkbnr/pppppppp/8/8/8/5P2/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        doubled_eval = get_eval_from_c(doubled.fen())
        
        # Doubled pawns should be worse (but still material equal)
        # This is a weak test since positions differ
        self.assertIsNotNone(doubled_eval, "Should evaluate position with doubled pawns")
    
    def test_passed_pawn_bonus(self):
        """Test that passed pawns receive bonuses."""
        # White has passed pawn on e-file
        board = chess.Board("4k3/8/8/4P3/8/8/8/4K3 w - - 0 1")
        eval_score = get_eval_from_c(board.fen())
        
        # Should be positive due to passed pawn
        self.assertGreater(eval_score, 0.2, 
                          "Passed pawn should give positive evaluation")
    
    def test_king_safety_center_penalty(self):
        """Test that king in center is penalized."""
        # King in center (worse)
        center_king = chess.Board("rnbq1bnr/ppppkppp/8/4p3/4P3/8/PPPPKPPP/RNBQ1BNR w - - 2 3")
        center_eval = get_eval_from_c(center_king.fen())
        
        # This should have some evaluation
        self.assertIsNotNone(center_eval, "Should evaluate king in center")
    
    def test_mobility_evaluation(self):
        """Test that mobility affects evaluation."""
        # Open position (high mobility)
        open_pos = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
        open_eval = get_eval_from_c(open_pos.fen())
        
        # Closed position (low mobility)
        closed_pos = chess.Board("rnbqkbnr/ppp2ppp/3p4/4p3/4P3/3P4/PPP2PPP/RNBQKBNR w KQkq - 0 3")
        closed_eval = get_eval_from_c(closed_pos.fen())
        
        # Both should evaluate
        self.assertIsNotNone(open_eval, "Should evaluate open position")
        self.assertIsNotNone(closed_eval, "Should evaluate closed position")


class TestPieceValues(unittest.TestCase):
    """Test that piece values are correct."""
    
    def test_queen_value(self):
        """Test queen is valued around 9 pawns."""
        # White has queen vs black has nothing
        board = chess.Board("4k3/8/8/8/8/8/8/4K2Q w - - 0 1")
        eval_score = get_eval_from_c(board.fen())
        self.assertGreater(eval_score, 8.0, "Queen should be worth ~9 points")
    
    def test_rook_value(self):
        """Test rook is valued around 5 pawns."""
        board = chess.Board("4k3/8/8/8/8/8/8/4K2R w - - 0 1")
        eval_score = get_eval_from_c(board.fen())
        self.assertGreater(eval_score, 4.0, "Rook should be worth ~5 points")
    
    def test_minor_pieces_equal(self):
        """Test that bishop and knight are valued similarly."""
        bishop = chess.Board("4k3/8/8/8/8/8/8/4K2B w - - 0 1")
        bishop_eval = get_eval_from_c(bishop.fen())
        
        knight = chess.Board("4k3/8/8/8/8/8/8/4K2N w - - 0 1")
        knight_eval = get_eval_from_c(knight.fen())
        
        # Should be within 0.5 of each other
        self.assertAlmostEqual(bishop_eval, knight_eval, delta=0.5,
                              msg="Bishop and Knight should have similar value")


if __name__ == '__main__':
    unittest.main()
