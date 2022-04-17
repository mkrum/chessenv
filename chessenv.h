#include "board.h"

typedef struct T T;

struct T {
    Board boards[1024];
    size_t N;
};

void reset_env(T* env, int n);
void print_board(T *env);
void step_env(T *env, int* moves);
void get_boards(T *env, int* boards);
