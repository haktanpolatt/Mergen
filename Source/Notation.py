###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess

def save_game_log(board, maximizing_player, depth):
    # game_date = date.today().strftime("%d %B %Y")
    mergen_color = "white" if maximizing_player else "black"
    # result = board.outcome().winner
    # result_str = "Mergen won" if result == (not maximizing_player) else "Human won" if result is not None else "Draw"

    moves = []
    board_copy = chess.Board()
    for i, move in enumerate(board.move_stack):
        if i % 2 == 0:
            moves.append(f"{(i // 2) + 1}. {board_copy.san(move)}")
        else:
            moves[-1] += f" {board_copy.san(move)}"
        board_copy.push(move)

    with open("games.md", "a") as f:
        f.write(f"- Mergen was **{mergen_color}**, depth = {depth}, with alpha-beta pruning\n")
        f.write("```pgn\n")
        f.write(" ".join(moves))
        f.write("\n```\n")