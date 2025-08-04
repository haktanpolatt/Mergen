/*
###############################
#                             #
#   Created on June 3, 2025   #
#                             #
###############################
*/

#include <stdlib.h>
#include <string.h>
#include "MoveGen.h"
#include "Rules.h"
#include "Move.h"

static void square_to_uci(int fr, int ff, int tr, int tf, char* buffer) {
    buffer[0] = 'a' + ff;
    buffer[1] = '8' - fr;
    buffer[2] = 'a' + tf;
    buffer[3] = '8' - tr;
    buffer[4] = '\0';
}

// Empty or not attacked square
static int is_empty(Piece board[8][8], int rank, int file) {
    return board[rank][file].type == 0;
}

int generate_pawn_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int dir = is_white ? -1 : 1;
    int start_rank = is_white ? 6 : 1;
    int next_rank = rank + dir;

    // Go 1 square forward
    if (next_rank >= 0 && next_rank < 8 && board[next_rank][file].type == 0) {
        square_to_uci(rank, file, next_rank, file, moves[move_index++]);

        // Go 2 squares forward from starting position
        if (rank == start_rank && board[rank + dir * 2][file].type == 0) {
            square_to_uci(rank, file, rank + dir * 2, file, moves[move_index++]);
        }
    }

    // Capture diagonally
    for (int df = -1; df <= 1; df += 2) {
        int new_file = file + df;
        if (new_file >= 0 && new_file < 8 && next_rank >= 0 && next_rank < 8) {
            Piece target = board[next_rank][new_file];
            if (target.type != 0 && target.is_white != is_white) {
                square_to_uci(rank, file, next_rank, new_file, moves[move_index++]);
            }
        }
    }

    // En passant
    if (pos->ep_rank != -1 && pos->ep_file != -1) {
        if (rank == (is_white ? 3 : 4) &&
            abs(file - pos->ep_file) == 1 &&
            pos->ep_rank == next_rank) {
            square_to_uci(rank, file, pos->ep_rank, pos->ep_file, moves[move_index++]);
        }
    }

    return move_index;
}


int generate_knight_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[8][2] = {
        {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
        {1, -2},  {1, 2},  {2, -1},  {2, 1}
    };

    for (int i = 0; i < 8; i++) {
        int r = rank + directions[i][0];
        int f = file + directions[i][1];
        if (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type == 0 || target.is_white != is_white) {
                square_to_uci(rank, file, r, f, moves[move_index]);
                move_index++;
            }
        }
    }

    return move_index;
}

int generate_bishop_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[4][2] = {
        {-1, -1}, {-1, 1},
        {1, -1},  {1, 1}
    };

    for (int d = 0; d < 4; d++) {
        int dr = directions[d][0];
        int df = directions[d][1];
        int r = rank + dr;
        int f = file + df;

        while (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type == 0) {
                square_to_uci(rank, file, r, f, moves[move_index++]);
            } else {
                if (target.is_white != is_white) {
                    square_to_uci(rank, file, r, f, moves[move_index++]);
                }
                break; // Stop if we hit a piece
            }

            r += dr;
            f += df;
        }
    }

    return move_index;
}

int generate_rook_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[4][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1}
    };

    for (int d = 0; d < 4; d++) {
        int dr = directions[d][0];
        int df = directions[d][1];
        int r = rank + dr;
        int f = file + df;

        while (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type == 0) {
                square_to_uci(rank, file, r, f, moves[move_index++]);
            } else {
                if (target.is_white != is_white) {
                    square_to_uci(rank, file, r, f, moves[move_index++]);
                }
                break;
            }

            r += dr;
            f += df;
        }
    }

    return move_index;
}

int generate_queen_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[8][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1},
        {-1, -1}, {-1, 1}, {1, -1}, {1, 1}
    };

    for (int d = 0; d < 8; d++) {
        int dr = directions[d][0];
        int df = directions[d][1];
        int r = rank + dr;
        int f = file + df;

        while (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type == 0) {
                square_to_uci(rank, file, r, f, moves[move_index++]);
            } else {
                if (target.is_white != is_white) {
                    square_to_uci(rank, file, r, f, moves[move_index++]);
                }
                break;
            }
            r += dr;
            f += df;
        }
    }

    return move_index;
}

int generate_king_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[8][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1},
        {-1, -1}, {-1, 1}, {1, -1}, {1, 1}
    };

    // Normal king moves
    for (int d = 0; d < 8; d++) {
        int r = rank + directions[d][0];
        int f = file + directions[d][1];

        if (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type == 0 || target.is_white != is_white) {
                square_to_uci(rank, file, r, f, moves[move_index++]);
            }
        }
    }

    // Castling
    if (is_white && rank == 7 && file == 4) {
        if (pos->white_king_side_castle &&
            board[7][5].type == 0 &&
            board[7][6].type == 0) {
            square_to_uci(7, 4, 7, 6, moves[move_index++]);  // Short castling (O-O)
        }
        if (pos->white_queen_side_castle &&
            board[7][1].type == 0 &&
            board[7][2].type == 0 &&
            board[7][3].type == 0) {
            square_to_uci(7, 4, 7, 2, moves[move_index++]);  // Long castling (O-O-O)
        }
    }

    if (!is_white && rank == 0 && file == 4) {
        if (pos->black_king_side_castle &&
            board[0][5].type == 0 &&
            board[0][6].type == 0) {
            square_to_uci(0, 4, 0, 6, moves[move_index++]);  // Short castling (O-O)
        }
        if (pos->black_queen_side_castle &&
            board[0][1].type == 0 &&
            board[0][2].type == 0 &&
            board[0][3].type == 0) {
            square_to_uci(0, 4, 0, 2, moves[move_index++]);  // Long castling (O-O-O)
        }
    }

    return move_index;
}

int generate_pseudo_legal_moves(Position* pos, int is_white, char moves[][6]) {
    Piece (*board)[8] = pos->board;
    int move_index = 0;

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type == 0 || p.is_white != is_white) continue;
            
            switch (p.type) {
                case 'p': move_index = generate_pawn_moves(pos, rank, file, moves, move_index); break;
                case 'n': move_index = generate_knight_moves(pos, rank, file, moves, move_index); break;
                case 'b': move_index = generate_bishop_moves(pos, rank, file, moves, move_index); break;
                case 'r': move_index = generate_rook_moves(pos, rank, file, moves, move_index); break;
                case 'q': move_index = generate_queen_moves(pos, rank, file, moves, move_index); break;
                case 'k': move_index = generate_king_moves(pos, rank, file, moves, move_index); break;
            }
        }
    }

    return move_index;
}

int generate_legal_moves(Position* pos, int is_white, char moves[][6]) {
    char temp[256][6];
    int temp_index = generate_pseudo_legal_moves(pos, is_white, temp);
    int move_index = 0;

    for (int i = 0; i < temp_index; i++) {
        Position copy = *pos;
        make_move(&copy, temp[i]);

        if (!is_in_check(&copy, is_white)) {
            strcpy(moves[move_index++], temp[i]);
        }
    }

    return move_index;
}

static int generate_pawn_capture_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int dir = is_white ? -1 : 1;
    int next_rank = rank + dir;

    // Normal diagonal captures
    for (int df = -1; df <= 1; df += 2) {
        int new_file = file + df;
        if (new_file >= 0 && new_file < 8 && next_rank >= 0 && next_rank < 8) {
            Piece target = board[next_rank][new_file];
            if (target.type != 0 && target.is_white != is_white) {
                square_to_uci(rank, file, next_rank, new_file, moves[move_index++]);
            }
        }
    }

    // En passant
    if (pos->ep_rank != -1 && pos->ep_file != -1) {
        if (rank == (is_white ? 3 : 4) &&
            abs(file - pos->ep_file) == 1 &&
            pos->ep_rank == next_rank) {
            square_to_uci(rank, file, pos->ep_rank, pos->ep_file, moves[move_index++]);
        }
    }

    return move_index;
}

static int generate_knight_capture_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[8][2] = {
        {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
        {1, -2},  {1, 2},  {2, -1},  {2, 1}
    };

    for (int i = 0; i < 8; i++) {
        int r = rank + directions[i][0];
        int f = file + directions[i][1];
        if (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type != 0 && target.is_white != is_white) {
                square_to_uci(rank, file, r, f, moves[move_index++]);
            }
        }
    }
    return move_index;
}

static int generate_sliding_capture_moves(Position* pos, int rank, int file, char moves[][6], int move_index, int directions[][2], int dir_count) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;

    for (int d = 0; d < dir_count; d++) {
        int r = rank + directions[d][0];
        int f = file + directions[d][1];

        while (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type != 0) {
                if (target.is_white != is_white) {
                    square_to_uci(rank, file, r, f, moves[move_index++]);
                }
                break; // stop if we hit a piece
            }
            r += directions[d][0];
            f += directions[d][1];
        }
    }
    return move_index;
}

static int generate_king_capture_moves(Position* pos, int rank, int file, char moves[][6], int move_index) {
    Piece (*board)[8] = pos->board;
    int is_white = board[rank][file].is_white;
    int directions[8][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1},
        {-1, -1}, {-1, 1}, {1, -1}, {1, 1}
    };

    for (int d = 0; d < 8; d++) {
        int r = rank + directions[d][0];
        int f = file + directions[d][1];
        if (r >= 0 && r < 8 && f >= 0 && f < 8) {
            Piece target = board[r][f];
            if (target.type != 0 && target.is_white != is_white) {
                square_to_uci(rank, file, r, f, moves[move_index++]);
            }
        }
    }
    return move_index;
}

int generate_capture_moves(Position* pos, int is_white, char moves[][6]) {
    int move_index = 0;
    int bishop_dirs[4][2] = {{-1,-1},{-1,1},{1,-1},{1,1}};
    int rook_dirs[4][2]   = {{-1,0},{1,0},{0,-1},{0,1}};
    int queen_dirs[8][2]  = {{-1,0},{1,0},{0,-1},{0,1},{-1,-1},{-1,1},{1,-1},{1,1}};

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = pos->board[rank][file];
            if (p.type == 0 || p.is_white != is_white) continue;

            switch (p.type) {
                case 'p':
                    move_index = generate_pawn_capture_moves(pos, rank, file, moves, move_index);
                    break;
                case 'n':
                    move_index = generate_knight_capture_moves(pos, rank, file, moves, move_index);
                    break;
                case 'b':
                    move_index = generate_sliding_capture_moves(pos, rank, file, moves, move_index, bishop_dirs, 4);
                    break;
                case 'r':
                    move_index = generate_sliding_capture_moves(pos, rank, file, moves, move_index, rook_dirs, 4);
                    break;
                case 'q':
                    move_index = generate_sliding_capture_moves(pos, rank, file, moves, move_index, queen_dirs, 8);
                    break;
                case 'k':
                    move_index = generate_king_capture_moves(pos, rank, file, moves, move_index);
                    break;
            }
        }
    }
    return move_index;
}
