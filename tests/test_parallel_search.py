"""
Sanity tests for parallel (multi-threaded) search paths.
These catch regressions where the parallel code returns illegal moves or crashes.
"""

import unittest
import chess

from Interface import (
    find_best_move_parallel_from_c,
    find_best_move_parallel_timed_from_c,
)


class TestParallelSearch(unittest.TestCase):
    """Check that parallel search returns legal moves."""

    def test_parallel_fixed_depth_is_legal(self):
        board = chess.Board()
        move_uci = find_best_move_parallel_from_c(board.fen(), depth=2, num_threads=2)
        move = chess.Move.from_uci(move_uci)
        self.assertIn(move, board.legal_moves, "Parallel fixed-depth move should be legal")

    def test_parallel_timed_is_legal(self):
        board = chess.Board()
        move_uci, depth_reached, _ = find_best_move_parallel_timed_from_c(
            board.fen(), max_time_ms=500, num_threads=2
        )
        move = chess.Move.from_uci(move_uci)
        self.assertIn(move, board.legal_moves, "Parallel timed move should be legal")
        self.assertGreaterEqual(depth_reached, 1, "Timed search should report a reached depth")


if __name__ == "__main__":
    unittest.main()
