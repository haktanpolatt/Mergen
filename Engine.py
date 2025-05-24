###############################
#                             #
#   Created on May 23, 2025   #
#                             #
###############################

import chess
from Mergen import Mergen

def evaluate_board(board):
    score = 0
    values = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':10, 
              'p':-1, 'n':-3, 'b':-3, 'r':-5, 'q':-10}
    
    pieces = board.piece_map()
    for square, piece in pieces.items():
        symbol = piece.symbol()
        if symbol in values:
            score += values[symbol]

    return score
    
def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player == True:
        max_eval = float('-inf')

        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth -1, not maximizing_player)
            board.pop()
            max_eval = max(max_eval, score)

        return max_eval
    
    else:
        min_eval = float('inf')

        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, not maximizing_player)
            board.pop()
            min_eval = min(min_eval, score)

        return min_eval

def find_best_move(board, depth, maximizing_player):
    if maximizing_player == True:
        best_score = float('-inf')
    else:
        best_score = float('inf')
    best_move = None

    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, not maximizing_player)
        board.pop()

        if maximizing_player == True and score > best_score:
            best_score = score
            best_move = move
        elif maximizing_player == False and score < best_score:
            best_score = score
            best_move = move

    return best_move

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

if __name__ == "__main__":
    main()
