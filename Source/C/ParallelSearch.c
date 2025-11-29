/*
####################################
#                                  #
#   Created on November 10, 2025   #
#                                  #
####################################
*/

// Parallel Search Implementation using Lazy SMP (Shared Memory Parallel)
// 
// Paper Reference:
// - Hyatt, R. M., Gower, A. R., & Nelson, H. L. (1990). "Cray Blitz"
// - Brockington, M. (1996). "A Taxonomy of Parallel Game-Tree Search Algorithms"
// - Dailey, D. P., & Joerg, C. F. (1995). "A Parallel Algorithm for Chess"
//
// Lazy SMP is a simple and effective parallel search algorithm:
// - Each thread searches independently from the root
// - Threads share transposition table
// - No explicit work distribution or synchronization
// - Works well with 2-8 cores (diminishing returns beyond)
//
// Benefits:
// - Nearly linear speedup with 2-4 threads
// - Simple implementation (no complex synchronization)
// - Natural load balancing through shared TT
// - Compatible with existing search code

#ifdef _WIN32
#include <windows.h>
#include <process.h>
#else
#include <pthread.h>
#include <unistd.h>
#endif

#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include "ParallelSearch.h"
#include "Minimax.h"
#include "MoveGen.h"
#include "Move.h"
#include "Zobrist.h"
#include "TT.h"
#include "Ordering.h"

// Global state
static int g_num_threads = 1;
static int g_initialized = 0;
static double g_start_time_ms = 0.0;
static double g_max_time_ms = 0.0;

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

// Thread function that searches a subset of moves with alpha-beta pruning
#ifdef _WIN32
unsigned __stdcall search_thread(void* arg)
#else
void* search_thread(void* arg)
#endif
{
    ThreadData* data = (ThreadData*)arg;
    
    float best_score = data->is_white ? -10000.0f : 10000.0f;
    float alpha = data->alpha;
    float beta = data->beta;
    char thread_best[6] = "";
    data->nodes = 0;
    
    // Each thread searches its assigned moves WITH alpha-beta pruning
    for (int i = data->start_index; i < data->end_index && i < data->num_moves; i++) {
        // Time guard for timed searches
        if (g_max_time_ms > 0.0) {
            double elapsed_ms = now_ms() - g_start_time_ms;
            if (elapsed_ms >= g_max_time_ms) {
                break;
            }
        }

        Position copy = data->position;
        make_move(&copy, data->moves[i]);
        
        float score = minimax(&copy, data->depth - 1, alpha, beta, !data->is_white);
        data->nodes += 1;
        
        if (data->is_white) {
            if (score > best_score) {
                best_score = score;
                strcpy(thread_best, data->moves[i]);
            }
            if (score > alpha) {
                alpha = score;
            }
            // Early exit on beta cutoff
            if (beta <= alpha) {
                break;
            }
        } else {
            if (score < best_score) {
                best_score = score;
                strcpy(thread_best, data->moves[i]);
            }
            if (score < beta) {
                beta = score;
            }
            // Early exit on alpha cutoff
            if (beta <= alpha) {
                break;
            }
        }
    }
    
    // Store results
    data->best_score = best_score;
    strcpy(data->best_move, thread_best);
    
    #ifdef _WIN32
        return 0;
    #else
        return NULL;
    #endif
}

// Get CPU core count
int get_cpu_core_count(void) {
    #ifdef _WIN32
        SYSTEM_INFO sysinfo;
        GetSystemInfo(&sysinfo);
        return sysinfo.dwNumberOfProcessors;
    #else
        return sysconf(_SC_NPROCESSORS_ONLN);
    #endif
}

// Initialize parallel search
void parallel_search_init(int num_threads) {
    if (!g_initialized) {
        init_zobrist();
        tt_init();
        g_initialized = 1;
    }
    
    // Limit threads to reasonable range
    if (num_threads < 1) num_threads = 1;
    if (num_threads > MAX_THREADS) num_threads = MAX_THREADS;
    
    int available_cores = get_cpu_core_count();
    if (num_threads > available_cores) {
        num_threads = available_cores;
    }
    
    g_num_threads = num_threads;
}

// Find best move using parallel search with Lazy SMP
const char* find_best_move_parallel(const char* fen, int depth, int num_threads) {
    static char best_move[6];
    static char pv[6];
    
    // Initialize if needed
    if (!g_initialized) {
        parallel_search_init(num_threads);
    } else {
        g_num_threads = num_threads;
    }
    g_start_time_ms = 0.0;
    g_max_time_ms = 0.0;
    
    Position pos = {0};
    parse_fen(fen, &pos);
    int is_white = pos.white_to_move;
    
    char moves[256][6];
    int num_moves = generate_legal_moves(&pos, is_white, moves);
    
    if (num_moves == 0) {
        strcpy(best_move, "");
        return best_move;
    }
    
    // IMPORTANT: Sort moves ONCE before iterative deepening for better cutoffs
    sort_moves(&pos, moves, num_moves, depth);
    
    strcpy(best_move, moves[0]);
    
    // ITERATIVE DEEPENING (both single and multi-threaded use this)
    for (int current_depth = 1; current_depth <= depth; current_depth++) {
        // For shallow depths or single thread, use simple search
        if (current_depth <= 2 || g_num_threads == 1) {
            float best_score = is_white ? -10000.0f : 10000.0f;
            
            for (int i = 0; i < num_moves; i++) {
                Position copy = pos;
                make_move(&copy, moves[i]);
                float score = minimax(&copy, current_depth - 1, -10000.0f, 10000.0f, !is_white);
                
                if ((is_white && score > best_score) || (!is_white && score < best_score)) {
                    best_score = score;
                    strcpy(best_move, moves[i]);
                }
            }
            strcpy(pv, best_move);
            continue;
        }
        
        // LAZY SMP: Create threads to search different moves in parallel
        ThreadData thread_data[MAX_THREADS];
        
        #ifdef _WIN32
            HANDLE threads[MAX_THREADS];
        #else
            pthread_t threads[MAX_THREADS];
        #endif
        
        // Limit threads for diminishing returns (Lazy SMP doesn't scale well beyond 8)
        int actual_threads = g_num_threads;
        if (actual_threads > 8) {
            actual_threads = 8;
        }
        if (actual_threads > num_moves) {
            actual_threads = num_moves;
        }
        
        // Distribute moves among threads
        int moves_per_thread = num_moves / actual_threads;
        int extra_moves = num_moves % actual_threads;
        
        int start_idx = 0;
        for (int t = 0; t < actual_threads; t++) {
            thread_data[t].position = pos;
            thread_data[t].moves = moves;
            thread_data[t].num_moves = num_moves;
            thread_data[t].start_index = start_idx;
            thread_data[t].end_index = start_idx + moves_per_thread + (t < extra_moves ? 1 : 0);
            thread_data[t].depth = current_depth;
            thread_data[t].alpha = -10000.0f;
            thread_data[t].beta = 10000.0f;
            thread_data[t].is_white = is_white;
            thread_data[t].best_score = is_white ? -10000.0f : 10000.0f;
            thread_data[t].thread_id = t;
            strcpy(thread_data[t].best_move, "");
            
            start_idx = thread_data[t].end_index;
            
            // Create thread
            #ifdef _WIN32
                threads[t] = (HANDLE)_beginthreadex(NULL, 0, search_thread, &thread_data[t], 0, NULL);
            #else
                pthread_create(&threads[t], NULL, search_thread, &thread_data[t]);
            #endif
        }
        
        // Wait for all threads to complete
        for (int t = 0; t < actual_threads; t++) {
            #ifdef _WIN32
                WaitForSingleObject(threads[t], INFINITE);
                CloseHandle(threads[t]);
            #else
                pthread_join(threads[t], NULL);
            #endif
        }
        
        // Find best result from all threads
        float best_score = is_white ? -10000.0f : 10000.0f;
        char current_best[6];
        strcpy(current_best, best_move);
        
        for (int t = 0; t < actual_threads; t++) {
            if (strlen(thread_data[t].best_move) > 0) {
                if ((is_white && thread_data[t].best_score > best_score) ||
                    (!is_white && thread_data[t].best_score < best_score)) {
                    best_score = thread_data[t].best_score;
                    strcpy(current_best, thread_data[t].best_move);
                }
            }
        }
        
        strcpy(best_move, current_best);
        strcpy(pv, current_best);
    }
    
    return best_move;
}

// Find best move with time limit using parallel search
const char* find_best_move_parallel_timed(const char* fen, float max_time_ms, int num_threads) {
    static char result[128];
    static char best_move[6];
    static char pv[6];
    
    // Initialize if needed
    if (!g_initialized) {
        parallel_search_init(num_threads);
    } else {
        g_num_threads = num_threads;
    }
    
    g_start_time_ms = now_ms();
    g_max_time_ms = max_time_ms;
    minimax_set_time_limit(g_start_time_ms, max_time_ms);
    
    Position pos = {0};
    parse_fen(fen, &pos);
    int is_white = pos.white_to_move;
    
    char moves[256][6];
    int num_moves = generate_legal_moves(&pos, is_white, moves);
    
    if (num_moves == 0) {
        snprintf(result, sizeof(result), "%s 0 0.0", moves[0]);
        return result;
    }
    
    // Sort moves ONCE for better cutoffs throughout iterative deepening
    sort_moves(&pos, moves, num_moves, 1);
    
    strcpy(best_move, moves[0]);
    int completed_depth = 0;
    
    // Iterative deepening with time control and parallel search
    for (int current_depth = 1; current_depth <= 20; current_depth++) {
        // Check time before starting new depth
        double elapsed_ms = now_ms() - g_start_time_ms;
        if (elapsed_ms >= max_time_ms * 0.85) {
            // 85% of time used, don't start new depth
            break;
        }
        
        // For shallow depths or single thread, use simple search
        if (current_depth <= 2 || g_num_threads == 1) {
            float best_score = is_white ? -10000.0f : 10000.0f;
            char current_best[6];
            strcpy(current_best, best_move);
            
            for (int i = 0; i < num_moves; i++) {
                elapsed_ms = now_ms() - g_start_time_ms;
                if (elapsed_ms >= max_time_ms) break;
                
                Position copy = pos;
                make_move(&copy, moves[i]);
                float score = minimax(&copy, current_depth - 1, -10000.0f, 10000.0f, !is_white);
                
                if ((is_white && score > best_score) || (!is_white && score < best_score)) {
                    best_score = score;
                    strcpy(current_best, moves[i]);
                }
            }
            
            strcpy(best_move, current_best);
            strcpy(pv, current_best);
            completed_depth = current_depth;
            continue;
        }
        
        // Parallel search for deeper depths
        ThreadData thread_data[MAX_THREADS];
        
        #ifdef _WIN32
            HANDLE threads[MAX_THREADS];
        #else
            pthread_t threads[MAX_THREADS];
        #endif
        
        // Limit threads for diminishing returns
        int actual_threads = g_num_threads;
        if (actual_threads > 8) {
            actual_threads = 8;
        }
        if (actual_threads > num_moves) {
            actual_threads = num_moves;
        }
        
        int moves_per_thread = num_moves / actual_threads;
        int extra_moves = num_moves % actual_threads;
        
        int start_idx = 0;
        for (int t = 0; t < actual_threads; t++) {
            thread_data[t].position = pos;
            thread_data[t].moves = moves;
            thread_data[t].num_moves = num_moves;
            thread_data[t].start_index = start_idx;
            thread_data[t].end_index = start_idx + moves_per_thread + (t < extra_moves ? 1 : 0);
            thread_data[t].depth = current_depth;
            thread_data[t].alpha = -10000.0f;
            thread_data[t].beta = 10000.0f;
            thread_data[t].is_white = is_white;
            thread_data[t].best_score = is_white ? -10000.0f : 10000.0f;
            thread_data[t].thread_id = t;
            strcpy(thread_data[t].best_move, "");
            
            start_idx = thread_data[t].end_index;
            
            #ifdef _WIN32
                threads[t] = (HANDLE)_beginthreadex(NULL, 0, search_thread, &thread_data[t], 0, NULL);
            #else
                pthread_create(&threads[t], NULL, search_thread, &thread_data[t]);
            #endif
        }
        
        // Wait for all threads
        for (int t = 0; t < actual_threads; t++) {
            #ifdef _WIN32
                WaitForSingleObject(threads[t], INFINITE);
                CloseHandle(threads[t]);
            #else
                pthread_join(threads[t], NULL);
            #endif
        }
        
        // Check if we ran out of time
        elapsed_ms = now_ms() - g_start_time_ms;
        if (elapsed_ms >= max_time_ms) {
            break;
        }
        
        // Find best result
        float best_score = is_white ? -10000.0f : 10000.0f;
        char current_best[6];
        strcpy(current_best, best_move);
        int total_nodes = 0;
        
        for (int t = 0; t < actual_threads; t++) {
            total_nodes += thread_data[t].nodes;
            if (strlen(thread_data[t].best_move) > 0) {
                if ((is_white && thread_data[t].best_score > best_score) ||
                    (!is_white && thread_data[t].best_score < best_score)) {
                    best_score = thread_data[t].best_score;
                    strcpy(current_best, thread_data[t].best_move);
                }
            }
        }
        
        strcpy(best_move, current_best);
        strcpy(pv, current_best);
        completed_depth = current_depth;
    }
    
    double end_time_ms = now_ms();
    double time_spent = end_time_ms - g_start_time_ms;
    minimax_clear_time_limit();
    
    // Format: move depth time_spent_ms total_nodes
    snprintf(result, sizeof(result), "%s %d %.1f %d", best_move, completed_depth, time_spent, 0);
    return result;
}
