###############################
#                             #
#   Created on Nov 10, 2025   #
#                             #
###############################

import json
import os
import random
from typing import List, Optional, Dict
import chess

class OpeningBook:
    """
    Opening book system for Mergen chess engine.
    Stores and retrieves opening moves for common positions.
    """
    
    def __init__(self, book_path: str = "Data/opening_book.json"):
        self.book_path = book_path
        self.book: Dict[str, List[Dict]] = {}
        self.load_book()
    
    def load_book(self):
        """Load opening book from JSON file."""
        if os.path.exists(self.book_path):
            try:
                with open(self.book_path, 'r') as f:
                    self.book = json.load(f)
                print(f"[INFO] Loaded opening book with {len(self.book)} positions")
            except Exception as e:
                print(f"[WARNING] Could not load opening book: {e}")
                self.book = {}
        else:
            print(f"[INFO] No opening book found at {self.book_path}")
            self.book = {}
    
    def save_book(self):
        """Save opening book to JSON file."""
        os.makedirs(os.path.dirname(self.book_path), exist_ok=True)
        with open(self.book_path, 'w') as f:
            json.dump(self.book, f, indent=2)
        print(f"[INFO] Saved opening book with {len(self.book)} positions")
    
    def get_book_move(self, board: chess.Board) -> Optional[str]:
        """
        Get a move from the opening book for the current position.
        Returns UCI move string or None if position not in book.
        """
        fen = board.fen()
        
        # Simplify FEN to only include position (ignore move counters)
        fen_parts = fen.split(' ')
        position_key = ' '.join(fen_parts[:4])  # board, turn, castling, en passant
        
        if position_key in self.book:
            moves = self.book[position_key]
            if moves:
                # Select move based on weight (popularity/quality)
                total_weight = sum(move['weight'] for move in moves)
                rand = random.uniform(0, total_weight)
                
                cumulative = 0
                for move in moves:
                    cumulative += move['weight']
                    if rand <= cumulative:
                        return move['uci']
                
                # Fallback to first move
                return moves[0]['uci']
        
        return None
    
    def add_move(self, fen: str, uci_move: str, weight: int = 100, name: str = ""):
        """
        Add a move to the opening book.
        
        Args:
            fen: Position in FEN notation
            uci_move: Move in UCI format (e.g., "e2e4")
            weight: Weight/priority of this move (higher = more likely to be chosen)
            name: Optional name/description of the opening
        """
        # Simplify FEN
        fen_parts = fen.split(' ')
        position_key = ' '.join(fen_parts[:4])
        
        if position_key not in self.book:
            self.book[position_key] = []
        
        # Check if move already exists
        for move in self.book[position_key]:
            if move['uci'] == uci_move:
                # Update weight if move exists
                move['weight'] = max(move['weight'], weight)
                if name:
                    move['name'] = name
                return
        
        # Add new move
        self.book[position_key].append({
            'uci': uci_move,
            'weight': weight,
            'name': name
        })
    
    def add_opening_line(self, moves: List[str], name: str = "", weight: int = 100):
        """
        Add a complete opening line to the book.
        
        Args:
            moves: List of moves in UCI format (e.g., ["e2e4", "e7e5", "g1f3"])
            name: Name of the opening
            weight: Weight/priority for all moves in this line
        """
        board = chess.Board()
        
        for i, move_uci in enumerate(moves):
            try:
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    move_name = f"{name} (move {i+1})" if name else ""
                    self.add_move(board.fen(), move_uci, weight, move_name)
                    board.push(move)
                else:
                    print(f"[WARNING] Illegal move in opening line: {move_uci}")
                    break
            except Exception as e:
                print(f"[ERROR] Error adding move {move_uci}: {e}")
                break
    
    def is_in_book(self, board: chess.Board) -> bool:
        """Check if current position is in the opening book."""
        fen_parts = board.fen().split(' ')
        position_key = ' '.join(fen_parts[:4])
        return position_key in self.book
    
    def get_statistics(self) -> Dict:
        """Get statistics about the opening book."""
        total_positions = len(self.book)
        total_moves = sum(len(moves) for moves in self.book.values())
        
        return {
            'positions': total_positions,
            'total_moves': total_moves,
            'avg_moves_per_position': total_moves / total_positions if total_positions > 0 else 0
        }


def create_default_opening_book():
    """
    Create a comprehensive opening book with openings from Wikipedia.
    Includes major opening systems and popular variations.
    Source: https://en.wikipedia.org/wiki/List_of_chess_openings
    """
    book = OpeningBook()
    
    print("[INFO] Building opening book from Wikipedia's list of chess openings...")
    
    # ===========================================
    # OPEN GAMES (1.e4 e5)
    # ===========================================
    
    # Italian Game
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"],
        "Italian Game",
        weight=150
    )
    
    # Giuoco Piano (Italian continuation)
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"],
        "Giuoco Piano",
        weight=140
    )
    
    # Two Knights Defense
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"],
        "Two Knights Defense",
        weight=130
    )
    
    # Ruy Lopez (Spanish Opening) - Main Line
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
        "Ruy Lopez",
        weight=150
    )
    
    # Ruy Lopez - Berlin Defense
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6"],
        "Ruy Lopez - Berlin Defense",
        weight=140
    )
    
    # Ruy Lopez - Morphy Defense
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6"],
        "Ruy Lopez - Morphy Defense",
        weight=145
    )
    
    # Scotch Game
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "d2d4"],
        "Scotch Game",
        weight=120
    )
    
    # Scotch Gambit
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "d2d4", "e5d4", "f1c4"],
        "Scotch Gambit",
        weight=110
    )
    
    # Four Knights Game
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "b1c3", "g8f6"],
        "Four Knights Game",
        weight=110
    )
    
    # Petrov's Defense (Russian Game)
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "g8f6"],
        "Petrov's Defense",
        weight=110
    )
    
    # Philidor Defense
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "d7d6"],
        "Philidor Defense",
        weight=100
    )
    
    # King's Gambit
    book.add_opening_line(
        ["e2e4", "e7e5", "f2f4"],
        "King's Gambit",
        weight=105
    )
    
    # King's Gambit Accepted
    book.add_opening_line(
        ["e2e4", "e7e5", "f2f4", "e5f4"],
        "King's Gambit Accepted",
        weight=100
    )
    
    # Vienna Game
    book.add_opening_line(
        ["e2e4", "e7e5", "b1c3"],
        "Vienna Game",
        weight=110
    )
    
    # Bishop's Opening
    book.add_opening_line(
        ["e2e4", "e7e5", "f1c4"],
        "Bishop's Opening",
        weight=105
    )
    
    # Center Game
    book.add_opening_line(
        ["e2e4", "e7e5", "d2d4"],
        "Center Game",
        weight=95
    )
    
    # ===========================================
    # SEMI-OPEN GAMES (1.e4 other)
    # ===========================================
    
    # Sicilian Defense - Open Variation
    book.add_opening_line(
        ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4"],
        "Sicilian Defense - Open",
        weight=140
    )
    
    # Sicilian Defense - Najdorf
    book.add_opening_line(
        ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "a7a6"],
        "Sicilian - Najdorf",
        weight=145
    )
    
    # Sicilian Defense - Dragon
    book.add_opening_line(
        ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "g7g6"],
        "Sicilian - Dragon",
        weight=140
    )
    
    # Sicilian Defense - Closed
    book.add_opening_line(
        ["e2e4", "c7c5", "b1c3"],
        "Sicilian - Closed",
        weight=120
    )
    
    # Sicilian Defense - Alapin
    book.add_opening_line(
        ["e2e4", "c7c5", "c2c3"],
        "Sicilian - Alapin",
        weight=125
    )
    
    # French Defense - Main Line
    book.add_opening_line(
        ["e2e4", "e7e6", "d2d4", "d7d5"],
        "French Defense",
        weight=130
    )
    
    # French Defense - Advance Variation
    book.add_opening_line(
        ["e2e4", "e7e6", "d2d4", "d7d5", "e4e5"],
        "French - Advance",
        weight=125
    )
    
    # French Defense - Exchange Variation
    book.add_opening_line(
        ["e2e4", "e7e6", "d2d4", "d7d5", "e4d5"],
        "French - Exchange",
        weight=120
    )
    
    # Caro-Kann Defense - Main Line
    book.add_opening_line(
        ["e2e4", "c7c6", "d2d4", "d7d5"],
        "Caro-Kann Defense",
        weight=130
    )
    
    # Caro-Kann - Advance Variation
    book.add_opening_line(
        ["e2e4", "c7c6", "d2d4", "d7d5", "e4e5"],
        "Caro-Kann - Advance",
        weight=125
    )
    
    # Caro-Kann - Exchange Variation
    book.add_opening_line(
        ["e2e4", "c7c6", "d2d4", "d7d5", "e4d5"],
        "Caro-Kann - Exchange",
        weight=120
    )
    
    # ===========================================
    # CLOSED GAMES (1.d4 d5)
    # ===========================================
    
    # Queen's Gambit
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4"],
        "Queen's Gambit",
        weight=150
    )
    
    # Queen's Gambit Accepted
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "d5c4"],
        "Queen's Gambit Accepted",
        weight=130
    )
    
    # Queen's Gambit Declined - Orthodox
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "e7e6"],
        "Queen's Gambit Declined",
        weight=145
    )
    
    # Queen's Gambit Declined - Tartakower
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5", "f8e7", "e2e3", "h7h6"],
        "QGD - Tartakower",
        weight=135
    )
    
    # Semi-Slav Defense
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "g1f3", "c7c6"],
        "Semi-Slav Defense",
        weight=135
    )
    
    # London System
    book.add_opening_line(
        ["d2d4", "d7d5", "g1f3", "g8f6", "c1f4"],
        "London System",
        weight=125
    )
    
    # Colle System
    book.add_opening_line(
        ["d2d4", "d7d5", "g1f3", "g8f6", "e2e3"],
        "Colle System",
        weight=110
    )
    
    # Torre Attack
    book.add_opening_line(
        ["d2d4", "d7d5", "g1f3", "g8f6", "c1g5"],
        "Torre Attack",
        weight=110
    )
    
    # Trompowsky Attack
    book.add_opening_line(
        ["d2d4", "g8f6", "c1g5"],
        "Trompowsky Attack",
        weight=105
    )
    
    # ===========================================
    # INDIAN DEFENSES (1.d4 Nf6)
    # ===========================================
    
    # King's Indian Defense - Main Line
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7"],
        "King's Indian Defense",
        weight=135
    )
    
    # King's Indian - Classical Variation
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7", "e2e4", "d7d6", "g1f3", "e8g8"],
        "KID - Classical",
        weight=130
    )
    
    # King's Indian - Sämisch Variation
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7", "e2e4", "d7d6", "f2f3"],
        "KID - Sämisch",
        weight=125
    )
    
    # Nimzo-Indian Defense - Main Line
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4"],
        "Nimzo-Indian Defense",
        weight=140
    )
    
    # Nimzo-Indian - Classical Variation
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4", "d1c2"],
        "Nimzo-Indian - Classical",
        weight=135
    )
    
    # Queen's Indian Defense
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e6", "g1f3", "b7b6"],
        "Queen's Indian Defense",
        weight=130
    )
    
    # Bogo-Indian Defense
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e6", "g1f3", "f8b4"],
        "Bogo-Indian Defense",
        weight=120
    )
    
    # Catalan Opening
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e6", "g2g3"],
        "Catalan Opening",
        weight=125
    )
    
    # English Opening
    book.add_opening_line(
        ["c2c4", "e7e5"],
        "English Opening",
        weight=120
    )
    
    # Scotch Game
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "d2d4"],
        "Scotch Game",
        weight=120
    )
    
    # Four Knights Game
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "b1c3", "g8f6"],
        "Four Knights Game",
        weight=110
    )
    
    # Petrov's Defense
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "g8f6"],
        "Petrov's Defense",
        weight=110
    )
    
    # Scandinavian Defense (Center Counter)
    book.add_opening_line(
        ["e2e4", "d7d5"],
        "Scandinavian Defense",
        weight=110
    )
    
    # Scandinavian - Modern Variation
    book.add_opening_line(
        ["e2e4", "d7d5", "e4d5", "g8f6"],
        "Scandinavian - Modern",
        weight=105
    )
    
    # Alekhine's Defense
    book.add_opening_line(
        ["e2e4", "g8f6"],
        "Alekhine's Defense",
        weight=105
    )
    
    # Alekhine's Defense - Four Pawns Attack
    book.add_opening_line(
        ["e2e4", "g8f6", "e4e5", "f6d5", "d2d4", "d7d6", "c2c4"],
        "Alekhine's - Four Pawns",
        weight=100
    )
    
    # Pirc Defense
    book.add_opening_line(
        ["e2e4", "d7d6", "d2d4", "g8f6", "b1c3", "g7g6"],
        "Pirc Defense",
        weight=110
    )
    
    # Modern Defense
    book.add_opening_line(
        ["e2e4", "g7g6"],
        "Modern Defense",
        weight=100
    )
    
    # Owen's Defense
    book.add_opening_line(
        ["e2e4", "b7b6"],
        "Owen's Defense",
        weight=85
    )
    
    # Nimzowitsch Defense
    book.add_opening_line(
        ["e2e4", "b8c6"],
        "Nimzowitsch Defense",
        weight=90
    )
    
    # London System
    book.add_opening_line(
        ["d2d4", "d7d5", "g1f3", "g8f6", "c1f4"],
        "London System",
        weight=120
    )
    
    # Slav Defense - Main Line
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "c7c6"],
        "Slav Defense",
        weight=130
    )
    
    # Slav Defense - Exchange Variation
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "c7c6", "c4d5"],
        "Slav - Exchange",
        weight=120
    )
    
    # Grünfeld Defense - Main Line
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5"],
        "Grünfeld Defense",
        weight=130
    )
    
    # Grünfeld - Exchange Variation
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5", "c4d5", "f6d5", "e2e4"],
        "Grünfeld - Exchange",
        weight=125
    )
    
    # Dutch Defense - Main Line
    book.add_opening_line(
        ["d2d4", "f7f5"],
        "Dutch Defense",
        weight=110
    )
    
    # Dutch Defense - Leningrad
    book.add_opening_line(
        ["d2d4", "f7f5", "g2g3", "g8f6", "f1g2", "g7g6"],
        "Dutch - Leningrad",
        weight=105
    )
    
    # Dutch Defense - Stonewall
    book.add_opening_line(
        ["d2d4", "f7f5", "c2c4", "g8f6", "g2g3", "e7e6", "f1g2", "d7d5"],
        "Dutch - Stonewall",
        weight=105
    )
    
    # Benoni Defense - Modern
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "c7c5"],
        "Benoni Defense",
        weight=110
    )
    
    # Benoni Defense - Old Benoni
    book.add_opening_line(
        ["d2d4", "c7c5"],
        "Old Benoni",
        weight=95
    )
    
    # Budapest Gambit
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e5"],
        "Budapest Gambit",
        weight=95
    )
    
    # ===========================================
    # FLANK OPENINGS (1.c4, 1.Nf3, 1.f4, etc.)
    # ===========================================
    
    # English Opening - Symmetrical
    book.add_opening_line(
        ["c2c4", "c7c5"],
        "English - Symmetrical",
        weight=130
    )
    
    # English Opening - Reversed Sicilian
    book.add_opening_line(
        ["c2c4", "e7e5"],
        "English - Reversed Sicilian",
        weight=130
    )
    
    # English Opening - Anglo-Indian
    book.add_opening_line(
        ["c2c4", "g8f6"],
        "English - Anglo-Indian",
        weight=125
    )
    
    # English Opening - Four Knights
    book.add_opening_line(
        ["c2c4", "e7e5", "b1c3", "g8f6", "g1f3", "b8c6"],
        "English - Four Knights",
        weight=120
    )
    
    # Réti Opening
    book.add_opening_line(
        ["g1f3", "d7d5", "c2c4"],
        "Réti Opening",
        weight=120
    )
    
    # Réti Opening - King's Indian Attack
    book.add_opening_line(
        ["g1f3", "g8f6", "g2g3"],
        "Réti - KIA",
        weight=115
    )
    
    # Bird's Opening
    book.add_opening_line(
        ["f2f4"],
        "Bird's Opening",
        weight=100
    )
    
    # Bird's Opening - From's Gambit
    book.add_opening_line(
        ["f2f4", "e7e5"],
        "Bird's - From's Gambit",
        weight=95
    )
    
    # Larsen's Opening
    book.add_opening_line(
        ["b2b3"],
        "Larsen's Opening",
        weight=95
    )
    
    # ===========================================
    # UNCOMMON BUT PLAYABLE OPENINGS
    # ===========================================
    
    # Polish Opening (Sokolsky)
    book.add_opening_line(
        ["b2b4"],
        "Polish Opening",
        weight=85
    )
    
    # King's Indian Attack (KIA)
    book.add_opening_line(
        ["g1f3", "d7d5", "g2g3", "g8f6", "f1g2"],
        "King's Indian Attack",
        weight=105
    )
    
    book.save_book()
    print(f"[SUCCESS] Created default opening book")
    stats = book.get_statistics()
    print(f"  - Positions: {stats['positions']}")
    print(f"  - Total moves: {stats['total_moves']}")
    print(f"  - Avg moves per position: {stats['avg_moves_per_position']:.2f}")
    
    return book


if __name__ == "__main__":
    # Create default opening book
    print("Creating default opening book...")
    book = create_default_opening_book()
