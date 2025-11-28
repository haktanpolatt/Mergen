# Engine vs Engine Testing Framework

## Overview

The testing framework allows you to:
- Play chess engines against each other
- Run automated tournaments
- Measure engine strength objectively
- Test improvements and optimizations
- Generate PGN files of games
- Calculate statistics and win rates

## Files

- **tournament.py** - Main tournament framework
- **test_selfplay.py** - Quick self-play test script

## Quick Start

### 1. Test Mergen Against Itself

```bash
python3 test_selfplay.py
```

This will play Mergen against itself at different depths to verify everything works.

### 2. Run a Custom Tournament

```bash
# Play Mergen at depth 4 vs depth 3 (10 games each pairing)
python3 tournament.py --depth 4 --games 10 --names "Mergen D4" "Mergen D3"

# Use time control instead of depth
python3 tournament.py --movetime 2000 --games 4 --names "Mergen 2s" "Mergen 1s"
```

### 3. Test Against External Engines

```bash
# Test Mergen vs Stockfish (if you have stockfish installed)
python3 tournament.py \
    --engines "python3 uci.py" "stockfish" \
    --names "Mergen" "Stockfish-Weak" \
    --depth 4 \
    --games 10
```

## Usage Examples

### Basic Self-Play Tournament

```python
from tournament import Tournament

engines = [
    {
        "command": "python3 uci.py",
        "name": "Mergen v1",
        "options": {"Threads": "1"}
    },
    {
        "command": "python3 uci.py",
        "name": "Mergen v2",
        "options": {"Threads": "1"}
    }
]

# Run tournament at depth 5, 4 games per pairing
tournament = Tournament(engines, {"depth": 5}, games_per_pair=4)
tournament.run()
tournament.save_results("my_tournament.json")
```

### Testing Engine Improvements

When you make changes to the engine:

```bash
# Save current version
cp Engine.so Engine_old.so

# Make your changes and recompile
# (edit Source/C/*.c files)
gcc -shared -fPIC -O3 -march=native -o Engine.so Source/C/*.c -lm -lpthread

# Test old vs new
python3 tournament.py \
    --engines "python3 uci.py" "python3 uci.py" \
    --names "New Version" "Old Version (baseline)" \
    --depth 4 \
    --games 20 \
    --output improvement_test.json

# Restore if needed
# mv Engine_old.so Engine.so
```

### Different Time Controls

```bash
# Fixed depth
python3 tournament.py --depth 5 --games 10

# Fixed time per move  
python3 tournament.py --movetime 3000 --games 10  # 3 seconds per move

# Multiple engines at different settings
python3 tournament.py \
    --engines "python3 uci.py" "python3 uci.py" "python3 uci.py" \
    --names "Mergen-Fast" "Mergen-Medium" "Mergen-Strong" \
    --depth 3 --games 6
```

## Tournament Output

The tournament will print:

```
======================================================================
TOURNAMENT RESULTS
======================================================================

Rank   Engine                    Score    W-D-L        Games   Win%   
----------------------------------------------------------------------
1      Mergen Depth 5            7.5      6-3-1        10      60.0
2      Mergen Depth 4            5.0      3-4-3        10      30.0
3      Mergen Depth 3            2.5      1-3-6        10      10.0

======================================================================
```

Results are also saved to JSON with detailed game information including PGN.

## Command Line Options

```
--engines CMD [CMD ...]       Engine commands (default: python3 uci.py)
--names NAME [NAME ...]       Engine names
--depth N                     Search depth
--movetime MS                 Milliseconds per move
--games N                     Games per pairing (default: 2)
--threads N                   Threads per engine (default: 1)
--output FILE                 Output JSON file (default: tournament_results.json)
```

## Use Cases

### 1. Regression Testing

Before committing changes, verify you haven't broken anything:

```bash
python3 test_selfplay.py
```

If games complete normally, basic functionality is intact.

### 2. Performance Testing

Measure the impact of optimizations:

```bash
# Test with/without opening book
python3 tournament.py --depth 4 --games 20 --output book_test.json
```

Compare results before and after changes.

### 3. Strength Progression

Track engine strength over time:

```bash
# Save each version
cp Engine.so versions/Engine_v1.0.so
cp Engine.so versions/Engine_v1.1.so

# Compare versions
python3 tournament.py \
    --engines "python3 uci.py" "python3 uci.py" \
    --names "v1.1" "v1.0" \
    --depth 4 \
    --games 50 \
    --output version_comparison.json
```

### 4. Parameter Tuning

Test different engine parameters:

```bash
# Create multiple uci_launcher scripts with different settings
# Then compare them in a tournament
```

## ELO Estimation

With sufficient games (50+), you can estimate ELO differences:

- **+1.0 score (~70% win rate)** ≈ +200 ELO
- **+0.5 score (~60% win rate)** ≈ +70 ELO
- **+0.25 score (~55% win rate)** ≈ +35 ELO

Use online ELO calculators for more precise estimates.

## Tips

1. **Use consistent time controls** - Compare apples to apples
2. **Run enough games** - At least 20 games for meaningful results
3. **Disable opening books** - For fair testing (unless testing book specifically)
4. **Test incrementally** - One change at a time
5. **Save baselines** - Keep old Engine.so versions for comparison
6. **Watch for bugs** - Crashes or illegal moves indicate problems

## Troubleshooting

### "Engine failed to return move"
- Check that uci.py works: `echo -e "uci\nquit" | python3 uci.py`
- Verify Engine.so is compiled: `ls -lh Engine.so`
- Check for crashes: Look at stderr output

### "Illegal move returned"
- Bug in move generation or position handling
- Run engine manually to reproduce

### Games taking too long
- Reduce depth or movetime
- Use --games 2 for quick tests

### Import errors
- Install chess library: `pip install chess`

## Future Enhancements

Potential additions to the framework:
- [ ] Parallel game execution
- [ ] Web interface for viewing results
- [ ] Automatic ELO calculation
- [ ] Swiss-system tournaments
- [ ] Time control with increment
- [ ] Adjudication (stop clearly won/lost games)
- [ ] Integration with external tournament managers
