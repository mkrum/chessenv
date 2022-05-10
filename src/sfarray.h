
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

void generate_stockfish_move(Env* env, SFArray *sfa, int* moves);
void create_sfarray(SFArray *sfa, int depth);
void clean_sfarray(SFArray *sfa);
void board_arr_to_moves(int *moves, SFArray *sfa, int *boards, size_t N);
void board_arr_to_move_int(int *moves, SFArray *sfa, int *boards, size_t N);
