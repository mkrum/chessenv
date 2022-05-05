from dataclasses import dataclass

from typing import List
import chess
import numpy as np
from cffi import FFI

from chessenv_c.lib import (
    fen_to_array,
    array_to_fen,
    move_str_to_array,
    array_to_move_str,
    array_to_possible,
    move_arr_to_int,
    int_to_move_arr,
    legal_mask_to_move_arr_mask,
)

_ffi = FFI()


@dataclass(frozen=True)
class CMove:
    """
    Wrapper for move datatypes.

    Implements the conversions between raw numpy arrays, integers, strings.

    Example
    -------
    >>> from chessenv.rep import CMove
    >>> move = CMove.from_str("e2e4")
    >>> move.to_int()
    2925
    >>> move.to_array()
    array([4, 1, 4, 3, 0], dtype=int32)
    >>> move.to_str()
    'e2e4'
    >>> move = CMove.from_int(2925)
    >>> move.to_str()
    'e2e4'
    """

    data: np.array

    @classmethod
    def from_str(cls, move):
        data = _move_str_to_array(move)
        return cls(data)

    def to_str(self):
        return _array_to_move_str(self.data)

    @classmethod
    def from_move(self, move):
        return self.from_str(str(move))

    def to_move(self):
        return chess.Move.from_uci(self.to_str())

    @classmethod
    def from_array(cls, arr):
        return cls(arr)

    def to_array(self):
        return self.data

    @classmethod
    def from_int(cls, move_int):
        return cls(_int_to_move_arr(move_int))

    def to_int(self):
        return _move_arr_to_int(self.data)

@dataclass(frozen=True)
class CBoard:
    """
    Wrapper for board datatypes.

    Implements the conversions between raw numpy arrays, FEN notation, and
    python-chess objects.

    Example
    -------
    >>> from chessenv.rep import CBoard
    >>> import chess
    >>> board = chess.Board()
    >>> board
    Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    >>> cboard = CBoard.from_fen(board.fen())
    >>> cboard.to_array()
    array([10,  8,  9, 11, 12,  9,  8, 10,  7,  7,  7,  7,  7,  7,  7,  7,  0,
            0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,
            1,  1,  1,  1,  1,  4,  2,  3,  5,  6,  3,  2,  4, 14, 22, 20, 18,
            16], dtype=int32)
    >>> cboard.to_fen()
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
    >>> cboard.to_board()
    Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    """

    data: np.array

    @classmethod
    def from_array(cls, arr):
        return cls(arr)

    def to_fen(self):
        return _array_to_fen(self.data)

    @classmethod
    def from_fen(cls, fen_str):
        fen_str = fen_str.replace("-", "")
        return cls(_fen_to_array(fen_str))

    def to_array(self):
        return self.data

    @classmethod
    def from_board(cls, board):
        return cls.from_fen(board.fen())

    def to_board(self):
        fen = self.to_fen()
        return chess.Board(fen)
    
    def to_possible_moves(self):
        # Replace this with a C openmp version
        return CMoves.from_array(_array_to_possible(self.data))

    def __str__(self):
        board = self.to_board()
        return str(board)

    def __repr__(self):
        board = self.to_board()
        return repr(board)



@dataclass(frozen=True)
class CMoves:
    """
    Stack of CMove objects

    Implements the conversions between raw numpy arrays, integers, strings for
    a group of CMoves. Useful for interacting with the environment, which will
    return all of the moves within a single array. See CMove.
    """
    data: np.array

    @classmethod
    def from_int(cls, move_ints):
        return cls(np.concatenate([CMove.from_int(m).to_array() for m in move_ints]))

    def to_int(self):
        cmoves = []
        for i in range(0, self.data.shape[0], 5):
            cmoves.append(CMove(self.data[i : i + 5]).to_int())
        return np.array(cmoves)

    def to_cmoves(self):
        cmoves = []
        for i in range(0, self.data.shape[0], 5):
            cmoves.append(CMove(self.data[i : i + 5]))
        return cmoves

    @classmethod
    def from_cmoves(cls, cmoves):
        return cls(np.concatenate([c.data for c in cmoves]))

    @classmethod
    def from_str(cls, move_list):

        data = np.zeros(5 * len(move_list), dtype=np.int32)
        for (i, move) in enumerate(move_list):
            data[5 * i : 5 * (i + 1)] = _move_str_to_array(move)

        return cls(data)

    def to_str(self):
        moves = []
        for idx in range(0, self.data.shape[0], 5):
            moves.append(_array_to_move_str(self.data[idx : idx + 5]))
        return moves

    def to_move(self):
        return [chess.Move.from_uci(m) for m in self.to_str()]

    @classmethod
    def from_move(self, moves):
        str_list = [str(m) for m in moves]
        return self.from_str(str_list)

    @classmethod
    def from_array(cls, arr):
        return cls(arr)

    def to_array(self):
        return self.data

@dataclass(frozen=True)
class CBoards:
    """
    Stack of CBoard objects

    Implements the conversions between raw numpy arrays, integers, strings for
    a group of CBoards. Useful for interacting with the environment, which will
    return all of the boards within a single array. See CBoard.
    """

    data: np.array

    def to_possible_moves(self):
        moves = []
        for idx in range(0, self.data.shape[0], 69):
            moves.append(
                CMoves.from_array(_array_to_possible(self.data[idx : idx + 69]))
            )
        return moves

    @classmethod
    def from_array(cls, arr):
        return cls(arr)

    def to_fen(self):
        fens = []
        for idx in range(0, self.data.shape[0], 69):
            fens.append(_array_to_fen(self.data[idx : idx + 69]))
        return fens

    @classmethod
    def from_fen(cls, fen_str_list):

        data = np.zeros(69 * len(fen_str_list), dtype=np.int32)
        for (i, idx) in enumerate(range(0, data.shape[0], 69)):
            data[idx : idx + 69] = _fen_to_array(fen_str_list[i])

        return cls(data)

    def to_array(self):
        return self.data

    @classmethod
    def from_board(cls, boards):
        fens = [b.fen() for b in boards]
        return cls.from_fen(fens)

    def to_board(self):
        fens = self.to_fen()
        return [chess.Board(f) for f in fens]

"""
Below is the wrapper code for interacting with the C library. These functions
wrap the underlying C defintion with a function that only operates on numpy
arrays for simplicity. See src/ and build.py
"""

def _fen_to_array(fen_str):
    """ Converts a fen to a board array """
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    x = _ffi.new(f"char[{len(fen_str) + 10}]", bytes(fen_str, encoding="utf-8"))
    fen_to_array(_ffi.cast("int *", board_arr.ctypes.data), _ffi.cast("char *", x))
    _ffi.release(x)
    return board_arr


def _array_to_fen(board_arr):
    """ Converts a board array to fen """
    x = _ffi.new(f"char[512]", bytes("\0" * 512, encoding="utf-8"))
    array_to_fen(_ffi.cast("char *", x), _ffi.cast("int *", board_arr.ctypes.data))
    x_str = _ffi.string(x).decode("utf-8")
    _ffi.release(x)

    pieces, to_move, castling, ep = x_str.split(" ")
    castling = list(castling)
    castling.reverse()
    castling = "".join(castling)

    if len(castling) == 0:
        castling = "-"

    return f"{pieces} {to_move} {castling} {ep}"


def _move_str_to_array(move_str):
    """ Converts string representation of a move ("e2e4") to an array """
    move_arr = np.zeros(shape=(5), dtype=np.int32)
    x = _ffi.new(f"char[10]", bytes(move_str, encoding="utf-8"))
    move_str_to_array(_ffi.cast("int *", move_arr.ctypes.data), _ffi.cast("char *", x))
    _ffi.release(x)
    return move_arr


def _array_to_move_str(move_arr):
    """ Converts move array to a string representation of a move ("e2e4") """
    x = _ffi.new(f"char[10]", bytes("\0" * 10, encoding="utf-8"))
    array_to_move_str(x, _ffi.cast("int *", move_arr.ctypes.data))
    x_str = _ffi.string(x).decode("utf-8")

    # remove possible trailing space
    if x_str[-1] == " ":
        x_str = x_str[:-1]

    _ffi.release(x)
    return x_str


def _array_to_possible(data):
    """ Converts a board array to a move array of the possible moves """
    move_arr = np.zeros(shape=(256 * 5), dtype=np.int32)
    array_to_possible(
        _ffi.cast("int *", move_arr.ctypes.data), _ffi.cast("int*", data.ctypes.data)
    )
    move_arr = move_arr.reshape(256, 5)
    move_arr = move_arr[np.sum(move_arr, axis=1) > 0]
    move_arr = move_arr.flatten()
    return move_arr


def _move_arr_to_int(move_arr):
    """ Converts a move array to a move id """
    move_int = np.zeros(shape=(1,), dtype=np.int32)
    move_arr_to_int(
        _ffi.cast("int *", move_int.ctypes.data),
        _ffi.cast("int*", move_arr.ctypes.data),
    )
    return move_int[0]


def _int_to_move_arr(move_int):
    """ Converts a move id to a move array """
    move_int = np.array([move_int])
    move_arr = np.zeros(shape=(5,), dtype=np.int32)
    int_to_move_arr(
        _ffi.cast("int*", move_arr.ctypes.data),
        _ffi.cast("int *", move_int.ctypes.data),
    )
    return move_arr


def legal_mask_convert(legal_mask):
    """ Converts the id version of the move mask into an array based version """
    n = legal_mask.shape[0]
    legal_mask = legal_mask.flatten()

    move_arr = -np.ones(shape=(n * 256 * 2), dtype=np.int32)

    legal_mask_to_move_arr_mask(
        _ffi.cast("int*", move_arr.ctypes.data),
        _ffi.cast("int *", legal_mask.ctypes.data),
        n,
    )

    move_arr = move_arr.reshape(n, 256, 2)

    move_map = {}

    for i in range(n):
        valid = move_arr[i, move_arr[i, :, 0] > -1]
        valid = np.concatenate((np.zeros((valid.shape[0], 1)), valid), axis=1)
        move_map[i] = valid

    return move_map
