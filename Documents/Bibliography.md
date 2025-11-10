# Bibliography: Chess Engine Algorithms and Techniques

This document provides academic references and citations for the algorithms and techniques implemented in the Mergen chess engine.

---

## Core Search Algorithms

### 1. Minimax Algorithm

**Paper:**
- Shannon, C. E. (1950). "Programming a Computer for Playing Chess." *Philosophical Magazine*, Series 7, Vol. 41, No. 314, pp. 256-275.

**Description:**
The minimax algorithm is a decision-making algorithm used in two-player games. It assumes that both players play optimally, with the maximizing player trying to maximize the score and the minimizing player trying to minimize it. The algorithm recursively explores the game tree to find the best move.

**Implementation in Mergen:**
- Located in `Source/C/Minimax.c`
- Used as the core search function for finding the best move
- Recursively evaluates positions up to a specified depth

---

### 2. Alpha-Beta Pruning

**Papers:**
- Knuth, D. E., & Moore, R. W. (1975). "An Analysis of Alpha-Beta Pruning." *Artificial Intelligence*, 6(4), pp. 293-326.
- McCarthy, J. (1956). "The Inversion of Functions Defined by Turing Machines." *Automata Studies*, Princeton University Press, pp. 177-181.

**Description:**
Alpha-beta pruning is an optimization technique for the minimax algorithm that eliminates branches that cannot possibly affect the final decision. It maintains two values (alpha and beta) representing the best guaranteed scores for the maximizing and minimizing players, respectively. When a branch is found that cannot improve these values, it is pruned from the search tree.

**Implementation in Mergen:**
- Integrated into the minimax function in `Source/C/Minimax.c`
- Significantly reduces the number of nodes evaluated
- Enables deeper search within the same time constraint
- Beta cutoffs store killer moves for improved move ordering

---

### 3. Iterative Deepening

**Papers:**
- Slate, D. J., & Atkin, L. R. (1977). "CHESS 4.5 - The Northwestern University Chess Program." *Chess Skill in Man and Machine*, Springer-Verlag, pp. 82-118.
- Korf, R. E. (1985). "Depth-First Iterative-Deepening: An Optimal Admissible Tree Search." *Artificial Intelligence*, 27(1), pp. 97-109.

**Description:**
Iterative deepening performs a series of depth-limited searches with increasing depth limits. While this appears wasteful (re-searching shallower depths), it provides several benefits:
1. Better move ordering from previous iterations improves alpha-beta efficiency
2. Enables time management (can stop at any completed iteration)
3. The overhead is minimal due to exponential growth of nodes with depth
4. Always has a best move available even if search is interrupted

**Implementation in Mergen:**
- Implemented in `Source/C/Engine.c` in the `find_best_move_from_fen()` function
- Searches from depth 1 up to the target depth
- Principal Variation (PV) from previous iteration is tried first
- Provides progressive refinement of the best move

---

### 4. Quiescence Search

**Papers:**
- Slate, D. J., & Atkin, L. R. (1977). "CHESS 4.5 - The Northwestern University Chess Program." *Chess Skill in Man and Machine*, Springer-Verlag, pp. 82-118.
- Marsland, T. A. (1986). "A Review of Game-Tree Pruning." *ICCA Journal*, 9(1), pp. 3-19.

**Description:**
Quiescence search addresses the "horizon effect" where the search stops at a position that appears quiet but is actually in the middle of a tactical sequence. Instead of evaluating at a fixed depth, quiescence search continues searching until reaching a "quiet" position (no captures available). This prevents the engine from missing tactics that occur just beyond the search horizon.

**Implementation in Mergen:**
- Implemented in `Source/C/Minimax.c` as the `quiescence()` function
- Called when depth reaches 0 instead of immediate evaluation
- Only considers capture moves to limit explosion of nodes
- Uses stand-pat evaluation (current position score) as a baseline
- Continues until no more captures are available

---

## Position Evaluation

### 5. Piece-Square Tables (PST)

**Papers:**
- Levy, D. N. L., & Newborn, M. (1991). "How Computers Play Chess." *Computer Science Press*, ISBN 0-7167-8121-2.
- Shannon, C. E. (1950). "Programming a Computer for Playing Chess." *Philosophical Magazine*, Series 7, Vol. 41, No. 314.

**Description:**
Piece-Square Tables assign bonuses or penalties to pieces based on their location on the board. Different piece types have different ideal squares (e.g., knights are stronger in the center, rooks on open files, kings safe in the corner during opening).

**Implementation in Mergen:**
- Defined in `Source/PST.py` and used in `Source/Evaluation.py` and `Source/C/Evaluate.c`
- Separate tables for each piece type (pawn, knight, bishop, rook, queen, king)
- King has different tables for opening/middlegame vs. endgame
- Tables are mirrored for black pieces

---

### 6. Pawn Structure Evaluation

**Papers:**
- Berliner, H. J. (1974). "Chess as Problem Solving: The Development of a Tactics Analyzer." *PhD Thesis, Carnegie Mellon University*.
- Euwe, M., & Kramer, H. (1964). "The Middle Game in Chess." *Dover Publications*.

**Description:**
Pawn structure evaluation considers strategic pawn formations:
- **Passed Pawns**: Pawns with no opposing pawns blocking their path to promotion (valuable)
- **Isolated Pawns**: Pawns with no friendly pawns on adjacent files (weakness)
- **Doubled Pawns**: Multiple pawns of the same color on the same file (weakness)

**Implementation in Mergen:**
- Implemented in `Source/Evaluation.py` in the `evaluate_pawn_structure()` function
- Also in `Source/C/Evaluate.c` for the C engine
- Awards bonuses for passed pawns (+0.3)
- Penalizes isolated pawns (-0.2)
- Penalizes doubled pawns (-0.1 per extra pawn)

---

## Optimization Techniques

### 7. Transposition Tables

**Papers:**
- Greenblatt, R. D., Eastlake, D. E., & Crocker, S. D. (1967). "The Greenblatt Chess Program." *Proceedings of the AFIPS Fall Joint Computer Conference*, 31, pp. 801-810.
- Breuker, D. M., Uiterwijk, J. W. H. M., & van den Herik, H. J. (1994). "Replacement Schemes for Transposition Tables." *ICCA Journal*, 17(4), pp. 183-193.

**Description:**
Transposition tables cache previously evaluated positions to avoid redundant computation. In chess, the same position can be reached through different move orders (transpositions). By storing the position's hash, evaluation, and depth, the engine can reuse previous work.

**Implementation in Mergen:**
- Implemented in `Source/C/TT.c` (Transposition Table)
- Uses Zobrist hashing for position identification
- Stores evaluation and depth for each position
- Lookup before search; store after evaluation

---

### 8. Zobrist Hashing

**Paper:**
- Zobrist, A. L. (1970). "A New Hashing Method with Application for Game Playing." *Technical Report #88, Computer Sciences Department, University of Wisconsin, Madison, Wisconsin*.

**Description:**
Zobrist hashing is an efficient method for hashing chess positions. Each piece on each square is assigned a random 64-bit number. The hash of a position is computed by XORing the numbers for all pieces present. Moving a piece updates the hash incrementally by XORing out the old square and XORing in the new square.

**Implementation in Mergen:**
- Implemented in `Source/C/Zobrist.c`
- Initialized with random 64-bit numbers for each piece-square combination
- Computed in `compute_zobrist_hash()` function
- Used as keys for the transposition table

---

### 9. Move Ordering and Killer Moves

**Papers:**
- Akl, S. G., & Newborn, M. M. (1977). "The Principal Continuation and the Killer Heuristic." *Proceedings of the 1977 Annual Conference, ACM*, pp. 466-473.
- Slate, D. J., & Atkin, L. R. (1977). "CHESS 4.5 - The Northwestern University Chess Program." *Chess Skill in Man and Machine*, Springer-Verlag.

**Description:**
Move ordering is critical for alpha-beta pruning efficiency. Better moves should be searched first to cause more cutoffs. Techniques include:
- **PV (Principal Variation)**: Try the best move from the previous iteration first
- **MVV-LVA (Most Valuable Victim - Least Valuable Attacker)**: Prioritize captures by value
- **Killer Moves**: Non-capture moves that caused cutoffs at the same depth in sibling nodes
- **History Heuristic**: Moves that historically caused cutoffs are tried earlier

**Implementation in Mergen:**
- Move ordering in `Source/C/Ordering.c`
- Killer moves tracked in `Source/C/KillerMoves.c`
- Captures prioritized by MVV-LVA
- History heuristic for quiet moves
- PV move tried first in iterative deepening

---

## Game Phase Detection

### 10. Opening, Middlegame, and Endgame Recognition

**Papers:**
- Berliner, H. J. (1974). "Chess as Problem Solving: The Development of a Tactics Analyzer." *PhD Thesis, Carnegie Mellon University*.
- Müller, H., & Lorenz, U. (1995). "Dual* - A New Approach for Automatic Construction of Endgame Databases." *Advances in Computer Chess 8*, pp. 77-98.

**Description:**
Chess positions have different characteristics depending on the game phase. The evaluation function should adapt:
- **Opening**: King safety, piece development
- **Middlegame**: Tactics, piece activity, king safety
- **Endgame**: King activity, pawn promotion, simplified positions

**Implementation in Mergen:**
- Phase detection in `Source/Evaluation.py` and `Source/C/Evaluate.c`
- Phase score computed based on material (queens, rooks, knights, bishops)
- King uses different piece-square tables for opening vs. endgame
- Threshold at phase_score ≤ 14 for endgame detection

---

## Additional References

### General Chess Programming

- Levy, D. N. L., & Newborn, M. (1991). *How Computers Play Chess.* Computer Science Press.
- Hyatt, R. M. (1997). "The Chess Program Crafty." *University of Alabama at Birmingham*.
- Schaeffer, J. (1989). "The History Heuristic and Alpha-Beta Search Enhancements in Practice." *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 11(11), pp. 1203-1212.

### Chess Programming Wikis and Resources

- Chess Programming Wiki: https://www.chessprogramming.org/
  - Comprehensive resource for chess programming techniques
- Computer Chess Club: http://www.talkchess.com/
  - Forum for chess programming discussion

---

## Opening Theory

### 11. Opening Book

**Papers:**
- Newborn, M. (1975). *Computer Chess.* Academic Press.
- Levy, D. N. L., & Newborn, M. (1991). "Opening Books." *How Computers Play Chess*, Computer Science Press, Chapter 5.
- Hyatt, R. M., Gower, A. E., & Nelson, H. L. (1990). "Cray Blitz." *Computers, Chess, and Cognition*, Springer-Verlag, pp. 111-130.

**Description:**
Opening books are databases of opening theory that allow chess engines to play strong, well-established opening moves without extensive search. Instead of calculating from the start position every time, the engine looks up positions in a pre-compiled database of good opening moves. This provides several benefits:
1. **Faster opening play**: No calculation needed for book positions
2. **Stronger opening**: Leverages centuries of human opening theory
3. **Variety**: Multiple moves can be stored per position with different weights
4. **Learning**: Books can be updated based on engine games and analysis

**Opening Book Formats:**
- **Polyglot**: Binary format (.bin), compact and fast, used by many engines
- **CTG**: ChessBase format, proprietary but widely used
- **JSON/Text**: Human-readable, easy to edit, flexible
- **ABK**: Arena opening book format
- **EPD**: Extended Position Description with best moves

**Implementation in Mergen:**
- JSON-based opening book in `Source/OpeningBook.py`
- Stores positions with FEN keys (simplified to first 4 fields)
- Multiple moves per position with weights for variety
- Weighted random selection for move diversity
- Database file: `Data/opening_book.json`
- Includes 25+ major opening systems:
  - Italian Game, Ruy Lopez, Sicilian Defense
  - French Defense, Caro-Kann Defense
  - Queen's Gambit (Accepted & Declined)
  - King's Indian, Nimzo-Indian Defense
  - English Opening, Réti Opening
  - And many more...

**Usage:**
- Checked before engine search
- Falls back to engine calculation if position not in book
- Can be disabled for pure engine play
- Book moves displayed with "(from book)" indicator

---

## Future Techniques to Implement

The following techniques are commonly used in modern chess engines and are candidates for future implementation in Mergen:

### Null Move Pruning
- Donninger, C. (1993). "Null Move and Deep Search: Selective-Search Heuristics for Obtuse Chess Programs." *ICCA Journal*, 16(3), pp. 137-143.

### Late Move Reductions (LMR)
- Heinz, E. A. (2000). "Adaptive Null-Move Pruning." *ICCA Journal*, 23(3), pp. 123-134.

### Neural Network Evaluation (NNUE)
- Nasu, Y. (2018). "Efficiently Updatable Neural-Network-based Evaluation Functions for Computer Shogi." *The 28th World Computer Shogi Championship Appeal Document*.

### Endgame Tablebases
- Thompson, K. (1986). "Retrograde Analysis of Certain Endgames." *ICCA Journal*, 9(3), pp. 131-139.
- Nalimov, E., Haworth, G. M., & Heinz, E. A. (2000). "Space-Efficient Indexing of Chess Endgame Tables." *ICGA Journal*, 23(3), pp. 148-162.

---

## Implementation Notes

All algorithms in Mergen are implemented with careful attention to:
1. **Correctness**: Following the original papers' specifications
2. **Efficiency**: Optimized C implementation for performance-critical code
3. **Clarity**: Well-commented code with references to techniques used
4. **Modularity**: Separate modules for each major component

---

*Last Updated: November 10, 2025*
*Mergen Chess Engine - Inspired by Wisdom, Built with Intelligence*
