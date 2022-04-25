#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <time.h>
#include "chessenv.h"

#include "board.h"
#include "move.h" 
#include "gen.h"

static T Env;

void reset_env(T* env, int n) {

    bb_init();
    srand(time(0));

    for (int i = 0; i < n; i++){
        board_reset(&env->boards[i]);
    }
    env->N = n;
}

void print_board(T *env) {
    for (int i = 0; i < env->N; i++){
        board_print(&env->boards[i]);
    }
}

void board_to_vec(Board board, int* boards) {
    int idx = 0;
    for (int rank = 7; rank >= 0; rank--) {
        for (int file = 0; file < 8; file++) {
            char c;
            int piece = board.squares[RF(rank, file)];
    
            switch (PIECE(piece)) {
                case EMPTY:  c = '.'; break;
                case PAWN:   c = 'P'; break;
                case KNIGHT: c = 'N'; break;
                case BISHOP: c = 'B'; break;
                case ROOK:   c = 'R'; break;
                case QUEEN:  c = 'Q'; break;
                case KING:   c = 'K'; break;
            };
    
            if (COLOR(piece)) {
                c |= 0x20;
            }
    
            int s = 0;
            switch (c) {
                case 'P':   s = 1; break;
                case 'N':   s = 2; break;
                case 'B':   s = 3; break;
                case 'R':   s = 4; break;
                case 'Q':   s = 5; break;
                case 'K':   s = 6; break;
                case 'p':   s = 7; break;
                case 'n':   s = 8; break;
                case 'b':   s = 9; break;
                case 'r':   s = 10; break;
                case 'q':   s = 11; break;
                case 'k':   s = 12; break;
            };

            if (board.ep == BIT(RF(rank, file))) {
                printf("Hello!\n");
                s = 13;
            }
    
            boards[idx] = s;
            ++idx;
        }
    }
    
    // Get side to move
    if (board.color == WHITE) {
        boards[idx] = 14;
    } else {
        boards[idx] = 15;
    }
    ++idx;

    int castle = board.castle; 
    if (castle >= 8) {
        boards[idx] = 22;
        castle -= 8;
    } else {
        boards[idx] = 23;
    }
    idx++;

    if (castle >= 4) {
        boards[idx] = 20;
        castle -= 4;
    } else {
        boards[idx] = 21;
    }
    idx++;

    if (castle >= 2) {
        boards[idx] = 18;
        castle -= 2;
    } else {
        boards[idx] = 19;
    }
    idx++;

    if (castle >= 1) {
        boards[idx] = 16;
    } else {
        boards[idx] = 17;
    }
    idx++;
    
}

void fen_to_vec(char *fen, int* boards) {
    Board board;
    board_load_fen(&board, fen);
    board_to_vec(board, boards);
}


void get_boards(T *env, int* boards) {
    int idx = 0;
    for (size_t i = 0; i < env->N; i++){
        Board board = env->boards[i];
        board_to_vec(board, boards);
        boards += 69;
    }
}

void step_env(T *env, int *moves, int *dones, int *reward) {

    char rows[8] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
    char cols[8] = {'1', '2', '3', '4', '5', '6', '7', '8'};
    char promos[5] = {' ', 'n', 'b', 'r', 'q'};

//#pragma omp parallel for
    for (size_t i = 0; i < env->N; i += 1) {

        char start_row = rows[moves[5 * i]];
        char start_col = cols[moves[5 * i + 1]];
        char end_row = rows[moves[5 * i + 2]];
        char end_col = cols[moves[5 * i + 3]];
        char promo = promos[moves[5 * i + 4]];

        char move_str[5] = {start_row, start_col, end_row, end_col, promo};

        Move move;
        move_from_string(&move, move_str);
        Move possible_moves[MAX_MOVES];

        int total_legal = gen_legal_moves(&env->boards[i], possible_moves);

        int legal = 0;
        for (int i = 0; i < total_legal; i++) {
            if ((move.src == possible_moves[i].src) && (move.dst == possible_moves[i].dst)) {
                legal = 1;
            }
        }

        Undo undo;
        if (legal) {
            do_move(&env->boards[i], &move, &undo);

            int total = gen_legal_moves(&env->boards[i], possible_moves);
            dones[i] = (total == 0);
            reward[i] = (total == 0);

        } else {
            // just a dummy move
            do_move(&env->boards[i], &possible_moves[0], &undo);

            reward[i] = -1;
            dones[i] = 1;
        }

    }
}

void get_possible_moves(T* env, int* total_moves) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {

        Move possible_moves[MAX_MOVES];
        int total_legal = gen_legal_moves(&env->boards[i], possible_moves);

        int idx = MAX_MOVES * 5 * i;

        for (int i = 0; i < total_legal; i++) {
            char move_str[10];
            move_to_string(&possible_moves[i], move_str);

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
            total_moves[idx] = from_row;
            total_moves[idx + 1] = from_col;
            total_moves[idx + 2] = to_row;
            total_moves[idx + 3] = to_col;
            total_moves[idx + 4] = promotion;
            idx += 5;
        }
    }
}

void reset_boards(T *env, int *reset) {
    for (size_t i = 0; i < env->N; i += 1) {
        if (reset[i] == 1) {
            board_reset(&env->boards[i]);
        }
    }
}

void generate_random_move(T *env, int *moves) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {
        Move possible_moves[MAX_MOVES];

        int total = gen_legal_moves(&env->boards[i], possible_moves);

        if (total == 0) {
            continue;
        }

        int random_idx = rand() % total;
        Move move = possible_moves[random_idx];

        char move_str[10];
        move_to_string(&move, move_str);

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

void step_random_move_env(T *env, int *moves, int *dones) {
    generate_random_move(env, moves);
    step_env(env, moves, dones, NULL);
}

void board_to_fen(char *fen, Board board) {
    
    int idx = 0;
    
    int blank_count = 0;
    for (int rank = 7; rank >= 0; rank--) {
        for (int file = 0; file < 8; file++) {

            int piece_int = board.squares[RF(rank, file)];
            int piece = PIECE(piece_int);

            if (piece == EMPTY) {
                blank_count++;
            } else {
                if (blank_count > 0) {
                    fen[idx] = blank_count + '0'; 
                    idx++;
                    blank_count = 0;
                }
                switch (PIECE(piece_int)) {
                    case PAWN:   fen[idx] = 'P'; break;
                    case KNIGHT: fen[idx] = 'N'; break;
                    case BISHOP: fen[idx] = 'B'; break;
                    case ROOK:   fen[idx] = 'R'; break;
                    case QUEEN:  fen[idx] = 'Q'; break;
                    case KING:   fen[idx] = 'K'; break;
                };

                if (COLOR(piece_int)) {
                    fen[idx] |= 0x20;
                }

                idx++;

            }
        }

        if (blank_count > 0) {
            fen[idx] = blank_count + '0'; 
            idx++;
            blank_count = 0;
        }

        fen[idx] = '/';
        idx++;
    }
    fen[idx-1] = ' ';

    if (board.color == WHITE) {
        fen[idx] = 'w';
    } else {
        fen[idx] = 'b';
    }
    ++idx;

    fen[idx] = ' ';
    ++idx;
   
    int castle = board.castle; 
    if (castle >= 8) {
        fen[idx] = 'q';
        idx++;
        castle -= 8;
    }
    if (castle >= 4) {
        fen[idx] = 'k';
        idx++;
        castle -= 4;
    }
    if (castle >= 2) {
        fen[idx] = 'Q';
        idx++;
        castle -= 2;
    }
    if (castle >= 1) {
        fen[idx] = 'K';
        idx++;
    }
    fen[idx] = '\0';
}

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

void generate_stockfish_move(T *env, SFArray *sfa, int* moves) {

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

int main(int argc, char *argv) {
    char *pos = "4k2r/6r1/8/8/8/8/3R4/R3K3 w KQqk - 0 1";
    Board board;
    board_load_fen(&board, pos);

    char test[256];
    board_to_fen(test, board);
    printf("%s\n", test);
}
