/*
################################
#                              #
#   Created on July 13, 2025   #
#                              #
################################
*/

#ifndef TT_H
#define TT_H

#include <stdint.h>

typedef struct {
    uint64_t key;
    float eval;
    int depth;
} TTEntry;

void tt_init();
void tt_store(uint64_t key, float eval, int depth);
int tt_lookup(uint64_t key, float* eval, int depth);

#endif
