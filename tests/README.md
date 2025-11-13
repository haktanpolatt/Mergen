# Mergen Chess Engine Test Suite

Comprehensive test suite to verify the correctness and performance of the Mergen chess engine.

## Test Categories

### 1. Move Generation (`test_move_generation.py`)
Tests the legality and correctness of move generation:
- **Legal Move Generation**: Verifies starting position has 20 legal moves
- **Illegal Move Prevention**: Ensures invalid moves are rejected
- **Checkmate Detection**: Tests game-ending position recognition
- **Stalemate Detection**: Tests draw condition recognition
- **Castling**: Validates kingside and queenside castling
- **En Passant**: Tests pawn capture special rules
- **Pawn Promotion**: Verifies promotion to queen/knight
- **PERFT Testing**: Position verification at depths 1-2

### 2. Evaluation (`test_evaluation.py`)
Tests the position evaluation function:
- **Material Balance**: Equal positions score near 0
- **Material Advantage**: Queen/rook/piece advantages scored correctly
- **Piece Values**: Queen ~9, Rook ~5, Minor pieces ~3
- **Pawn Structure**: Tests doubled/isolated pawn penalties
- **Passed Pawns**: Bonuses for advanced passed pawns
- **King Safety**: Penalties for exposed kings
- **Mobility**: Bonuses for piece activity

### 3. Tactical Patterns (`test_tactics.py`)
Tests tactical awareness and solving ability:
- **Mate in One**: Back rank mate, smothered mate detection
- **Mate in Two**: Anastasia's mate, Arabian mate sequences
- **Tactical Motifs**: Forks, pins, discovered attacks
- **Endgame Knowledge**: K+Q vs K, K+R vs K technique
- **Blunder Avoidance**: Don't hang pieces, defend against threats

### 4. Opening Book (`test_opening_book.py`)
Tests opening repertoire functionality:
- **Book Loading**: Verifies JSON database loads correctly
- **Move Retrieval**: Gets book moves from starting position
- **Opening Coverage**: Tests e4, d4, Sicilian, French responses
- **Out-of-Book Behavior**: Returns None when position not in book
- **Statistics**: Validates position/move counts
- **Manipulation**: Add moves and variations

### 5. PGN Save/Load (`test_pgn.py`)
Tests game persistence and notation:
- **Save Games**: Export games to standard PGN format
- **Load Games**: Import games from PGN files
- **PGN Headers**: Correct event, player, date information
- **Game Listing**: List all saved games
- **FEN Export/Import**: Save and load positions
- **Results**: Checkmate (1-0, 0-1) and draw (1/2-1/2) recording

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Category
```bash
python run_tests.py moves      # Move generation only
python run_tests.py eval       # Evaluation only
python run_tests.py tactics    # Tactical tests only
python run_tests.py book       # Opening book only
python run_tests.py pgn        # PGN save/load only
```

### Verbosity Options
```bash
python run_tests.py -v         # Verbose output
python run_tests.py -q         # Quiet (minimal) output
```

### Run Individual Test File
```bash
python -m unittest tests.test_move_generation
python -m unittest tests.test_evaluation
python -m unittest tests.test_tactics
python -m unittest tests.test_opening_book
python -m unittest tests.test_pgn
```

### Run Specific Test Class
```bash
python -m unittest tests.test_tactics.TestMateInOne
python -m unittest tests.test_evaluation.TestPieceValues
```

## Test Results Interpretation

### Success Output
```
Tests run: 45
Successes: 45
Failures: 0
Errors: 0

✓ All tests passed!
```

### Failure Output
If a test fails, you'll see:
- **Test name**: Which specific test failed
- **Assertion error**: What was expected vs what was received
- **Line number**: Where in the test file the failure occurred

### Common Issues

1. **PERFT failures**: May indicate move generation bugs
2. **Evaluation failures**: Check if evaluation weights changed
3. **Tactical failures**: Might need deeper search or better evaluation
4. **Book failures**: Verify `Data/opening_book.json` is present and valid
5. **PGN failures**: Check `Records/` directory exists and is writable

## Test Coverage

Current test suite covers:
- ✅ Legal move generation and validation
- ✅ Special moves (castling, en passant, promotion)
- ✅ Position evaluation accuracy
- ✅ Tactical pattern recognition
- ✅ Mate-in-N solving
- ✅ Opening book functionality
- ✅ PGN save/load functionality
- ✅ FEN import/export
- ✅ Game result detection

## Adding New Tests

To add new tests:

1. Create test file in `tests/` directory
2. Import `unittest` and required modules
3. Create test class inheriting from `unittest.TestCase`
4. Write test methods starting with `test_`
5. Add test class to `run_tests.py` in appropriate category

Example:
```python
import unittest
import chess

class TestNewFeature(unittest.TestCase):
    def test_something(self):
        board = chess.Board()
        # Test code here
        self.assertTrue(condition, "Explanation")
```

## Dependencies

Tests require:
- `chess` library (python-chess)
- Source modules: `Board`, `Evaluation`, `Mergen`, `OpeningBook`, `Notation`
- C engine compiled (for search tests)

## Performance Tests

Some tests (especially PERFT and tactical puzzles) may take time:
- PERFT depth 2: ~1-2 seconds
- Mate-in-2 puzzles: ~2-5 seconds each
- Deep tactical positions: May take 10+ seconds

Use `-q` flag for faster minimal output during development.

## Continuous Integration

These tests are suitable for CI/CD pipelines:
```bash
python run_tests.py -q  # Returns exit code 0 on success, 1 on failure
```

## Test Philosophy

Tests are designed to:
1. **Verify correctness**: Engine plays legal, sensible chess
2. **Prevent regressions**: Changes don't break existing functionality
3. **Document behavior**: Tests serve as examples/documentation
4. **Enable refactoring**: Safely improve code with test safety net
