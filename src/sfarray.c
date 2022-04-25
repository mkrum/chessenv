#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <time.h>
#include "chessenv.h"
#include "sfarray.h"

#include "board.h"
#include "move.h" 
#include "gen.h"

void get_sf_move(SFPipe *sfpipe, char * fen, int depth, char *move) {
    char cmd[256];
    char buf[1024];
    char start[5] = { 0 };

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
            //clean_sfpipe(sfpipe);
            //create_sfpipe(sfpipe);

            sprintf(cmd, "position fen %s\n", fen);
            printf("%s\n", cmd);
            exit(1);
            //fwrite(cmd, sizeof(char), strlen(cmd), sfpipe->out);
            //fflush(sfpipe->out);

            //sprintf(cmd, "go depth %i\n", depth);
            //printf("%s\n", cmd);
            //fwrite(cmd, sizeof(char), strlen(cmd), sfpipe->out);
            //fflush(sfpipe->out);

        } else {

            strncpy(start, buf, 4);
            start[5] = '\0';
            strncpy(move, buf+9, 5);
            move[6] = '\0';
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
        
        execl("/nfs/Stockfish/src/stockfish", "stockfish", (char*) NULL);
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
    fclose(pipe->in);
    fclose(pipe->out);
}

void create_sfarray(SFArray* sfa, int depth, size_t N) {
    sfa->N = N;
    sfa->depth = depth;
    for (size_t i = 0; i < N; i++) {
        create_sfpipe(&sfa->sfpipe[i]);
    }
}

void clean_sfarray(SFArray* arr) {
    for (size_t i = 0; i < arr->N; i++) {
        clean_sfpipe(&arr->sfpipe[i]);
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

        int from_row = move_str[0] - 'a';
        int from_col = move_str[1] - '1';
        int to_row = move_str[2] - 'a';
        int to_col = move_str[3] - '1';
        
        int promotion = 0;
        switch (move_str[4]) {
            case 'n': promotion = 1; break;
            case 'b': promotion = 2; break;
            case 'r': promotion = 3; break;
            case 'q': promotion = 4; break;
        }
        moves[5 * i] = from_row;
        moves[5 * i + 1] = from_col;
        moves[5 * i + 2] = to_row;
        moves[5 * i + 3] = to_col;
        moves[5 * i + 4] = promotion;
    }
}
