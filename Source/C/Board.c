/*
###############################
#                             #
#   Created on June 3, 2025   #
#                             #
###############################
*/

#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include "Board.h"

void parse_fen(const char* fen, Position* pos) {
    int rank = 0, file = 0;
    memset(pos, 0, sizeof(Position));  // tüm değerleri sıfırla

    // Tahta yerleşimi
    for (int i = 0; fen[i] && fen[i] != ' '; i++) {
        char c = fen[i];
        if (c == '/') {
            rank++;
            file = 0;
        } else if (isdigit(c)) {
            file += c - '0';
        } else {
            Piece p;
            p.is_white = isupper(c);
            p.type = tolower(c);
            pos->board[rank][file++] = p;
        }
    }

    // Hamle sırası
    const char* ptr = strchr(fen, ' ');
    if (ptr && *(ptr + 1) == 'w') pos->white_to_move = 1;

    // Rok hakları
    const char* castling = strchr(ptr + 1, ' ');
    if (castling) {
        castling += 1;
        while (*castling && *castling != ' ') {
            switch (*castling) {
                case 'K': pos->white_king_side_castle = 1; break;
                case 'Q': pos->white_queen_side_castle = 1; break;
                case 'k': pos->black_king_side_castle = 1; break;
                case 'q': pos->black_queen_side_castle = 1; break;
            }
            castling++;
        }

        // En passant
        const char* ep = strchr(castling, ' ');
        if (ep && *(ep + 1) != '-') {
            int file_char = ep[1];
            int rank_char = ep[2];
            pos->ep_file = file_char - 'a';
            pos->ep_rank = '8' - rank_char;
        } else {
            pos->ep_file = -1;
            pos->ep_rank = -1;
        }
    }
}

void fen_to_board(const char* fen, Position* pos) {
    int rank = 0, file = 0;
    const char* ptr = fen;

    // Taş yerleşimi
    while (*ptr && *ptr != ' ') {
        char c = *ptr++;
        if (c == '/') {
            rank++;
            file = 0;
        } else if (isdigit(c)) {
            file += c - '0';
        } else {
            Piece p;
            p.is_white = isupper(c);
            p.type = tolower(c);
            pos->board[rank][file++] = p;
        }
    }

    // 1 boşluk: sıradaki taraf
    while (*ptr == ' ') ptr++;
    pos->white_to_move = (*ptr == 'w') ? 1 : 0;

    // 2. boşluk: rok hakları (atla)
    int space_count = 0;
    while (*ptr && space_count < 2) {
        if (*ptr == ' ') space_count++;
        ptr++;
    }

    // 3. boşluk sonrası: en passant hedef karesi
    pos->ep_rank = -1;
    pos->ep_file = -1;

    if (*ptr != '-') {
        if (ptr[0] >= 'a' && ptr[0] <= 'h' && ptr[1] >= '1' && ptr[1] <= '8') {
            pos->ep_file = ptr[0] - 'a';
            pos->ep_rank = 8 - (ptr[1] - '0');
        }
    }
}

void print_board(Piece board[8][8]) {
    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type == 0) {
                printf(". ");
            } else {
                char symbol = p.is_white ? toupper(p.type) : p.type;
                printf("%c ", symbol);
            }
        }
        printf("\n");
    }
}

void copy_board(Piece src[8][8], Piece dest[8][8]) {
    for (int r = 0; r < 8; r++) {
        for (int f = 0; f < 8; f++) {
            dest[r][f] = src[r][f];
        }
    }
}
