import numpy as np
from cffi import FFI

import chessenv_c
from chessenv_c.lib import (
    board_arr_to_move_int,
    board_arr_to_moves,
    clean_sfarray,
    create_sfarray,
)

_ffi = FFI()


class SFArray:

    def __init__(self, depth, n_threads=0):
        self.depth = depth
        self._sfa = chessenv_c.ffi.new("SFArray *")
        # The third parameter specifies how many Stockfish instances to create
        # If n_threads is 0, it will use a reasonable default based on CPU cores
        create_sfarray(self._sfa, self.depth, n_threads)

    def get_moves(self, board_arr):
        N = board_arr.shape[0]
        board_arr = np.int32(board_arr.flatten())
        move = np.zeros(2 * N, dtype=np.int32)
        board_arr_to_moves(
            _ffi.cast("int *", move.ctypes.data),
            self._sfa,
            _ffi.cast("int *", board_arr.ctypes.data),
            N,
        )
        move = move.reshape(N, 2)
        move = np.concatenate((np.zeros((move.shape[0], 1)), move), axis=1)
        return move

    def get_move_ints(self, board_arr):
        N = board_arr.shape[0]
        board_arr = np.int32(board_arr.flatten())
        move = np.zeros(N, dtype=np.int32)
        board_arr_to_move_int(
            _ffi.cast("int *", move.ctypes.data),
            self._sfa,
            _ffi.cast("int *", board_arr.ctypes.data),
            N,
        )
        return move

    def __del__(self):
        clean_sfarray(self._sfa)
