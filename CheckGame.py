###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

def check_game_over(board):
    if board.is_checkmate():
        print("Checkmate! Game over.")
        return True
    elif board.is_stalemate():
        print("Game drawn by stalemate.")
        return True
    elif board.is_insufficient_material():
        print("Game drawn due to insufficient material.")
        return True
    elif board.is_seventyfive_moves():
        print("Draw by 75-move rule.")
        return True
    elif board.is_fivefold_repetition():
        print("Draw by repetition.")
        return True
    return False