from cffi import FFI
import glob

ffibuilder = FFI()

ffibuilder.cdef(
    """
typedef struct T T;

typedef unsigned long long bb;

typedef struct {
    int squares[64];
    int color;
    int castle;
    int white_material;
    int black_material;
    int white_position;
    int black_position;
    bb ep;
    bb all;
    bb white;
    bb black;
    bb white_pawns;
    bb black_pawns;
    bb white_knights;
    bb black_knights;
    bb white_bishops;
    bb black_bishops;
    bb white_rooks;
    bb black_rooks;
    bb white_queens;
    bb black_queens;
    bb white_kings;
    bb black_kings;
    bb hash;
    bb pawn_hash;
} Board;

struct T {
    Board boards[1024];
    size_t N;
};

void reset_env(T* env, int n);
void get_boards(T *env, int* boards);
void print_board(T *env);
void step_env(T *env, int* moves, int* dones);
void step_random_move_env(T *env, int* moves, int* dones);
void generate_random_move(T *env, int* moves);
void fen_to_vec(char* fen, int* boards);
"""
)

ffibuilder.set_source(
    "chessenv_c",
    """
    #include "chessenv.h"
""",
    sources=["chessenv.c"],
    include_dirs=["MisterQueen/src/", "./MisterQueen/src/deps/tinycthread/"],
    library_dirs=["/usr/local/lib"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"],
    libraries=["m", "pthread", "misterqueen", "tinycthread"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
