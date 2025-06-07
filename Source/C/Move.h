/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#ifndef MOVE_H
#define MOVE_H

#include "Board.h"

typedef struct {
    int from_rank, from_file;
    int to_rank, to_file;
    Piece moved;
    Piece captured;
    int prev_ep_rank, prev_ep_file;
    int prev_white_to_move;

    // Rok hakları
    int prev_white_king_side_castle;
    int prev_white_queen_side_castle;
    int prev_black_king_side_castle;
    int prev_black_queen_side_castle;
} MoveInfo;

void make_move(Position* pos, const char* move);
void undo_move(Position* pos, const MoveInfo* info);

#endif

