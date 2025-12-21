<div align="center">
    <img src="Images/Mergen.png" alt="Mergen" height=500 />
    (Mergen (right) and Timur (left) playing chess on the Central Asian steppes, image created by Gemini.)
</div>

# MERGEN: A Chess AI Inspired by the Spirit of Intelligence and Strategy
Mergen is not just a chess engine; it's an artificial intelligence project that bridges the wisdom of the past with the intellect of the future, inspired by the Turkish mythological deity of wisdom and precision.

# Inspiration: Who is Mergen?
In Turkish mythology, Mergen is known as the symbol of intelligence, wisdom, and insight. This celestial figure, who never misses a target with his bow, also represents keen intuition, deep understanding, and precise decision-making. In the myths, Mergen is not only a warrior but also a guide and philosopher.
Drawing inspiration from this legendary figure, we have developed a chess AI that bases its moves not only on power but on foresight, balance, and intuition.

# Features
- **UCI Protocol Support**: Compatible with any chess GUI (Arena, ChessBase, Cute Chess, lichess bots)
- **Deep Move Prediction**: Mergen evaluates dozens of possibilities with every move using iterative deepening
- **Intelligence and Intuition**: Adapts its playing style with advanced algorithms like quiescence search and alpha-beta pruning
- **Opening Book**: 108 positions with 186 moves covering major openings
- **Tactical Awareness**: Quiescence search prevents horizon effect and tactical blindness
- **Optimized Performance**: 8.6x search speedup with futility pruning and enhanced evaluation
- **Search Enhancements**: 
  - Iterative deepening with Principal Variation (PV) tracking
  - Aspiration windows for faster search
  - Null move pruning for deep searches
  - Late move reductions (LMR)
  - Countermove heuristic for better move ordering
- **Multi-Threading**: Lazy SMP parallel search (1-16 threads, 2-4x speedup)
- **Pawn Promotion Choice**: Select promotion piece (queen, rook, bishop, knight)
- **Smart Time Management**: Adaptive time allocation with support for bullet, blitz, rapid, and classical time controls
- **Game Persistence**: PGN save/load with full game history
- **Comprehensive Tests**: 62 unit tests covering all components
- **Testing Framework**: Engine vs Engine tournament system for objective strength measurement
- **Developer Utilities**: `parallel_benchmark.py` to spot single vs. multi-thread timing regressions at depth 3

## How to Run Mergen?

### 1. Prerequisites
Before running Mergen, ensure you have the following installed:

- **Python** `3.11.9` (or compatible 3.11.x version)
- **GCC Compiler** (for building the C engine)
  - **Windows:** [MinGW-w64](https://www.mingw-w64.org/) or similar
  - **Linux/macOS:** GCC is usually pre-installed. If not:
    ```bash
    sudo apt install build-essential   # Ubuntu/Debian
    sudo pacman -S base-devel          # Arch
    xcode-select --install             # macOS
    ```

---

### 2. Installation
1. **Clone the repository:**
    ```bash
    git clone https://github.com/haktanpolatt/Mergen.git
    cd Mergen
    ```
2. **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` includes:
    ```text
    chess
    rich
    ```

---

### 3. Running the Project

#### Step 1 — Build the Engine
Run `Interface.py` first to build and load the C engine:
```bash
python Interface.py
```

- On the first run, Interface.py will:
  - Detect your OS (Windows/Linux/macOS)
  - Automatically compile the C engine into .dll, .so, or .dylib
  - Load it into Python

#### Step 2 — Start the Game
After building the engine, you can run the main program:
```bash
python main.py
```

### 4. Manual Build (Optional)
If you prefer to compile the C engine yourself:

#### Windows (MinGW):
```bash
cd Source\C
gcc -O3 -shared -o Engine.dll Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c Zobrist.c TT.c Ordering.c KillerMoves.c -Wno-stringop-overflow
```

#### Linux:
```bash
cd Source/C
gcc -O3 -shared -fPIC -o Engine.so Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c Zobrist.c TT.c Ordering.c KillerMoves.c -Wno-stringop-overflow
```

#### macOS:
```bash
cd Source/C
gcc -O3 -shared -fPIC -o Engine.dylib Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c Zobrist.c TT.c Ordering.c KillerMoves.c -Wno-stringop-overflow
```

## Recent Updates (December 2025)

### Countermove Heuristic (December 21) **NEW!**
- **Better Move Ordering**: Tracks which moves work well as responses to opponent moves
- **Smarter Search**: Complements killer moves and history heuristic
- **Expected Gain**: 10-20 ELO improvement
- **Integration**: Fully integrated with existing search optimizations

### Engine vs Engine Testing Framework (December 21) **NEW!**
- **Tournament System**: Round-robin tournaments between engine versions
- **Objective Measurement**: ELO estimation and win rate tracking
- **Regression Testing**: Verify improvements don't break functionality
- **PGN Export**: Save all tournament games for analysis
- **Usage**: `python3 tournament.py --engines "python3 uci.py" "python3 uci.py" --depth 3 --games 4`
- See `Documents/Testing.md` for complete guide

### UCI Protocol Support (November 24)
- **Universal Chess Interface**: Compatible with any UCI chess GUI
- **GUI Support**: Arena, ChessBase, Cute Chess, and more
- **Online Play**: Can be used as lichess.org bot
- **Tournament Ready**: Standardized communication protocol
- **Easy Setup**: `python uci_launcher.py` or configure in GUI
- See `Documents/UCI.md` for full guide

### Performance Breakthrough (November 13)
- **8.6x Search Speedup**: Futility pruning + mobility evaluation (43s → 5s at depth 3!)
- **Enhanced Evaluation**: Pawn chains, king safety improvements, mobility bonuses
- **Expanded Opening Book**: 108 positions (from 84), +29% more coverage
- **PGN Support**: Save/load games, auto-save, game history
- **Comprehensive Test Suite**: 62 tests covering all components (100% passing)

### Pawn Promotion
- Players can now choose promotion piece (Q/R/B/N)
- Engine generates all promotion variations

### Engine Enhancements
- **Iterative Deepening**: Progressive depth search for better move ordering
- **Principal Variation Tracking**: Shows engine's intended continuation
- **Search Information Display**: Real-time depth, evaluation, and PV

### Time Management NEW!
- **Smart Time Allocation**: Adjusts based on position complexity and game phase
- **Multiple Time Controls**: Bullet, Blitz, Rapid, Classical, Infinite
- **Increment Support**: Handles Fischer increment (e.g., 3+2, 10+5)
- **Emergency Mode**: Special handling when time < 10 seconds
- **Adaptive Depth**: Searches as deep as possible within time limit
- See `Documents/TimeManagement.md` for details

### Documentation
- **Testing Framework Guide**: Engine vs Engine tournament system (`Documents/Testing.md`) **NEW!**
- **UCI Protocol Guide**: Complete UCI implementation guide (`Documents/UCI.md`)
- **Bibliography**: Academic references for all algorithms (`Documents/Bibliography.md`)
- **Time Management Guide**: Complete guide to time controls (`Documents/TimeManagement.md`)
- **Opening Book Guide**: Opening coverage and customization (`Documents/OpeningBook.md`)
- **Multi-Threading Guide**: Lazy SMP parallelization (`Documents/MultiThreading.md`)
- **Test Suite Guide**: Test coverage and usage (`Documents/TestSuite.md`)
- **Update Summary**: All improvements documented (`Documents/UpdateSummary.md`)
- Proper citations for minimax, alpha-beta, transposition tables, and moreg book, PGN, time management, parallel-search sanity
- **Test Runner**: `python3 run_tests.py` (with category support)
- **100% Passing**: All tests verified
- **CI/CD Ready**: Professional test infrastructure
- See `tests/README.md` for details

### Documentation
- **UCI Protocol Guide**: Complete UCI implementation guide (`Documents/UCI.md`)
- **Bibliography**: Academic references for all algorithms (`Documents/Bibliography.md`)
- **Time Management Guide**: Complete guide to time controls (`Documents/TimeManagement.md`)
- **Opening Book Guide**: Opening coverage and customization (`Documents/OpeningBook.md`)
- **Multi-Threading Guide**: Lazy SMP parallelization (`Documents/MultiThreading.md`)
- **Test Suite Guide**: Test coverage and usage (`Documents/TestSuite.md`)
- **Update Summary**: All improvements documented (`Documents/UpdateSummary.md`)
- Proper citations for minimax, alpha-beta, transposition tables, and more

# Why "Mergen"?
Just like the mythological Mergen's arrow, this AI makes every move on the chessboard with wisdom and precision. The name is more than just a reference, it symbolizes the very character of our AI.

# License
Mergen is open-source and released under the MIT license. We welcome your contributions and improvements.

# Contribute
Mergen is more than an artificial intelligence, it's a piece of software written with a mythological soul. Join the legend by contributing to the project.
