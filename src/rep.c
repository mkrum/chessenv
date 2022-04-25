
#include "rep.h"
#include "board.h"

void board_to_vec(Board board, int* boards) {
    int idx = 0;
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

            if (board.ep == BIT(RF(rank, file))) {
                printf("Hello!\n");
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

void fen_to_vec(char *fen, int* boards) {
    Board board;
    board_load_fen(&board, fen);
    board_to_vec(board, boards);
}

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
    fen[idx-1] = ' ';

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
    fen[idx] = '\0';
}

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

void array_to_move(Move *move, int* move_arr) {
    char move_str[5];
    array_to_move_str(move_str, move_arr);
    move_from_string(move, move_str);
}

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

void move_to_array(int* move_arr, Move move) {
    char move_str[10];
    move_to_string(&move, move_str);
    move_str_to_array(move_arr, move_str);
}
