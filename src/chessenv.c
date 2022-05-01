#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <time.h>

#include "chessenv.h"
#include "rep.h"
#include "move_map.h"

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

void get_mask(Env* env, int *move_mask) {
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++){

        Move possible_moves[MAX_MOVES];
        int total_legal = gen_legal_moves(&env->boards[i], possible_moves);

        for (int j = 0; j < total_legal; j++) {
            int move_arr[5];
            move_to_array(move_arr, possible_moves[j]);

            int move_int;
            move_arr_to_int(&move_int, move_arr);
            move_mask[i * 64 * OFF_TOTAL + move_int] = 1;
        }
    }
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
    for (size_t i = 0; i < env->N; i++) {

        Move move;
        int_to_move(&move, moves[i]);
        make_move(&env->boards[i], &move);

        Move possible_moves[MAX_MOVES];
        int total = gen_legal_moves(&env->boards[i], possible_moves);

        dones[i] = (total == 0);
        reward[i] = (total == 0);
    }
}


void get_possible_moves(Env* env, int* total_moves) {

    bb_init();
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

    bb_init();
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {
        Move possible_moves[MAX_MOVES];

        int total = gen_legal_moves(&env->boards[i], possible_moves);

        if (total == 0) {
            continue;
        }

        int random_idx = rand() % total;
        Move move = possible_moves[random_idx];
        
        move_to_int(&moves[i], move);
    }
}

void step_random_move_env(Env *env, int *moves, int *dones) {
    generate_random_move(env, moves);
    step_env(env, moves, dones, NULL);
}
