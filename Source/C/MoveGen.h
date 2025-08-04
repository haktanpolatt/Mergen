/*
###############################
#                             #
#   Created on June 3, 2025   #
#                             #
###############################
*/

#ifndef MOVEGEN_H
#define MOVEGEN_H

#include "Board.h"

int generate_pawn_moves(Position* pos, int rank, int file, char moves[][6], int move_index);
int generate_knight_moves(Position* pos, int rank, int file, char moves[][6], int move_index);
int generate_bishop_moves(Position* pos, int rank, int file, char moves[][6], int move_index);
int generate_rook_moves(Position* pos, int rank, int file, char moves[][6], int move_index);
int generate_queen_moves(Position* pos, int rank, int file, char moves[][6], int move_index);
int generate_king_moves(Position* pos, int rank, int file, char moves[][6], int move_index);

int generate_pseudo_legal_moves(Position* pos, int is_white, char moves[][6]);
int generate_legal_moves(Position* pos, int is_white, char moves[][6]);

int generate_capture_moves(Position* pos, int is_white, char moves[][6]);

#endif
