/*
####################################
#                                  #
#   Created on November 10, 2025   #
#                                  #
####################################
*/

#ifndef PARALLEL_SEARCH_H
#define PARALLEL_SEARCH_H

#include "Board.h"

// Maximum number of threads to use
#define MAX_THREADS 16

// Thread data structure for parallel search
typedef struct {
    Position position;
    char moves[256][6];
    int num_moves;
    int start_index;
    int end_index;
    int depth;
    float alpha;
    float beta;
    int is_white;
    float best_score;
    char best_move[6];
    int thread_id;
} ThreadData;

// Initialize parallel search system
void parallel_search_init(int num_threads);

// Find best move using parallel search
const char* find_best_move_parallel(const char* fen, int depth, int num_threads);

// Find best move with time limit using parallel search
const char* find_best_move_parallel_timed(const char* fen, float max_time_ms, int num_threads);

// Get number of available CPU cores
int get_cpu_core_count(void);

#endif
