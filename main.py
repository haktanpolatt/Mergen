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
from Source.Interface import get_best_move_from_c

console = Console()

def main():
    mergen = Mergen()
    white_time = 0.0
    black_time = 0.0

    print(f"[blue]Initial Board:[/blue]")
    board = mergen.board
    print_board_rich(board)

    while not board.is_game_over():
        try:
            start_time = time.time()
            human_move_str = input("Your move (in UCI format, e.g. e2e4): ")
            human_move = chess.Move.from_uci(human_move_str)
            elapsed = time.time() - start_time
            white_time += elapsed
        except:
            console.print("Illegal move, please try again.", style="bold red")
            continue
        
        if human_move in board.legal_moves:
            print(f"[bold green]You played: {human_move_str}[/bold green]")
            board.push(human_move)
            print_board_rich(board)

            score = evaluate_board(board)
            white_score = max(score, 0)
            black_score = -min(score, 0)
            print_status(white_score, black_score, white_time, black_time)
        else:
            console.print("Illegal move, please try again.", style="bold red")
            continue
        
        if check_game_over(board):
            break
        
        start_time = time.time()
        mergen_move = chess.Move.from_uci(get_best_move_from_c(board.fen(), depth=5))
        elapsed = time.time() - start_time
        black_time += elapsed
        
        print(f"[bold blue]Mergen played: {mergen_move}[/bold blue]")
        board.push(mergen_move)
        print_board_rich(board)

        score = evaluate_board(board)
        white_score = max(score, 0)
        black_score = -min(score, 0)
        print_status(white_score, black_score, white_time, black_time)

        if check_game_over(board):
            break

    save_game_log(board, maximizing_player=False, depth=5)

if __name__ == "__main__":
    main()