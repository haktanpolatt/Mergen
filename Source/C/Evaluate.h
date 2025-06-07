/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#ifndef EVALUATE_H
#define EVALUATE_H

#include "Board.h"

float evaluate_material(Position* pos);
float evaluate_pawn_structure(Position* pos);
float evaluate_center_control(Position* pos);
float evaluate_development(Position* pos);
float evaluate_king_safety(Position* pos);
float evaluate_rook_activity(Position* pos);

float evaluate_board(Position* pos);

#endif
