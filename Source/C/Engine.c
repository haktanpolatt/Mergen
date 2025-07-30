/*
###############################
#                             #
#   Created on June 2, 2025   #
#                             #
###############################
*/

// gcc -O3 -shared -o Engine.dll Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c Zobrist.c TT.c -Wno-stringop-overflow

#include <string.h>
#include "Board.h"
#include "MoveGen.h"
#include "Evaluate.h"
#include "Minimax.h"
#include "Move.h"
#include "Zobrist.h"
#include "TT.h"

// FIND BEST MOVE
// This function finds the best move for the given position in FEN format using the minimax algorithm.
// It returns the best move in standard algebraic notation.
const char* find_best_move_from_fen(const char* fen, int depth) {
    static char best_move[6];
    static int initialized = 0;

    if (!initialized) {
        init_zobrist();
        tt_init();
        initialized = 1;
    }

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

// EVALUATE BOARD
// This function evaluates the board position given in FEN format and returns a score.
float evaluate_fen(const char* fen) {
    Position pos;
    parse_fen(fen, &pos);
    return evaluate_board(&pos);
}



