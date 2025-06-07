/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#include <stdlib.h>
#include "Move.h"

void make_move(Position* pos, const char* move) {
    int from_file = move[0] - 'a';
    int from_rank = '8' - move[1];
    int to_file   = move[2] - 'a';
    int to_rank   = '8' - move[3];

    Piece (*board)[8] = pos->board;
    Piece moving = board[from_rank][from_file];
    Piece captured = board[to_rank][to_file];

    // En passant yakalama
    if (moving.type == 'p' && to_file != from_file && captured.type == 0) {
        int cap_rank = moving.is_white ? to_rank + 1 : to_rank - 1;
        board[cap_rank][to_file] = (Piece){0};
    }

    // Rok hakkı güncellemesi (şah ya da kale oynadıysa)
    if (moving.type == 'k') {
        if (moving.is_white) {
            pos->white_king_side_castle = 0;
            pos->white_queen_side_castle = 0;
        } else {
            pos->black_king_side_castle = 0;
            pos->black_queen_side_castle = 0;
        }
    }

    if (moving.type == 'r') {
        if (moving.is_white) {
            if (from_rank == 7 && from_file == 0)
                pos->white_queen_side_castle = 0;
            else if (from_rank == 7 && from_file == 7)
                pos->white_king_side_castle = 0;
        } else {
            if (from_rank == 0 && from_file == 0)
                pos->black_queen_side_castle = 0;
            else if (from_rank == 0 && from_file == 7)
                pos->black_king_side_castle = 0;
        }
    }

    // Eğer bir kale yakalandıysa rok hakkını sıfırla
    if (captured.type == 'r') {
        if (captured.is_white) {
            if (to_rank == 7 && to_file == 0)
                pos->white_queen_side_castle = 0;
            else if (to_rank == 7 && to_file == 7)
                pos->white_king_side_castle = 0;
        } else {
            if (to_rank == 0 && to_file == 0)
                pos->black_queen_side_castle = 0;
            else if (to_rank == 0 && to_file == 7)
                pos->black_king_side_castle = 0;
        }
    }

    // Rok (castling)
    if (moving.type == 'k' && abs(to_file - from_file) == 2) {
        if (moving.is_white) {
            if (to_file == 6) {  // e1g1 küçük rok
                board[7][5] = board[7][7];  // h1 -> f1
                board[7][7] = (Piece){0};
            } else if (to_file == 2) {  // e1c1 büyük rok
                board[7][3] = board[7][0];  // a1 -> d1
                board[7][0] = (Piece){0};
            }
        } else {
            if (to_file == 6) {  // e8g8 küçük rok
                board[0][5] = board[0][7];  // h8 -> f8
                board[0][7] = (Piece){0};
            } else if (to_file == 2) {  // e8c8 büyük rok
                board[0][3] = board[0][0];  // a8 -> d8
                board[0][0] = (Piece){0};
            }
        }
    }

    // Taşı hedef kareye taşı
    board[to_rank][to_file] = moving;
    board[from_rank][from_file] = (Piece){0};

    // Piyon terfisi (şimdilik hep vezir)
    if (moving.type == 'p' && (to_rank == 0 || to_rank == 7)) {
        moving.type = 'q';  // Her zaman vezire terfi
    }

    // En passant hedefini ayarla (piyon 2 kare ilerlediyse)
    if (moving.type == 'p' && abs(to_rank - from_rank) == 2) {
        pos->ep_rank = (from_rank + to_rank) / 2;
        pos->ep_file = from_file;
    } else {
        pos->ep_rank = -1;
        pos->ep_file = -1;
    }

    // Sıra değiştir
    pos->white_to_move = !pos->white_to_move;
}

void undo_move(Position* pos, const MoveInfo* info) {
    Piece (*board)[8] = pos->board;

    // Taşları geri taşı
    board[info->from_rank][info->from_file] = info->moved;
    board[info->to_rank][info->to_file] = info->captured;

    // Önceki rok/en passant/sıra bilgilerini geri yükle
    pos->ep_rank = info->prev_ep_rank;
    pos->ep_file = info->prev_ep_file;
    pos->white_to_move = info->prev_white_to_move;

    pos->white_king_side_castle = info->prev_white_king_side_castle;
    pos->white_queen_side_castle = info->prev_white_queen_side_castle;
    pos->black_king_side_castle = info->prev_black_king_side_castle;
    pos->black_queen_side_castle = info->prev_black_queen_side_castle;
}
