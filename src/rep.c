
#include <stdlib.h>
#include <stdio.h>

#include "rep.h"
#include "board.h"
#include "gen.h"

void invert_board(Board *board) {
    char fen[512];
    board_to_inverted_fen(fen, *board);
    board_load_fen(board, fen);
}

void invert_array(int *board_arr) {
    Board board;
    board_reset(&board);
    array_to_board(&board, board_arr);
    invert_board(&board);
    board_to_array(board_arr, board);
}

/* Converts a Board type into a board array */
void board_to_array(int* boards, Board board) {
    int idx = 0;
    for (int rank = 7; rank >= 0; rank--) {
        for (int file = 0; file < 8; file++) {
            // Get piece map
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
                case 'P':   s = 1; break;
                case 'N':   s = 2; break;
                case 'B':   s = 3; break;
                case 'R':   s = 4; break;
                case 'Q':   s = 5; break;
                case 'K':   s = 6; break;
                case 'p':   s = 7; break;
                case 'n':   s = 8; break;
                case 'b':   s = 9; break;
                case 'r':   s = 10; break;
                case 'q':   s = 11; break;
                case 'k':   s = 12; break;
            };

            if (board.ep == (long long int)BIT(RF(rank, file))) {
                s = 13;
            }

            boards[idx] = s;
            ++idx;
        }
    }

    // Get side to move
    if (board.color == WHITE) {
        boards[idx] = 14;
    } else {
        boards[idx] = 15;
    }
    ++idx;

    // Get casling setup
    int castle = board.castle;
    if (castle >= 8) {
        boards[idx] = 22;
        castle -= 8;
    } else {
        boards[idx] = 23;
    }
    idx++;

    if (castle >= 4) {
        boards[idx] = 20;
        castle -= 4;
    } else {
        boards[idx] = 21;
    }
    idx++;

    if (castle >= 2) {
        boards[idx] = 18;
        castle -= 2;
    } else {
        boards[idx] = 19;
    }
    idx++;

    if (castle >= 1) {
        boards[idx] = 16;
    } else {
        boards[idx] = 17;
    }
    idx++;

}

/* Converts raw array type into a Board type */
void array_to_board(Board *board, int* board_arr) {

    board_clear(board);

    int idx = 0;
    for (int rank = 7; rank >= 0; rank--) {
        for (int file = 0; file < 8; file++) {
            switch (board_arr[idx]) {
                case 1: board_set(board, RF(rank, file), WHITE_PAWN); break;
                case 2: board_set(board, RF(rank, file), WHITE_KNIGHT); break;
                case 3: board_set(board, RF(rank, file), WHITE_BISHOP); break;
                case 4: board_set(board, RF(rank, file), WHITE_ROOK); break;
                case 5: board_set(board, RF(rank, file), WHITE_QUEEN); break;
                case 6: board_set(board, RF(rank, file), WHITE_KING); break;
                case 7: board_set(board, RF(rank, file), BLACK_PAWN); break;
                case 8: board_set(board, RF(rank, file), BLACK_KNIGHT); break;
                case 9: board_set(board, RF(rank, file), BLACK_BISHOP); break;
                case 10: board_set(board, RF(rank, file), BLACK_ROOK); break;
                case 11: board_set(board, RF(rank, file), BLACK_QUEEN); break;
                case 12: board_set(board, RF(rank, file), BLACK_KING); break;
                case 13: board->ep = BIT(RF(rank, file));
                         board->hash ^= HASH_EP[LSB(board->ep) % 8];
                         board->pawn_hash ^= HASH_EP[LSB(board->ep) % 8];
                         break;
                case 0 : break;
            }
            idx++;
        }
    }

    if (board_arr[idx] == 14) {
        board->color = WHITE;
    } else if (board_arr[idx] == 15) {
        board->color = BLACK;
    } else {
        printf("1\n");
        printf("%i\n", board_arr[idx]);
        exit(1);
    }
    idx++;

    board->castle = 0;
    if (board_arr[idx] == 22) {
        board->castle |= CASTLE_BLACK_QUEEN;
    } else if (board_arr[idx] != 23) {
        printf("2");
        exit(1);
    }
    idx++;
    if (board_arr[idx] == 20) {
        board->castle |= CASTLE_BLACK_KING;
    } else if (board_arr[idx] != 21) {
        printf("3");
        exit(1);
    }
    idx++;
    if (board_arr[idx] == 18) {
        board->castle |= CASTLE_WHITE_QUEEN;
    } else if (board_arr[idx] != 19) {
        printf("4");
        exit(1);
    }
    idx++;
    if (board_arr[idx] == 16) {
        board->castle |= CASTLE_WHITE_KING;
    } else if (board_arr[idx] != 17) {
        printf("5");
        exit(1);
    }
    idx++;
    board->hash ^= HASH_CASTLE[CASTLE_ALL];
    board->hash ^= HASH_CASTLE[board->castle];
    board->pawn_hash ^= HASH_CASTLE[CASTLE_ALL];
    board->pawn_hash ^= HASH_CASTLE[board->castle];
}

/* Converts fen string into an array */
void fen_to_array(int* boards, char *fen) {
    Board board;
    board_load_fen(&board, fen);
    board_to_array(boards, board);
}

/* Converts array into fen string */
void array_to_fen(char *fen, int *boards) {
    Board board;
    array_to_board(&board, boards);
    board_to_fen(fen, board);
}

void array_to_fen_noep(char *fen, int *boards) {
    Board board;
    array_to_board(&board, boards);
    board_to_fen_noep(fen, board);
}

void array_to_inverted_fen(char *fen, int *boards) {
    Board board;
    array_to_board(&board, boards);
    board_to_inverted_fen(fen, board);
}

/* Converts Board type into fen string */
void board_to_fen(char *fen, Board board) {

    int idx = 0;

    int blank_count = 0;
    for (int rank = 7; rank >= 0; rank--) {
        for (int file = 0; file < 8; file++) {

            int piece_int = board.squares[RF(rank, file)];
            int piece = PIECE(piece_int);

            if (piece == EMPTY) {
                blank_count++;
            } else {
                if (blank_count > 0) {
                    fen[idx] = blank_count + '0';
                    idx++;
                    blank_count = 0;
                }
                switch (PIECE(piece_int)) {
                    case PAWN:   fen[idx] = 'P'; break;
                    case KNIGHT: fen[idx] = 'N'; break;
                    case BISHOP: fen[idx] = 'B'; break;
                    case ROOK:   fen[idx] = 'R'; break;
                    case QUEEN:  fen[idx] = 'Q'; break;
                    case KING:   fen[idx] = 'K'; break;
                };

                if (COLOR(piece_int)) {
                    fen[idx] |= 0x20;
                }

                idx++;

            }
        }

        if (blank_count > 0) {
            fen[idx] = blank_count + '0';
            idx++;
            blank_count = 0;
        }

        fen[idx] = '/';
        idx++;
    }
    idx--;
    fen[idx] = ' ';
    idx++;

    if (board.color == WHITE) {
        fen[idx] = 'w';
    } else {
        fen[idx] = 'b';
    }
    ++idx;

    fen[idx] = ' ';
    ++idx;

    int castle = board.castle;
    if (castle >= 8) {
        fen[idx] = 'q';
        idx++;
        castle -= 8;
    }
    if (castle >= 4) {
        fen[idx] = 'k';
        idx++;
        castle -= 4;
    }
    if (castle >= 2) {
        fen[idx] = 'Q';
        idx++;
        castle -= 2;
    }
    if (castle >= 1) {
        fen[idx] = 'K';
        idx++;
    }

    fen[idx] = ' ';
    ++idx;

    if (board.ep == 0) {
        fen[idx] = '-';
        idx++;
    } else {
        for (int rank = 0; rank < 8; rank++) {
            for (int file = 0; file < 8; file++) {
                if (board.ep == (long long int)BIT(RF(rank, file))) {
                    fen[idx] = 'a' + file;
                    idx++;
                    fen[idx] = '1' + rank;
                    idx++;
                    break;
                }
            }
        }
    }
    fen[idx] = '\0';
}

/* Converts array intro move string */
void array_to_move_str(char* move_str, int* move_arr) {
    char rows[8] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
    char cols[8] = {'1', '2', '3', '4', '5', '6', '7', '8'};
    char promos[5] = {' ', 'n', 'b', 'r', 'q'};

    move_str[0] = rows[move_arr[0]];
    move_str[1] = cols[move_arr[1]];
    move_str[2] = rows[move_arr[2]];
    move_str[3] = cols[move_arr[3]];
    move_str[4] = promos[move_arr[4]];
}

/* Converts move array into Move */
void array_to_move(Move *move, int* move_arr) {
    char move_str[5];
    array_to_move_str(move_str, move_arr);
    move_from_string(move, move_str);
}

/* Converts move string into array */
void move_str_to_array(int* move_arr, char *move_str) {

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

    move_arr[0] = from_row;
    move_arr[1] = from_col;
    move_arr[2] = to_row;
    move_arr[3] = to_col;
    move_arr[4] = promotion;
}

/* Converts Move into an array */
void move_to_array(int* move_arr, Move move) {
    char move_str[10];
    move_to_string(&move, move_str);
    move_str_to_array(move_arr, move_str);
}

/* Converts a move array into an array of possible moves */
void array_to_possible(int *move_arr, int *board_arr) {
    // Create a board from the array
    bb_init();
    Board board;
    array_to_board(&board, board_arr);

    // Generate legal moves
    Move possible_moves[MAX_MOVES];
    int total_legal = gen_legal_moves(&board, possible_moves);

    // Convert moves to array format
    int idx = 0;
    for (int i = 0; i < total_legal; i++) {
        move_to_array(&move_arr[idx], possible_moves[i]);
        idx += 5;
    }

    // Zero out the rest of the buffer
    for (int i = idx; i < MAX_MOVES * 5; i++) {
        move_arr[i] = 0;
    }
}

/*
 * Converts multiple board arrays into their respective possible moves in parallel
 *
 * Parameters:
 * move_arr - Preallocated buffer for all moves, size should be n * MAX_MOVES * 5 integers
 * board_arrs - Array of board arrays, each 69 integers
 * n - Number of boards to process
 *
 * NOTE: This implementation has a known limitation: it does not correctly generate
 * en passant capture moves. If your application requires accurate en passant move
 * generation, use array_to_possible for individual boards instead.
 */
void parallel_array_to_possible(int *move_arr, int *board_arrs, int n) {
    bb_init();  // Make sure bitboards are initialized

    // Try to parallelize with OpenMP if available
    #if defined(_OPENMP)
    #pragma omp parallel for
    #endif
    for (int i = 0; i < n; i++) {
        // Create a board from the array
        Board board;
        array_to_board(&board, board_arrs + i * 69);

        // Generate legal moves
        Move possible_moves[MAX_MOVES];
        int total_legal = gen_legal_moves(&board, possible_moves);

        // Calculate offset for this board's moves in the output array
        int move_offset = i * MAX_MOVES * 5;

        // Write all legal moves to the output array
        for (int j = 0; j < total_legal; j++) {
            move_to_array(&move_arr[move_offset + j * 5], possible_moves[j]);
        }

        // If there are fewer than MAX_MOVES legal moves, zero out the rest
        // This marks the end of the move list for this board
        for (int j = total_legal * 5; j < MAX_MOVES * 5; j++) {
            move_arr[move_offset + j] = 0;
        }
    }
}

/* Converts a fen string into an array of possible moves */
void fen_to_possible(int *move_arr, char *fen) {
    bb_init();
    Board board;
    board_load_fen(&board, fen);

    Move possible_moves[MAX_MOVES];
    int total_legal = gen_legal_moves(&board, possible_moves);

    /* DEBUG - Check if en passant square is set */
    int has_ep = board.ep != 0;

    int idx = 0;
    for (int i = 0; i < total_legal; i++) {
        char move_str[10];
        move_to_array(&move_arr[idx], possible_moves[i]);
        idx += 5;
    }

    /* Initialize any remaining move entries to zero */
    for (int i = idx; i < MAX_MOVES * 5; i++) {
        move_arr[i] = 0;
    }
}


void board_to_inverted_fen(char *fen, Board board) {

    int idx = 0;
    int blank_count = 0;

    /// Start at bottom and work backwards
    for (int rank = 0; rank < 8; rank++) {
        for (int file = 0; file < 8; file++) {

            int piece_int = board.squares[RF(rank, file)];
            int piece = PIECE(piece_int);

            if (piece == EMPTY) {
                blank_count++;
            } else {
                if (blank_count > 0) {
                    fen[idx] = blank_count + '0';
                    idx++;
                    blank_count = 0;
                }
                switch (PIECE(piece_int)) {
                    case PAWN:   fen[idx] = 'P'; break;
                    case KNIGHT: fen[idx] = 'N'; break;
                    case BISHOP: fen[idx] = 'B'; break;
                    case ROOK:   fen[idx] = 'R'; break;
                    case QUEEN:  fen[idx] = 'Q'; break;
                    case KING:   fen[idx] = 'K'; break;
                };

                // Invert the inversion
                if (!COLOR(piece_int)) {
                    fen[idx] |= 0x20;
                }

                idx++;
            }
        }

        if (blank_count > 0) {
            fen[idx] = blank_count + '0';
            idx++;
            blank_count = 0;
        }

        fen[idx] = '/';
        idx++;
    }
    idx--;
    fen[idx] = ' ';
    idx++;

    // Flip these
    if (board.color == WHITE) {
        fen[idx] = 'b';
    } else {
        fen[idx] = 'w';
    }
    ++idx;

    fen[idx] = ' ';
    ++idx;

    int castle = board.castle;
    if (castle >= 8) {
        fen[idx] = 'Q';
        idx++;
        castle -= 8;
    }
    if (castle >= 4) {
        fen[idx] = 'K';
        idx++;
        castle -= 4;
    }
    if (castle >= 2) {
        fen[idx] = 'q';
        idx++;
        castle -= 2;
    }
    if (castle >= 1) {
        fen[idx] = 'k';
        idx++;
    }

    fen[idx] = ' ';
    ++idx;

    if (board.ep == 0) {
        fen[idx] = '-';
        idx++;
    } else {
        for (int rank = 0; rank < 8; rank++) {
            for (int file = 0; file < 8; file++) {
                if (board.ep == (long long int)BIT(RF(rank, file))) {
                    fen[idx] = 'a' + file;
                    idx++;
                    fen[idx] = '8' - rank;
                    idx++;
                    break;
                }
            }
        }
    }
    fen[idx] = '\0';
}

void board_to_fen_noep(char *fen, Board board) {

    int idx = 0;

    int blank_count = 0;
    for (int rank = 7; rank >= 0; rank--) {
        for (int file = 0; file < 8; file++) {

            int piece_int = board.squares[RF(rank, file)];
            int piece = PIECE(piece_int);

            if (piece == EMPTY) {
                blank_count++;
            } else {
                if (blank_count > 0) {
                    fen[idx] = blank_count + '0';
                    idx++;
                    blank_count = 0;
                }
                switch (PIECE(piece_int)) {
                    case PAWN:   fen[idx] = 'P'; break;
                    case KNIGHT: fen[idx] = 'N'; break;
                    case BISHOP: fen[idx] = 'B'; break;
                    case ROOK:   fen[idx] = 'R'; break;
                    case QUEEN:  fen[idx] = 'Q'; break;
                    case KING:   fen[idx] = 'K'; break;
                };

                if (COLOR(piece_int)) {
                    fen[idx] |= 0x20;
                }

                idx++;

            }
        }

        if (blank_count > 0) {
            fen[idx] = blank_count + '0';
            idx++;
            blank_count = 0;
        }

        fen[idx] = '/';
        idx++;
    }
    idx--;
    fen[idx] = ' ';
    idx++;

    if (board.color == WHITE) {
        fen[idx] = 'w';
    } else {
        fen[idx] = 'b';
    }
    ++idx;

    fen[idx] = ' ';
    ++idx;

    int castle = board.castle;
    if (castle >= 8) {
        fen[idx] = 'q';
        idx++;
        castle -= 8;
    }
    if (castle >= 4) {
        fen[idx] = 'k';
        idx++;
        castle -= 4;
    }
    if (castle >= 2) {
        fen[idx] = 'Q';
        idx++;
        castle -= 2;
    }
    if (castle >= 1) {
        fen[idx] = 'K';
        idx++;
    }

    fen[idx] = ' ';
    ++idx;

    fen[idx] = '-';
    idx++;
    fen[idx] = '\0';
}
