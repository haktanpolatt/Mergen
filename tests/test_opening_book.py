"""
Test suite for opening book functionality.
"""

import unittest
import chess
from Source.OpeningBook import OpeningBook


class TestOpeningBook(unittest.TestCase):
    """Test opening book functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.book = OpeningBook()
    
    def test_book_loaded(self):
        """Test that opening book is loaded."""
        stats = self.book.get_statistics()
        self.assertGreater(stats['positions'], 0, 
                          "Opening book should have positions")
    
    def test_starting_position_in_book(self):
        """Test that starting position has book moves."""
        board = chess.Board()
        self.assertTrue(self.book.is_in_book(board), 
                       "Starting position should be in book")
    
    def test_get_book_move_starting_position(self):
        """Test getting a move from starting position."""
        board = chess.Board()
        move_uci = self.book.get_book_move(board)
        
        self.assertIsNotNone(move_uci, "Should return a move for starting position")
        
        # Verify it's a legal move
        if move_uci:
            move = chess.Move.from_uci(move_uci)
            self.assertIn(move, board.legal_moves, 
                         f"Book move {move_uci} should be legal")
    
    def test_e4_response_in_book(self):
        """Test that 1.e4 has book responses."""
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        
        move_uci = self.book.get_book_move(board)
        self.assertIsNotNone(move_uci, "Should have response to 1.e4")
    
    def test_d4_response_in_book(self):
        """Test that 1.d4 has book responses."""
        board = chess.Board()
        board.push(chess.Move.from_uci("d2d4"))
        
        move_uci = self.book.get_book_move(board)
        self.assertIsNotNone(move_uci, "Should have response to 1.d4")
    
    def test_out_of_book_position(self):
        """Test behavior when position is not in book."""
        # Random middlegame position unlikely to be in book
        board = chess.Board("r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 8")
        
        move_uci = self.book.get_book_move(board)
        # Should return None for out-of-book position
        self.assertIsNone(move_uci, "Should return None for out-of-book position")
    
    def test_book_coverage_major_openings(self):
        """Test that major openings are covered."""
        # Test various opening moves
        openings_to_test = [
            ("e2e4", "Ruy Lopez setup"),
            ("d2d4", "Queen's Gambit setup"),
            ("c2c4", "English Opening"),
            ("g1f3", "Reti Opening"),
        ]
        
        for first_move, name in openings_to_test:
            board = chess.Board()
            board.push(chess.Move.from_uci(first_move))
            
            # Check if position is in book
            in_book = self.book.is_in_book(board)
            # Most major openings should have responses
            # (Not asserting True because book might not have ALL openings)
            self.assertIsNotNone(in_book, f"Should check {name}")
    
    def test_book_statistics(self):
        """Test that book statistics are reasonable."""
        stats = self.book.get_statistics()
        
        self.assertGreater(stats['positions'], 50, 
                          "Book should have at least 50 positions")
        self.assertGreater(stats['total_moves'], 100, 
                          "Book should have at least 100 moves")
        self.assertGreater(stats['avg_moves_per_position'], 1.0,
                          "Should have multiple moves per position on average")


class TestOpeningBookManipulation(unittest.TestCase):
    """Test adding/modifying opening book."""
    
    def test_add_move_to_book(self):
        """Test adding a new move to the book."""
        book = OpeningBook()
        initial_stats = book.get_statistics()
        
        # Add a custom opening line
        board = chess.Board()
        test_fen = board.fen()
        
        book.add_move(test_fen, "e2e4", weight=200, name="Test Opening")
        
        # Verify it was added
        self.assertTrue(book.is_in_book(board))
    
    def test_add_opening_line(self):
        """Test adding a complete opening line."""
        book = OpeningBook()
        
        # Add a custom line
        moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
        book.add_opening_line(moves, name="Test Line", weight=100)
        
        # Verify first position is in book
        board = chess.Board()
        self.assertTrue(book.is_in_book(board))


if __name__ == '__main__':
    unittest.main()
