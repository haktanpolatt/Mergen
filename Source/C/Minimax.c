/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#include <stdlib.h>
#include "Minimax.h"
#include "Evaluate.h"
#include "MoveGen.h"
#include "Move.h"
#include "Rules.h"

float minimax(Position* pos, int depth, float alpha, float beta, int maximizingPlayer) {
    if (depth == 0 || is_game_over(pos)) {
        return evaluate_board(pos);
    }

    char moves[256][6];
    int num_moves = generate_legal_moves(pos, maximizingPlayer, moves);

    if (maximizingPlayer) {
        float max_eval = -10000.0f;
        for (int i = 0; i < num_moves; i++) {
            Position* copy = malloc(sizeof(Position));
            *copy = *pos;

            make_move(copy, moves[i]);
            float eval = minimax(copy, depth - 1, alpha, beta, 0);
            free(copy);
            
            if (eval > max_eval) max_eval = eval;
            if (eval > alpha) alpha = eval;
            if (beta <= alpha) break;
        }
        return max_eval;
    } else {
        float min_eval = 10000.0f;
        for (int i = 0; i < num_moves; i++) {
            Position* copy = malloc(sizeof(Position));
            *copy = *pos;

            make_move(copy, moves[i]);
            float eval = minimax(copy, depth - 1, alpha, beta, 1);
            free(copy);

            if (eval < min_eval) min_eval = eval;
            if (eval < beta) beta = eval;
            if (beta <= alpha) break;
        }
        return min_eval;
    }
}
