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
    Create a default opening book with popular openings.
    This includes major opening systems for both White and Black.
    """
    book = OpeningBook()
    
    # Italian Game
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"],
        "Italian Game",
        weight=150
    )
    
    # Ruy Lopez (Spanish Opening)
    book.add_opening_line(
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
        "Ruy Lopez",
        weight=150
    )
    
    # Sicilian Defense - Open
    book.add_opening_line(
        ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4"],
        "Sicilian Defense - Open",
        weight=140
    )
    
    # French Defense
    book.add_opening_line(
        ["e2e4", "e7e6", "d2d4", "d7d5"],
        "French Defense",
        weight=130
    )
    
    # Caro-Kann Defense
    book.add_opening_line(
        ["e2e4", "c7c6", "d2d4", "d7d5"],
        "Caro-Kann Defense",
        weight=130
    )
    
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
        weight=120
    )
    
    # Queen's Gambit Declined
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "e7e6"],
        "Queen's Gambit Declined",
        weight=140
    )
    
    # King's Indian Defense
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7"],
        "King's Indian Defense",
        weight=130
    )
    
    # Nimzo-Indian Defense
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4"],
        "Nimzo-Indian Defense",
        weight=130
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
    
    # Scandinavian Defense
    book.add_opening_line(
        ["e2e4", "d7d5"],
        "Scandinavian Defense",
        weight=100
    )
    
    # Alekhine's Defense
    book.add_opening_line(
        ["e2e4", "g8f6"],
        "Alekhine's Defense",
        weight=100
    )
    
    # Pirc Defense
    book.add_opening_line(
        ["e2e4", "d7d6", "d2d4", "g8f6", "b1c3", "g7g6"],
        "Pirc Defense",
        weight=100
    )
    
    # Modern Defense
    book.add_opening_line(
        ["e2e4", "g7g6"],
        "Modern Defense",
        weight=90
    )
    
    # London System
    book.add_opening_line(
        ["d2d4", "d7d5", "g1f3", "g8f6", "c1f4"],
        "London System",
        weight=120
    )
    
    # Slav Defense
    book.add_opening_line(
        ["d2d4", "d7d5", "c2c4", "c7c6"],
        "Slav Defense",
        weight=120
    )
    
    # Grünfeld Defense
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5"],
        "Grünfeld Defense",
        weight=120
    )
    
    # Dutch Defense
    book.add_opening_line(
        ["d2d4", "f7f5"],
        "Dutch Defense",
        weight=100
    )
    
    # Benoni Defense
    book.add_opening_line(
        ["d2d4", "g8f6", "c2c4", "c7c5"],
        "Benoni Defense",
        weight=100
    )
    
    # Bird's Opening
    book.add_opening_line(
        ["f2f4"],
        "Bird's Opening",
        weight=90
    )
    
    # Réti Opening
    book.add_opening_line(
        ["g1f3", "d7d5", "c2c4"],
        "Réti Opening",
        weight=110
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
