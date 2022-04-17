from cffi import FFI
import glob
ffibuilder = FFI()

ffibuilder.cdef("""
typedef struct T T;
typedef struct Board Board;
struct Board {};

struct T {
    Board board;
};

T get_test();
void print_board(T board_struct);
"""
)

ffibuilder.set_source("chessenv_c", 
"""
    #include "chessenv.h"
""",
    sources=['chessenv.c'],
    include_dirs=["MisterQueen/src/", "./MisterQueen/src/deps/tinycthread/"],
    library_dirs=["/usr/local/lib"],
    libraries=['m', 'pthread', 'misterqueen', 'tinycthread'])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
