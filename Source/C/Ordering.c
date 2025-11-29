/*
################################
#                              #
#   Created on July 31, 2025   #
#                              #
################################
*/

#include <stdlib.h>
#include <string.h>
#include "Ordering.h"
#include "KillerMoves.h"

// History table for move ordering (quiet moves)
int history_table[64][64] = {0};

// Global pointer (for qsort)
static Position* current_pos = NULL;

// Piece values for MVV-LVA (Most Valuable Victim - Least Valuable Attacker) (p, n, b, r, q, k)
static const int mvv_lva[6][6] = {
    {105, 205, 305, 405, 505, 605}, // victim = pawn
    {104, 204, 304, 404, 504, 604}, // victim = knight
    {103, 203, 303, 403, 503, 603}, // victim = bishop
    {102, 202, 302, 402, 502, 602}, // victim = rook
    {101, 201, 301, 401, 501, 601}, // victim = queen
    {100, 200, 300, 400, 500, 600}  // victim = king
};

// Piece index mapping for mvv_lva
// p = 0, n = 1, b = 2, r =
static int piece_index(char type) {
    switch (type) {
        case 'p': return 0;
        case 'n': return 1;
        case 'b': return 2;
        case 'r': return 3;
        case 'q': return 4;
        case 'k': return 5;
        default: return 0;
    }
}

// Calculate the score of a move based on MVV-LVA
static int move_score(const char* move, int depth) {
    int from_file = move[0] - 'a';
    int from_rank = '8' - move[1];
    int to_file   = move[2] - 'a';
    int to_rank   = '8' - move[3];

    Piece attacker = current_pos->board[from_rank][from_file];
    Piece victim   = current_pos->board[to_rank][to_file];

    if (victim.type != 0) {
        // Capture → MVV-LVA
        return mvv_lva[piece_index(victim.type)][piece_index(attacker.type)] + 100000;
    } else {
        // Quiet move → history + killer bonus
        int from_sq = from_rank * 8 + from_file;
        int to_sq   = to_rank * 8 + to_file;
        int score   = history_table[from_sq][to_sq];

        for (int i = 0; i < 2; i++) { // iki killer move tutuluyor
            if (strcmp(killer_moves[depth][i], move) == 0) {
                score += 90000; // killer move bonus
                break;
            }
        }
        return score;
    }
}

#ifdef _WIN32

// Compare function for qsort to order moves based on their score
// Higher scores come first, so we sort in descending order.
static int compare_moves_win(void *depth_ptr, const void *a, const void *b) {
    int depth = *(int*)depth_ptr;
    const char* move_a = (const char*)a;
    const char* move_b = (const char*)b;

    int score_a = move_score(move_a, depth);
    int score_b = move_score(move_b, depth);

    return score_b - score_a; // Higher score first
}

// Sort moves using MVV-LVA heuristic
void sort_moves(Position *pos, char moves[][6], int num_moves, int depth) {
    current_pos = pos;
    qsort_s(moves, num_moves, sizeof(moves[0]), compare_moves_win, &depth);
}

#else

// Compare function for qsort to order moves based on their score
// Higher scores come first, so we sort in descending order.
static int compare_moves_unix(const void* a, const void* b, void* depth_ptr) {
    int depth = *(int*)depth_ptr;
    const char* move_a = (const char*)a;
    const char* move_b = (const char*)b;

    int score_a = move_score(move_a, depth);
    int score_b = move_score(move_b, depth);

    return score_b - score_a; // Higher score first
}

// Sort moves using MVV-LVA heuristic
void sort_moves(Position *pos, char moves[][6], int num_moves, int depth) {
    current_pos = pos;
    qsort_r(moves, num_moves, sizeof(moves[0]), compare_moves_unix, &depth);
}

#endif

// Update the history table for the given move
// The depth is used to scale the history score.
void update_history(const char* move, int depth) {
    int from_file = move[0] - 'a';
    int from_rank = '8' - move[1];
    int to_file   = move[2] - 'a';
    int to_rank   = '8' - move[3];

    int from_sq = from_rank * 8 + from_file;
    int to_sq = to_rank * 8 + to_file;

    history_table[from_sq][to_sq] += depth * depth; // depth squared for better scaling

    if (history_table[from_sq][to_sq] > 1000000) {
        for (int i = 0; i < 64; i++) {
            for (int j = 0; j < 64; j++) {
                history_table[i][j] /= 2;
            }
        }
    }
}
