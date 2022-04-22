#include "board.h"

typedef struct T T;

struct T {
    Board boards[1024];
    size_t N;
};

struct SFPipe {
    int pid;
    FILE* in;
    FILE* out;
};
typedef struct SFPipe SFPipe;

struct SFArray {
    size_t N;
    int depth;
    SFPipe sfpipe[256];
};
typedef struct SFArray SFArray;

void reset_env(T* env, int n);
void print_board(T *env);
void step_env(T *env, int* moves, int *dones);
void get_boards(T *env, int* boards);
void step_random_move_env(T *env, int* boards, int *dones);
void generate_random_move(T *env, int* boards);
void board_to_vec(Board board, int* boards);
void fen_to_vec(char* fen, int* boards);
void reset_boards(T *env, int *reset);

void board_to_fen(char *fen, Board board);
void generate_stockfish_move(T* env, SFArray *sfa, int* moves);
void create_sfarray(SFArray *sfa, int depth, size_t N);
void clean_sfarray(SFArray *sfa);
