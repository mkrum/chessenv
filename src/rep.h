#include "move.h"

void fen_to_vec(char* fen, int* boards);
void board_to_fen(char *fen, Board board);
void board_to_vec(Board board, int* boards);

void move_to_array(int* move_arr, Move move);
void array_to_move(Move *move, int* move_arr);
void move_str_to_array(int* move_arr, char *move_str);
void array_to_move_str(char* move_str, int* move_arr);
