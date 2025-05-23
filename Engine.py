###############################
#                             #
#   Created on May 23, 2025   #
#                             #
###############################

import chess

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
    
depth = 3
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



# def find_best_move():
    