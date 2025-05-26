###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

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