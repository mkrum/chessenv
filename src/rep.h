#include "move.h"

void fen_to_array(int* boards, char *fen);
void array_to_fen(char* fen, int* boards);
void board_to_fen(char *fen, Board board);
void board_to_array(int* boards, Board board);
void array_to_board(Board *board, int* boards);

void move_to_array(int* move_arr, Move move);
void array_to_move(Move *move, int* move_arr);
void move_str_to_array(int* move_arr, char *move_str);
void array_to_move_str(char* move_str, int* move_arr);

void fen_to_possible(int * move_arr, char *fen);
void array_to_possible(int * move_arr, int *board_arr);
