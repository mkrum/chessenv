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

# Get platform and architecture information
system = platform.system()
machine = platform.machine()

# Platform specific flags
if system == "Darwin":
    # macOS specific settings
    if machine == "arm64":
        # Apple Silicon (M1/M2)
        extra_compile_args.extend(["-arch", "arm64"])
        extra_link_args.extend(["-arch", "arm64"])
    else:
        # Intel Mac
        extra_compile_args.extend(["-arch", "x86_64"])
        extra_link_args.extend(["-arch", "x86_64"])

    # OpenMP is tricky on macOS
    # Assume users have installed libomp via brew
    # extra_compile_args.append("-Xpreprocessor -fopenmp")
    # extra_link_args.append("-lomp")
    pass  # For now, skip OpenMP on macOS

elif system == "Linux":
    # Linux specific settings
    if machine == "x86_64":
        # Intel/AMD 64-bit
        extra_compile_args.append("-m64")
    elif machine == "aarch64" or machine == "arm64":
        # ARM 64-bit
        pass  # Default flags are fine

    # Add OpenMP flags for Linux
    extra_compile_args.append("-fopenmp")
    extra_link_args.append("-fopenmp")

elif system == "Windows":
    # Windows specific settings will need MSVC flags
    # This is just a placeholder, Windows build would need more setup
    pass

ffibuilder.set_source(
    "fastchessenv_c",
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
    include_dirs=[
        "MisterQueen/src/",
        "MisterQueen/src/deps/tinycthread/",
        "src/",
        os.path.join(current_dir, "MisterQueen", "src"),
        os.path.join(current_dir, "MisterQueen", "src", "deps", "tinycthread"),
    ],
    library_dirs=[lib_dir],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    libraries=["m", "pthread", "misterqueen"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
