import time
from dataclasses import dataclass

import chess
from cffi import FFI
import chessenv_c
import numpy as np

from typing import List

from chessenv_c.lib import (
    reset_env,
    get_boards,
    step_env,
    reset_env,
    generate_random_move,
    generate_stockfish_move,
    reset_boards,
    create_sfarray,
    clean_sfarray,
    get_possible_moves,
)

from chessenv.rep import CMoves, CBoards


class CChessEnv:
    def __init__(self, n, max_step=100, draw_reward=0):
        self.ffi = FFI()
        self.n = n
        self.max_step = max_step
        self.draw_reward = draw_reward
        self._env = chessenv_c.ffi.new("Env *")

        self.t = np.zeros(self.n)

    def _make_board_arr(self):
        return np.zeros(shape=(self.n * 69), dtype=np.int32)

    def _make_move_arr(self):
        return np.zeros(shape=(self.n * 5), dtype=np.int32)

    def _make_vec_arr(self):
        return np.zeros(shape=(self.n), dtype=np.int32)

    def reset(self):
        self.t = np.zeros(self.n)
        reset_env(self._env, self.n)
        return self.get_state()

    def get_state(self):
        board_arr = self._make_board_arr()
        get_boards(self._env, self.ffi.cast("int *", board_arr.ctypes.data))
        return board_arr.reshape(self.n, 69)

    def random(self):
        move_arr = self._make_move_arr()
        generate_random_move(self._env, self.ffi.cast("int *", move_arr.ctypes.data))
        return move_arr

    def sample_opponent(self):
        return self.random()

    def push_moves(self, move_arr):
        done = self._make_vec_arr()
        reward = self._make_vec_arr()

        self.t += 1

        step_env(
            self._env,
            self.ffi.cast("int *", move_arr.ctypes.data),
            self.ffi.cast("int *", done.ctypes.data),
            self.ffi.cast("int *", reward.ctypes.data),
        )

        reset_boards(self._env, self.ffi.cast("int *", done.ctypes.data))
        return done, reward

    def step_arr(self, move_arr):

        done_one, my_reward = self.push_moves(move_arr)
        response = self.sample_opponent()
        done_two, their_reward = self.push_moves(response)

        reward = my_reward - (1 - done_one) * (their_reward)
        reward[(self.t > self.max_step)] = self.draw_reward

        total_done = ((done_one + done_two) > 0) | (self.t > self.max_step)
        total_done = np.int32(total_done)
        self.t[(total_done == 1)] = 0

        reset_boards(self._env, self.ffi.cast("int *", total_done.ctypes.data))

        return self.get_state(), reward, total_done

    def get_possible_moves(self):
        move_arr = np.zeros(shape=(self.n * 5 * 256), dtype=np.int32)
        get_possible_moves(self._env, self.ffi.cast("int *", move_arr.ctypes.data))
        move_arr = move_arr.reshape(self.n, 256, 5)

        moves = []
        for i in range(self.n):
            valid_moves = move_arr[i, np.sum(move_arr[i], axis=1) > 0]
            moves.append(CMoves.from_array(valid_moves.flatten()))

        return moves

    def step(self, moves):
        moves = CMoves.from_str(moves)
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
