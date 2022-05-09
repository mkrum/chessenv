
from dataclasses import dataclass

from cffi import FFI
from chessenv_c.lib import (
    create_sfarray,
    clean_sfarray,
    board_arr_to_moves,
)
import chessenv_c
import numpy as np

from chessenv.rep import CBoard

_ffi = FFI()

class SFArray:

    def __init__(self, depth):
        self.depth = depth
        self._sfa = chessenv_c.ffi.new("SFArray *")
        create_sfarray(self._sfa, self.depth)

    def get_moves(self, board_arr):
        N = board_arr.shape[0]
        board_arr = np.int32(board_arr.flatten())
        move = np.zeros(2 * N, dtype=np.int32)
        board_arr_to_moves(_ffi.cast("int *", move.ctypes.data), self._sfa, _ffi.cast("int *", board_arr.ctypes.data), N)
        move = move.reshape(N, 2)
        move = np.concatenate((np.zeros((move.shape[0], 1)), move), axis=1)
        return move
    
    def __del__(self):
        clean_sfarray(self._sfa)
