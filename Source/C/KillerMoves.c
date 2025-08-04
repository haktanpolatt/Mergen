/*
#################################
#                               #
#   Created on August 4, 2025   #
#                               #
#################################
*/

#include <string.h>
#include "KillerMoves.h"

char killer_moves[MAX_DEPTH][2][6] = {{{0}}};

void add_killer_move(int depth, const char* move) {
    if (depth < 0 || depth >= MAX_DEPTH) return;

    // Check if the move is already a killer move
    if (strcmp(killer_moves[depth][0], move) == 0) return;
    if (strcmp(killer_moves[depth][1], move) == 0) return;

    // Shift the new [1] move to [0] and the old [0] to [1]
    strcpy(killer_moves[depth][1], killer_moves[depth][0]);
    strcpy(killer_moves[depth][0], move);
}

// Check if a move is a killer move for the given depth
int is_killer_move(int depth, const char* move) {
    if (depth < 0 || depth >= MAX_DEPTH) return 0;
    return (strcmp(killer_moves[depth][0], move) == 0 ||
            strcmp(killer_moves[depth][1], move) == 0);
}
