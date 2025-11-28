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

// Default to 64MB unless overridden
#define TT_DEFAULT_MB 64
// Hard cap to avoid runaway allocations (~1GB with 64 million entries at ~16B)
#define TT_MAX_ENTRIES (1u << 26)
#define TT_MIN_ENTRIES 1024

static TTEntry* table = NULL;
static size_t tt_size_entries = 0;

static size_t clamp_entries_from_mb(int megabytes) {
    if (megabytes < 1) {
        megabytes = 1;
    }
    size_t bytes = (size_t)megabytes * 1024 * 1024;
    size_t entries = bytes / sizeof(TTEntry);
    if (entries < TT_MIN_ENTRIES) {
        entries = TT_MIN_ENTRIES;
    }
    if (entries > TT_MAX_ENTRIES) {
        entries = TT_MAX_ENTRIES;
    }
    return entries;
}

static void tt_allocate(size_t entries) {
    if (table != NULL) {
        free(table);
    }
    table = malloc(sizeof(TTEntry) * entries);
    if (table != NULL) {
        memset(table, 0, sizeof(TTEntry) * entries);
        tt_size_entries = entries;
    } else {
        tt_size_entries = 0;
    }
}

void tt_resize(int megabytes) {
    size_t entries = clamp_entries_from_mb(megabytes);
    tt_allocate(entries);
}

void tt_init() {
    if (tt_size_entries == 0 || table == NULL) {
        tt_resize(TT_DEFAULT_MB);
    }
}

void tt_store(uint64_t key, float eval, int depth) {
    if (table == NULL || tt_size_entries == 0) {
        tt_init();
    }
    uint64_t index = key % tt_size_entries;
    if (depth >= table[index].depth) {
        table[index].key = key;
        table[index].eval = eval;
        table[index].depth = depth;
    }
}

int tt_lookup(uint64_t key, float* eval, int depth) {
    if (table == NULL || tt_size_entries == 0) {
        return 0;
    }
    uint64_t index = key % tt_size_entries;
    if (table[index].key == key && table[index].depth >= depth) {
        *eval = table[index].eval;
        return 1;
    }
    return 0;
}
