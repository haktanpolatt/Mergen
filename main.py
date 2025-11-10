###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess
import time
from rich import print
from rich.console import Console
from Source.Mergen import Mergen
from Source.CheckGame import check_game_over
from Source.Search import find_best_move
from Source.Notation import save_game_log
from Source.Board import print_board_rich
from Source.Time import print_status
from Source.Evaluation import evaluate_board
from Source.OpeningBook import OpeningBook
from Source.TimeManagement import TimeManager, TimeControl, detect_time_control
from Interface import get_best_move_from_c, get_eval_from_c, get_search_info_from_c, find_best_move_timed_from_c

console = Console()

def main():
    mergen = Mergen()
    white_time = 0.0
    black_time = 0.0
    
    # Load opening book
    opening_book = OpeningBook()
    use_opening_book = True
    
    # Time management setup
    print("[cyan]Select time control:[/cyan]")
    print("1. Bullet (1 min)")
    print("2. Blitz (3 min + 2 sec)")
    print("3. Rapid (10 min + 5 sec)")
    print("4. Classical (30 min)")
    print("5. Infinite (no time limit)")
    print("6. Fixed depth (search to depth 5)")
    
    choice = input("Enter choice (1-6, default=6): ").strip()
    
    use_time_management = False
    time_manager = None
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
        print("[green]Fixed depth mode: searching to depth 5[/green]")

    print(f"[blue]Initial Board:[/blue]")
    board = mergen.board
    print_board_rich(board)
    
    if opening_book.get_statistics()['positions'] > 0:
        print(f"[green]Opening book loaded: {opening_book.get_statistics()['positions']} positions[/green]")
    
    if use_time_management:
        print(f"[yellow]Mergen has {time_manager.format_time(time_manager.total_time)} remaining[/yellow]")

    while not board.is_game_over():
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
        if use_time_management:
            # Calculate time allocation
            target_time, max_time = time_manager.get_time_for_move(board)
            print(f"[yellow]Mergen is thinking... (target: {time_manager.format_time(target_time)}, max: {time_manager.format_time(max_time)})[/yellow]")
            
            # Use time-limited search
            move_uci, depth_reached, time_spent_ms = find_best_move_timed_from_c(board.fen(), max_time * 1000)
            mergen_move = chess.Move.from_uci(move_uci)
            elapsed = time_spent_ms / 1000.0
            
            # Update time manager
            time_manager.update_time(elapsed)
            black_time += elapsed
            
            print(f"[dim]Depth: {depth_reached}, Time: {elapsed:.2f}s[/dim]")
            print(f"[bold blue]Mergen played: {mergen_move}[/bold blue] [dim](remaining: {time_manager.format_time(time_manager.total_time)})[/dim]")
        else:
            # Fixed depth search
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

        if check_game_over(board):
            break

    save_game_log(board, maximizing_player=False, depth=5)

if __name__ == "__main__":
    main()