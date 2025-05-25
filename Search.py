###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

from Evaluation import evaluate_board

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player == True:
        max_eval = float('-inf')

        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth -1, alpha, beta, not maximizing_player)
            board.pop()
            max_eval = max(max_eval, score)
            alpha = max(alpha, max_eval)
            
            if beta <= alpha:
                break

        return max_eval
    
    else:
        min_eval = float('inf')

        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, not maximizing_player)
            board.pop()
            min_eval = min(min_eval, score)
            beta = min(beta, min_eval)

            if beta <= alpha:
                break

        return min_eval

def find_best_move(board, depth, maximizing_player):
    if maximizing_player == True:
        best_score = float('-inf')
    else:
        best_score = float('inf')
    best_move = None

    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, float('-inf'), float('inf'), not maximizing_player)
        board.pop()

        if maximizing_player == True and score > best_score:
            best_score = score
            best_move = move
        elif maximizing_player == False and score < best_score:
            best_score = score
            best_move = move

    return best_move