/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#include <stdlib.h>
#include <time.h>
#ifdef _WIN32
#include <windows.h>
#endif
#include "Minimax.h"
#include "Evaluate.h"
#include "MoveGen.h"
#include "Move.h"
#include "Rules.h"
#include "Zobrist.h"
#include "TT.h"
#include "Ordering.h"
#include "KillerMoves.h"

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

static int g_time_limit_enabled = 0;
static double g_time_start_ms = 0.0;
static double g_time_limit_ms = 0.0;
static int g_time_up = 0;

static int count_pieces(Position* pos) {
    int count = 0;
    for (int r = 0; r < 8; r++) {
        for (int f = 0; f < 8; f++) {
            if (pos->board[r][f].type != 0) {
                count++;
            }
        }
    }
    return count;
}

void minimax_set_time_limit(double start_ms, double limit_ms) {
    g_time_limit_enabled = 1;
    g_time_start_ms = start_ms;
    g_time_limit_ms = limit_ms;
    g_time_up = 0;
}

void minimax_clear_time_limit(void) {
    g_time_limit_enabled = 0;
    g_time_start_ms = 0.0;
    g_time_limit_ms = 0.0;
    g_time_up = 0;
}

static int time_exceeded(void) {
    if (!g_time_limit_enabled || g_time_up) {
        return g_time_up;
    }
    double elapsed = now_ms() - g_time_start_ms;
    if (elapsed >= g_time_limit_ms) {
        g_time_up = 1;
        return 1;
    }
    return 0;
}

// QUIESCENCE SEARCH
static float quiescence(Position* pos, float alpha, float beta, int maximizingPlayer, int depth) {
    if (time_exceeded()) {
        return evaluate_board(pos);
    }
    float stand_pat = evaluate_board(pos);

    // Alpha-beta cutoffs
    if (maximizingPlayer) {
        if (stand_pat >= beta) return beta;
        if (stand_pat > alpha) alpha = stand_pat;
    } else {
        if (stand_pat <= alpha) return alpha;
        if (stand_pat < beta) beta = stand_pat;
    }

    // Generate capture moves only (optimized version)
    char moves[256][6];
    int num_moves = generate_capture_moves(pos, maximizingPlayer, moves);
    sort_moves(pos, moves, num_moves, depth);
    if (num_moves == 0) return stand_pat; // no captures → stop

    for (int i = 0; i < num_moves; i++) {
        Position copy = *pos;
        make_move(&copy, moves[i]);

        float score = quiescence(&copy, alpha, beta, !maximizingPlayer, depth);

        if (maximizingPlayer) {
            if (score > alpha) alpha = score;
            if (alpha >= beta) return beta;
        } else {
            if (score < beta) beta = score;
            if (beta <= alpha) return alpha;
        }
    }

    return maximizingPlayer ? alpha : beta;
}

// MINIMAX + TT + QUIESCENCE + LATE MOVE REDUCTIONS + FUTILITY PRUNING
float minimax(Position* pos, int depth, float alpha, float beta, int maximizingPlayer) {
    if (time_exceeded()) {
        return evaluate_board(pos);
    }
    uint64_t hash = compute_zobrist_hash(pos);

    float cached_eval;
    if (tt_lookup(hash, &cached_eval, depth)) {
        return cached_eval;
    }

    int in_check = is_in_check(pos, maximizingPlayer);

    if (depth == 0 || is_game_over(pos)) {
        float eval = quiescence(pos, alpha, beta, maximizingPlayer, depth);
        tt_store(hash, eval, depth);
        return eval;
    }

    // FUTILITY PRUNING: Check if static eval is hopeless
    // Only apply at low depths (1-2) with sufficient margin
    float static_eval = -1.0f; // Invalid value
    int do_futility_pruning = 0;
    float futility_margin = 0.0f;
    
    if (!in_check && depth <= 2) {
        static_eval = evaluate_board(pos);
        futility_margin = (depth == 1) ? 2.0f : 4.0f; // 2 pawns at depth 1, 4 at depth 2
        
        if (maximizingPlayer) {
            if (static_eval + futility_margin <= alpha) {
                do_futility_pruning = 1;
            }
        } else {
            if (static_eval - futility_margin >= beta) {
                do_futility_pruning = 1;
            }
        }
    }

    // NULL MOVE PRUNING
    if (!in_check && depth >= 4 && count_pieces(pos) > 10) {
        int reduction = (depth >= 6) ? 3 : 2;
        Position null_pos = *pos;
        null_pos.white_to_move = !pos->white_to_move;
        null_pos.ep_rank = -1;
        null_pos.ep_file = -1;

        float null_eval = minimax(&null_pos, depth - 1 - reduction, alpha, beta, !maximizingPlayer);
        if (maximizingPlayer && null_eval >= beta) {
            tt_store(hash, beta, depth);
            return beta;
        } else if (!maximizingPlayer && null_eval <= alpha) {
            tt_store(hash, alpha, depth);
            return alpha;
        }
    }

    char moves[256][6];
    int num_moves = generate_legal_moves(pos, maximizingPlayer, moves);
    sort_moves(pos, moves, num_moves, depth);

    if (num_moves == 0) { // No moves → game might be over
        float eval = evaluate_board(pos);
        tt_store(hash, eval, depth);
        return eval;
    }

    if (maximizingPlayer) {
        float max_eval = -10000.0f;
        for (int i = 0; i < num_moves; i++) {
            Position copy = *pos; // Copy of stack
            
            // Check if this is a capture or tactical move
            int to_file = moves[i][2] - 'a';
            int to_rank = '8' - moves[i][3];
            Piece victim = copy.board[to_rank][to_file];
            int is_capture = (victim.type != 0);
            
            // FUTILITY PRUNING: Skip quiet moves when position is hopeless
            if (do_futility_pruning && !is_capture) {
                continue; // Skip this quiet move
            }
            
            make_move(&copy, moves[i]);

            // LATE MOVE REDUCTIONS (LMR):
            // After first 4 moves at depth>=3, reduce depth for quiet moves
            int search_depth = depth - 1;
            int needs_full_search = 0;
            
            if (i >= 4 && depth >= 3 && !is_capture) {
                // Reduce depth by 1 for late quiet moves
                search_depth = depth - 2;
                needs_full_search = 1;
            }
            
            float eval = minimax(&copy, search_depth, alpha, beta, 0);
            
            // If LMR search raised alpha, re-search at full depth
            if (needs_full_search && eval > alpha) {
                eval = minimax(&copy, depth - 1, alpha, beta, 0);
            }

            if (eval > max_eval) max_eval = eval;
            if (eval > alpha) alpha = eval;
            if (beta <= alpha) { // Beta cut-off
                if (!is_capture) { // Quiet move
                    update_history(moves[i], depth);
                    add_killer_move(depth, moves[i]);
                }
                break;
            }
        }
        tt_store(hash, max_eval, depth);
        return max_eval;
    } else {
        float min_eval = 10000.0f;
        for (int i = 0; i < num_moves; i++) {
            Position copy = *pos;
            
            // Check if this is a capture or tactical move
            int to_file = moves[i][2] - 'a';
            int to_rank = '8' - moves[i][3];
            Piece victim = copy.board[to_rank][to_file];
            int is_capture = (victim.type != 0);
            
            // FUTILITY PRUNING: Skip quiet moves when position is hopeless
            if (do_futility_pruning && !is_capture) {
                continue; // Skip this quiet move
            }
            
            make_move(&copy, moves[i]);

            // LATE MOVE REDUCTIONS (LMR) for minimizing player
            int search_depth = depth - 1;
            int needs_full_search = 0;
            
            if (i >= 4 && depth >= 3 && !is_capture) {
                search_depth = depth - 2;
                needs_full_search = 1;
            }
            
            float eval = minimax(&copy, search_depth, alpha, beta, 1);
            
            // If LMR search lowered beta, re-search at full depth
            if (needs_full_search && eval < beta) {
                eval = minimax(&copy, depth - 1, alpha, beta, 1);
            }

            if (eval < min_eval) min_eval = eval;
            if (eval < beta) beta = eval;
            if (beta <= alpha) { // Alpha cut-off
                if (!is_capture) { // Quiet move
                    update_history(moves[i], depth);
                    add_killer_move(depth, moves[i]);
                }
                break;
            }
        }
        tt_store(hash, min_eval, depth);
        return min_eval;
    }
}
