
#include "move.h"

#define OFF_TOTAL 88

void move_arr_to_int(int *move_int, int*move_arr);
void int_to_move_arr(int *move_int, int*move_arr);
void int_to_move(Move *move, int move_int);
void move_to_int(int *move_int, Move move);
void legal_mask_to_move_arr_mask(int *move_arr_mask, int *legal_mask, int N);
