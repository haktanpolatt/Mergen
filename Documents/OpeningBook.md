# Opening Book Guide

## Overview

Mergen now includes an opening book system that provides strong, established opening moves without calculation. This makes the opening phase faster and stronger by leveraging proven opening theory.

## Features

- **25+ Major Openings**: Includes popular systems like Italian Game, Ruy Lopez, Sicilian Defense, Queen's Gambit, and more
- **Weighted Moves**: Each position can have multiple moves with different weights for variety
- **Fast Lookup**: Instant move selection from book (no search required)
- **Fallback to Engine**: Automatically switches to engine search when out of book
- **JSON Format**: Human-readable and easy to customize

## Included Openings

### For White (1.e4)
- Italian Game
- Ruy Lopez (Spanish Opening)
- Scotch Game
- Four Knights Game

### Against 1.e4
- Sicilian Defense (Open)
- French Defense
- Caro-Kann Defense
- Petrov's Defense
- Scandinavian Defense
- Alekhine's Defense
- Pirc Defense
- Modern Defense

### For White (1.d4)
- Queen's Gambit
- London System

### Against 1.d4
- Queen's Gambit Declined/Accepted
- King's Indian Defense
- Nimzo-Indian Defense
- Slav Defense
- Grünfeld Defense
- Dutch Defense
- Benoni Defense

### Other Openings
- English Opening (1.c4)
- Réti Opening (1.Nf3)
- Bird's Opening (1.f4)

## Usage

The opening book is automatically loaded when you run `main.py`. You'll see:

```
Opening book loaded: 33 positions
```

When Mergen plays a move from the book, it will display:
```
Mergen played (from book): e2e4 (took 0.0012s)
```

## Customizing the Opening Book

### Adding New Openings

Edit `Source/OpeningBook.py` and add your opening to `create_default_opening_book()`:

```python
book.add_opening_line(
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"],
    "Italian Game - Giuoco Piano",
    weight=150
)
```

Then regenerate the book:
```bash
python Source\OpeningBook.py
```

### Weight System

- **150+**: Main line openings (e.g., Ruy Lopez, Italian Game, Queen's Gambit)
- **120-140**: Solid alternatives (e.g., Scotch Game, Slav Defense)
- **100-110**: Sidelines and less common openings
- **<100**: Rare or sharp variations

Higher weights make moves more likely to be selected when multiple options exist.

### Manual Editing

The opening book is stored in `Data/opening_book.json`. You can edit it directly:

```json
{
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": [
    {
      "uci": "e2e4",
      "weight": 150,
      "name": "King's Pawn Opening"
    },
    {
      "uci": "d2d4",
      "weight": 150,
      "name": "Queen's Pawn Opening"
    }
  ]
}
```

## Disabling the Opening Book

To play without the opening book, edit `main.py`:

```python
use_opening_book = False  # Change to False
```

## Statistics

Get opening book statistics:

```python
from Source.OpeningBook import OpeningBook

book = OpeningBook()
stats = book.get_statistics()
print(stats)
```

Output:
```python
{
    'positions': 33,
    'total_moves': 56,
    'avg_moves_per_position': 1.70
}
```

## Best Practices

1. **Keep it Focused**: Include only well-analyzed openings
2. **Update Weights**: Adjust based on engine performance
3. **Add Variety**: Multiple moves per position prevent predictability
4. **Test Thoroughly**: Ensure all moves are legal and sound
5. **Document Names**: Label opening lines for easier maintenance

## Future Enhancements

Potential improvements for the opening book system:

- **Polyglot Format**: Support binary .bin format used by many engines
- **Learning**: Update weights based on game results
- **Deeper Lines**: Extend opening lines to 15-20 moves
- **Transposition Handling**: Recognize move order transpositions
- **Opening Statistics**: Track success rates for different lines
- **Import from PGN**: Parse games to build custom books
- **UCI Option**: Enable/disable book through UCI protocol

## References

- Levy, D. N. L., & Newborn, M. (1991). "Opening Books." *How Computers Play Chess*.
- Polyglot Opening Book Format: http://hgm.nubati.net/book_format.html
- Chess Opening Theory: https://www.chess.com/openings

---

*Happy Opening Preparation!*
