/*
###############################
#                             #
#   Created on June 2, 2025   #
#                             #
###############################
*/

// gcc -O3 -shared -o Engine.dll Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c -Wno-stringop-overflow

#include <string.h>
#include "Board.h"
#include "MoveGen.h"
#include "Evaluate.h"
#include "Minimax.h"
#include "Move.h"

// FIND BEST MOVE
const char* find_best_move_from_fen(const char* fen, int depth) {
    static char best_move[6];

    Position pos = {0};
    parse_fen(fen, &pos);

    int is_white = pos.white_to_move;

    char moves[256][6];
    int num_moves = generate_legal_moves(&pos, is_white, moves);

    float best_score = is_white ? -10000.0f : 10000.0f;

    for (int i = 0; i < num_moves; i++) {
        Position copy = pos;
        make_move(&copy, moves[i]);

        float score = minimax(&copy, depth - 1, -10000.0f, 10000.0f, !is_white);

        if ((is_white && score > best_score) || (!is_white && score < best_score)) {
            best_score = score;
            strcpy(best_move, moves[i]);
        }
    }

    return best_move;
}



