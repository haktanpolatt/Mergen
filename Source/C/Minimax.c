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
#include "Zobrist.h"
#include "TT.h"
#include "Ordering.h"
#include "KillerMoves.h"

// QUIESCENCE SEARCH
static float quiescence(Position* pos, float alpha, float beta, int maximizingPlayer, int depth) {
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

// MINIMAX + TT + QUIESCENCE
float minimax(Position* pos, int depth, float alpha, float beta, int maximizingPlayer) {
    uint64_t hash = compute_zobrist_hash(pos);

    float cached_eval;
    if (tt_lookup(hash, &cached_eval, depth)) {
        return cached_eval;
    }

    if (depth == 0 || is_game_over(pos)) {
        float eval = quiescence(pos, alpha, beta, maximizingPlayer, depth);
        tt_store(hash, eval, depth);
        return eval;
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
            make_move(&copy, moves[i]);

            float eval = minimax(&copy, depth - 1, alpha, beta, 0);

            if (eval > max_eval) max_eval = eval;
            if (eval > alpha) alpha = eval;
            if (beta <= alpha) { // Beta cut-off
                int to_file = moves[i][2] - 'a';
                int to_rank = '8' - moves[i][3];
                Piece victim = copy.board[to_rank][to_file];
                
                if (victim.type == 0) { // Quiet move
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
            make_move(&copy, moves[i]);

            float eval = minimax(&copy, depth - 1, alpha, beta, 1);

            if (eval < min_eval) min_eval = eval;
            if (eval < beta) beta = eval;
            if (beta <= alpha) { // Alpha cut-off
                int to_file = moves[i][2] - 'a';
                int to_rank = '8' - moves[i][3];
                Piece victim = copy.board[to_rank][to_file];
                
                if (victim.type == 0) { // Quiet move
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
