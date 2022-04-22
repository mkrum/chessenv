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
    fen_to_vec,
    reset_boards,
    create_sfarray,
    clean_sfarray,
)

from chessenv.rep import CMove, CBoard


class CChessEnv:
    def __init__(self, n):
        self.ffi = FFI()
        self.n = n
        self._env = chessenv_c.ffi.new("T *")

        self.board_arr = np.zeros(shape=(self.n * 69), dtype=np.int32)
        self.move_arr = np.zeros(shape=(self.n * 5), dtype=np.int32)

        self.done_arr = np.zeros(shape=(self.n), dtype=np.int32)

    def reset(self):
        reset_env(self._env, self.n)
        return self._get_state()

    def _get_state(self):
        get_boards(self._env, self.ffi.cast("int *", self.board_arr.ctypes.data))
        return self.board_arr.reshape(self.n, 69)

    def random_sample(self):
        generate_random_move(
            self._env, self.ffi.cast("int *", self.move_arr.ctypes.data)
        )
        return np.copy(self.move_arr)

    def stockfish_sample(self, sfa):
        generate_stockfish_move(
            self._env, sfa, self.ffi.cast("int *", self.move_arr.ctypes.data)
        )
        return np.copy(self.move_arr)

    def step_arr(self, move_arr):
        self.move_arr = np.copy(move_arr)

        done_one = np.zeros(shape=(self.n), dtype=np.int32)
        done_two = np.zeros(shape=(self.n), dtype=np.int32)

        step_env(
            self._env,
            self.ffi.cast("int *", self.move_arr.ctypes.data),
            self.ffi.cast("int *", done_one.ctypes.data),
        )

        reward = np.copy(done_one)

        step_random_move_env(
            self._env,
            self.ffi.cast("int *", self.move_arr.ctypes.data),
            self.ffi.cast("int *", done_two.ctypes.data),
        )

        reward -= np.copy(done_two)

        total_done = (done_one + done_two) > 0
        total_done = np.int32(total_done)
        reset_boards(self._env, self.ffi.cast("int *", total_done.ctypes.data))

        return self._get_state(), reward, total_done

    def step(self, moves):
        moves = CMove.from_str(moves)
        return step_arr(moves.data)


def fen_to_array(fen_str):
    ffi = FFI()
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    char_arr = np.char.array(list(fen_str)).ctypes.data
    x = ffi.new(f"char[{len(fen_str)}]", bytes(fen_str, encoding="utf-8"))
    fen_to_vec(x, ffi.cast("int *", board_arr.ctypes.data))
    ffi.release(x)
    return board_arr


if __name__ == "__main__":
    sfa = chessenv_c.ffi.new("SFArray *")

    N = 8

    create_sfarray(sfa, N, N)

    env = CChessEnv(N)
    states = env.reset()

    dones = np.zeros(N)
    t = 0
    while (t < 1000): #(not dones[0]) and (t < 100):
        board = CBoard.from_arr(np.copy(states[0]))
        moves = env.stockfish_sample(sfa)
        states, rewards, dones = env.step_arr(moves)
        print(rewards)
        t += 1

    print(t)
    clean_sfarray(sfa)
