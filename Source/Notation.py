###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess
import chess.pgn
from datetime import datetime
from typing import Optional
import os

def save_game_log(board, maximizing_player, depth):
    """Legacy function for saving to markdown format."""
    mergen_color = "white" if maximizing_player else "black"

    moves = []
    board_copy = chess.Board()
    for i, move in enumerate(board.move_stack):
        if i % 2 == 0:
            moves.append(f"{(i // 2) + 1}. {board_copy.san(move)}")
        else:
            moves[-1] += f" {board_copy.san(move)}"
        board_copy.push(move)

    with open("Records/games.md", "a") as f:
        f.write(f"- Mergen was **{mergen_color}**, depth = {depth}, with alpha-beta pruning, C integrated, zobrist and TT, \n")
        f.write("```pgn\n")
        f.write(" ".join(moves))
        f.write("\n```\n")


def save_game_pgn(board: chess.Board, 
                  filename: Optional[str] = None,
                  white_player: str = "Human",
                  black_player: str = "Mergen",
                  event: str = "Casual Game",
                  site: str = "Local",
                  depth: int = 4,
                  time_control: str = "-") -> str:
    """
    Save game in standard PGN format.
    
    Args:
        board: Chess board with move history
        filename: Output filename (default: auto-generated)
        white_player: Name of white player
        black_player: Name of black player
        event: Event name
        site: Location/site
        depth: Search depth used by engine
        time_control: Time control used
        
    Returns:
        Path to saved PGN file
    """
    # Create Records directory if it doesn't exist
    os.makedirs("Records", exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Records/game_{timestamp}.pgn"
    elif not filename.startswith("Records/"):
        filename = f"Records/{filename}"
    
    # Ensure .pgn extension
    if not filename.endswith(".pgn"):
        filename += ".pgn"
    
    # Create PGN game
    game = chess.pgn.Game()
    
    # Set headers
    game.headers["Event"] = event
    game.headers["Site"] = site
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["Round"] = "?"
    game.headers["White"] = white_player
    game.headers["Black"] = black_player
    
    # Set result
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            game.headers["Result"] = "0-1"  # Black wins
        else:
            game.headers["Result"] = "1-0"  # White wins
    elif board.is_stalemate() or board.is_insufficient_material() or \
         board.is_seventyfive_moves() or board.is_fivefold_repetition():
        game.headers["Result"] = "1/2-1/2"  # Draw
    else:
        game.headers["Result"] = "*"  # Ongoing
    
    # Add custom headers
    game.headers["Mergen"] = f"Depth {depth}"
    game.headers["TimeControl"] = time_control
    
    # Add moves to game
    node = game
    temp_board = chess.Board()
    
    for move in board.move_stack:
        node = node.add_variation(move)
        temp_board.push(move)
    
    # Save to file
    with open(filename, "w") as f:
        exporter = chess.pgn.FileExporter(f)
        game.accept(exporter)
    
    return filename


def load_game_pgn(filename: str) -> Optional[chess.Board]:
    """
    Load a game from PGN file.
    
    Args:
        filename: Path to PGN file
        
    Returns:
        Chess board with loaded position, or None if failed
    """
    if not filename.startswith("Records/"):
        filename = f"Records/{filename}"
    
    if not os.path.exists(filename):
        print(f"[ERROR] File not found: {filename}")
        return None
    
    try:
        with open(filename) as f:
            game = chess.pgn.read_game(f)
            
        if game is None:
            print("[ERROR] No game found in PGN file")
            return None
        
        # Create board and replay moves
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
        
        return board
    
    except Exception as e:
        print(f"[ERROR] Failed to load PGN: {e}")
        return None


def list_saved_games() -> list:
    """
    List all saved PGN games.
    
    Returns:
        List of tuples (filename, white, black, result, date)
    """
    games = []
    
    if not os.path.exists("Records"):
        return games
    
    for filename in os.listdir("Records"):
        if filename.endswith(".pgn"):
            try:
                with open(f"Records/{filename}") as f:
                    game = chess.pgn.read_game(f)
                    
                if game:
                    games.append({
                        'filename': filename,
                        'white': game.headers.get("White", "?"),
                        'black': game.headers.get("Black", "?"),
                        'result': game.headers.get("Result", "*"),
                        'date': game.headers.get("Date", "?.?.?"),
                        'event': game.headers.get("Event", "?")
                    })
            except:
                pass
    
    return sorted(games, key=lambda x: x['date'], reverse=True)


def export_position_fen(board: chess.Board, filename: Optional[str] = None) -> str:
    """
    Export current position as FEN to file.
    
    Args:
        board: Chess board
        filename: Output filename (default: auto-generated)
        
    Returns:
        Path to saved file
    """
    os.makedirs("Records", exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Records/position_{timestamp}.fen"
    elif not filename.startswith("Records/"):
        filename = f"Records/{filename}"
    
    if not filename.endswith(".fen"):
        filename += ".fen"
    
    with open(filename, "w") as f:
        f.write(board.fen())
    
    return filename


def load_position_fen(filename: str) -> Optional[chess.Board]:
    """
    Load a position from FEN file.
    
    Args:
        filename: Path to FEN file
        
    Returns:
        Chess board with loaded position, or None if failed
    """
    if not filename.startswith("Records/"):
        filename = f"Records/{filename}"
    
    if not os.path.exists(filename):
        print(f"[ERROR] File not found: {filename}")
        return None
    
    try:
        with open(filename) as f:
            fen = f.read().strip()
        
        board = chess.Board(fen)
        return board
    
    except Exception as e:
        print(f"[ERROR] Failed to load FEN: {e}")
        return None