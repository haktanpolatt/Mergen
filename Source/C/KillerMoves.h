/*
#################################
#                               #
#   Created on August 4, 2025   #
#                               #
#################################
*/

#ifndef KILLER_MOVES_H
#define KILLER_MOVES_H

#define MAX_DEPTH 64

// Killer moves table
extern char killer_moves[MAX_DEPTH][2][6];

void add_killer_move(int depth, const char* move);
int is_killer_move(int depth, const char* move);

#endif
