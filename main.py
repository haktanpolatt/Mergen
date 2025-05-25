###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess
from Mergen import Mergen
from CheckGame import check_game_over
from Search import find_best_move
from Notation import save_game_log

def main():
    mergen = Mergen()

    print("Initial Board:")
    mergen.print_board()

    board = mergen.board

    while not board.is_game_over():
        try:
            human_move_str = input("Your move (in UCI format, e.g. e2e4): ")
            human_move = chess.Move.from_uci(human_move_str)
        except:
            print("Illegal move, please try again.")
            continue
        
        if human_move in board.legal_moves:
            board.push(human_move)
            mergen.print_board()
        else:
            print("Illegal move, please try again.")
            continue
        
        if check_game_over(board):
            break

        mergen_move = find_best_move(board, depth = 5, maximizing_player=False)
        print(mergen_move)
        board.push(mergen_move)
        mergen.print_board()

        if check_game_over(board):
            break

    save_game_log(board, maximizing_player=False, depth=5)

if __name__ == "__main__":
    main()