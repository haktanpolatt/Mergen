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

// Countermove Heuristic
extern char countermove_table[64][64][6];
void update_countermove(const char* previous_move, const char* response_move);
const char* get_countermove(const char* previous_move);

#endif
