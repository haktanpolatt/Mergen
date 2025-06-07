/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#include <string.h>
#include "Rules.h"
#include "MoveGen.h"
#include "Rules.h"

int is_checkmate(Position* pos) {
    char moves[256][6];
    int num_moves = generate_legal_moves(pos, pos->white_to_move, moves);
    return num_moves == 0 && is_in_check(pos, pos->white_to_move);
}

int is_stalemate(Position* pos) {
    char moves[256][6];
    int num_moves = generate_legal_moves(pos, pos->white_to_move, moves);
    return num_moves == 0 && !is_in_check(pos, pos->white_to_move);
}

int is_game_over(Position* pos) {
    return is_checkmate(pos) || is_stalemate(pos);
}

int is_in_check(Position* pos, int is_white) {
    Piece (*board)[8] = pos->board;
    int king_rank = -1, king_file = -1;

    // Şahın yerini bul
    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type == 'k' && p.is_white == is_white) {
                king_rank = rank;
                king_file = file;
                break;
            }
        }
    }

    if (king_rank == -1) return 0;  // şah yoksa tehditte değil

    char temp_moves[256][6];
    int count = generate_pseudo_legal_moves(pos, !is_white, temp_moves);

    for (int i = 0; i < count; i++) {
        int to_rank = '8' - temp_moves[i][3];
        int to_file = temp_moves[i][2] - 'a';
        if (to_rank == king_rank && to_file == king_file) {
            return 1;  // şah tehdit altında
        }
    }

    return 0;
}

int find_king_rank(Position* pos, int is_white) {
    for (int r = 0; r < 8; r++)
        for (int f = 0; f < 8; f++)
            if (pos->board[r][f].type == 'k' && pos->board[r][f].is_white == is_white)
                return r;
    return -1;
}

int find_king_file(Position* pos, int is_white) {
    for (int r = 0; r < 8; r++)
        for (int f = 0; f < 8; f++)
            if (pos->board[r][f].type == 'k' && pos->board[r][f].is_white == is_white)
                return f;
    return -1;
}

// Şah ve kale oynamamış olmalı, aradaki kareler boş olmalı
int can_castle_kingside(Position* pos, int is_white) {
    int rank = pos->white_to_move ? 7 : 0;

    // Kale ve şah yerinde mi?
    Piece king = pos->board[rank][4];
    Piece rook = pos->board[rank][7];
    if (king.type != 'k' || king.is_white != pos->white_to_move) return 0;
    if (rook.type != 'r' || rook.is_white != pos->white_to_move) return 0;

    // Aradaki kareler boş mu? (f ve g)
    if (pos->board[rank][5].type != 0 || pos->board[rank][6].type != 0) return 0;

    // Rok hakkı var mı?
    if (pos->white_to_move && !pos->white_king_side_castle) return 0;
    if (!pos->white_to_move && !pos->black_king_side_castle) return 0;

    return 1;
}

int can_castle_queenside(Position* pos, int is_white) {
    int rank = pos->white_to_move ? 7 : 0;

    Piece king = pos->board[rank][4];
    Piece rook = pos->board[rank][0];
    if (king.type != 'k' || king.is_white != pos->white_to_move) return 0;
    if (rook.type != 'r' || rook.is_white != pos->white_to_move) return 0;

    // Aradaki kareler boş mu? (b, c, d) → 1, 2, 3
    if (pos->board[rank][1].type != 0) return 0;
    if (pos->board[rank][2].type != 0) return 0;
    if (pos->board[rank][3].type != 0) return 0;

    // Rok hakkı var mı?
    if (pos->white_to_move && !pos->white_queen_side_castle) return 0;
    if (!pos->white_to_move && !pos->black_queen_side_castle) return 0;

    return 1;
}

int is_square_attacked(Position* pos, int rank, int file, int by_white) {
    Piece (*board)[8] = pos->board;
    char moves[256][6];
    int num_moves = generate_legal_moves(pos, by_white, moves);

    for (int i = 0; i < num_moves; i++) {
        int to_rank = '8' - moves[i][3];
        int to_file = moves[i][2] - 'a';

        if (to_rank == rank && to_file == file)
            return 1;
    }

    return 0;
}
