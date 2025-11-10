###############################
#                             #
#   Created on Nov 10, 2025   #
#                             #
###############################

"""
Time Management System for Mergen Chess Engine

This module implements smart time allocation based on:
- Game phase (opening/middlegame/endgame)
- Position complexity
- Time remaining
- Time control type
- Move urgency

References:
- Hyatt, R. M. (1997). "The Chess Program Crafty"
- Hsu, F. (2002). "Behind Deep Blue" - Time management strategies
"""

import chess
from typing import Tuple, Optional
from enum import Enum


class TimeControl(Enum):
    """Types of time controls"""
    BULLET = "bullet"           # < 3 minutes
    BLITZ = "blitz"             # 3-10 minutes
    RAPID = "rapid"             # 10-60 minutes
    CLASSICAL = "classical"     # > 60 minutes
    INFINITE = "infinite"       # No time limit
    FIXED_TIME = "fixed_time"   # Fixed time per move


class GamePhase(Enum):
    """Game phases for time allocation"""
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"


class TimeManager:
    """
    Smart time management for chess engine.
    
    Allocates time based on:
    1. Time control type
    2. Remaining time
    3. Game phase
    4. Position complexity
    5. Move number
    """
    
    def __init__(self, 
                 total_time: float,
                 increment: float = 0.0,
                 moves_to_go: Optional[int] = None,
                 time_control: TimeControl = TimeControl.RAPID):
        """
        Initialize time manager.
        
        Args:
            total_time: Total remaining time in seconds
            increment: Increment per move in seconds
            moves_to_go: Moves until next time control (or None for sudden death)
            time_control: Type of time control
        """
        self.total_time = total_time
        self.increment = increment
        self.moves_to_go = moves_to_go
        self.time_control = time_control
        self.move_number = 0
        
        # Time allocation factors
        self.base_time_factor = 0.04  # Base: 4% of remaining time per move
        self.min_time_factor = 0.01   # Minimum: 1% of remaining time
        self.max_time_factor = 0.15   # Maximum: 15% of remaining time
        
        # Emergency time threshold (seconds)
        self.emergency_threshold = 10.0
        
    def get_time_for_move(self, board: chess.Board) -> Tuple[float, float]:
        """
        Calculate time allocation for current move.
        
        Returns:
            Tuple of (target_time, max_time) in seconds
            - target_time: Ideal time to spend
            - max_time: Maximum time allowed (hard limit)
        """
        if self.time_control == TimeControl.INFINITE:
            return (float('inf'), float('inf'))
        
        if self.time_control == TimeControl.FIXED_TIME:
            return (self.total_time, self.total_time)
        
        # Detect game phase
        phase = self._detect_game_phase(board)
        
        # Calculate position complexity
        complexity = self._calculate_complexity(board)
        
        # Estimate moves remaining in game
        estimated_moves = self._estimate_moves_remaining(board, phase)
        
        # Base time allocation
        if self.moves_to_go:
            # Classical time control with moves to go
            base_time = (self.total_time - 5.0) / max(self.moves_to_go, 1)
        else:
            # Sudden death (no moves to go)
            base_time = (self.total_time - 5.0) / estimated_moves
        
        # Apply time control adjustment
        tc_factor = self._get_time_control_factor()
        base_time *= tc_factor
        
        # Apply game phase adjustment
        phase_factor = self._get_phase_factor(phase)
        base_time *= phase_factor
        
        # Apply complexity adjustment
        complexity_factor = 0.8 + (complexity * 0.4)  # 0.8 to 1.2
        base_time *= complexity_factor
        
        # Add increment to available time
        available_time = self.total_time + self.increment
        
        # Calculate target and max time
        target_time = max(0.1, min(base_time, available_time * self.max_time_factor))
        max_time = min(target_time * 2.5, available_time * 0.25)
        
        # Emergency time management
        if self.total_time < self.emergency_threshold:
            target_time = min(target_time, self.total_time * 0.1)
            max_time = min(max_time, self.total_time * 0.15)
        
        # Ensure we always have some time
        target_time = max(0.01, target_time)
        max_time = max(target_time, max_time)
        
        return (target_time, max_time)
    
    def _detect_game_phase(self, board: chess.Board) -> GamePhase:
        """
        Detect current game phase based on material and move count.
        
        Opening: Moves 1-15, most pieces on board
        Middlegame: Complex positions, many pieces
        Endgame: Few pieces remaining
        """
        move_count = board.fullmove_number
        
        # Count material
        piece_count = len(board.piece_map())
        
        # Simple phase detection
        if move_count <= 10:
            return GamePhase.OPENING
        elif piece_count <= 10:  # Few pieces = endgame
            return GamePhase.ENDGAME
        else:
            return GamePhase.MIDDLEGAME
    
    def _calculate_complexity(self, board: chess.Board) -> float:
        """
        Calculate position complexity (0.0 to 1.0).
        
        Factors:
        - Number of legal moves (mobility)
        - Material on board
        - Piece activity
        - Checks and threats
        """
        # Number of legal moves (normalized)
        legal_moves = len(list(board.legal_moves))
        mobility_score = min(legal_moves / 50.0, 1.0)
        
        # Material count (more pieces = more complex)
        piece_count = len(board.piece_map())
        material_score = min(piece_count / 32.0, 1.0)
        
        # Check if position has checks/captures
        tactical_score = 0.0
        if board.is_check():
            tactical_score += 0.3
        
        # Count available captures
        captures = sum(1 for move in board.legal_moves if board.is_capture(move))
        tactical_score += min(captures / 10.0, 0.2)
        
        # Weighted combination
        complexity = (
            mobility_score * 0.4 +
            material_score * 0.3 +
            tactical_score * 0.3
        )
        
        return min(max(complexity, 0.0), 1.0)
    
    def _estimate_moves_remaining(self, board: chess.Board, phase: GamePhase) -> int:
        """
        Estimate moves remaining in the game.
        
        Average game length: ~40 moves per side
        Adjust based on current phase and position
        """
        current_move = board.fullmove_number
        
        if phase == GamePhase.OPENING:
            # Estimate 35-40 more moves
            return max(35, 40 - current_move)
        elif phase == GamePhase.MIDDLEGAME:
            # Estimate 20-30 more moves
            return max(20, 35 - current_move)
        else:  # ENDGAME
            # Estimate 10-20 more moves
            return max(10, 25 - current_move)
    
    def _get_time_control_factor(self) -> float:
        """
        Get time allocation factor based on time control type.
        
        Bullet: Play faster, less thinking
        Blitz: Moderate speed
        Rapid: More thinking time
        Classical: Deep thinking
        """
        factors = {
            TimeControl.BULLET: 0.7,      # Play faster
            TimeControl.BLITZ: 0.9,       # Slightly faster
            TimeControl.RAPID: 1.0,       # Normal
            TimeControl.CLASSICAL: 1.2,   # Take more time
            TimeControl.INFINITE: 1.5,
            TimeControl.FIXED_TIME: 1.0
        }
        return factors.get(self.time_control, 1.0)
    
    def _get_phase_factor(self, phase: GamePhase) -> float:
        """
        Get time allocation factor based on game phase.
        
        Opening: Use book, think less
        Middlegame: Most critical, think more
        Endgame: Precision needed, moderate time
        """
        factors = {
            GamePhase.OPENING: 0.7,      # Use opening book, think less
            GamePhase.MIDDLEGAME: 1.2,   # Most complex, think more
            GamePhase.ENDGAME: 1.0       # Precision important
        }
        return factors.get(phase, 1.0)
    
    def should_stop_search(self, elapsed_time: float, target_time: float, 
                          max_time: float, depth: int) -> bool:
        """
        Decide whether to stop the search.
        
        Args:
            elapsed_time: Time spent so far
            target_time: Target time for this move
            max_time: Maximum allowed time
            depth: Current search depth
            
        Returns:
            True if search should stop, False otherwise
        """
        # Always stop if we exceed max time
        if elapsed_time >= max_time:
            return True
        
        # If we're below target time and haven't reached reasonable depth, continue
        if elapsed_time < target_time and depth < 4:
            return False
        
        # If we've reached target time and have reasonable depth, stop
        if elapsed_time >= target_time and depth >= 3:
            return True
        
        # In emergency time, stop after any completed depth
        if self.total_time < self.emergency_threshold and depth >= 2:
            return True
        
        return False
    
    def update_time(self, time_spent: float):
        """
        Update remaining time after a move.
        
        Args:
            time_spent: Time spent on the move in seconds
        """
        self.total_time -= time_spent
        self.total_time += self.increment
        self.total_time = max(0.0, self.total_time)
        self.move_number += 1
        
        # Update moves to go if applicable
        if self.moves_to_go is not None:
            self.moves_to_go -= 1
            if self.moves_to_go <= 0:
                # Reached time control, reset (implementation depends on rules)
                pass
    
    def get_status(self) -> dict:
        """Get current time management status."""
        return {
            'total_time': self.total_time,
            'increment': self.increment,
            'moves_to_go': self.moves_to_go,
            'time_control': self.time_control.value,
            'move_number': self.move_number,
            'emergency_mode': self.total_time < self.emergency_threshold
        }
    
    def format_time(self, seconds: float) -> str:
        """Format time in human-readable format."""
        if seconds >= 60:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            return f"{seconds:.1f}s"


def detect_time_control(total_time: float) -> TimeControl:
    """
    Auto-detect time control type based on total time.
    
    Args:
        total_time: Total time in seconds
        
    Returns:
        TimeControl enum
    """
    if total_time < 180:  # < 3 minutes
        return TimeControl.BULLET
    elif total_time < 600:  # < 10 minutes
        return TimeControl.BLITZ
    elif total_time < 3600:  # < 60 minutes
        return TimeControl.RAPID
    else:
        return TimeControl.CLASSICAL


# Example usage and testing
if __name__ == "__main__":
    import chess
    
    # Test 1: Rapid game (10 minutes)
    print("=== Test 1: Rapid Game (10 min) ===")
    tm = TimeManager(total_time=600, increment=5, time_control=TimeControl.RAPID)
    board = chess.Board()
    
    target, max_time = tm.get_time_for_move(board)
    print(f"Move 1 - Target: {tm.format_time(target)}, Max: {tm.format_time(max_time)}")
    print(f"Status: {tm.get_status()}\n")
    
    # Test 2: Blitz game (3+2)
    print("=== Test 2: Blitz Game (3+2) ===")
    tm2 = TimeManager(total_time=180, increment=2, time_control=TimeControl.BLITZ)
    target, max_time = tm2.get_time_for_move(board)
    print(f"Move 1 - Target: {tm2.format_time(target)}, Max: {tm2.format_time(max_time)}")
    print(f"Status: {tm2.get_status()}\n")
    
    # Test 3: Complex middlegame position
    print("=== Test 3: Complex Middlegame ===")
    tm3 = TimeManager(total_time=300, increment=3, time_control=TimeControl.RAPID)
    # Simulate move 20
    for _ in range(19):
        tm3.move_number += 1
    board.push(chess.Move.from_uci("e2e4"))
    board.push(chess.Move.from_uci("e7e5"))
    
    target, max_time = tm3.get_time_for_move(board)
    print(f"Move 20 - Target: {tm3.format_time(target)}, Max: {tm3.format_time(max_time)}")
    print(f"Status: {tm3.get_status()}\n")
    
    # Test 4: Emergency time
    print("=== Test 4: Emergency Time ===")
    tm4 = TimeManager(total_time=5, increment=2, time_control=TimeControl.BLITZ)
    target, max_time = tm4.get_time_for_move(board)
    print(f"Emergency mode - Target: {tm4.format_time(target)}, Max: {tm4.format_time(max_time)}")
    print(f"Status: {tm4.get_status()}\n")
