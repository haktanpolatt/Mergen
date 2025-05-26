###############################
#                             #
#   Created on May 26, 2025   #
#                             #
###############################

import chess
from rich.console import Console
from rich.table import Table

unicode_pieces = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}

def print_board_rich(board):
    console = Console()
    table = Table(show_header=False, box=None, padding=(0, 0))

    files = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    table.add_row("", *files)

    for rank in range(8, 0, -1):
        row = [str(rank) + " "]
        for file in range(8):
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            if piece:
                symbol = unicode_pieces[piece.symbol()]
            else:
                symbol = " "

            if (file + rank) % 2 == 0:
                style = "on #eeeeee"
            else:
                style = "on #cccccc"

            row.append(f"[{style}]{symbol} [/{style}]")

        table.add_row(*row)

    console.print(table)
