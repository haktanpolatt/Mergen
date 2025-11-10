/*
################################
#                              #
#   Created on July 13, 2025   #
#                              #
################################
*/

#include "TT.h"
#include <stdlib.h>
#include <string.h>

// Increased from 1M to 16M entries (128MB instead of 8MB)
// This significantly reduces hash collisions in deep searches
#define TT_SIZE (1 << 24)

static TTEntry* table = NULL;

void tt_init() {
    table = malloc(sizeof(TTEntry) * TT_SIZE);
    memset(table, 0, sizeof(TTEntry) * TT_SIZE);
}

void tt_store(uint64_t key, float eval, int depth) {
    uint64_t index = key % TT_SIZE;
    if (depth >= table[index].depth) {
        table[index].key = key;
        table[index].eval = eval;
        table[index].depth = depth;
    }
}

int tt_lookup(uint64_t key, float* eval, int depth) {
    uint64_t index = key % TT_SIZE;
    if (table[index].key == key && table[index].depth >= depth) {
        *eval = table[index].eval;
        return 1;
    }
    return 0;
}
