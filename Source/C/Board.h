/*
###############################
#                             #
#   Created on June 3, 2025   #
#                             #
###############################
*/

#ifndef BOARD_H
#define BOARD_H

typedef struct {
    char type;      // p, n, b, r, q, k (minuscule)
    int is_white;   // 1 = white, 0 = black
} Piece;

typedef struct {
    Piece board[8][8];
    int white_to_move;
    int ep_rank;
    int ep_file;
    int white_king_side_castle;
    int white_queen_side_castle;
    int black_king_side_castle;
    int black_queen_side_castle;
    // Additional fields can be added here for more game state information
} Position;

void parse_fen(const char* fen, Position* pos);

#endif

