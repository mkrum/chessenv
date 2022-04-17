/* filename: pi.c*/
#include <stdlib.h>
#include <math.h>
#include "chessenv.h"
#include "board.h"

static T myStruct;

T get_test() {
    Board b;
    board_reset(&b);
    T new_struct;
    new_struct.board = b;
    return new_struct;
}

void print_board(T board_struct) {
    board_print(&board_struct.board);
}

