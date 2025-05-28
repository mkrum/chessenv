#ifndef CHESSENV_H
#define CHESSENV_H

#include "../MisterQueen/src/board.h"

struct Env {
    Board boards[1024];
    size_t N;
};
typedef struct Env Env;

void get_mask(Env* env, int *move_mask);
void reset_env(Env* env, int n);
void print_board(Env* env);
void step_env(Env *env, int* moves, int *dones, int *reward);
void get_boards(Env *env, int* boards);
void step_random_move_env(Env *env, int* boards, int *dones);
void generate_random_move(Env *env, int* boards);
void reset_boards(Env *env, int *reset);
void get_possible_moves(Env* env, int*);
void reset_and_randomize_boards(Env *env, int *reset, int min_rand, int max_rand);
void invert_env(Env* env, int n);
void reset_and_randomize_boards_invert(Env *env, int *reset, int min_rand, int max_rand);

void board_arr_to_mask(int* board_arr, int *move_mask);
void board_to_mask(Board* board, int *move_mask);

#endif /* CHESSENV_H */
