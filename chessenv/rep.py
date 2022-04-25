
from dataclasses import dataclass

from typing import List
import chess
import numpy as np
from cffi import FFI

from chessenv_c.lib import fen_to_array, array_to_fen, move_str_to_array, array_to_move_str

_ffi = FFI()

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

@dataclass(frozen=True)
class CMoves:

    data: np.array

    def to_cmoves(self):
        cmoves = []
        for i in range(0, self.data.shape[0], 5):
            cmoves.append(CMove(self.data[i:i+5]))
        return cmoves
    
    @classmethod
    def from_cmoves(cls, cmoves):
        return cls(np.concatenate([c.data for c in cmoves]))

    @classmethod
    def from_str(cls, move_list):

        data = np.zeros(5 * len(move_list), dtype=np.int32)
        for (i, move) in enumerate(move_list):
            data[5*i : 5*(i+1)] = _move_str_to_array(move)

        return cls(data)

    def to_str(self):
        moves = []
        for idx in range(0, self.data.shape[0], 5):
            moves.append(_array_to_move_str(self.data[idx:idx+5]))
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
class CBoard:
    
    data: np.array

    def __str__(self):
        board = self.to_board()
        return str(board)

    def __repr__(self):
        board = self.to_board()
        return repr(board)

    @classmethod
    def from_arr(cls, arr):
        return cls(arr)

    def to_fen(self):
        fen = _array_to_fen(self.data)
        pieces, to_move, castling, ep = fen.split(" ")
        castling = list(castling)
        castling.reverse()
        castling = ''.join(castling)
        return f'{pieces} {to_move} {castling} {ep}'

    @classmethod
    def from_fen(cls, fen_str):
        return cls(_fen_to_array(fen_str))

    def to_array(self):
        return self.data

    @classmethod
    def from_board(cls, board):
        return self.from_fen(board.fen())

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
    x = _ffi.new(f"char[512]", bytes('\0' * 512, encoding="utf-8"))
    array_to_fen(_ffi.cast("char *", x), _ffi.cast("int *", board_arr.ctypes.data))
    x_str = _ffi.string(x).decode("utf-8")
    _ffi.release(x)
    return x_str

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
