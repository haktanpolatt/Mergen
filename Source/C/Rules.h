/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#ifndef RULES_H
#define RULES_H

#include "Board.h"

int is_checkmate(Position* pos);
int is_stalemate(Position* pos);
int is_game_over(Position* pos);

int is_in_check(Position* pos, int is_white);

int find_king_rank(Position* pos, int is_white);
int find_king_file(Position* pos, int is_white);

int can_castle_kingside(Position* pos, int is_white);
int can_castle_queenside(Position* pos, int is_white);

int is_square_attacked(Position* pos, int rank, int file, int by_white);

#endif
