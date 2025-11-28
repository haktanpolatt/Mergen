#!/usr/bin/env python3
"""
Engine vs Engine Testing Framework for Mergen Chess Engine

This framework allows you to:
1. Play engines against each other
2. Run tournaments with multiple games
3. Calculate ELO ratings
4. Analyze game results and statistics
5. Test engine improvements objectively

Usage:
    python3 tournament.py --help
"""

import sys
import os
import subprocess
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import chess
import chess.pgn

class UCIEngine:
    """Wrapper for UCI chess engines"""
    
    def __init__(self, command: str, name: str, options: Dict[str, str] = None):
        """
        Initialize UCI engine
        
        Args:
            command: Command to start the engine (e.g., "python3 uci.py")
            name: Display name for the engine
            options: UCI options to set (e.g., {"Threads": "1", "Hash": "64"})
        """
        self.command = command
        self.name = name
        self.options = options or {}
        self.process = None
        
    def start(self):
        """Start the engine process"""
        self.process = subprocess.Popen(
            self.command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Initialize UCI
        self._send("uci")
        self._wait_for("uciok")
        
        # Set options
        for option, value in self.options.items():
            self._send(f"setoption name {option} value {value}")
            
        # Confirm ready
        self._send("isready")
        self._wait_for("readyok")
        
    def stop(self):
        """Stop the engine process"""
        if self.process:
            self._send("quit")
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            
    def _send(self, command: str):
        """Send command to engine"""
        if self.process and self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
        else:
            print(f"ERROR: Cannot send '{command}' - process not running")
            
    def _wait_for(self, expected: str, timeout: float = 5.0) -> Optional[str]:
        """Wait for expected response from engine"""
        start = time.time()
        while time.time() - start < timeout:
            if self.process and self.process.stdout:
                line = self.process.stdout.readline().strip()
                if line and expected in line:
                    return line
        print(f"WARNING: Timeout waiting for '{expected}' after {timeout}s")
        return None
        
    def get_move(self, board: chess.Board, movetime: int = None, depth: int = None) -> Optional[str]:
        """
        Get best move from engine
        
        Args:
            board: Current board position
            movetime: Time in milliseconds to search
            depth: Search depth (alternative to movetime)
            
        Returns:
            Move in UCI format (e.g., "e2e4") or None if failed
        """
        # Send position
        fen = board.fen()
        self._send(f"position fen {fen}")
        
        # Ensure engine is ready
        self._send("isready")
        self._wait_for("readyok", timeout=2.0)
        
        # Send go command
        if depth is not None:
            self._send(f"go depth {depth}")
        elif movetime is not None:
            self._send(f"go movetime {movetime}")
        else:
            self._send("go depth 4")  # Default depth
            
        # Wait for bestmove
        response = self._wait_for("bestmove", timeout=max(movetime/1000.0 + 5.0 if movetime else 30.0, 10.0))
        
        if response and "bestmove" in response:
            parts = response.split()
            if len(parts) >= 2:
                return parts[1]
        return None


class Game:
    """Manages a single game between two engines"""
    
    def __init__(self, white_engine: UCIEngine, black_engine: UCIEngine, 
                 time_control: Dict = None, max_moves: int = 150):
        """
        Initialize game
        
        Args:
            white_engine: Engine playing white
            black_engine: Engine playing black
            time_control: {"movetime": 1000} or {"depth": 4}
            max_moves: Maximum moves before declaring draw
        """
        self.white_engine = white_engine
        self.black_engine = black_engine
        self.time_control = time_control or {"depth": 4}
        self.max_moves = max_moves
        self.board = chess.Board()
        self.pgn_game = chess.pgn.Game()
        self.pgn_game.headers["White"] = white_engine.name
        self.pgn_game.headers["Black"] = black_engine.name
        self.pgn_game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        
    def play(self) -> Tuple[str, str]:
        """
        Play the game
        
        Returns:
            (result, reason) where result is "1-0", "0-1", or "1/2-1/2"
        """
        # Signal new game to engines
        self.white_engine._send("ucinewgame")
        self.black_engine._send("ucinewgame")
        self.white_engine._send("isready")
        self.black_engine._send("isready")
        self.white_engine._wait_for("readyok", timeout=2.0)
        self.black_engine._wait_for("readyok", timeout=2.0)
        
        node = self.pgn_game
        move_count = 0
        
        while not self.board.is_game_over() and move_count < self.max_moves:
            # Select engine
            engine = self.white_engine if self.board.turn else self.black_engine
            
            # Get move
            move_uci = engine.get_move(self.board, **self.time_control)
            
            if not move_uci:
                # Engine failed to return move
                result = "0-1" if self.board.turn else "1-0"
                return result, f"{engine.name} failed to return move"
                
            try:
                move = chess.Move.from_uci(move_uci)
                if move not in self.board.legal_moves:
                    result = "0-1" if self.board.turn else "1-0"
                    return result, f"{engine.name} returned illegal move: {move_uci}"
                    
                # Make move
                self.board.push(move)
                node = node.add_variation(move)
                move_count += 1
                
            except Exception as e:
                result = "0-1" if self.board.turn else "1-0"
                return result, f"{engine.name} error: {str(e)}"
                
        # Game over
        if self.board.is_checkmate():
            result = "0-1" if self.board.turn else "1-0"
            reason = "Checkmate"
        elif self.board.is_stalemate():
            result = "1/2-1/2"
            reason = "Stalemate"
        elif self.board.is_insufficient_material():
            result = "1/2-1/2"
            reason = "Insufficient material"
        elif self.board.can_claim_fifty_moves():
            result = "1/2-1/2"
            reason = "Fifty move rule"
        elif self.board.can_claim_threefold_repetition():
            result = "1/2-1/2"
            reason = "Threefold repetition"
        elif move_count >= self.max_moves:
            result = "1/2-1/2"
            reason = "Max moves reached"
        else:
            result = "1/2-1/2"
            reason = "Draw by agreement"
            
        self.pgn_game.headers["Result"] = result
        return result, reason
        
    def get_pgn(self) -> str:
        """Get PGN string of the game"""
        return str(self.pgn_game)


class Tournament:
    """Manages a tournament between engines"""
    
    def __init__(self, engines: List[Dict], time_control: Dict, games_per_pair: int = 2):
        """
        Initialize tournament
        
        Args:
            engines: List of engine configs, e.g.:
                [{"command": "python3 uci.py", "name": "Mergen v1", "options": {"Threads": "1"}}, ...]
            time_control: {"movetime": 1000} or {"depth": 4}
            games_per_pair: Number of games per pairing (switch colors)
        """
        self.engine_configs = engines
        self.time_control = time_control
        self.games_per_pair = games_per_pair
        self.results = {e["name"]: {"wins": 0, "losses": 0, "draws": 0, "games": []} 
                        for e in engines}
        
    def run(self):
        """Run the tournament"""
        print(f"\n{'='*70}")
        print(f"TOURNAMENT: {len(self.engine_configs)} engines, {self.games_per_pair} games per pair")
        print(f"Time Control: {self.time_control}")
        print(f"{'='*70}\n")
        
        total_games = len(self.engine_configs) * (len(self.engine_configs) - 1) * self.games_per_pair // 2
        game_num = 0
        
        # Round-robin tournament
        for i, engine1_config in enumerate(self.engine_configs):
            for engine2_config in self.engine_configs[i+1:]:
                
                for game_in_pair in range(self.games_per_pair):
                    game_num += 1
                    
                    # Alternate colors
                    if game_in_pair % 2 == 0:
                        white_config, black_config = engine1_config, engine2_config
                    else:
                        white_config, black_config = engine2_config, engine1_config
                        
                    print(f"\nGame {game_num}/{total_games}: {white_config['name']} (W) vs {black_config['name']} (B)")
                    
                    # Create engines
                    white_engine = UCIEngine(**white_config)
                    black_engine = UCIEngine(**black_config)
                    
                    try:
                        # Start engines
                        white_engine.start()
                        black_engine.start()
                        
                        # Play game
                        game = Game(white_engine, black_engine, self.time_control)
                        result, reason = game.play()
                        
                        print(f"  Result: {result} ({reason})")
                        
                        # Update results
                        if result == "1-0":
                            self.results[white_config["name"]]["wins"] += 1
                            self.results[black_config["name"]]["losses"] += 1
                        elif result == "0-1":
                            self.results[black_config["name"]]["wins"] += 1
                            self.results[white_config["name"]]["losses"] += 1
                        else:
                            self.results[white_config["name"]]["draws"] += 1
                            self.results[black_config["name"]]["draws"] += 1
                            
                        self.results[white_config["name"]]["games"].append({
                            "opponent": black_config["name"],
                            "color": "white",
                            "result": result,
                            "reason": reason,
                            "pgn": game.get_pgn()
                        })
                        self.results[black_config["name"]]["games"].append({
                            "opponent": white_config["name"],
                            "color": "black",
                            "result": result,
                            "reason": reason,
                            "pgn": game.get_pgn()
                        })
                        
                    finally:
                        # Stop engines
                        white_engine.stop()
                        black_engine.stop()
                        
        self._print_results()
        
    def _print_results(self):
        """Print tournament results"""
        print(f"\n{'='*70}")
        print("TOURNAMENT RESULTS")
        print(f"{'='*70}\n")
        
        # Calculate scores
        standings = []
        for name, results in self.results.items():
            wins = results["wins"]
            draws = results["draws"]
            losses = results["losses"]
            games = wins + draws + losses
            score = wins + 0.5 * draws
            win_rate = (wins / games * 100) if games > 0 else 0
            
            standings.append({
                "name": name,
                "score": score,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "games": games,
                "win_rate": win_rate
            })
            
        # Sort by score
        standings.sort(key=lambda x: x["score"], reverse=True)
        
        # Print table
        print(f"{'Rank':<6} {'Engine':<25} {'Score':<8} {'W-D-L':<12} {'Games':<7} {'Win%':<7}")
        print("-" * 70)
        
        for rank, standing in enumerate(standings, 1):
            wdl = f"{standing['wins']}-{standing['draws']}-{standing['losses']}"
            print(f"{rank:<6} {standing['name']:<25} {standing['score']:<8.1f} {wdl:<12} "
                  f"{standing['games']:<7} {standing['win_rate']:<7.1f}")
                  
        print(f"\n{'='*70}\n")
        
    def save_results(self, filename: str = "tournament_results.json"):
        """Save tournament results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description="Engine vs Engine Testing Framework")
    parser.add_argument("--engines", nargs="+", default=["python3 uci.py"],
                        help="Engine commands (default: python3 uci.py)")
    parser.add_argument("--names", nargs="+", default=None,
                        help="Engine names (default: generated from commands)")
    parser.add_argument("--depth", type=int, default=None,
                        help="Search depth (alternative to movetime)")
    parser.add_argument("--movetime", type=int, default=None,
                        help="Time per move in milliseconds")
    parser.add_argument("--games", type=int, default=2,
                        help="Games per pairing (default: 2)")
    parser.add_argument("--threads", type=int, default=1,
                        help="Number of threads per engine (default: 1)")
    parser.add_argument("--output", default="tournament_results.json",
                        help="Output file for results")
                        
    args = parser.parse_args()
    
    # Set default time control
    if args.depth is None and args.movetime is None:
        args.depth = 4  # Default depth
        
    time_control = {}
    if args.depth:
        time_control["depth"] = args.depth
    if args.movetime:
        time_control["movetime"] = args.movetime
        
    # Generate engine names if not provided
    if args.names is None:
        args.names = [f"Engine {i+1}" for i in range(len(args.engines))]
    elif len(args.names) != len(args.engines):
        print("Error: Number of names must match number of engines")
        return
        
    # Create engine configs
    engine_configs = []
    for command, name in zip(args.engines, args.names):
        engine_configs.append({
            "command": command,
            "name": name,
            "options": {"Threads": str(args.threads)}
        })
        
    # Run tournament
    tournament = Tournament(engine_configs, time_control, args.games)
    tournament.run()
    tournament.save_results(args.output)


if __name__ == "__main__":
    main()
