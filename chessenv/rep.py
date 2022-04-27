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
)

_ffi = FFI()


def square_to_ints(square):
    cols = ["a", "b", "c", "d", "e", "f", "g", "h"]
    col, row = list(square)
    col = cols.index(col)
    row = int(row) - 1
    return row, col


def move_to_array(move_str):
    from_square = move_str[:2]
    to_square = move_str[2:4]
    promos = ["r", "b", "n", "q"]
    promo_int = 0
    if len(move_str) == 5:
        promo_int = promos.index(move_str[5])

    return np.array(
        [*square_to_ints(from_square), *square_to_ints(to_square), promo_int]
    )


def get_offset(move_arr):
    return (move_arr[0] - move_arr[2], move_arr[1] - move_arr[3])


def pair_to_sum(x, y, z):
    return x * 10000 + (y + 8) * 100 + z


def sum_to_pair(sum_val):
    x = sum_val // 10000
    y = (sum_val - x * 10000) // 100
    z = sum_val - ((x * 10000) + (y * 100))
    return (x, y - 8, z)


unique_offsets = []
for x in range(-7, 8):
    if x != 0:
        unique_offsets.append((x, 0, 0))
        unique_offsets.append((0, x, 0))
        unique_offsets.append((x, x, 0))
        unique_offsets.append((x, -1 * x, 0))

unique_offsets.append((2, 1, 0))
unique_offsets.append((2, -1, 0))
unique_offsets.append((1, 2, 0))
unique_offsets.append((-1, 2, 0))
unique_offsets.append((-2, 1, 0))
unique_offsets.append((-2, -1, 0))
unique_offsets.append((1, -2, 0))
unique_offsets.append((-1, -2, 0))

for promo in [1, 2, 3, 4]:
    unique_offsets.append((0, 1, promo))
    unique_offsets.append((1, 1, promo))
    unique_offsets.append((-1, 1, promo))
    unique_offsets.append((0, -1, promo))
    unique_offsets.append((1, -1, promo))
    unique_offsets.append((-1, -1, promo))

unique_offsets = list(map(lambda x: pair_to_sum(*x), unique_offsets))

TOTAL_OFF = 88

def move_to_int(move_str):
    move = CMove.from_str(move_str)
    move_arr = move.to_array()
    promo = move_arr[-1]
    offset_x, offset_y = get_offset(move_arr)
    return (
        (8 * move_arr[0] + move_arr[1]) * len(unique_offsets)
    ) + unique_offsets.index(pair_to_sum(offset_x, offset_y, promo))


def int_to_move(move_int):

    first_int = move_int // TOTAL_OFF
    move_arr = np.int32(np.zeros(5))
    move_arr[0] = first_int // 8
    move_arr[1] = first_int - (8 * move_arr[0])

    second_int = move_int - first_int * len(unique_offsets)

    x_offset, y_offset, promo = sum_to_pair(unique_offsets[second_int])
    move_arr[2] = move_arr[0] - x_offset
    move_arr[3] = move_arr[1] - y_offset
    move_arr[4] = promo

    return CMove.from_array(move_arr).to_str()


@dataclass(frozen=True)
class CMove:

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
class CMoves:

    data: np.array

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


@dataclass(frozen=True)
class CBoard:

    data: np.array

    def to_possible_moves(self):
        # Replace this with a C openmp version
        return CMoves.from_array(_array_to_possible(self.data))

    def __str__(self):
        board = self.to_board()
        return str(board)

    def __repr__(self):
        board = self.to_board()
        return repr(board)

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


def _fen_to_array(fen_str):
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    x = _ffi.new(f"char[{len(fen_str) + 10}]", bytes(fen_str, encoding="utf-8"))
    fen_to_array(_ffi.cast("int *", board_arr.ctypes.data), _ffi.cast("char *", x))
    _ffi.release(x)
    return board_arr


def _array_to_fen(board_arr):
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
    move_arr = np.zeros(shape=(5), dtype=np.int32)
    x = _ffi.new(f"char[10]", bytes(move_str, encoding="utf-8"))
    move_str_to_array(_ffi.cast("int *", move_arr.ctypes.data), _ffi.cast("char *", x))
    _ffi.release(x)
    return move_arr


def _array_to_move_str(move_arr):
    x = _ffi.new(f"char[10]", bytes("\0" * 10, encoding="utf-8"))
    array_to_move_str(x, _ffi.cast("int *", move_arr.ctypes.data))
    x_str = _ffi.string(x).decode("utf-8")

    # remove possible trailing space
    if x_str[-1] == " ":
        x_str = x_str[:-1]

    _ffi.release(x)
    return x_str


def _array_to_possible(data):
    move_arr = np.zeros(shape=(256 * 5), dtype=np.int32)
    array_to_possible(
        _ffi.cast("int *", move_arr.ctypes.data), _ffi.cast("int*", data.ctypes.data)
    )
    move_arr = move_arr.reshape(256, 5)
    move_arr = move_arr[np.sum(move_arr, axis=1) > 0]
    move_arr = move_arr.flatten()
    return move_arr


def _move_arr_to_int(move_arr):
    move_int = np.zeros(shape=(1,), dtype=np.int32)
    move_arr_to_int(
        _ffi.cast("int *", move_int.ctypes.data),
        _ffi.cast("int*", move_arr.ctypes.data),
    )
    return move_int[0]


def _int_to_move_arr(move_int):
    move_int = np.array([move_int])
    move_arr = np.zeros(shape=(5,), dtype=np.int32)
    int_to_move_arr(
        _ffi.cast("int*", move_arr.ctypes.data),
        _ffi.cast("int *", move_int.ctypes.data),
    )
    return move_arr
