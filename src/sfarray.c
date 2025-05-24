#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <time.h>
#include <sys/wait.h> /* For waitpid */

/* Handle OpenMP conditionally */
#ifdef _OPENMP
#include <omp.h>
#define HAVE_OPENMP 1
#else
/* Define OpenMP functions as no-ops for platforms without OpenMP */
#define HAVE_OPENMP 0
static inline int omp_get_thread_num() { return 0; }
static inline void omp_set_num_threads(int num) { (void)num; }
#endif

#include "chessenv.h"
#include "sfarray.h"
#include "move_map.h"
#include "rep.h"

#include "board.h"
#include "move.h"
#include "gen.h"

void get_sf_move(SFPipe *sfpipe, char * fen, int depth, char *move) {
    char cmd[256];
    char buf[1024];
    char start[6] = { 0 }; // Increased to 6 for null terminator

    sprintf(cmd, "position fen %s\n", fen);
    fwrite(cmd, sizeof(char), strlen(cmd), sfpipe->out);
    fflush(sfpipe->out);

    sprintf(cmd, "go depth %i\n", depth);
    fwrite(cmd, sizeof(char), strlen(cmd), sfpipe->out);
    fflush(sfpipe->out);

    // not ideal...
    while (strcmp(start, "best") != 0) {

        if (!fgets(buf, 1024, sfpipe->in)) {

	    fprintf(stderr, "Stockfish failed on: %s\n", fen);
	    exit(1);

        } else {
            strncpy(start, buf, 4);
            start[4] = '\0'; // Make sure it's null-terminated
            strncpy(move, buf+9, 5);
            move[5] = '\0'; // Ensure null termination
        }
    }
}

void create_sfpipe(SFPipe *sfpipe) {
    int in_pipe_f[2];
    int out_pipe_f[2];

    pipe(in_pipe_f);
    pipe(out_pipe_f);

    int pid = fork();
    if (pid == 0) {
        dup2(out_pipe_f[0], STDIN_FILENO);
        dup2(in_pipe_f[1], STDOUT_FILENO);
        dup2(in_pipe_f[1], STDERR_FILENO);

        execlp("stockfish", "stockfish", (char*) NULL);

        fprintf(stderr, "Failed to find stockfish executable\n");
        exit(1);
    }

    close(out_pipe_f[0]);
    close(in_pipe_f[1]);

    sfpipe->pid = pid;
    sfpipe->in = fdopen(in_pipe_f[0], "r");
    sfpipe->out = fdopen(out_pipe_f[1], "w");
}

void clean_sfpipe(SFPipe *pipe) {
    kill(pipe->pid, SIGKILL);
    waitpid(pipe->pid, NULL, 0);
    fclose(pipe->in);
    fclose(pipe->out);
}

void create_sfarray(SFArray* sfa, int depth, size_t n_threads) {
    // Default to 4 threads/pipes if not specified
    size_t num_threads = 4;

    // If n_threads is provided and valid, use it
    if (n_threads > 0) {
        num_threads = n_threads;
    } else {
        #ifdef _OPENMP
        // Otherwise use the number of available processors if OpenMP is available
        num_threads = omp_get_num_procs();
        if (num_threads > 8) num_threads = 8;  // Cap at 8 to avoid too many stockfish instances
        if (num_threads < 1) num_threads = 1;  // Ensure at least 1 thread
        #endif
    }

    // Cap at 256 which is the max size of sfpipe array
    if (num_threads > 256) num_threads = 256;

    omp_set_num_threads(num_threads);
    sfa->N = num_threads;
    sfa->depth = depth;

    // Print OpenMP status
    printf("OpenMP Status: %s\n", HAVE_OPENMP ? "Enabled" : "Disabled");
    printf("Number of threads: %zu\n", num_threads);

    #ifdef _OPENMP
    printf("OpenMP Version: %d\n", _OPENMP);
    printf("Max threads available: %d\n", omp_get_max_threads());
    #endif

    for (size_t i = 0; i < sfa->N; i++) {
        create_sfpipe(&sfa->sfpipe[i]);
    }
}

void clean_sfarray(SFArray* arr) {
    for (size_t i = 0; i < arr->N; i++) {
        clean_sfpipe(&arr->sfpipe[i]);
    }
}

void board_arr_to_moves(int* moves, SFArray *sfa, int* boards, size_t N) {
#pragma omp parallel for
    for (size_t i = 0; i < N; i++) {
        // Use thread_id modulo number of Stockfish instances
        int thread_id = omp_get_thread_num() % sfa->N;

        char fen[512];
        array_to_fen_noep(fen, &boards[i * 69]);
        // Unused variable 'len' removed

        char move_str[10];
        get_sf_move(&sfa->sfpipe[thread_id], fen, sfa->depth, move_str);

        int move_arr[5];
        move_str_to_array(move_arr, move_str);
        move_arr_to_move_rep(&moves[2 * i], move_arr);
    }
}

void board_arr_to_move_int(int* moves, SFArray *sfa, int* boards, size_t N) {
#pragma omp parallel for
    for (size_t i = 0; i < N; i++) {
        // Use thread_id modulo number of Stockfish instances
        int thread_id = omp_get_thread_num() % sfa->N;

        char fen[512];
        array_to_fen_noep(fen, &boards[i * 69]);
        // Unused variable 'len' removed

        char move_str[10];
        get_sf_move(&sfa->sfpipe[thread_id], fen, sfa->depth, move_str);

        int move_arr[5];
        move_str_to_array(move_arr, move_str);
        move_arr_to_int(&moves[i], move_arr);
    }
}

void generate_stockfish_move(Env *env, SFArray *sfa, int* moves) {
    // When OpenMP is disabled, this section runs sequentially
    // but still distributes environments across available Stockfish instances
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {
        // Use modulo to wrap around if we have more environments than Stockfish instances
        int sf_idx = i % sfa->N;

        char fen[512];
        char move_str[10];

        Board board = env->boards[i];
        board_to_fen(fen, board);

        get_sf_move(&sfa->sfpipe[sf_idx], fen, sfa->depth, move_str);

        int move_arr[5];
        move_str_to_array(move_arr, move_str);

        move_arr_to_int(&moves[i], move_arr);
    }
}
