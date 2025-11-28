/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#ifndef MINIMAX_H
#define MINIMAX_H

#include "Board.h"

float minimax(Position* pos, int depth, float alpha, float beta, int maximizingPlayer);
void minimax_set_time_limit(double start_ms, double limit_ms);
void minimax_clear_time_limit(void);

#endif
