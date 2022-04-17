/* filename: pi.c*/
#include <stdlib.h>
#include <math.h>
#include "chessenv.h"

#include "board.h"
#include "move.h"
#include "gen.h"

static T Env;

void reset_env(T* env, int n) {
    bb_init();
    for (int i = 0; i < n; i++){
        board_reset(&env->boards[i]);
    }

    env->N = n;
}

void print_board(T *env) {
    for (int i = 0; i < env->N; i++){
        board_print(&env->boards[i]);
    }
}

void get_boards(T *env, int* boards) {

    int idx = 0;
    for (int i = 0; i < env->N; i++){

        Board board  = env->boards[i];

        // Get pieces
        for (int rank = 7; rank >= 0; rank--) {
            for (int file = 0; file < 8; file++) {

                char c;

                int piece = board.squares[RF(rank, file)];

                switch (PIECE(piece)) {
                    case EMPTY:  c = '.'; break;
                    case PAWN:   c = 'P'; break;
                    case KNIGHT: c = 'N'; break;
                    case BISHOP: c = 'B'; break;
                    case ROOK:   c = 'R'; break;
                    case QUEEN:  c = 'Q'; break;
                    case KING:   c = 'K'; break;
                };

                if (COLOR(piece)) {
                    c |= 0x20;
                }

                int s = 0;
                switch (c) {
                    case 'P':       s = 1; break;
                    case 'N':       s = 2; break;
                    case 'B':       s = 3; break;
                    case 'R':       s = 4; break;
                    case 'Q':       s = 5; break;
                    case 'K':       s = 6; break;
                    case 'p':       s = 7; break;
                    case 'n':       s = 8; break;
                    case 'b':       s = 9; break;
                    case 'r':       s = 10; break;
                    case 'q':       s = 11; break;
                    case 'k':       s = 12; break;
                };

                if (board.ep == BIT(RF(rank, file))) {
                    s = 13;
                }

                boards[idx] = s;
                ++idx;
            }
        }

        // Get side to move
        if (board.color == WHITE) {
            boards[idx] = 1;
        }
        ++idx;

        // Get castling
        if (board.castle && CASTLE_WHITE_KING) {
            boards[idx] = 1;
        } 
        ++idx;

        if (board.castle && CASTLE_WHITE_QUEEN) {
            boards[idx] = 1;
        }
        ++idx;

        if (board.castle && CASTLE_BLACK_KING) {
            boards[idx] = 1;
        } 
        ++idx;

        if (board.castle && CASTLE_BLACK_QUEEN) {
            boards[idx] = 1;
        }
        ++idx;
    }
}

void step_env(T *env, int *moves) {

    char rows[8] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
    char cols[8] = {'1', '2', '3', '4', '5', '6', '7', '8'};
    char promos[5] = {' ', 'n', 'b', 'r', 'q'};

#pragma omp parallel for
    for (int i = 0; i < (5 * env->N); i += 5) {
        char start_row = rows[moves[i]];
        char start_col = cols[moves[i + 1]];
        char end_row = rows[moves[i + 2]];
        char end_col = cols[moves[i + 3]];
        char promo = promos[moves[i + 4]];

        char move_str[5] = {start_row, start_col, end_row, end_col, promo};

        Move move;
        move_from_string(&move, move_str);
        make_move(&env->boards[i/5], &move);
    }
}

void step_random_move_env(T *env, int *moves) {

#pragma omp parallel for
    for (int i = 0; i < env->N; i++) {
        Move possible_moves[MAX_MOVES];

        int total = gen_moves(&env->boards[i], possible_moves);
        int random_idx = (rand() % (total + 1));
        Move move = possible_moves[random_idx];

        char move_str[10];
        move_to_string(&move, move_str);

        int from_row = move_str[0] - 'a';
        int from_col = move_str[1] - '1';
        int to_row = move_str[2] - 'a';
        int to_col = move_str[3] - '1';
        
        int promotion = 0;
        switch (move_str[4]) {
            case 'n': promotion = 1; break;
            case 'b': promotion = 2; break;
            case 'r': promotion = 3; break;
            case 'q': promotion = 4; break;
        }
        moves[5 * i] = from_row;
        moves[5 * i + 1] = from_col;
        moves[5 * i + 2] = to_row;
        moves[5 * i + 3] = to_col;
        moves[5 * i + 4] = promotion;

        make_move(&env->boards[i], &move);
    }
}
