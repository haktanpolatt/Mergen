###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess
from Source.Constants import values, phase_values, POSITION_WEIGHT
from Source.PST import pawn_table, knight_table, bishop_table, rook_table, queen_table, king_table_opening, king_table_endgame

def evaluate_board(board):
    material_score = 0
    position_score = 0
    phase_score = 0

    pieces = board.piece_map()
    for square, piece in pieces.items():
        symbol = piece.symbol()
        s = symbol.lower()

        if symbol in values:
            material_score += values[symbol]
        
        if s in phase_values:
            phase_score += phase_values[s]

        if s == 'p':
            if piece.color == chess.WHITE:
                pst_score = pawn_table[square]
            else:
                pst_score = -pawn_table[chess.square_mirror(square)]
            position_score += pst_score
        elif s == 'n':
            if piece.color == chess.WHITE:
                pst_score = knight_table[square]
            else:
                pst_score = -knight_table[chess.square_mirror(square)]
            position_score += pst_score
        elif s == 'b':
            if piece.color == chess.WHITE:
                pst_score = bishop_table[square]
            else:
                pst_score = -bishop_table[chess.square_mirror(square)]
            position_score += pst_score
        elif s == 'r':
            if piece.color == chess.WHITE:
                pst_score = rook_table[square]
            else:
                pst_score = -rook_table[chess.square_mirror(square)]
            position_score += pst_score
        elif s == 'q':
            if piece.color == chess.WHITE:
                pst_score = queen_table[square]
            else:
                pst_score = -queen_table[chess.square_mirror(square)]
            position_score += pst_score
        elif s == 'k':
            if phase_score <= 14:
                table = king_table_endgame
            else:
                table = king_table_opening

            if piece.color == chess.WHITE:
                pst_score = table[square]
            else:
                pst_score = -table[chess.square_mirror(square)]

            position_score += pst_score

    return material_score + POSITION_WEIGHT * position_score