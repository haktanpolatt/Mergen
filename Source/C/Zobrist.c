/*
################################
#                              #
#   Created on July 13, 2025   #
#                              #
################################
*/

#include "Zobrist.h"
#include <stdlib.h>
#include <time.h>

uint64_t zobrist_table[8][8][12]; // 64 squares, 12 piece types
uint64_t zobrist_white_to_move;

void init_zobrist() {
    srand(0xCAFEBABE); // for deterministic results

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            for (int piece = 0; piece < 12; piece++) {
                zobrist_table[rank][file][piece] =
                    ((uint64_t)rand() << 32) | rand();
            }
        }
    }

    zobrist_white_to_move = ((uint64_t)rand() << 32) | rand();
}

int piece_index(Piece p) {
    if (p.type == 0) return -1;
    int type_index;
    switch (p.type) {
        case 'p': type_index = 0; break;
        case 'n': type_index = 1; break;
        case 'b': type_index = 2; break;
        case 'r': type_index = 3; break;
        case 'q': type_index = 4; break;
        case 'k': type_index = 5; break;
        default: return -1;
    }
    return type_index + (p.is_white ? 0 : 6);
}

uint64_t compute_zobrist_hash(Position* pos) {
    uint64_t hash = 0;
    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            int idx = piece_index(pos->board[rank][file]);
            if (idx != -1) {
                hash ^= zobrist_table[rank][file][idx];
            }
        }
    }
    if (pos->white_to_move)
        hash ^= zobrist_white_to_move;
    return hash;
}
