#include "board.h"

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
