###############################
#                             #
#   Created on May 23, 2025   #
#                             #
###############################

import chess

class Mergen:
    def __init__(self):
        self.board = chess.Board()

    def get_legal_moves(self):
        return list(self.board.legal_moves)
    
    def make_move(self, move_uci):
        move = chess.Move.from_uci(move_uci)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False
    
    def undo_move(self):
        if self.board.move_stack:
            self.board.pop()

    def print_board(self):
        print(self.board)

if __name__ == "__main__":
    mergen = Mergen()

    print("Initial Board:")
    mergen.print_board()

    print("\nLegal Moves:")
    print([move.uci() for move in mergen.get_legal_moves()])

    print("\nMaking a move: e2e4")
    if mergen.make_move("e2e4"):
        print("Move made successfully.")
        mergen.print_board()
    else:
        print("Invalid move.")
    
    print("\nUndoing the move.")
    mergen.undo_move()
    mergen.print_board()
