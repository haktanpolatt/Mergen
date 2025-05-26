###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

from rich import print

def check_game_over(board):
    if board.is_checkmate():
        print("[bold red]Checkmate! Game over.[/bold red]")
        return True
    elif board.is_stalemate():
        print("[yellow]Game drawn by stalemate.[/yellow]")
        return True
    elif board.is_insufficient_material():
        print("[blue]Game drawn due to insufficient material.[/blue]")
        return True
    elif board.is_seventyfive_moves():
        print("[magenta]Draw by 75-move rule.[/magenta]")
        return True
    elif board.is_fivefold_repetition():
        print("[cyan]Draw by repetition.[/cyan]")
        return True
    return False