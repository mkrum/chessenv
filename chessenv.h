#include "board.h"

typedef struct T T;

struct T {
    Board boards[1024];
    size_t N;
};

void reset_env(T* env, int n);
void print_board(T *env);
void step_env(T *env, int* moves, int *dones);
void get_boards(T *env, int* boards);
void step_random_move_env(T *env, int* boards, int *dones);
void generate_random_move(T *env, int* boards);
void board_to_vec(Board board, int* boards);
void fen_to_vec(char* fen, int* boards);
void reset_boards(T *env, int *reset);
