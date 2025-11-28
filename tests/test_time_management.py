"""
Tests for the time management system.
Focuses on detecting controls, emergency mode, and the fixed/infinite cases.
"""

import unittest
import chess

from Source.TimeManagement import (
    TimeManager,
    TimeControl,
    GamePhase,
    detect_time_control,
)


class TestTimeManagement(unittest.TestCase):
    """Validate core time-allocation behaviors."""

    def test_detect_time_control(self):
        self.assertEqual(detect_time_control(60), TimeControl.BULLET)
        self.assertEqual(detect_time_control(300), TimeControl.BLITZ)
        self.assertEqual(detect_time_control(1200), TimeControl.RAPID)
        self.assertEqual(detect_time_control(4000), TimeControl.CLASSICAL)

    def test_infinite_and_fixed_time(self):
        board = chess.Board()
        tm_inf = TimeManager(total_time=9999, time_control=TimeControl.INFINITE)
        target, max_time = tm_inf.get_time_for_move(board)
        self.assertTrue(target == float("inf") and max_time == float("inf"))

        tm_fixed = TimeManager(total_time=5.0, time_control=TimeControl.FIXED_TIME)
        target, max_time = tm_fixed.get_time_for_move(board)
        self.assertEqual(target, 5.0)
        self.assertEqual(max_time, 5.0)

    def test_emergency_mode_limits_time(self):
        board = chess.Board()
        tm = TimeManager(total_time=5.0, increment=0.0, time_control=TimeControl.BLITZ)
        target, max_time = tm.get_time_for_move(board)
        self.assertLessEqual(target, 0.5, "Emergency target should be <=10% of remaining")
        self.assertLessEqual(max_time, 0.75, "Emergency max should be <=15% of remaining")

    def test_time_updates_include_increment(self):
        tm = TimeManager(total_time=60.0, increment=2.0, time_control=TimeControl.BLITZ)
        tm.update_time(5.0)
        self.assertAlmostEqual(tm.total_time, 57.0)
        tm.update_time(10.0)
        self.assertAlmostEqual(tm.total_time, 49.0)

    def test_phase_detection_opening_and_endgame(self):
        tm = TimeManager(total_time=600, time_control=TimeControl.RAPID)
        opening_board = chess.Board()
        self.assertEqual(tm._detect_game_phase(opening_board), GamePhase.OPENING)
        endgame_board = chess.Board("8/8/8/8/8/8/4K3/7k w - - 0 20")
        self.assertEqual(tm._detect_game_phase(endgame_board), GamePhase.ENDGAME)

    def test_time_allocation_scales_by_control(self):
        board = chess.Board()
        bullet_tm = TimeManager(total_time=180, increment=0, time_control=TimeControl.BULLET)
        classical_tm = TimeManager(total_time=1800, increment=0, time_control=TimeControl.CLASSICAL)
        bullet_target, _ = bullet_tm.get_time_for_move(board)
        classical_target, _ = classical_tm.get_time_for_move(board)
        self.assertLess(bullet_target, classical_target, "Bullet allocation should be smaller than classical")


if __name__ == "__main__":
    unittest.main()
