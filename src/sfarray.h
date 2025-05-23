#ifndef SFARRAY_H
#define SFARRAY_H

#include "chessenv.h"

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

/* Function declarations */
void create_sfpipe(SFPipe *sfpipe);
void clean_sfpipe(SFPipe *pipe);
void create_sfarray(SFArray* sfa, int depth, size_t n_threads);
void clean_sfarray(SFArray* arr);
void get_sf_move(SFPipe *sfpipe, char *fen, int depth, char *move);
void board_arr_to_moves(int* moves, SFArray *sfa, int* boards, size_t N);
void board_arr_to_move_int(int* moves, SFArray *sfa, int* boards, size_t N);
void generate_stockfish_move(Env *env, SFArray *sfa, int* moves);

#endif /* SFARRAY_H */
