/*
################################
#                              #
#   Created on July 31, 2025   #
#                              #
################################
*/

#ifndef ORDERING_H
#define ORDERING_H

#include "Board.h"

// Sort moves using MVV-LVA (Most Valuable Victim - Least Valuable Attacker) heuristic
void sort_moves(Position* pos, char moves[][6], int num_moves, int depth);

// History Heuristic
extern int history_table[64][64];
void update_history(const char* move, int depth);

#endif
