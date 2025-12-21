# Mergen UCI Protocol Implementation

## Overview

Mergen now supports the **Universal Chess Interface (UCI) protocol**, making it compatible with virtually any modern chess GUI and enabling online play, tournaments, and engine analysis.

## What is UCI?

UCI is a standardized protocol for chess engines to communicate with graphical user interfaces (GUIs). It was developed by Rudolf Huber and Stefan Meyer-Kahlen and is now the de facto standard for chess engines worldwide.

**Key Benefits:**
- Works with any UCI-compatible chess GUI
- Enables online play (lichess.org bots)
- Tournament ready
- Standardized communication protocol
- No GUI coding required

## Features

### Implemented Commands

1. **`uci`** - Engine identification
   - Returns engine name, author, and version
   - Lists available options

2. **`isready`** - Synchronization check
   - Responds with `readyok`

3. **`setoption`** - Configure engine
   - `Threads` (1-16): Number of search threads
   - `Hash` (1-1024 MB): Hash table size (resizes C transposition table)
   - `OwnBook` (true/false): Use opening book
   - `Debug` (true/false): Enable debug logging

4. **`ucinewgame`** - Start new game
   - Resets board position

5. **`position`** - Set board position
   - `position startpos` - Standard starting position
   - `position startpos moves e2e4 e7e5` - Starting position with moves
   - `position fen <fen_string>` - Set position from FEN

6. **`go`** - Start searching
   - `go depth 10` - Search to fixed depth
   - `go movetime 5000` - Search for fixed time (milliseconds)
   - `go wtime 60000 btime 60000` - Time control
   - `go wtime 60000 btime 60000 winc 1000 binc 1000` - With increment
   - `go infinite` - Infinite analysis mode

7. **`stop`** - Stop searching (placeholder)

8. **`quit`** - Exit engine

### Engine Options

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| Threads | spin | 1 | 1-16 | Number of search threads |
| Hash | spin | 64 | 1-1024 | Hash table size in MB (resizes TT) |
| OwnBook | check | true | - | Use internal opening book |
| Debug | check | false | - | Enable debug logging |

## Usage

### Command Line

Launch Mergen in UCI mode:

```bash
python uci_launcher.py
```

Or directly:

```bash
python uci.py
```

### Manual UCI Testing

You can test UCI commands manually:

```bash
$ python uci.py
uci
id name Mergen 2.0
id author Haktan Polat
option name Threads type spin default 1 min 1 max 16
option name Hash type spin default 64 min 1 max 1024
option name OwnBook type check default true
option name Debug type check default false
uciok

isready
readyok

position startpos moves e2e4
go depth 5
bestmove e7e5

quit
```

## GUI Setup Instructions

### Arena Chess GUI

1. Download Arena from http://www.playwitharena.de/
2. Launch Arena
3. Go to **Engines → Install New Engine**
4. Browse to `uci_launcher.py` (or `uci.py`)
5. Select **UCI** protocol
6. Click OK

**Engine Settings:**
- Engines → Manage → Select Mergen → Details
- Set threads, hash size, etc.

### Cute Chess

1. Download Cute Chess from https://cutechess.com/
2. Launch Cute Chess
3. Go to **Tools → Settings → Engines**
4. Click **Add**
5. **Name:** Mergen
6. **Command:** `python` (or `python3`)
7. **Working Directory:** Path to Mergen folder
8. **Arguments:** `uci_launcher.py`
9. **Protocol:** UCI
10. Click OK

### ChessBase

1. Launch ChessBase
2. Go to **Home → Add engine**
3. Select **UCI Engine**
4. Browse to `uci_launcher.py`
5. Click Open
6. Configure engine parameters

### Lichess Bot

Mergen can be used as a lichess.org bot with the `lichess-bot` framework:

1. Install lichess-bot: https://github.com/lichess-bot-devs/lichess-bot
2. Create bot account on lichess.org
3. Configure `config.yml`:
   ```yaml
   engine:
     dir: "./engines/mergen"
     name: "uci_launcher.py"
     protocol: "uci"
     uci_options:
       Threads: 4
       OwnBook: true
   ```
4. Run: `python lichess-bot.py`

## Time Management

Mergen uses intelligent time management:

### Fixed Time
```
go movetime 5000  # Search for 5 seconds
```

### Time Control
```
go wtime 300000 btime 300000 winc 5000 binc 5000
```
- Calculates optimal time per move
- Considers remaining time and increment
- Uses approximately 1/30 of remaining time + increment
- Safety limits prevent timeouts

### Fixed Depth
```
go depth 8  # Search to depth 8
```

### Infinite Analysis
```
go infinite  # Analyze until 'stop' command
```

## Opening Book Integration

Mergen automatically uses its opening book in UCI mode:
- 108 positions covering major openings
- Weighted random selection for variety
- Instant book moves (no search required)
- Seamless fallback to search when out of book

Disable with: `setoption name OwnBook value false`

## Multi-Threading Support

Mergen supports parallel search with Lazy SMP:

```
setoption name Threads value 4
```

**Recommended Thread Counts:**
- **1 thread:** ~1000 nodes/sec baseline
- **2 threads:** ~1.8x speedup
- **4 threads:** ~3x speedup
- **8 threads:** ~4.5x speedup

## Debug Mode

Enable debug logging to stderr:

```
setoption name Debug value true
```

Debug messages include:
- Commands received
- Engine responses
- Search parameters
- Time management decisions
- Errors and warnings

## Example UCI Session

```
# Engine startup
uci
id name Mergen 2.0
id author Haktan Polat
option name Threads type spin default 1 min 1 max 16
uciok

# Configure engine
setoption name Threads value 4
setoption name Debug value true
isready
readyok

# New game
ucinewgame

# Play e4
position startpos moves e2e4
go wtime 300000 btime 300000 winc 5000 binc 5000
info string Book move
bestmove c7c5

# Continue game
position startpos moves e2e4 c7c5 g1f3
go depth 6
bestmove d7d6

# Quit
quit
```

## Performance

### Search Speed (Single Thread)
- **Depth 3:** ~5 seconds
- **Depth 4:** ~35 seconds
- **Depth 5:** ~3-5 minutes

### With 4 Threads
- **Depth 3:** ~2 seconds (2.5x faster)
- **Depth 4:** ~12 seconds (3x faster)
- **Depth 5:** ~1-2 minutes (3x faster)

### Opening Book
- **Lookup time:** < 1ms (instant)
- **Coverage:** 108 positions, 186 moves
- **Hit rate:** ~80% in first 10 moves

## Troubleshooting

### Engine doesn't respond
- Check that `Interface.py` successfully built the C engine
- Verify `Data/opening_book.json` exists
- Enable debug mode to see error messages

### Illegal moves
- Engine validates moves before making them
- Falls back to legal move if search fails
- Check GUI is sending valid UCI commands

### Time management issues
- Mergen uses conservative time allocation
- Uses monotonic timers with in-search checks to avoid exceeding movetime
- Minimum 100ms per move

### Multi-threading not working
- Check available CPU cores: `from Interface import get_cpu_cores`
- Thread count capped at 16
- Single-threaded fallback for very fast searches

## Protocol Limitations

### Not Implemented (Yet)
1. **`stop` command** - Search interruption
   - Currently searches complete
   - Would require thread-safe interruption

2. **`ponderhit` / `ponder`** - Thinking on opponent's time
   - Planned for future release

3. **Info strings during search**
   - No real-time depth/eval updates
   - Only final bestmove sent

### Workarounds
- Use fixed depth or movetime for predictable search times
- Monitor via debug mode for development
- Trust Mergen's time management for tournaments

## Technical Details

### Architecture
- **uci.py:** UCI protocol handler (Python)
- **Interface.py:** C engine wrapper (ctypes)
- **Source/C/Engine.c:** Core search engine (C)
- **Source/OpeningBook.py:** Opening book handler

### Communication Flow
```
GUI → UCI Command → uci.py → Interface.py → Engine.c → Search
                                                  ↓
GUI ← Best Move ← uci.py ← Interface.py ← Search Result
```

### Thread Safety
- Each UCI command processed sequentially
- Parallel search threads managed by C engine
- No concurrent command processing

## Testing

### Unit Tests
Mergen includes UCI-compatible tests in `tests/` directory:

```bash
python3 run_tests.py
```

### Manual Testing
Test UCI compliance with `uci-tester` or similar tools:

```bash
# Install uci-tester
pip install python-chess

# Test basic commands
python uci_tester.py uci_launcher.py
```

### Engine vs Engine
Test against other engines:

```bash
cutechess-cli -engine cmd=python args=uci_launcher.py \
              -engine cmd=stockfish \
              -each tc=40/60 -rounds 10
```

## Future Enhancements

Planned UCI improvements:

1. **Real-time search info**
   - Depth, nodes, eval updates
   - Principal variation (PV)
   - Selective depth

2. **Search interruption**
   - Implement `stop` command
   - Thread-safe search cancellation

3. **Advanced options**
   - Null move pruning toggle
   - Futility pruning margins
   - Opening book path

4. **Performance improvements**
   - Hash table management
   - Pondering (background search)
   - Syzygy tablebase support

## References

- UCI Protocol Specification: http://wbec-ridderkerk.nl/html/UCIProtocol.html
- Chess Programming Wiki: https://www.chessprogramming.org/UCI
- Python-chess Documentation: https://python-chess.readthedocs.io/

## License

UCI implementation is part of Mergen and released under the MIT License.

---

**Mergen UCI Implementation**  
*Making chess engines accessible to everyone*

Version: 2.0  
Date: November 24, 2025  
Author: Haktan Polat
