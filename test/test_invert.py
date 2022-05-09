
from chessenv.rep import CBoard
from chessenv_c.lib import invert_array
import numpy as np

from cffi import FFI

_ffi = FFI()

def _invert_array(board_arr):
    board_arr = np.int32(board_arr)
    invert_array(
        _ffi.cast("int *", board_arr.ctypes.data),
    )
    return board_arr


def test_invert():
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    board = CBoard.from_fen(fen)
    print(fen)
    print(CBoard.from_array(_invert_array(board.to_array())).to_fen())

if __name__ == '__main__':
    test_invert()
