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
#ifdef _WIN32
#include <windows.h>
#endif
#include "Board.h"
#include "MoveGen.h"
#include "Evaluate.h"
#include "Minimax.h"
#include "Move.h"
#include "Zobrist.h"
#include "TT.h"
#include "Ordering.h"
#include "ParallelSearch.h"

// Allow external callers (e.g., UCI setoption) to adjust transposition table size in MB.
// Caps are enforced in TT.c to avoid runaway allocations.
void set_hash_size(int megabytes) {
    tt_resize(megabytes);
}

// Simple cross-platform monotonic timer in milliseconds
static double now_ms(void) {
#ifdef _WIN32
    LARGE_INTEGER freq, counter;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart * 1000.0 / (double)freq.QuadPart;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1e6;
#endif
}

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

    // ITERATIVE DEEPENING with ASPIRATION WINDOWS
    // Benefits:
    // 1. Better move ordering (PV from previous iteration tried first)
    // 2. Enables time management (can stop early if time runs out)
    // 3. Aspiration windows: narrow alpha-beta bounds for faster search
    float prev_score = 0.0f;
    
    for (int current_depth = 1; current_depth <= depth; current_depth++) {
        float best_score = is_white ? -10000.0f : 10000.0f;
        char current_best[6];
        strcpy(current_best, best_move);

        // ASPIRATION WINDOWS: Use narrow window for depth >= 3
        float alpha = -10000.0f;
        float beta = 10000.0f;
        float window = 50.0f; // Initial window size
        
        if (current_depth >= 3) {
            alpha = prev_score - window;
            beta = prev_score + window;
        }

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

        // Search with aspiration window
        int needs_research = 0;
        for (int i = 0; i < num_moves; i++) {
            Position copy = pos;
            make_move(&copy, moves[i]);

            float score = minimax(&copy, current_depth - 1, alpha, beta, !is_white);

            if ((is_white && score > best_score) || (!is_white && score < best_score)) {
                best_score = score;
                strcpy(current_best, moves[i]);
            }
            
            // Check if we failed outside the aspiration window
            if (current_depth >= 3) {
                if ((is_white && score <= alpha) || (is_white && score >= beta)) {
                    needs_research = 1;
                    break;
                }
                if ((!is_white && score >= beta) || (!is_white && score <= alpha)) {
                    needs_research = 1;
                    break;
                }
            }
        }

        // If aspiration window failed, re-search with full window
        if (needs_research) {
            best_score = is_white ? -10000.0f : 10000.0f;
            alpha = -10000.0f;
            beta = 10000.0f;
            
            for (int i = 0; i < num_moves; i++) {
                Position copy = pos;
                make_move(&copy, moves[i]);

                float score = minimax(&copy, current_depth - 1, alpha, beta, !is_white);

                if ((is_white && score > best_score) || (!is_white && score < best_score)) {
                    best_score = score;
                    strcpy(current_best, moves[i]);
                }
            }
        }

        // Update best move, PV, and previous score
        strcpy(best_move, current_best);
        strcpy(pv, current_best);
        prev_score = best_score;
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

    double start_time_ms = now_ms();

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
    minimax_set_time_limit(start_time_ms, max_time_ms);

    // Iterative deepening with time control
    for (int current_depth = 1; current_depth <= 20; current_depth++) {
        // Check time before starting new depth
        double elapsed_ms = now_ms() - start_time_ms;
        if (elapsed_ms >= max_time_ms * 0.9) {
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
            elapsed_ms = now_ms() - start_time_ms;
            if (elapsed_ms >= max_time_ms) {
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

    double end_time_ms = now_ms();
    double time_spent = end_time_ms - start_time_ms;
    minimax_clear_time_limit();

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
