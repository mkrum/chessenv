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
void get_boards(T *env, int* boards);
void print_board(T *env);
void step_env(T *env, int* moves, int* dones, int* rewards);
void step_random_move_env(T *env, int* moves, int* dones);
void generate_random_move(T *env, int* moves);
void fen_to_vec(char* fen, int* boards);
void reset_boards(T *env, int *reset);

void board_to_fen(char *fen, Board board);
void generate_stockfish_move(T* env, SFArray *sfa, int* moves);
void create_sfarray(SFArray *sfa, int depth, size_t N);
void clean_sfarray(SFArray* arr);
void get_possible_moves(T* env, int* total_moves);
"""
)

ffibuilder.set_source(
    "chessenv_c",
    """
    #include "chessenv.h"
""",
    sources=["src/chessenv.c"],
    include_dirs=["MisterQueen/src/", "MisterQueen/src/deps/tinycthread/", "src/"],
    library_dirs=["/usr/local/lib"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"],
    libraries=["m", "pthread", "misterqueen", "tinycthread"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
