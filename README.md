<div align="center">
    <img src="Images/Mergen.png" alt="Mergen" height=500 />
</div>

# ♟ MERGEN: A Chess AI Inspired by the Spirit of Intelligence and Strategy
Mergen is not just a chess engine; it's an artificial intelligence project that bridges the wisdom of the past with the intellect of the future, inspired by the Turkish mythological deity of wisdom and precision.

# 🧠 Inspiration: Who is Mergen?
In Turkish mythology, Mergen is known as the symbol of intelligence, wisdom, and insight. This celestial figure, who never misses a target with his bow, also represents keen intuition, deep understanding, and precise decision-making. In the myths, Mergen is not only a warrior but also a guide and philosopher.
Drawing inspiration from this legendary figure, we have developed a chess AI that bases its moves not only on power but on foresight, balance, and intuition.

# 🔧 Features
- ♟ **Deep Move Prediction**: Mergen evaluates dozens of possibilities with every move using iterative deepening
- 🌀 **Intelligence and Intuition**: Adapts its playing style with advanced algorithms like quiescence search and alpha-beta pruning
- 📚 **Opening Book**: Plays 25+ established opening systems including Ruy Lopez, Sicilian Defense, and Queen's Gambit
- 🎯 **Tactical Awareness**: Quiescence search prevents horizon effect and tactical blindness
- ⚡ **Optimized Performance**: Transposition tables with Zobrist hashing, killer move heuristic, and move ordering
- 🔍 **Search Enhancements**: Iterative deepening with Principal Variation (PV) tracking
- 📖 **Pawn Promotion Choice**: Select promotion piece (queen, rook, bishop, knight)
- ⏱️ **Smart Time Management**: Adaptive time allocation with support for bullet, blitz, rapid, and classical time controls
- 🕰️ **Time-Aware**: Tracks thinking time and provides search statistics

## 💻 How to Run Mergen?

### 1️⃣ Prerequisites
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

### 2️⃣ Installation
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

### 3️⃣ Running the Project

#### 🔹 Step 1 — Build the Engine
Run `Interface.py` first to build and load the C engine:
```bash
python Interface.py
```

- On the first run, Interface.py will:
  - Detect your OS (Windows/Linux/macOS)
  - Automatically compile the C engine into .dll, .so, or .dylib
  - Load it into Python

#### 🔹 Step 2 — Start the Game
After building the engine, you can run the main program:
```bash
python main.py
```

### 4️⃣ Manual Build (Optional)
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

## 🆕 Recent Updates (November 2025)

### Pawn Promotion
- Players can now choose promotion piece (Q/R/B/N)
- Engine generates all promotion variations

### Engine Enhancements
- **Iterative Deepening**: Progressive depth search for better move ordering
- **Principal Variation Tracking**: Shows engine's intended continuation
- **Search Information Display**: Real-time depth, evaluation, and PV

### Time Management ⏱️ NEW!
- **Smart Time Allocation**: Adjusts based on position complexity and game phase
- **Multiple Time Controls**: Bullet, Blitz, Rapid, Classical, Infinite
- **Increment Support**: Handles Fischer increment (e.g., 3+2, 10+5)
- **Emergency Mode**: Special handling when time < 10 seconds
- **Adaptive Depth**: Searches as deep as possible within time limit
- See `Documents/TimeManagement.md` for details

### Opening Book
- 25+ major opening systems
- Instant book moves (no calculation needed)
- Weighted move selection for variety
- See `Documents/OpeningBook.md` for details

### Documentation
- **Bibliography**: Academic references for all algorithms (`Documents/Bibliography.md`)
- **Time Management Guide**: Complete guide to time controls (`Documents/TimeManagement.md`)
- Proper citations for minimax, alpha-beta, transposition tables, and more

# 🎯 Why "Mergen"?
Just like the mythological Mergen's arrow, this AI makes every move on the chessboard with wisdom and precision. The name is more than just a reference—it symbolizes the very character of our AI.

# 📜 License
Mergen is open-source and released under the MIT license. We welcome your contributions and improvements.

# ✨ Contribute
Mergen is more than an artificial intelligence—it's a piece of software written with a mythological soul. Join the legend by contributing to the project.
