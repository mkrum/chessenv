import os
import platform

from cffi import FFI

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
void create_sfarray(SFArray *sfa, int depth, size_t n_threads);
void clean_sfarray(SFArray* arr);

void fen_to_array(int* boards, char *fen);
void array_to_fen(char* fen, int* boards);

void move_str_to_array(int* move_arr, char *move_str);
void array_to_move_str(char* move_str, int* move_arr);

void array_to_possible(int * move_arr, int *board_arr);
void parallel_array_to_possible(int *move_arr, int *board_arrs, int n);
void fen_to_possible(int *move_arr, char *fen);

void move_arr_to_int(int *move_int, int*move_arr);
void int_to_move_arr(int *move_int, int*move_arr);
void legal_mask_to_move_arr_mask(int *move_arr_mask, int *legal_mask, int N);
void reset_and_randomize_boards(Env *env, int *reset, int min_rand, int max_rand);

void board_to_inverted_fen(char *fen, Board board);
void array_to_inverted_fen(char* fen, int* boards);

void invert_board(Board *boards);
void invert_array(int *boards);

void invert_env(Env* env, int n);
void reset_and_randomize_boards_invert(Env *env, int *reset, int min_rand, int max_rand);
void board_arr_to_moves(int* moves, SFArray *sfa, int* boards, size_t N);
void board_arr_to_move_int(int *moves, SFArray *sfa, int *boards, size_t N);

void board_arr_to_mask(int* board_arr, int *move_mask);
"""
)

# Get current directory for library path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(current_dir, "lib")

# Determine platform-specific flags
extra_compile_args = []
extra_link_args = []

# We don't need rpath flags since we'll be using dynamic loading
# This makes the package more portable

# Add architecture flag for macOS arm64
if platform.system() == "Darwin" and platform.machine() == "arm64":
    extra_compile_args.append("-arch")
    extra_compile_args.append("arm64")
    extra_link_args.append("-arch")
    extra_link_args.append("arm64")

# Add OpenMP flags for all platforms
# On macOS, we need to ensure libomp is installed (e.g., via 'brew install libomp')
# But for now, let's disable OpenMP on macOS to ensure compilation works
if platform.system() == "Darwin":
    # For now, skip OpenMP on macOS since it requires additional setup
    pass
else:
    # For other platforms, use standard OpenMP flags
    extra_compile_args.append("-fopenmp")
    extra_link_args.append("-fopenmp")

ffibuilder.set_source(
    "chessenv_c",
    """
    #include "chessenv.h"
    #include "sfarray.h"
    #include "rep.h"
    #include "move_map.h"
""",
    sources=[
        "src/chessenv.c",
        "src/sfarray.c",
        "src/rep.c",
        "src/move_map.c",
    ],
    include_dirs=["MisterQueen/src/", "MisterQueen/src/deps/tinycthread/", "src/"],
    library_dirs=[lib_dir],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    libraries=["m", "pthread", "misterqueen"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
