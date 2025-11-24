###############################
#                             #
#   Created on Nov 24, 2025   #
#                             #
###############################

"""
UCI (Universal Chess Interface) Protocol Implementation for Mergen Chess Engine.

This module implements the UCI protocol, allowing Mergen to communicate with
chess GUIs like Arena, ChessBase, Cute Chess, and lichess.org bots.

UCI Protocol Documentation: http://wbec-ridderkerk.nl/html/UCIProtocol.html
"""

import sys
import chess
from typing import Optional
from Interface import (
    get_best_move_from_c,
    find_best_move_timed_from_c,
    find_best_move_parallel_from_c,
    find_best_move_parallel_timed_from_c,
    get_cpu_cores
)
from Source.OpeningBook import OpeningBook


class UCIEngine:
    """UCI protocol handler for Mergen chess engine."""
    
    def __init__(self):
        """Initialize UCI engine."""
        self.board = chess.Board()
        self.opening_book = OpeningBook()
        self.debug_mode = False
        self.threads = 1
        self.hash_size = 64  # MB (placeholder, not implemented)
        self.max_cores = get_cpu_cores()
        
        # Engine info
        self.name = "Mergen"
        self.author = "Haktan Polat"
        self.version = "2.0"
    
    def send(self, message: str):
        """Send message to GUI."""
        print(message, flush=True)
        if self.debug_mode:
            self.log(f">> {message}")
    
    def log(self, message: str):
        """Log debug message to stderr."""
        print(f"[DEBUG] {message}", file=sys.stderr, flush=True)
    
    def uci_command(self):
        """Handle 'uci' command - identify engine."""
        self.send(f"id name {self.name} {self.version}")
        self.send(f"id author {self.author}")
        
        # Options
        self.send("option name Threads type spin default 1 min 1 max 16")
        self.send("option name Hash type spin default 64 min 1 max 1024")
        self.send("option name OwnBook type check default true")
        self.send("option name Debug type check default false")
        
        self.send("uciok")
    
    def isready_command(self):
        """Handle 'isready' command - engine is ready."""
        self.send("readyok")
    
    def setoption_command(self, tokens: list):
        """Handle 'setoption' command - set engine options."""
        if len(tokens) < 4 or tokens[0] != "name":
            return
        
        option_name = tokens[1].lower()
        
        if option_name == "threads":
            if len(tokens) >= 4 and tokens[2] == "value":
                try:
                    self.threads = max(1, min(16, int(tokens[3])))
                    if self.debug_mode:
                        self.log(f"Threads set to {self.threads}")
                except ValueError:
                    pass
        
        elif option_name == "hash":
            if len(tokens) >= 4 and tokens[2] == "value":
                try:
                    self.hash_size = max(1, min(1024, int(tokens[3])))
                    if self.debug_mode:
                        self.log(f"Hash set to {self.hash_size} MB")
                except ValueError:
                    pass
        
        elif option_name == "debug":
            if len(tokens) >= 4 and tokens[2] == "value":
                self.debug_mode = tokens[3].lower() == "true"
                if self.debug_mode:
                    self.log("Debug mode enabled")
    
    def ucinewgame_command(self):
        """Handle 'ucinewgame' command - start new game."""
        self.board = chess.Board()
        if self.debug_mode:
            self.log("New game started")
    
    def position_command(self, tokens: list):
        """Handle 'position' command - set board position."""
        if not tokens:
            return
        
        if tokens[0] == "startpos":
            self.board = chess.Board()
            moves_index = 1
        elif tokens[0] == "fen":
            # Find 'moves' keyword or end of FEN
            fen_parts = []
            moves_index = 1
            while moves_index < len(tokens) and tokens[moves_index] != "moves":
                fen_parts.append(tokens[moves_index])
                moves_index += 1
            
            fen = " ".join(fen_parts)
            try:
                self.board = chess.Board(fen)
            except ValueError:
                if self.debug_mode:
                    self.log(f"Invalid FEN: {fen}")
                return
        else:
            return
        
        # Apply moves if present
        if moves_index < len(tokens) and tokens[moves_index] == "moves":
            for move_str in tokens[moves_index + 1:]:
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                    else:
                        if self.debug_mode:
                            self.log(f"Illegal move: {move_str}")
                        break
                except ValueError:
                    if self.debug_mode:
                        self.log(f"Invalid move format: {move_str}")
                    break
    
    def go_command(self, tokens: list):
        """Handle 'go' command - start searching."""
        # Parse go parameters
        depth = None
        movetime = None  # milliseconds
        wtime = None
        btime = None
        winc = 0
        binc = 0
        movestogo = None
        infinite = False
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token == "depth" and i + 1 < len(tokens):
                try:
                    depth = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "movetime" and i + 1 < len(tokens):
                try:
                    movetime = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "wtime" and i + 1 < len(tokens):
                try:
                    wtime = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "btime" and i + 1 < len(tokens):
                try:
                    btime = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "winc" and i + 1 < len(tokens):
                try:
                    winc = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "binc" and i + 1 < len(tokens):
                try:
                    binc = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "movestogo" and i + 1 < len(tokens):
                try:
                    movestogo = int(tokens[i + 1])
                    i += 2
                except ValueError:
                    i += 1
            
            elif token == "infinite":
                infinite = True
                i += 1
            
            else:
                i += 1
        
        # Try opening book first
        book_move = self.opening_book.get_book_move(self.board)
        if book_move:
            if self.debug_mode:
                self.log(f"Book move: {book_move}")
            self.send(f"info string Book move")
            self.send(f"bestmove {book_move}")
            return
        
        # Search for best move
        best_move = self._search(depth, movetime, wtime, btime, winc, binc, movestogo, infinite)
        
        if best_move:
            self.send(f"bestmove {best_move}")
        else:
            # No legal moves or error
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                self.send(f"bestmove {legal_moves[0].uci()}")
            else:
                self.send("bestmove 0000")
    
    def _search(self, depth: Optional[int], movetime: Optional[int],
                wtime: Optional[int], btime: Optional[int],
                winc: int, binc: int, movestogo: Optional[int],
                infinite: bool) -> Optional[str]:
        """Perform search and return best move."""
        fen = self.board.fen()
        
        # Determine search parameters
        if infinite:
            # Infinite analysis - use high depth
            search_depth = 20
        elif depth:
            # Fixed depth search
            search_depth = depth
        elif movetime:
            # Fixed time per move
            if self.threads > 1:
                best_move, _, _ = find_best_move_parallel_timed_from_c(
                    fen, movetime, self.threads
                )
            else:
                best_move, _, _ = find_best_move_timed_from_c(fen, movetime)
            return best_move
        else:
            # Time control - calculate time to use
            if self.board.turn == chess.WHITE:
                my_time = wtime if wtime else 60000
                my_inc = winc
            else:
                my_time = btime if btime else 60000
                my_inc = binc
            
            # Simple time management: use 1/30 of remaining time + increment
            if movestogo:
                time_to_use = (my_time / movestogo) + my_inc
            else:
                time_to_use = (my_time / 30) + my_inc
            
            time_to_use = max(100, min(time_to_use, my_time * 0.4))  # Safety limits
            
            if self.debug_mode:
                self.log(f"Time to use: {time_to_use:.0f}ms")
            
            if self.threads > 1:
                best_move, search_depth, _ = find_best_move_parallel_timed_from_c(
                    fen, int(time_to_use), self.threads
                )
            else:
                best_move, search_depth, _ = find_best_move_timed_from_c(fen, int(time_to_use))
            
            if self.debug_mode:
                self.log(f"Searched to depth {search_depth}")
            
            return best_move
        
        # Fixed depth search
        if self.threads > 1:
            best_move = find_best_move_parallel_from_c(fen, search_depth, self.threads)
        else:
            best_move = get_best_move_from_c(fen, search_depth)
        
        return best_move
    
    def quit_command(self):
        """Handle 'quit' command - exit engine."""
        if self.debug_mode:
            self.log("Quitting")
        sys.exit(0)
    
    def run(self):
        """Main UCI loop - read commands and respond."""
        if self.debug_mode:
            self.log("UCI engine started")
        
        while True:
            try:
                line = input().strip()
                
                if not line:
                    continue
                
                if self.debug_mode:
                    self.log(f"<< {line}")
                
                tokens = line.split()
                command = tokens[0].lower()
                
                if command == "uci":
                    self.uci_command()
                
                elif command == "isready":
                    self.isready_command()
                
                elif command == "setoption":
                    self.setoption_command(tokens[1:])
                
                elif command == "ucinewgame":
                    self.ucinewgame_command()
                
                elif command == "position":
                    self.position_command(tokens[1:])
                
                elif command == "go":
                    self.go_command(tokens[1:])
                
                elif command == "quit":
                    self.quit_command()
                
                elif command == "stop":
                    # Currently not supported (would need search interruption)
                    pass
                
                else:
                    if self.debug_mode:
                        self.log(f"Unknown command: {command}")
            
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                if self.debug_mode:
                    self.log(f"Error: {e}")
                continue


def main():
    """Entry point for UCI mode."""
    engine = UCIEngine()
    engine.run()


if __name__ == "__main__":
    main()
