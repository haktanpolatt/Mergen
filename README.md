<div align="center">
    <img src="Images/Mergen.png" alt="Mergen" height=500 />
</div>

# ♟ MERGEN: A Chess AI Inspired by the Spirit of Intelligence and Strategy
Mergen is not just a chess engine; it's an artificial intelligence project that bridges the wisdom of the past with the intellect of the future, inspired by the Turkish mythological deity of wisdom and precision.

# 🧠 Inspiration: Who is Mergen?
In Turkish mythology, Mergen is known as the symbol of intelligence, wisdom, and insight. This celestial figure, who never misses a target with his bow, also represents keen intuition, deep understanding, and precise decision-making. In the myths, Mergen is not only a warrior but also a guide and philosopher.
Drawing inspiration from this legendary figure, we have developed a chess AI that bases its moves not only on power but on foresight, balance, and intuition.

# 🔧 Features
- ♟ Deep Move Prediction: Mergen evaluates dozens of possibilities with every move; it plays not just powerfully but strategically.
- 🌀 Intelligence and Intuition: Unlike traditional engines, Mergen adapts its playing style, showing aggressive or defensive behavior depending on the situation.
- 📚 Mythological Spirit, Modern Engineering: Named after the wise archer of the past, Mergen is built in Python with modern algorithms.
- 🕰️ Evolving Intelligence: Learns from training data, recognizes openings, and remembers opponent strategies.

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

# 🎯 Why “Mergen”?
Just like the mythological Mergen’s arrow, this AI makes every move on the chessboard with wisdom and precision. The name is more than just a reference—it symbolizes the very character of our AI.

# 📜 License
Mergen is open-source and released under the MIT license. We welcome your contributions and improvements.

# ✨ Contribute
Mergen is more than an artificial intelligence—it's a piece of software written with a mythological soul. Join the legend by contributing to the project.
