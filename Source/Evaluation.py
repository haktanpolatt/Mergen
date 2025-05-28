###############################
#                             #
#   Created on May 25, 2025   #
#                             #
###############################

import chess
from collections import defaultdict
from Source.Constants import values, phase_values, POSITION_WEIGHT, MOBILITY_WEIGHT
from Source.PST import pawn_table, knight_table, bishop_table, rook_table, queen_table, king_table_opening, king_table_endgame

def is_isolated_pawn(square, board):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    piece = board.piece_at(square)
    if not piece or piece.symbol().lower() != 'p':
        return False 

    is_white = piece.color == chess.WHITE
    own_pawn = 'P' if is_white else 'p'

    for df in [-1, 1]:
        neighbor_file = file + df
        if 0 <= neighbor_file <= 7:
            for r in range(8):
                neighbor_square = chess.square(neighbor_file, r)
                neighbor_piece = board.piece_at(neighbor_square)
                if neighbor_piece and neighbor_piece.symbol() == own_pawn:
                    return False

    return True

def evaluate_pawn_structure(board):
    total_pawn_score = 0
    white_files = defaultdict(int)
    black_files = defaultdict(int)
    
    for square, piece in board.piece_map().items():
        if piece.symbol().lower() != 'p':
            continue

        is_white = piece.color == chess.WHITE
        forward = 8 if is_white else -8
        left_diag = 7 if is_white else -9
        right_diag = 9 if is_white else -7
        opponent_pawn = 'p' if is_white else 'P'

        passed = True
        for offset in [forward, left_diag, right_diag]:
            target = square + offset
            if 0 <= target < 64:
                target_piece = board.piece_at(target)
                if target_piece and target_piece.symbol() == opponent_pawn:
                    passed = False
                    break

        if passed:
            total_pawn_score += 0.3

        if is_isolated_pawn(square, board):
            total_pawn_score -= 0.2

        file = chess.square_file(square)
        if is_white:
            white_files[file] += 1
        else:
            black_files[file] += 1

    for file in white_files:
        if white_files[file] > 1:
            total_pawn_score -= 0.1 * (white_files[file] - 1)
    for file in black_files:
        if black_files[file] > 1:
            total_pawn_score += 0.1 * (black_files[file] - 1)

    return total_pawn_score

def evaluate_mobility(board):
    white_moves = len(list(board.legal_moves))
    board.push(chess.Move.null())
    black_moves = len(list(board.legal_moves))
    board.pop()

    return white_moves - black_moves

def evaluate_board(board):
    material_score = 0
    position_score = 0
    phase_score = 0
    mobility_score = evaluate_mobility(board)
    pawn_structure_score = evaluate_pawn_structure(board)

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

    return material_score + POSITION_WEIGHT * position_score + MOBILITY_WEIGHT * mobility_score + pawn_structure_score