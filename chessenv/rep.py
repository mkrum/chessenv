
from dataclasses import dataclass

from typing import List
import chess
import numpy as np
from cffi import FFI

from chessenv_c.lib import fen_to_vec, move_str_to_array, array_to_move_str

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
        for i in range(0, len(self.data), 5):
            cmoves.append(CMove(self.data[5*i:5*(i+1)]))
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

class CBoard:

    piece_symbols = [
        "e",
        "P",
        "N",
        "B",
        "R",
        "Q",
        "K",
        "p",
        "n",
        "b",
        "r",
        "q",
        "k",
        "en",
    ]

    def __init__(self, board):
        self.board = board

    def __str__(self):
        return str(self.board)

    def __repr__(self):
        return repr(self.board)

    @classmethod
    def from_arr(cls, arr):
        board = array_to_board(arr)
        return cls(board)

    def to_fen(self):
        return self.board.fen()

    @classmethod
    def from_fen(cls, fen_str):
        board = chess.Board(fen_str)
        return cls(board)

    def to_array(self):
        fen = self.to_fen()
        return _fen_to_array(fen)

def _fen_to_array(fen_str):
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    x = _ffi.new(f"char[{len(fen_str)}]", bytes(fen_str, encoding="utf-8"))
    fen_to_vec(_ffi.cast("char *", x), _ffi.cast("int *", board_arr.ctypes.data))
    _ffi.release(x)
    return board_arr

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

def array_to_board(array):
    board = chess.Board()
    board._clear_board()

    # Place the pieces, load en-passant
    piece_squares = arr[:64]
    for (i, square) in enumerate(chess.SQUARES_180):

        piece_symbol = cls.piece_symbols[int(piece_squares[i])]

        if piece_symbol == "e":
            continue
        elif piece_symbol == "en":
            board.ep_square = square
        else:
            piece = chess.Piece.from_symbol(piece_symbol)
            board._set_piece_at(square, piece.piece_type, piece.color)

    to_move = int(arr[64])

    if to_move == 14:
        board.turn = chess.WHITE
    elif to_move == 15:
        board.turn = chess.BLACK
    else:
        raise (ValueError)

    castling_fen = ""

    if _castle_fen(arr, 68, 16, 17):
        castling_fen += "K"

    if _castle_fen(arr, 67, 18, 19):
        castling_fen += "Q"

    if _castle_fen(arr, 66, 20, 21):
        castling_fen += "k"

    if _castle_fen(arr, 65, 22, 23):
        castling_fen += "q"

    board.set_castling_fen(castling_fen)
    return board

def _castle_fen(arr, idx, yes_castle, no_castle):
    white_castle_king = int(arr[68])
    if white_castle_king == yes_castle:
        return True
    elif white_castle_king == no_castle:
        return False
    else:
        raise (ValueError)

