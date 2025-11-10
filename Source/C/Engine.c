/*
###############################
#                             #
#   Created on June 2, 2025   #
#                             #
###############################
*/

// gcc -O3 -shared -o Engine.dll Engine.c Board.c MoveGen.c Evaluate.c Minimax.c Move.c Rules.c Zobrist.c TT.c Ordering.c KillerMoves.c ParallelSearch.c -Wno-stringop-overflow

#include <string.h>
#include <stdio.h>
#include <time.h>
#include "Board.h"
#include "MoveGen.h"
#include "Evaluate.h"
#include "Minimax.h"
#include "Move.h"
#include "Zobrist.h"
#include "TT.h"
#include "Ordering.h"
#include "ParallelSearch.h"

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

    // Check if there are any legal moves
    if (num_moves == 0) {
        // No legal moves - checkmate or stalemate
        strcpy(best_move, "0000");
        return best_move;
    }

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

// FIND BEST MOVE WITH TIME MANAGEMENT
// This function finds the best move with iterative deepening and time management.
// It will search as deep as possible within the given time limit.
// Returns: "move depth time_spent"
const char* find_best_move_timed(const char* fen, float max_time_ms) {
    static char result[64];
    static char best_move[6];
    static char pv[6];
    static int initialized = 0;

    if (!initialized) {
        init_zobrist();
        tt_init();
        initialized = 1;
    }

    clock_t start_time = clock();
    float max_time_clocks = (max_time_ms / 1000.0f) * CLOCKS_PER_SEC;

    Position pos = {0};
    parse_fen(fen, &pos);
    int is_white = pos.white_to_move;

    char moves[256][6];
    int num_moves = generate_legal_moves(&pos, is_white, moves);

    if (num_moves == 0) {
        // No legal moves - checkmate or stalemate
        snprintf(result, sizeof(result), "0000 0 0.0");
        return result;
    }

    // Initialize best move
    strcpy(best_move, moves[0]);
    int completed_depth = 0;

    // Iterative deepening with time control
    for (int current_depth = 1; current_depth <= 20; current_depth++) {
        // Check time before starting new depth
        clock_t current_time = clock();
        float elapsed = (float)(current_time - start_time);
        
        if (elapsed >= max_time_clocks * 0.9) {
            // 90% of time used, don't start new depth
            break;
        }

        float best_score = is_white ? -10000.0f : 10000.0f;
        char current_best[6];
        strcpy(current_best, best_move);

        // Try PV move first if we have one
        if (current_depth > 1) {
            for (int i = 0; i < num_moves; i++) {
                if (strcmp(moves[i], pv) == 0 && i != 0) {
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

        // Search all moves at this depth
        int moves_searched = 0;
        for (int i = 0; i < num_moves; i++) {
            // Check time during search
            current_time = clock();
            elapsed = (float)(current_time - start_time);
            if (elapsed >= max_time_clocks) {
                break;  // Time's up
            }

            Position copy = pos;
            make_move(&copy, moves[i]);

            float score = minimax(&copy, current_depth - 1, -10000.0f, 10000.0f, !is_white);

            if ((is_white && score > best_score) || (!is_white && score < best_score)) {
                best_score = score;
                strcpy(current_best, moves[i]);
            }

            moves_searched++;
        }

        // Only update if we completed the depth
        if (moves_searched == num_moves) {
            strcpy(best_move, current_best);
            strcpy(pv, current_best);
            completed_depth = current_depth;
        } else {
            // Didn't finish this depth, use previous result
            break;
        }
    }

    clock_t end_time = clock();
    float time_spent = ((float)(end_time - start_time) / CLOCKS_PER_SEC) * 1000.0f;

    // Format: "move depth time_spent_ms"
    snprintf(result, sizeof(result), "%s %d %.1f", best_move, completed_depth, time_spent);
    return result;
}

// GET CPU CORE COUNT
// Returns the number of available CPU cores
int get_cpu_cores(void) {
    return get_cpu_core_count();
}

// FIND BEST MOVE WITH PARALLEL SEARCH
// Uses multiple threads to speed up search
const char* find_best_move_parallel_from_fen(const char* fen, int depth, int num_threads) {
    return find_best_move_parallel(fen, depth, num_threads);
}

// FIND BEST MOVE WITH PARALLEL SEARCH AND TIME LIMIT
// Uses multiple threads with time management
const char* find_best_move_parallel_timed_from_fen(const char* fen, float max_time_ms, int num_threads) {
    return find_best_move_parallel_timed(fen, max_time_ms, num_threads);
}





