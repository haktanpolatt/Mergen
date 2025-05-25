###############################
#                             #
#   Created on May 23, 2025   #
#                             #
###############################

import chess
from datetime import date
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
