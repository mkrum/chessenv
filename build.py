from cffi import FFI
import glob

ffibuilder = FFI()

ffibuilder.cdef(
    """
typedef struct {
} Board;

struct Env {
    Board boards[1024];
    size_t N;
};
typedef struct Env Env;

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

void get_mask(Env* env, int *move_mask);
void reset_env(Env* env, int n);
void print_board(Env* env);
void step_env(Env *env, int* moves, int *dones, int *reward);
void get_boards(Env *env, int* boards);
void step_random_move_env(Env *env, int* boards, int *dones);
void generate_random_move(Env *env, int* boards);
void reset_boards(Env *env, int *reset);
void get_possible_moves(Env* env, int*);

void generate_stockfish_move(Env* env, SFArray *sfa, int* moves);
void create_sfarray(SFArray *sfa, int depth, size_t N);
void clean_sfarray(SFArray* arr);

void fen_to_array(int* boards, char *fen);
void array_to_fen(char* fen, int* boards);

void move_str_to_array(int* move_arr, char *move_str);
void array_to_move_str(char* move_str, int* move_arr);

void array_to_possible(int * move_arr, int *board_arr);
void fen_to_possible(int *move_arr, char *fen);

void move_arr_to_int(int *move_int, int*move_arr);
void int_to_move_arr(int *move_int, int*move_arr);
void legal_mask_to_move_arr_mask(int *move_arr_mask, int *legal_mask, int N);
void reset_and_randomize_boards(Env *env, int *reset, int min_rand, int max_rand);
"""
)

ffibuilder.set_source(
    "chessenv_c",
    """
    #include "chessenv.h"
    #include "sfarray.h"
    #include "rep.h"
    #include "move_map.h"
""",
    sources=["src/chessenv.c", "src/sfarray.c", "src/rep.c", "src/move_map.c"],
    include_dirs=["MisterQueen/src/", "MisterQueen/src/deps/tinycthread/", "src/"],
    library_dirs=["/usr/local/lib"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"],
    libraries=["m", "pthread", "misterqueen", "tinycthread"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
