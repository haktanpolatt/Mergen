"""
Test suite for PGN save/load functionality.
"""

import unittest
import os
import chess
from Source.Notation import (save_game_pgn, load_game_pgn, list_saved_games,
                             export_position_fen, load_position_fen)


class TestPGNSaveLoad(unittest.TestCase):
    """Test PGN save and load functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = "test_pgn_save_load.pgn"
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(f"Records/{self.test_file}"):
            os.remove(f"Records/{self.test_file}")
    
    def test_save_game_pgn(self):
        """Test saving a game to PGN format."""
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))
        
        filename = save_game_pgn(
            board,
            filename=self.test_file,
            white_player="Test White",
            black_player="Test Black",
            event="Test Event"
        )
        
        self.assertTrue(os.path.exists(filename), "PGN file should be created")
    
    def test_load_game_pgn(self):
        """Test loading a game from PGN format."""
        # First save a game
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))
        board.push(chess.Move.from_uci("g1f3"))
        
        save_game_pgn(board, filename=self.test_file)
        
        # Now load it back
        loaded_board = load_game_pgn(self.test_file)
        
        self.assertIsNotNone(loaded_board, "Should load board from PGN")
        if loaded_board:
            self.assertEqual(len(loaded_board.move_stack), 3, 
                            "Should have 3 moves")
            self.assertEqual(loaded_board.fen(), board.fen(),
                            "Loaded position should match saved position")
    
    def test_pgn_headers(self):
        """Test that PGN headers are correct."""
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        
        save_game_pgn(
            board,
            filename=self.test_file,
            white_player="Alice",
            black_player="Bob",
            event="Championship",
            depth=5
        )
        
        # Read the PGN file
        with open(f"Records/{self.test_file}") as f:
            content = f.read()
        
        self.assertIn("Alice", content, "Should have white player name")
        self.assertIn("Bob", content, "Should have black player name")
        self.assertIn("Championship", content, "Should have event name")
        self.assertIn("Depth 5", content, "Should have depth in headers")
    
    def test_list_saved_games(self):
        """Test listing saved games."""
        # Save a test game
        board = chess.Board()
        save_game_pgn(board, filename=self.test_file)
        
        # List games
        games = list_saved_games()
        
        self.assertGreater(len(games), 0, "Should find saved games")
        
        # Check if our test game is in the list
        test_game_found = any(g['filename'] == self.test_file for g in games)
        self.assertTrue(test_game_found, "Should find our test game in list")


class TestFENSaveLoad(unittest.TestCase):
    """Test FEN save and load functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = "test_fen_save_load.fen"
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(f"Records/{self.test_file}"):
            os.remove(f"Records/{self.test_file}")
    
    def test_export_position_fen(self):
        """Test exporting position as FEN."""
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        
        filename = export_position_fen(board, filename=self.test_file)
        
        self.assertTrue(os.path.exists(filename), "FEN file should be created")
    
    def test_load_position_fen(self):
        """Test loading position from FEN."""
        # Create a position
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))
        
        # Save it
        export_position_fen(board, filename=self.test_file)
        
        # Load it back
        loaded_board = load_position_fen(self.test_file)
        
        self.assertIsNotNone(loaded_board, "Should load board from FEN")
        if loaded_board:
            self.assertEqual(loaded_board.fen(), board.fen(),
                            "Loaded position should match saved position")
    
    def test_fen_roundtrip(self):
        """Test FEN save/load roundtrip preserves position."""
        # Various positions
        test_positions = [
            chess.Board(),  # Starting position
            chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"),
            chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"),
        ]
        
        for original_board in test_positions:
            export_position_fen(original_board, filename=self.test_file)
            loaded_board = load_position_fen(self.test_file)
            
            self.assertIsNotNone(loaded_board)
            if loaded_board:
                self.assertEqual(loaded_board.fen(), original_board.fen(),
                               "Roundtrip should preserve FEN")


class TestPGNGameResults(unittest.TestCase):
    """Test PGN game result detection."""
    
    def test_checkmate_result(self):
        """Test that checkmate is recorded in PGN."""
        # Fool's mate
        board = chess.Board()
        board.push(chess.Move.from_uci("f2f3"))
        board.push(chess.Move.from_uci("e7e5"))
        board.push(chess.Move.from_uci("g2g4"))
        board.push(chess.Move.from_uci("d8h4"))  # Checkmate
        
        filename = save_game_pgn(board, filename="test_checkmate.pgn")
        
        # Read PGN and check result
        with open(filename) as f:
            content = f.read()
        
        self.assertIn("0-1", content, "Should record black victory")
        
        # Cleanup
        os.remove(filename)
    
    def test_stalemate_result(self):
        """Test that stalemate is recorded as draw."""
        # Create stalemate position - black king has no legal moves but not in check
        board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        
        self.assertTrue(board.is_stalemate(), "Position should be stalemate")
        
        filename = save_game_pgn(board, filename="test_stalemate.pgn")
        
        with open(filename) as f:
            content = f.read()
        
        self.assertIn("1/2-1/2", content, "Should record draw")
        
        # Cleanup
        os.remove(filename)


if __name__ == '__main__':
    unittest.main()
