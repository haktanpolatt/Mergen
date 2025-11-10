# Time Management Guide

## Overview

Mergen now includes an intelligent time management system that allocates thinking time based on position complexity, game phase, and time control. This makes the engine play more like a human, spending more time on critical positions and less on routine moves.

## Features

### Smart Time Allocation
- **Position Complexity**: Analyzes mobility, material, and tactics
- **Game Phase Detection**: Opening, middlegame, endgame
- **Time Control Awareness**: Adjusts for bullet, blitz, rapid, classical
- **Emergency Mode**: Special handling when time < 10 seconds
- **Increment Support**: Properly handles Fischer increment

### Supported Time Controls

1. **Bullet** (< 3 minutes)
   - Fast play with reduced thinking time
   - Quick tactical decisions
   - Example: 1+0 (1 minute, no increment)

2. **Blitz** (3-10 minutes)
   - Quick decisions with moderate depth
   - Balanced speed and accuracy
   - Example: 3+2 (3 minutes + 2 second increment)

3. **Rapid** (10-60 minutes)
   - Thoughtful play with good search depth
   - Example: 10+5 (10 minutes + 5 second increment)

4. **Classical** (> 60 minutes)
   - Deep analysis and maximum depth
   - Example: 30+0 (30 minutes, no increment)

5. **Infinite**
   - No time limit, searches to fixed depth
   - For analysis and correspondence games

6. **Fixed Depth**
   - Always searches to specified depth
   - Ignores time (for testing/analysis)

## How It Works

### Time Allocation Algorithm

```
1. Estimate moves remaining in game
   - Opening: ~35-40 moves
   - Middlegame: ~20-30 moves
   - Endgame: ~10-20 moves

2. Calculate base time
   base_time = (remaining_time - buffer) / estimated_moves

3. Apply adjustments
   - Time control factor (bullet=0.7, classical=1.2)
   - Phase factor (opening=0.7, middlegame=1.2, endgame=1.0)
   - Complexity factor (0.8 to 1.2 based on position)

4. Set limits
   target_time = base_time × adjustments
   max_time = target_time × 2.5 (but not > 25% of remaining)
```

### Position Complexity

Complexity score (0.0 to 1.0) based on:

- **Mobility** (40% weight): Number of legal moves
  - More moves = more complex
  - Normalized: legal_moves / 50

- **Material** (30% weight): Pieces on board
  - More pieces = more complex
  - Normalized: piece_count / 32

- **Tactical** (30% weight): Checks and captures
  - In check: +0.3 complexity
  - Available captures: up to +0.2

**Example Complexity Scores:**
- Simple endgame (K+P vs K): ~0.2
- Quiet middlegame: ~0.5
- Sharp tactical position: ~0.8-1.0

### Game Phase Detection

**Opening** (moves 1-10):
- Most pieces on board
- Use opening book when possible
- Reduced thinking time (0.7x)

**Middlegame** (moves 11-35, many pieces):
- Most critical phase
- Complex tactics and strategy
- Increased thinking time (1.2x)

**Endgame** (< 10 pieces):
- Precision important
- Simpler positions
- Normal thinking time (1.0x)

### Emergency Mode

When time < 10 seconds:
- Use only 10-15% of remaining time per move
- Reduced maximum depth
- Still tries to maintain quality
- Prevents time forfeit

## Usage

### In main.py

When you run `python main.py`, you'll see:

```
Select time control:
1. Bullet (1 min)
2. Blitz (3 min + 2 sec)
3. Rapid (10 min + 5 sec)
4. Classical (30 min)
5. Infinite (no time limit)
6. Fixed depth (search to depth 5)

Enter choice (1-6, default=6):
```

### Example Sessions

#### Blitz Game (3+2)
```
Blitz mode: 3 minutes + 2 seconds
Mergen has 3m 0s remaining

Move 1:
Mergen is thinking... (target: 2.8s, max: 7.0s)
Depth: 6, Time: 2.9s
Mergen played: e2e4 (remaining: 3m 2s)

Move 15 (complex middlegame):
Mergen is thinking... (target: 4.5s, max: 11.2s)
Depth: 7, Time: 4.8s
Mergen played: Nf3 (remaining: 2m 45s)
```

#### Emergency Time
```
Move 40 (8 seconds left):
[EMERGENCY MODE]
Mergen is thinking... (target: 0.8s, max: 1.2s)
Depth: 4, Time: 0.9s
Mergen played: Rxd5 (remaining: 7s)
```

### Programmatic Usage

```python
from Source.TimeManagement import TimeManager, TimeControl

# Create time manager
tm = TimeManager(
    total_time=600,           # 10 minutes
    increment=5,              # 5 second increment
    time_control=TimeControl.RAPID
)

# Get time for move
target, max_time = tm.get_time_for_move(board)
print(f"Target: {tm.format_time(target)}")
print(f"Max: {tm.format_time(max_time)}")

# Use time-limited search
move_uci, depth, time_ms = find_best_move_timed_from_c(
    board.fen(), 
    max_time * 1000  # Convert to milliseconds
)

# Update time after move
tm.update_time(time_ms / 1000.0)
```

## Time Allocation Examples

### 10 Minute Rapid Game

| Move | Phase      | Complexity | Time    | Depth | Remaining |
|------|------------|------------|---------|-------|-----------|
| 1    | Opening    | Low (0.3)  | 1.5s    | 7     | 10:05     |
| 10   | Opening    | Medium(0.5)| 2.0s    | 7     | 9:50      |
| 20   | Middlegame | High (0.8) | 6.5s    | 8     | 8:45      |
| 30   | Middlegame | Medium(0.6)| 4.0s    | 7     | 7:20      |
| 40   | Endgame    | Low (0.3)  | 2.5s    | 8     | 6:10      |

### 3 Minute Blitz Game

| Move | Phase      | Complexity | Time    | Depth | Remaining |
|------|------------|------------|---------|-------|-----------|
| 1    | Opening    | Low (0.3)  | 0.8s    | 5     | 3:02      |
| 15   | Middlegame | High (0.9) | 3.2s    | 6     | 2:40      |
| 25   | Middlegame | Medium(0.6)| 2.0s    | 6     | 2:10      |
| 35   | Endgame    | Low (0.4)  | 1.2s    | 6     | 1:45      |
| 45   | Emergency  | Any        | 0.3s    | 4     | 0:08      |

## Configuration

### Adjusting Time Allocation

Edit `Source/TimeManagement.py`:

```python
class TimeManager:
    def __init__(self, ...):
        # Customize these factors
        self.base_time_factor = 0.04    # 4% per move (default)
        self.min_time_factor = 0.01     # Minimum 1%
        self.max_time_factor = 0.15     # Maximum 15%
        self.emergency_threshold = 10.0  # Emergency at 10s
```

### Phase Factors

```python
def _get_phase_factor(self, phase):
    factors = {
        GamePhase.OPENING: 0.7,      # 70% time (use book)
        GamePhase.MIDDLEGAME: 1.2,   # 120% time (critical)
        GamePhase.ENDGAME: 1.0       # 100% time (normal)
    }
```

### Time Control Factors

```python
def _get_time_control_factor(self):
    factors = {
        TimeControl.BULLET: 0.7,      # Play faster
        TimeControl.BLITZ: 0.9,       # Slightly faster
        TimeControl.RAPID: 1.0,       # Normal
        TimeControl.CLASSICAL: 1.2,   # Think deeper
    }
```

## Performance Impact

### Depth Achieved by Time Control

**Bullet (1 min, ~1s per move):**
- Opening: Depth 5-6
- Middlegame: Depth 5-7
- Endgame: Depth 6-8

**Blitz (3+2, ~3s per move):**
- Opening: Depth 6-7
- Middlegame: Depth 6-8
- Endgame: Depth 7-9

**Rapid (10+5, ~10s per move):**
- Opening: Depth 7-8
- Middlegame: Depth 7-9
- Endgame: Depth 8-10

**Classical (30 min, ~30s per move):**
- Opening: Depth 8-9
- Middlegame: Depth 8-11
- Endgame: Depth 10-12

### Time Savings

- **Opening book**: Saves 1-3 seconds per move (moves 1-8)
- **Iterative deepening**: ~10-30% faster than fixed depth
- **Smart allocation**: Avoids wasting time on simple positions

## Best Practices

1. **Match Time Control**: Use appropriate TC for game situation
2. **Trust the System**: Don't manually override unless necessary
3. **Monitor Remaining Time**: Watch for emergency mode
4. **Opening Book**: Always use book to save time
5. **Increment Usage**: In increment games, engine includes increment in calculations

## Troubleshooting

### Engine Using Too Much Time

**Symptoms:** Frequently entering emergency mode

**Solutions:**
- Reduce `base_time_factor` (e.g., 0.03 instead of 0.04)
- Increase `emergency_threshold` (e.g., 15s instead of 10s)
- Use faster time control category

### Engine Playing Too Fast

**Symptoms:** Always finishing with lots of time left

**Solutions:**
- Increase `base_time_factor` (e.g., 0.05 instead of 0.04)
- Increase `max_time_factor` (e.g., 0.20 instead of 0.15)
- Use slower time control category

### Inconsistent Time Usage

**Symptoms:** Some moves very fast, others very slow

**Expected Behavior:** This is intentional!
- Simple positions should be fast
- Complex/tactical positions should be slower
- This is a feature, not a bug

## Future Enhancements

Potential improvements:

1. **Pondering**: Think during opponent's time
2. **Time Pressure Detection**: Better handling of low time
3. **Move Instability**: Give more time when evaluation fluctuates
4. **Learning**: Adjust based on past games
5. **UCI Time Commands**: Support standard UCI time protocols
6. **Multi-PV Time**: Allocate time for analyzing multiple variations

## References

- Hyatt, R. M. (1997). "The Chess Program Crafty"
- Hsu, F. (2002). "Behind Deep Blue" - Chapter on time management
- Heinz, E. A. (1999). "Adaptive Null-Move Pruning"
- Chess Programming Wiki: Time Management
  https://www.chessprogramming.org/Time_Management

---

*"In chess, as in life, time is the ultimate resource."*
