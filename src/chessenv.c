#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <time.h>

#include "chessenv.h"
#include "rep.h"

#include "board.h"
#include "move.h" 
#include "gen.h"

void reset_env(Env* env, int n) {

    bb_init();
    srand(time(0));

    for (int i = 0; i < n; i++){
        board_reset(&env->boards[i]);
    }
    env->N = n;
}

void print_board(Env *env) {
    for (int i = 0; i < env->N; i++){
        board_print(&env->boards[i]);
    }
}


void get_boards(Env *env, int* boards) {
    int idx = 0;
    for (size_t i = 0; i < env->N; i++){
        Board board = env->boards[i];
        board_to_array(boards, board);
        boards += 69;
    }
}

void step_env(Env *env, int *moves, int *dones, int *reward) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i += 1) {

        Move move;
        array_to_move(&move, &moves[5 * i]);

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

void get_possible_moves(Env* env, int* total_moves) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {

        Move possible_moves[MAX_MOVES];
        int total_legal = gen_legal_moves(&env->boards[i], possible_moves);

        int idx = MAX_MOVES * 5 * i;

        for (int i = 0; i < total_legal; i++) {
            char move_str[10];
            move_to_array(&total_moves[idx], possible_moves[i]);
            idx += 5;
        }
    }
}

void reset_boards(Env *env, int *reset) {
    for (size_t i = 0; i < env->N; i += 1) {
        if (reset[i] == 1) {
            board_reset(&env->boards[i]);
        }
    }
}

void generate_random_move(Env *env, int *moves) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {
        Move possible_moves[MAX_MOVES];

        int total = gen_legal_moves(&env->boards[i], possible_moves);

        if (total == 0) {
            continue;
        }

        int random_idx = rand() % total;
        Move move = possible_moves[random_idx];
        move_to_array(&moves[5 * i], move);
    }
}

void step_random_move_env(Env *env, int *moves, int *dones) {
    generate_random_move(env, moves);
    step_env(env, moves, dones, NULL);
}
