/*
################################
#                              #
#   Created on July 13, 2025   #
#                              #
################################
*/

#ifndef ZOBRIST_H
#define ZOBRIST_H

#include "Board.h"
#include <stdint.h>

void init_zobrist();
uint64_t compute_zobrist_hash(Position* pos);

#endif