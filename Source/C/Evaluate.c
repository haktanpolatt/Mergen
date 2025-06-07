/*
###############################
#                             #
#   Created on June 4, 2025   #
#                             #
###############################
*/

#include "Evaluate.h"
#include "MoveGen.h"

// EVALUATE MATERIAL
static float piece_value(char type) {
    switch (type) {
        case 'p': return 1.0;
        case 'n': return 3.0;
        case 'b': return 3.0;
        case 'r': return 5.0;
        case 'q': return 9.0;
        case 'k': return 0.0; // şah değeri verilmez
        default:  return 0.0;
    }
}

float evaluate_material(Position* pos) {
    Piece (*board)[8] = pos->board;
    float score = 0.0;

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type != 0) {
                float val = piece_value(p.type);
                score += p.is_white ? val : -val;
            }
        }
    }

    return score;
}

// EVALUATE PAWN STRUCTURE
float evaluate_pawn_structure(Position* pos) {
    Piece (*board)[8] = pos->board;
    float score = 0.0;

    int white_pawn_files[8] = {0};
    int black_pawn_files[8] = {0};

    // Önce tüm piyonları tarayalım
    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type != 'p') continue;

            int is_white = p.is_white;
            if (is_white)
                white_pawn_files[file]++;
            else
                black_pawn_files[file]++;
        }
    }

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type != 'p') continue;

            int is_white = p.is_white;
            int forward = is_white ? -1 : 1;
            float modifier = is_white ? 1.0f : -1.0f;

            // Çift piyon
            int count = is_white ? white_pawn_files[file] : black_pawn_files[file];
            if (count > 1) score += modifier * -0.2f;

            // İzole piyon
            int left = file > 0     ? (is_white ? white_pawn_files[file - 1] : black_pawn_files[file - 1]) : 0;
            int right = file < 7    ? (is_white ? white_pawn_files[file + 1] : black_pawn_files[file + 1]) : 0;
            if (left == 0 && right == 0)
                score += modifier * -0.25f;

            // Geçer piyon (önünde düşman piyon yoksa)
            int passed = 1;
            for (int r = rank + forward; r >= 0 && r < 8; r += forward) {
                for (int f = file - 1; f <= file + 1; f++) {
                    if (f < 0 || f > 7) continue;
                    Piece other = board[r][f];
                    if (other.type == 'p' && other.is_white != is_white) {
                        passed = 0;
                        break;
                    }
                }
            }
            if (passed) score += modifier * 0.3f;
        }
    }

    return score;
}

// EVALUATE CENTER CONTROL
static const int center_squares[4][2] = {
    {3, 3}, // d4
    {3, 4}, // e4
    {4, 3}, // d5
    {4, 4}  // e5
};

float evaluate_center_control(Position* pos) {
    Piece (*board)[8] = pos->board;
    float score = 0.0;

    int center_squares[4][2] = {
        {3, 3}, {3, 4}, {4, 3}, {4, 4}
    };

    for (int i = 0; i < 4; i++) {
        int rank = center_squares[i][0];
        int file = center_squares[i][1];
        Piece p = board[rank][file];

        // Üzerinde taş varsa
        if (p.type != 0) {
            score += p.is_white ? 0.2f : -0.2f;
        }

        // Bu kareyi kim tehdit ediyor? → legal hamlelerle bulalım
        char moves[256][6];
        int num_white = generate_legal_moves(pos, 1, moves);
        for (int m = 0; m < num_white; m++) {
            int to_rank = '8' - moves[m][3];
            int to_file = moves[m][2] - 'a';
            if (to_rank == rank && to_file == file) {
                score += 0.1f;
            }
        }

        int num_black = generate_legal_moves(pos, 0, moves);
        for (int m = 0; m < num_black; m++) {
            int to_rank = '8' - moves[m][3];
            int to_file = moves[m][2] - 'a';
            if (to_rank == rank && to_file == file) {
                score -= 0.1f;
            }
        }
    }

    return score;
}

// EVALUATE DEVELOPMENT
float evaluate_development(Position* pos) {
    Piece (*board)[8] = pos->board;
    float score = 0.0;

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece p = board[rank][file];
            if (p.type != 'n' && p.type != 'b') continue;

            float modifier = p.is_white ? 1.0f : -1.0f;

            // Gelişmemiş (1. ya da 8. yatayda)
            if ((p.is_white && rank == 7) || (!p.is_white && rank == 0)) {
                score += modifier * -0.15f;
            }

            // Hafif gelişmiş
            if ((p.is_white && rank == 6) || (!p.is_white && rank == 1)) {
                score += modifier * 0.1f;
            }

            // Merkez sütunlara çıkmışsa (c,d,e,f = 2..5)
            if (file >= 2 && file <= 5) {
                score += modifier * 0.05f;
            }
        }
    }

    return score;
}

// EVALUATE KING SAFETY
float evaluate_king_safety(Position* pos) {
    Piece (*board)[8] = pos->board;
    float score = 0.0;

    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {
            Piece king = board[rank][file];
            if (king.type != 'k') continue;

            float modifier = king.is_white ? 1.0f : -1.0f;

            // Merkezde mi?
            if ((file == 3 || file == 4) && (rank == 0 || rank == 7)) {
                score += modifier * -0.2f;
            }

            // Rok yapmış gibi bir pozisyonda mı? (örnek: g1 / c1 / g8 / c8)
            if ((file == 6 || file == 2) && (rank == 0 || rank == 7)) {
                score += modifier * 0.3f;
            }

            // Önünde piyon var mı?
            int front_rank = king.is_white ? rank - 1 : rank + 1;
            if (front_rank >= 0 && front_rank < 8) {
                for (int df = -1; df <= 1; df++) {
                    int f = file + df;
                    if (f < 0 || f > 7) continue;
                    Piece front = board[front_rank][f];
                    if (front.type == 'p' && front.is_white == king.is_white) {
                        goto safe;
                    }
                }
                score += modifier * -0.25f;
                safe:;
            }
        }
    }

    return score;
}

// EVALUATE ROOK ACTIVITY
float evaluate_rook_activity(Position* pos) {
    Piece (*board)[8] = pos->board;
    float score = 0.0;

    for (int file = 0; file < 8; file++) {
        int white_pawns = 0, black_pawns = 0;

        // Piyon sayısını kontrol et
        for (int rank = 0; rank < 8; rank++) {
            Piece p = board[rank][file];
            if (p.type == 'p') {
                if (p.is_white) white_pawns++;
                else black_pawns++;
            }
        }

        // Kale var mı bu sütunda?
        for (int rank = 0; rank < 8; rank++) {
            Piece p = board[rank][file];
            if (p.type != 'r') continue;

            float modifier = p.is_white ? 1.0f : -1.0f;

            if (white_pawns + black_pawns == 0) {
                // Tam açık hat
                score += modifier * 0.3f;
            } else if ((p.is_white && white_pawns == 0) || (!p.is_white && black_pawns == 0)) {
                // Yarı açık hat
                score += modifier * 0.15f;
            }
        }
    }

    return score;
}

// EVALUATE BOARD
float evaluate_board(Position* pos) {
    float score = 0.0;

    score += evaluate_material(pos);
    score += evaluate_pawn_structure(pos);
    score += evaluate_center_control(pos);
    score += evaluate_development(pos);
    score += evaluate_king_safety(pos);
    score += evaluate_rook_activity(pos);

    return score;
}
