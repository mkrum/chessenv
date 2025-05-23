import numpy as np
from cffi import FFI

from chessenv.rep import CBoard
from chessenv_c.lib import invert_array

_ffi = FFI()


def _invert_array(board_arr):
    board_arr = np.int32(board_arr)
    invert_array(
        _ffi.cast("int *", board_arr.ctypes.data),
    )
    return board_arr


def test_invert():
    fen = "Q1b1kbn1/2Pp1p2/2n1p3/p6p/7p/2q4P/1rP1PPP1/RNBK1BNR w KQkq a6"
    board = CBoard.from_fen(fen)
    print(fen)
    print(CBoard.from_array(_invert_array(board.to_array())).to_fen())


if __name__ == "__main__":
    test_invert()
