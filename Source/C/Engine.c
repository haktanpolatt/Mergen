/*
###############################
#                             #
#   Created on June 2, 2025   #
#                             #
###############################
*/

// gcc -O3 -shared -o Engine.dll Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c Zobrist.c TT.c Ordering.c KillerMoves.c -Wno-stringop-overflow

#include <string.h>
#include <stdio.h>
#include "Board.h"
#include "MoveGen.h"
#include "Evaluate.h"
#include "Minimax.h"
#include "Move.h"
#include "Zobrist.h"
#include "TT.h"
#include "Ordering.h"

// FIND BEST MOVE WITH ITERATIVE DEEPENING
// This function finds the best move for the given position in FEN format using iterative deepening.
// Iterative deepening progressively searches deeper, improving move ordering and enabling time management.
// It returns the best move in standard algebraic notation.
const char* find_best_move_from_fen(const char* fen, int depth) {
    static char best_move[6];
    static char pv[6];  // Principal Variation (best move from previous iteration)
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

    // Initialize best move
    strcpy(best_move, moves[0]);

    // ITERATIVE DEEPENING: Search progressively from depth 1 to target depth
    // Benefits:
    // 1. Better move ordering (PV from previous iteration tried first)
    // 2. Enables time management (can stop early if time runs out)
    // 3. More efficient alpha-beta cutoffs
    for (int current_depth = 1; current_depth <= depth; current_depth++) {
        float best_score = is_white ? -10000.0f : 10000.0f;
        char current_best[6];
        strcpy(current_best, best_move);

        // Try PV move first if we have one from previous iteration
        if (current_depth > 1) {
            // Search PV move first for better alpha-beta cutoffs
            for (int i = 0; i < num_moves; i++) {
                if (strcmp(moves[i], pv) == 0 && i != 0) {
                    // Move PV to front
                    char temp[6];
                    strcpy(temp, moves[i]);
                    for (int j = i; j > 0; j--) {
                        strcpy(moves[j], moves[j-1]);
                    }
                    strcpy(moves[0], temp);
                    break;
                }
            }
        }

        for (int i = 0; i < num_moves; i++) {
            Position copy = pos;
            make_move(&copy, moves[i]);

            float score = minimax(&copy, current_depth - 1, -10000.0f, 10000.0f, !is_white);

            if ((is_white && score > best_score) || (!is_white && score < best_score)) {
                best_score = score;
                strcpy(current_best, moves[i]);
            }
        }

        // Update best move and PV for this depth
        strcpy(best_move, current_best);
        strcpy(pv, current_best);
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

// GET SEARCH INFO WITH PRINCIPAL VARIATION
// Returns detailed search information including evaluation at each depth
// Format: "depth score pv_move"
const char* get_search_info(const char* fen, int max_depth) {
    static char info[256];
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
    
    if (num_moves == 0) {
        strcpy(info, "0 0.0 none");
        return info;
    }

    char best_move[6];
    strcpy(best_move, moves[0]);
    float final_score = 0.0f;

    // Iterative deepening to find best move and score
    for (int depth = 1; depth <= max_depth; depth++) {
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
        
        final_score = best_score;
    }

    // Format: "depth score pv_move"
    snprintf(info, sizeof(info), "%d %.2f %s", max_depth, final_score, best_move);
    return info;
}



