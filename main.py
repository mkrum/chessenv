
import time
from chessenv_c.lib import reset_env, print_board, get_boards, step_env, reset_env, step_random_move_env
from cffi import FFI
import chessenv_c
import numpy as np

ffi = FFI()

class CChessEnv:

    rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    cols= ['1', '2', '3', '4', '5', '6', '7', '8']
    promos = [' ', 'n', 'b', 'r', 'q']

    def __init__(self, n):
        self.n = n
        self._env = chessenv_c.ffi.new("T *")

        self.board_arr = np.zeros(shape=(self.n * 69), dtype=np.int32)
        self.move_arr = np.zeros(shape=(self.n * 69), dtype=np.int32)

    def reset(self):
        reset_env(self._env, self.n)
        return self._get_state()

    def _get_state(self):
        get_boards(self._env, ffi.cast("int *", self.board_arr.ctypes.data))
        return self.board_arr.reshape(self.n, 69)

    def step(self, moves):

        idx = 0
        for move in moves:
            self.move_arr[idx] = self.rows.index(move[0])
            self.move_arr[idx + 1] = self.cols.index(move[1])
    
            self.move_arr[idx + 2] = self.rows.index(move[2])
            self.move_arr[idx + 3] = self.cols.index(move[3])
    
            if len(moves) == 4:
                self.move_arr[idx + 4] = self.promos.index(move[4])
            else:
                self.move_arr[idx + 4] = 0
    
            idx += 5
        step_env(self._env, ffi.cast("int *", self.move_arr.ctypes.data))
        step_random_move_env(self._env, ffi.cast("int *", self.move_arr.ctypes.data))
        return self._get_state()

env = CChessEnv(20)

states = env.reset()

print_board(env._env)

moves = ['e2e4' for _ in range(10)]
states = env.step(moves)

print(states)
print_board(env._env)

