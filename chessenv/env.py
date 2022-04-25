import time
from dataclasses import dataclass

import chess
from cffi import FFI
import chessenv_c
import numpy as np

from typing import List

from chessenv_c.lib import (
    reset_env,
    print_board,
    get_boards,
    step_env,
    reset_env,
    step_random_move_env,
    generate_random_move,
    generate_stockfish_move,
    reset_boards,
    create_sfarray,
    clean_sfarray,
    get_possible_moves,
)

from chessenv.rep import CMove, CBoard


class CChessEnv:
    def __init__(self, n, max_step=100, draw_reward=0):
        self.ffi = FFI()
        self.n = n
        self.max_step = max_step
        self.draw_reward = draw_reward
        self._env = chessenv_c.ffi.new("T *")

        self.board_arr = np.zeros(shape=(self.n * 69), dtype=np.int32)
        self.move_arr = np.zeros(shape=(self.n * 5), dtype=np.int32)
        self.done_arr = np.zeros(shape=(self.n), dtype=np.int32)
        self.reward_arr = np.zeros(shape=(self.n), dtype=np.int32)
        self.t = np.zeros(self.n)

    def reset(self):
        self.t = np.zeros(self.n)
        reset_env(self._env, self.n)
        return self._get_state()

    def _get_state(self):
        get_boards(self._env, self.ffi.cast("int *", self.board_arr.ctypes.data))
        return self.board_arr.reshape(self.n, 69)

    def random(self):
        generate_random_move(
            self._env, self.ffi.cast("int *", self.move_arr.ctypes.data)
        )
        return np.copy(self.move_arr)

    def sample_opponent(self):
        return self.random()

    def step_arr(self, move_arr):
        self.move_arr = np.copy(move_arr)

        done_one = np.zeros(shape=(self.n), dtype=np.int32)
        done_two = np.zeros(shape=(self.n), dtype=np.int32)

        my_reward = np.zeros(shape=(self.n), dtype=np.int32)
        their_reward = np.zeros(shape=(self.n), dtype=np.int32)

        step_env(
            self._env,
            self.ffi.cast("int *", self.move_arr.ctypes.data),
            self.ffi.cast("int *", done_one.ctypes.data),
            self.ffi.cast("int *", my_reward.ctypes.data),
        )

        self.move_arr = self.sample_opponent()

        step_env(
            self._env,
            self.ffi.cast("int *", self.move_arr.ctypes.data),
            self.ffi.cast("int *", done_two.ctypes.data),
            self.ffi.cast("int *", their_reward.ctypes.data),
        )

        reward = my_reward - (1 - done_one) * (their_reward)

        self.t += 1

        reward[(self.t > self.max_step)] = self.draw_reward

        total_done = ((done_one + done_two) > 0) | (self.t > self.max_step)
        total_done = np.int32(total_done)
        self.t[(total_done == 1)] = 0

        reset_boards(self._env, self.ffi.cast("int *", total_done.ctypes.data))

        return self._get_state(), reward, total_done

    def get_possible(self):
        possible_moves = -np.ones(shape=(self.n * 256 * 5), dtype=np.int32)
        real_poss = -np.ones(shape=(self.n, 256, 5), dtype=np.int32)
        get_possible_moves(
            self._env, self.ffi.cast("int *", possible_moves.ctypes.data)
        )

        for i in range(self.n):
            real_poss[i] = possible_moves[256 * 5 * i : 256 * 5 * (i + 1)].reshape(
                256, 5
            )

        return real_poss

    def step(self, moves):
        moves = CMove.from_str(moves)
        return self.step_arr(moves.data)


class SFCChessEnv(CChessEnv):
    def __init__(self, n, depth):
        super().__init__(n)
        self._sfa = chessenv_c.ffi.new("SFArray *")
        create_sfarray(self._sfa, depth, n)

    def sample_opponent(self):
        generate_stockfish_move(
            self._env, self._sfa, self.ffi.cast("int *", self.move_arr.ctypes.data)
        )
        return np.copy(self.move_arr)

    def __del__(self):
        clean_sfarray(self._sfa)


if __name__ == "__main__":

    N = 5
    env = CChessEnv(N)  # , 1)

    states = env.reset()

    print(possible_moves[0])
    print(possible_moves[1])

    exit()

    dones = np.zeros(N)
    t = 0
    while t < 1000:
        board = CBoard.from_arr(np.copy(states[0]))
        moves = env.random()
        states, rewards, dones = env.step_arr(moves)
        print(rewards[dones == 1])
        t += 1

    print(t)
