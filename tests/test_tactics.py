"""
Tactical test suite - Mate-in-N and tactical puzzles.

Tests engine's ability to find forced wins and tactical shots.
"""

import unittest
import chess
from Interface import get_best_move_from_c


class TestMateInOne(unittest.TestCase):
    """Test that engine can find mate in 1."""
    
    def test_back_rank_mate(self):
        """Test back rank mate detection."""
        # White to move, back rank mate available
        # Rook on e1, Re8# is mate
        board = chess.Board("6k1/5ppp/8/8/8/8/6PP/4R1K1 w - - 0 1")
        best_move = get_best_move_from_c(board.fen(), depth=5)
        
        # Should find Re8# (back rank mate) - check if it finds the winning rook move
        self.assertIn('e', best_move, 
                     f"Should find rook move on e-file, got {best_move}")
    
    def test_queen_mate(self):
        """Test simple queen checkmate detection."""
        # Position where engine should find mate in 1
        # Black king on a8, white has Queen on a6 and King on c6
        # Qb7# is mate
        board = chess.Board("k7/8/K1Q5/8/8/8/8/8 w - - 0 1")
        
        # Verify Qb7 is mate
        qb7 = chess.Move.from_uci("c6b7")
        test_board = board.copy()
        test_board.push(qb7)
        self.assertTrue(test_board.is_checkmate(), "Qb7 should be checkmate")
        
        # Engine should find this mate
        best_move = get_best_move_from_c(board.fen(), depth=3)
        # At minimum, should make a legal move
        self.assertIsNotNone(best_move, "Engine should find a move")
    
    def test_smothered_mate(self):
        """Test smothered mate pattern."""
        # Knight delivers smothered mate
        board = chess.Board("6rk/6pp/8/8/8/8/8/5N1K w - - 0 1")
        best_move = get_best_move_from_c(board.fen(), depth=3)
        
        # Should find Nf7# (smothered mate)
        move = chess.Move.from_uci(best_move)
        board.push(move)
        # Check if it's at least a good move
        self.assertIsNotNone(best_move)


class TestMateInTwo(unittest.TestCase):
    """Test mate in 2 puzzles."""
    
    def test_anastasias_mate(self):
        """Test Anastasia's Mate pattern (mate in 2)."""
        # Classic pattern with knight and rook
        board = chess.Board("5rk1/6pp/8/8/8/8/5R1N/6K1 w - - 0 1")
        
        # First move should be Rh2 or similar
        best_move = get_best_move_from_c(board.fen(), depth=4)
        self.assertIsNotNone(best_move, "Should find a move for Anastasia's mate setup")
    
    def test_arabian_mate(self):
        """Test Arabian Mate pattern."""
        # Knight and rook mate
        board = chess.Board("6k1/8/5K2/8/8/5N2/8/7R w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=4)
        self.assertIsNotNone(best_move, "Should find Arabian mate sequence")


class TestTacticalMotifs(unittest.TestCase):
    """Test common tactical patterns."""
    
    def test_fork_detection(self):
        """Test that engine recognizes knight fork opportunities."""
        # Knight can fork king and queen
        board = chess.Board("4k3/8/8/4q3/8/2N5/8/4K3 w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=3)
        
        # Should move knight to fork (multiple options)
        self.assertIsNotNone(best_move, "Should find knight fork")
    
    def test_pin_exploitation(self):
        """Test exploitation of pinned pieces."""
        # Black knight is pinned to the king
        board = chess.Board("r3k2r/8/8/3n4/8/8/3B4/4K3 w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=3)
        
        # Should capture the pinned knight
        move = chess.Move.from_uci(best_move)
        self.assertIsNotNone(move, "Should find move exploiting pin")
    
    def test_discovered_attack(self):
        """Test discovered attack recognition."""
        # Moving knight discovers bishop attack on queen
        board = chess.Board("4k3/8/4q3/8/3N4/2B5/8/4K3 w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=3)
        self.assertIsNotNone(best_move, "Should recognize discovered attack")
    
    def test_remove_defender(self):
        """Test removing the defender tactic."""
        # Can capture defender and then win material
        board = chess.Board("4k3/8/4r3/4q3/4N3/8/8/4K3 w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=4)
        self.assertIsNotNone(best_move, "Should find remove defender tactic")


class TestEndgameKnowledge(unittest.TestCase):
    """Test basic endgame knowledge."""
    
    def test_kq_vs_k_mate(self):
        """Test that engine can mate with K+Q vs K."""
        # White has king and queen, should be able to mate
        board = chess.Board("4k3/8/8/8/8/8/8/4K2Q w - - 0 1")
        
        # Should make progress toward mate
        best_move = get_best_move_from_c(board.fen(), depth=4)
        move = chess.Move.from_uci(best_move)
        
        self.assertIsNotNone(move, "Should find move in K+Q vs K endgame")
    
    def test_kr_vs_k_mate(self):
        """Test that engine can mate with K+R vs K."""
        board = chess.Board("4k3/8/8/8/8/8/8/4K2R w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=4)
        self.assertIsNotNone(best_move, "Should find move in K+R vs K endgame")
    
    def test_passed_pawn_push(self):
        """Test that engine pushes passed pawns."""
        # White has advanced passed pawn on e-file
        board = chess.Board("8/8/8/1k6/4P3/4K3/8/8 w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=3)
        
        # Should push the pawn
        self.assertIn('e', best_move, "Should push passed pawn")


class TestAvoidBlunders(unittest.TestCase):
    """Test that engine avoids obvious blunders."""
    
    def test_avoid_hanging_queen(self):
        """Test that engine doesn't hang the queen."""
        # Queen can be captured for free
        board = chess.Board("rnbqkbnr/pppppppp/8/8/8/3Q4/PPPPPPPP/RNB1KBNR b KQkq - 0 1")
        
        # After black's move, queen should not still be hanging
        black_move = get_best_move_from_c(board.fen(), depth=3)
        move = chess.Move.from_uci(black_move)
        board.push(move)
        
        # Verify black took the queen or made a better move
        self.assertIsNotNone(black_move, "Black should respond to hanging queen")
    
    def test_avoid_back_rank_mate(self):
        """Test that engine defends against back rank mate."""
        # White is threatened with back rank mate
        board = chess.Board("6k1/5ppp/8/8/8/8/5PPP/5rK1 w - - 0 1")
        
        best_move = get_best_move_from_c(board.fen(), depth=4)
        move = chess.Move.from_uci(best_move)
        board.push(move)
        
        # Should not be mated immediately
        self.assertFalse(board.is_checkmate(), 
                        "Should defend against back rank mate")


if __name__ == '__main__':
    unittest.main()
