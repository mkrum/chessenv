
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
void create_sfarray(SFArray *sfa, int depth, size_t N);
void clean_sfarray(SFArray *sfa);
