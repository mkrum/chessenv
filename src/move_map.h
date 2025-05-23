#ifndef MOVE_MAP_H
#define MOVE_MAP_H

#include "move.h"

#define OFF_TOTAL 88

/* Function declarations */
void move_arr_to_int(int *move_int, int *move_arr);
void move_arr_to_move_rep(int *move_rep, int *move_arr);
void int_to_move_arr(int *move_arr, int *move_int_arr);
void int_to_move(Move *move, int move_int);
void move_to_int(int *move_int, Move move);
void legal_mask_to_move_arr_mask(int *move_arr_mask, int *legal_mask, int N);
int offset_to_id(int offset_x, int offset_y, int promo);
void id_to_offset(int unique_id, int* offset_x, int *offset_y, int *promo);
int index_to_offset_id(int index);
int offset_id_to_index(int offset_id);
int move_str_to_rep_int(char *move_str);

#endif /* MOVE_MAP_H */
