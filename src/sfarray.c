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
#else
/* Define OpenMP functions as no-ops for platforms without OpenMP */
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
            // Try again?
            clean_sfpipe(sfpipe);
            create_sfpipe(sfpipe);

            sprintf(cmd, "position fen %s\n", fen);
            printf("%s", cmd);

            move[0] = 'e';
            move[1] = '2';
            move[2] = 'e';
            move[3] = '4';
            move[4] = ' ';
            move[5] = '\0';
            break;
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
        
        execl("/home/michael/stockfish/src/stockfish", "stockfish", (char*) NULL);
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

void create_sfarray(SFArray* sfa, int depth) {
    omp_set_num_threads(4);
    sfa->N = 4;
    sfa->depth = depth;

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
        int thread_id = omp_get_thread_num();

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
        int thread_id = omp_get_thread_num();

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
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {
        char fen[512];
        char move_str[10];
        
        Board board = env->boards[i];
        board_to_fen(fen, board);

        get_sf_move(&sfa->sfpipe[i], fen, sfa->depth, move_str);

        int move_arr[5];
        move_str_to_array(move_arr, move_str);

        move_arr_to_int(&moves[i], move_arr);
    }
}