# Countermove Heuristic

## Overview

The countermove heuristic is a move ordering optimization that tracks which moves work well as responses to specific opponent moves. This complements the killer move heuristic by providing context-specific move ordering.

## Implementation Date
**December 21, 2025**

## How It Works

### Basic Concept
When a quiet move causes a beta cutoff (refutation), we record it as the "countermove" to the opponent's previous move. When we encounter that opponent move again in future searches, we try its countermove early in the move ordering.

### Data Structure
```c
// Countermove table: [from_square][to_square] -> response_move
char countermove_table[64][64][6];
```

For each possible move (represented by from_square and to_square), we store the best known response.

### Update Logic
When a quiet move causes a beta cutoff:
```c
if (beta_cutoff && !is_capture) {
    update_countermove(opponent_previous_move, this_move);
}
```

### Move Ordering Integration
The countermove bonus is applied during move ordering, positioned between:
1. **Hash/TT move** (highest priority)
2. **Countermove** (new - second priority)
3. **Captures** (MVV-LVA ordering)
4. **Killer moves**
5. **History heuristic**
6. **Quiet moves**

## Expected Performance Gain
- **ELO Improvement**: 10-20 ELO
- **Cutoff Efficiency**: Reduces nodes searched by finding refutations earlier
- **Search Speed**: Faster beta cutoffs lead to more pruning

## Integration with Existing Features

### Works With
- **Killer Moves**: Countermoves provide context-specific ordering, killers provide depth-specific ordering
- **History Heuristic**: Both track successful moves, but countermoves are context-aware
- **Transposition Table**: Countermoves help when TT has no entry
- **LMR**: Better move ordering means fewer LMR re-searches
- **Alpha-Beta Pruning**: Earlier cutoffs improve pruning efficiency

### Key Files Modified
- `Source/C/Ordering.h` - Added countermove function declarations
- `Source/C/Ordering.c` - Implemented countermove table and update logic
- `Source/C/Minimax.h` - Added `minimax_with_last_move` function
- `Source/C/Minimax.c` - Integrated countermove updates on beta cutoffs

## Usage Example

```c
// In search, when beta cutoff occurs:
if (beta <= alpha) {
    if (!is_capture) {
        update_history(moves[i], depth);      // History heuristic
        add_killer_move(depth, moves[i]);     // Killer move
        if (last_move) {
            update_countermove(last_move, moves[i]);  // Countermove NEW!
        }
    }
    break;
}
```

## Testing

### Functional Test
```bash
python3 -c "
import subprocess, time
p = subprocess.Popen(['python3', 'uci.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
p.stdin.write('uci\n'); p.stdin.flush()
# ... (initialize engine)
p.stdin.write('go depth 4\n'); p.stdin.flush()
# Should complete without errors
"
```

### Strength Test
Use the tournament framework to measure ELO change:
```bash
# Test old version vs new version
python3 tournament.py --engines "old_version/uci.py" "python3 uci.py" \
    --names "Before" "After" --depth 4 --games 100
```

## References
- **Countermove Heuristic**: Common in modern chess engines (Stockfish, etc.)
- Related to **Continuation History**: More advanced version tracking move sequences
- Part of broader **History-Based Move Ordering** techniques

## Future Enhancements
- **Continuation History**: Track 2-move sequences (grandparent move → parent move → response)
- **Follow-up Moves**: Track which moves work well after our own moves
- **Piece-To History**: Track history per piece type moving to specific squares

## Performance Notes
- **Memory Usage**: 64 × 64 × 6 bytes = ~24 KB (negligible)
- **Update Cost**: O(1) per beta cutoff
- **Lookup Cost**: O(1) during move ordering
- **Overall Impact**: Minimal overhead, measurable speedup
