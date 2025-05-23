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

// Forward declarations
void random_step_board(Board *board, int n_moves);
void random_step_board_invert(Board *board, int n_moves);
void board_to_mask(Board *board, int *move_mask);

/** Resets the boards in the environment */
void reset_env(Env* env, int n) {

    bb_init();
    srand(time(0));

    for (size_t i = 0; i < (size_t)n; i++){
        board_reset(&env->boards[i]);

    }
    env->N = n;
}

void invert_env(Env* env, int n) {

    bb_init();
    srand(time(0));

#pragma omp parallel for
    for (size_t i = 0; i < (size_t)n; i++){
        invert_board(&env->boards[i]);

    }
    env->N = n;
}

/** Computes the mask of legal moves for each board. Mask is based on move id
 * */
void get_mask(Env* env, int *move_mask) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++){
        board_to_mask(&env->boards[i], move_mask + i * 64 * OFF_TOTAL);
    }
}

void board_to_mask(Board *board, int *move_mask) {
    Move possible_moves[MAX_MOVES];
    int total_legal = gen_legal_moves(board, possible_moves);

    // Write them to array
    for (int j = 0; j < total_legal; j++) {
        int move_arr[5];
        move_to_array(move_arr, possible_moves[j]);

        int move_int;
        move_arr_to_int(&move_int, move_arr);
        move_mask[move_int] = 1;
    }

}

void board_arr_to_mask(int* board_arr, int *move_mask) {
    Board board;
    array_to_board(&board, board_arr);
    board_to_mask(&board, move_mask);
}


void print_board(Env *env) {
    for (size_t i = 0; i < env->N; i++){
        board_print(&env->boards[i]);
    }
}

/** Returns a board array for the current environment state */
void get_boards(Env *env, int* boards) {
    for (size_t i = 0; i < env->N; i++){
        Board board = env->boards[i];
        board_to_array(boards, board);
        boards += 69;
    }
}


/** Steps the environment forward one step in time */
void step_env(Env *env, int *moves, int *dones, int *reward) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {

        // Convert move id to actual move, apply to board
        Move move;
        int_to_move(&move, moves[i]);
        make_move(&env->boards[i], &move);

        // See if there is a possible response, if not, you win.
        Move possible_moves[MAX_MOVES];
        int total = gen_legal_moves(&env->boards[i], possible_moves);

        dones[i] = (total == 0);
        reward[i] = (total == 0);
    }
}


/** Computes the total possible moves from the current environment state */
void get_possible_moves(Env* env, int* total_moves) {

#pragma omp parallel for
    for (size_t i = 0; i < env->N; i++) {

        // Get possible moves
        Move possible_moves[MAX_MOVES];
        int total_legal = gen_legal_moves(&env->boards[i], possible_moves);

        // Write to array
        int idx = MAX_MOVES * 5 * i;
        for (int j = 0; j < total_legal; j++) {
            move_to_array(&total_moves[idx], possible_moves[j]);
            idx += 5;
        }
    }
}

void reset_boards(Env *env, int *reset) {
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i += 1) {
        if (reset[i] == 1) {
            board_reset(&env->boards[i]);
        }
    }
}

/** Applies a random step to the board */
void random_step_board(Board *board, int n_moves) {

    Move possible_moves[MAX_MOVES];
    for (int i = 0; i < n_moves; i++) {

        int total = gen_legal_moves(board, possible_moves);

        if (total == 0) {
            board_reset(board);
            return random_step_board(board, n_moves);
        }

        int random_idx = rand() % total;
        Move move = possible_moves[random_idx];
        make_move(board, &move);
    }

    int total = gen_legal_moves(board, possible_moves);

    if (total == 0) {
        board_reset(board);
        return random_step_board(board, n_moves);
    }

}

/** Implement random_step_board_invert before it's used */
void random_step_board_invert(Board *board, int n_moves) {
    random_step_board(board, n_moves);

    if (n_moves % 2 == 1) {
        invert_board(board);
    }
}

/** Resets any done boards, applies a random number of moves in [min_rand, max_rand] */
void reset_and_randomize_boards(Env *env, int *reset, int min_rand, int max_rand) {
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i += 1) {
        if (reset[i] == 1) {
            board_reset(&env->boards[i]);
            int num = (rand() % (max_rand - min_rand + 1)) + min_rand;
            random_step_board(&env->boards[i], num);
        }
    }
}

void reset_and_randomize_boards_invert(Env *env, int *reset, int min_rand, int max_rand) {
#pragma omp parallel for
    for (size_t i = 0; i < env->N; i += 1) {
        if (reset[i] == 1) {
            board_reset(&env->boards[i]);
            int num = (rand() % (max_rand - min_rand + 1)) + min_rand;
            random_step_board_invert(&env->boards[i], num);
        }
    }
}

/** Samples a random move for the current environment state  */
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

        move_to_int(&moves[i], move);
    }
}

void step_random_move_env(Env *env, int *moves, int *dones) {
    generate_random_move(env, moves);
    step_env(env, moves, dones, NULL);
}
