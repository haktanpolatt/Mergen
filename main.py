###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess
import time
from typing import Optional
from rich import print
from rich.console import Console
from Source.Mergen import Mergen
from Source.CheckGame import check_game_over
from Source.Search import find_best_move
from Source.Notation import save_game_log, save_game_pgn, list_saved_games
from Source.Board import print_board_rich
from Source.Time import print_status
from Source.Evaluation import evaluate_board
from Source.OpeningBook import OpeningBook
from Source.TimeManagement import TimeManager, TimeControl, detect_time_control
from Interface import (get_best_move_from_c, get_eval_from_c, get_search_info_from_c, 
                       find_best_move_timed_from_c, get_cpu_cores, 
                       find_best_move_parallel_from_c, find_best_move_parallel_timed_from_c)

console = Console()

def main():
    mergen = Mergen()
    white_time = 0.0
    black_time = 0.0
    
    # Option to load saved game
    print("[cyan]Load a saved game?[/cyan]")
    print("1. Start new game")
    print("2. Load from PGN file")
    print("3. View saved games")
    
    load_choice = input("Enter choice (1-3, default=1): ").strip()
    
    if load_choice == "2":
        filename = input("Enter PGN filename (in Records/): ").strip()
        from Source.Notation import load_game_pgn
        loaded_board = load_game_pgn(filename)
        if loaded_board:
            mergen.board = loaded_board
            print(f"[green]✓ Loaded game from {filename}[/green]")
        else:
            print("[yellow]Failed to load, starting new game[/yellow]")
    elif load_choice == "3":
        games = list_saved_games()
        if games:
            print(f"\n[cyan]Found {len(games)} saved game(s):[/cyan]")
            for i, game in enumerate(games[:10], 1):
                print(f"{i}. {game['filename']}: {game['white']} vs {game['black']} - {game['result']} ({game['date']})")
            print("\nStarting new game...")
        else:
            print("[yellow]No saved games found[/yellow]")
    
    # Load opening book
    opening_book = OpeningBook()
    use_opening_book = True
    
    # Multi-threading setup
    cpu_cores = get_cpu_cores()
    print(f"\n[cyan]Detected {cpu_cores} CPU cores[/cyan]")
    print("[cyan]Enable multi-threading?[/cyan]")
    print("1. Single-threaded (1 core) [recommended - multi-threading has a bug]")
    print("2. Multi-threaded (2 cores) [experimental]")
    print("3. Multi-threaded (4 cores) [experimental]")
    print(f"4. Multi-threaded (8 cores) [experimental]")
    print(f"[dim yellow]⚠️  Warning: Multi-threading currently has a performance bug at depth 4+[/dim yellow]")
    
    thread_choice = input("Enter choice (1-4, default=1): ").strip()
    
    use_multithreading = False
    num_threads = 1
    
    if thread_choice == "2":
        num_threads = min(2, cpu_cores)
        use_multithreading = True
        print(f"[yellow]Using {num_threads} threads (experimental - may be slow)[/yellow]")
    elif thread_choice == "3":
        num_threads = min(4, cpu_cores)
        use_multithreading = True
        print(f"[yellow]Using {num_threads} threads (experimental - may be slow)[/yellow]")
    elif thread_choice == "4":
        num_threads = min(8, cpu_cores)
        use_multithreading = True
        print(f"[yellow]Using {num_threads} threads (experimental - may be slow)[/yellow]")
    else:  # Default is 1 (single thread)
        print("[green]Single-threaded mode (recommended)[/green]")
    
    # Time management setup
    print("\n[cyan]Select time control:[/cyan]")
    print("1. Bullet (1 min)")
    print("2. Blitz (3 min + 2 sec)")
    print("3. Rapid (10 min + 5 sec)")
    print("4. Classical (30 min)")
    print("5. Infinite (no time limit)")
    print("6. Fixed depth (custom depth)")
    
    choice = input("Enter choice (1-6, default=6): ").strip()
    
    use_time_management = False
    time_manager: Optional[TimeManager] = None
    fixed_depth = 5
    
    if choice == "1":
        time_manager = TimeManager(60, 0, time_control=TimeControl.BULLET)
        use_time_management = True
        print("[green]Bullet mode: 1 minute[/green]")
    elif choice == "2":
        time_manager = TimeManager(180, 2, time_control=TimeControl.BLITZ)
        use_time_management = True
        print("[green]Blitz mode: 3 minutes + 2 seconds[/green]")
    elif choice == "3":
        time_manager = TimeManager(600, 5, time_control=TimeControl.RAPID)
        use_time_management = True
        print("[green]Rapid mode: 10 minutes + 5 seconds[/green]")
    elif choice == "4":
        time_manager = TimeManager(1800, 0, time_control=TimeControl.CLASSICAL)
        use_time_management = True
        print("[green]Classical mode: 30 minutes[/green]")
    elif choice == "5":
        print("[green]Infinite mode: no time limit, depth 8[/green]")
        fixed_depth = 8
    else:
        print("[yellow]⚠️  Note: Higher depths increase search time exponentially[/yellow]")
        print("   Depth 3: ~1 second")
        print("   Depth 4: ~5-10 seconds")
        print("   Depth 5: ~30-60 seconds or more")
        depth_input = input("Enter search depth (2-6, default=4): ").strip()
        
        try:
            fixed_depth = int(depth_input) if depth_input else 4
            fixed_depth = max(2, min(6, fixed_depth))  # Clamp between 2-6
        except ValueError:
            fixed_depth = 4
            
        print(f"[green]Fixed depth mode: searching to depth {fixed_depth}[/green]")

    print(f"[blue]Initial Board:[/blue]")
    board = mergen.board
    print_board_rich(board)
    
    if opening_book.get_statistics()['positions'] > 0:
        print(f"[green]Opening book loaded: {opening_book.get_statistics()['positions']} positions[/green]")
    
    if use_time_management and time_manager:
        print(f"[yellow]Mergen has {time_manager.format_time(time_manager.total_time)} remaining[/yellow]")

    while not board.is_game_over():
        # Check if player is in check at the start of their turn
        if board.is_check():
            print("[bold red]⚠️  You are in CHECK! You must move your king to safety or block the attack![/bold red]")
        
        try:
            start_time = time.time()
            human_move_str = input("Your move (in UCI format, e.g. e2e4 or e7e8q for promotion): ")
            
            # Handle promotion: if user enters 4 characters and it's a pawn reaching the last rank
            if len(human_move_str) == 4:
                from_square = chess.parse_square(human_move_str[:2])
                to_square = chess.parse_square(human_move_str[2:4])
                piece = board.piece_at(from_square)
                
                # Check if it's a pawn promotion move
                if piece and piece.piece_type == chess.PAWN:
                    to_rank = chess.square_rank(to_square)
                    if (piece.color == chess.WHITE and to_rank == 7) or (piece.color == chess.BLACK and to_rank == 0):
                        # Ask for promotion piece
                        promo = input("Promote to (q/r/b/n, default=q): ").strip().lower()
                        if promo not in ['q', 'r', 'b', 'n']:
                            promo = 'q'
                        human_move_str += promo
            
            human_move = chess.Move.from_uci(human_move_str)
            elapsed = time.time() - start_time
            white_time += elapsed
        except Exception as e:
            console.print(f"Illegal move, please try again. Error: {e}", style="bold red")
            continue
        
        if human_move in board.legal_moves:
            print(f"[bold green]You played: {human_move_str}[/bold green]")
            board.push(human_move)
            print_board_rich(board)

            score = get_eval_from_c(board.fen())
            white_score = max(score, 0)
            black_score = -min(score, 0)
            print_status(white_score, black_score, white_time, black_time)
            
            # Check if opponent is in check
            if board.is_check():
                print("[bold red]⚠️  CHECK! Mergen's king is under attack![/bold red]")
        else:
            console.print("Illegal move, please try again.", style="bold red")
            continue
        
        if check_game_over(board):
            break
        
        start_time = time.time()
        
        # Try opening book first
        book_move_uci = None
        if use_opening_book and opening_book.is_in_book(board):
            book_move_uci = opening_book.get_book_move(board)
            if book_move_uci:
                try:
                    mergen_move = chess.Move.from_uci(book_move_uci)
                    if mergen_move in board.legal_moves:
                        elapsed = time.time() - start_time
                        black_time += elapsed
                        print(f"[bold blue]Mergen played (from book): {mergen_move}[/bold blue] [dim](took {elapsed:.4f}s)[/dim]")
                        board.push(mergen_move)
                        print_board_rich(board)
                        
                        score = get_eval_from_c(board.fen())
                        white_score = max(score, 0)
                        black_score = -min(score, 0)
                        print_status(white_score, black_score, white_time, black_time)
                        
                        if check_game_over(board):
                            break
                        continue
                except:
                    pass
        
        # If not in book or book move failed, use engine
        if use_time_management and time_manager:
            # Type assertion for Pylance
            assert time_manager is not None
            
            # Calculate time allocation
            target_time, max_time = time_manager.get_time_for_move(board)
            
            if use_multithreading:
                print(f"[yellow]Mergen is thinking ({num_threads} threads)... (target: {time_manager.format_time(target_time)}, max: {time_manager.format_time(max_time)})[/yellow]")
                # Use parallel time-limited search
                move_uci, depth_reached, time_spent_ms = find_best_move_parallel_timed_from_c(board.fen(), max_time * 1000, num_threads)
            else:
                print(f"[yellow]Mergen is thinking... (target: {time_manager.format_time(target_time)}, max: {time_manager.format_time(max_time)})[/yellow]")
                # Use single-threaded time-limited search
                move_uci, depth_reached, time_spent_ms = find_best_move_timed_from_c(board.fen(), max_time * 1000)
            
            mergen_move = chess.Move.from_uci(move_uci)
            elapsed = time_spent_ms / 1000.0
            
            # Update time manager
            time_manager.update_time(elapsed)
            black_time += elapsed
            
            if use_multithreading:
                print(f"[dim]Depth: {depth_reached}, Time: {elapsed:.2f}s, Threads: {num_threads}[/dim]")
            else:
                print(f"[dim]Depth: {depth_reached}, Time: {elapsed:.2f}s[/dim]")
            print(f"[bold blue]Mergen played: {mergen_move}[/bold blue] [dim](remaining: {time_manager.format_time(time_manager.total_time)})[/dim]")
        else:
            # Fixed depth search
            if use_multithreading:
                print(f"[yellow]Mergen is thinking ({num_threads} threads)...[/yellow]")
                # Use parallel fixed-depth search
                move_uci = find_best_move_parallel_from_c(board.fen(), fixed_depth, num_threads)
                mergen_move = chess.Move.from_uci(move_uci)
                elapsed = time.time() - start_time
                black_time += elapsed
                
                # Get search information for display
                search_info = get_search_info_from_c(board.fen(), depth=fixed_depth)
                depth_str, eval_str, pv_move = search_info.split()
                
                print(f"[dim]Search depth: {depth_str}, Eval: {eval_str}, PV: {pv_move}, Threads: {num_threads}[/dim]")
                print(f"[bold blue]Mergen played: {mergen_move}[/bold blue] [dim](took {elapsed:.2f}s)[/dim]")
            else:
                print(f"[yellow]Mergen is thinking...[/yellow]")
                # Get search information (depth, eval, PV)
                search_info = get_search_info_from_c(board.fen(), depth=fixed_depth)
                depth_str, eval_str, pv_move = search_info.split()
                
                mergen_move = chess.Move.from_uci(get_best_move_from_c(board.fen(), depth=fixed_depth))
                elapsed = time.time() - start_time
                black_time += elapsed
                
                print(f"[dim]Search depth: {depth_str}, Eval: {eval_str}, PV: {pv_move}[/dim]")
                print(f"[bold blue]Mergen played: {mergen_move}[/bold blue] [dim](took {elapsed:.2f}s)[/dim]")
        
        board.push(mergen_move)
        print_board_rich(board)

        score = get_eval_from_c(board.fen())
        white_score = max(score, 0)
        black_score = -min(score, 0)
        print_status(white_score, black_score, white_time, black_time)
        
        # Check if player is in check
        if board.is_check():
            print("[bold red]⚠️  CHECK! Your king is under attack![/bold red]")

        if check_game_over(board):
            break

    # Save game in both formats
    save_game_log(board, maximizing_player=False, depth=fixed_depth if not use_time_management else 5)
    
    # Save in standard PGN format
    if use_time_management and time_manager:
        time_control_str = f"{int(time_manager.total_time)}s"
    else:
        time_control_str = "Infinite"
    
    pgn_file = save_game_pgn(
        board,
        white_player="Human",
        black_player="Mergen Chess Engine",
        event="Human vs Computer",
        site="Local",
        depth=fixed_depth if not use_time_management else 5,
        time_control=time_control_str
    )
    print(f"\n[green]✓ Game saved to {pgn_file}[/green]")

if __name__ == "__main__":
    main()