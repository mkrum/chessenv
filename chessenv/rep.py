
from typing import List
import chess
import numpy as np
from cffi import FFI

from chessenv_c.lib import fen_to_vec

class CMove:

    rows: List[str] = ["a", "b", "c", "d", "e", "f", "g", "h"]
    cols: List[str] = ["1", "2", "3", "4", "5", "6", "7", "8"]
    promos: List[str] = [" ", "n", "b", "r", "q"]

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_str(cls, move_list):
        data = np.zeros(5 * len(move_list), dtype=np.int32)
        idx = 0
        for move in move_list:
            move = list(move)

            if move[0] not in cls.rows:
                move[0] = "a"
            data[idx] = cls.rows.index(move[0])

            if move[1] not in cls.cols:
                move[1] = "1"
            data[idx + 1] = cls.cols.index(move[1])

            if move[2] not in cls.rows:
                move[2] = "a"
            data[idx + 2] = cls.rows.index(move[2])

            if move[3] not in cls.cols:
                move[3] = "1"
            data[idx + 3] = cls.cols.index(move[3])

            if len(move) == 5 and move[4] in cls.promos:
                data[idx + 4] = cls.promos.index(move[4])
            else:
                data[idx + 4] = 0

            idx += 5

        return CMove(data)

    def to_str(self):
        moves = []
        for idx in range(0, self.data.shape[0], 5):
            move = ""
            move += self.rows[int(self.data[idx])]
            move += self.cols[int(self.data[idx + 1])]
            move += self.rows[int(self.data[idx + 2])]
            move += self.cols[int(self.data[idx + 3])]

            if self.data[idx + 4] > 0:
                move += self.promos[int(self.data[idx + 4])]

            moves.append(move)
        return moves

    @classmethod
    def from_arr(cls, arr):
        return cls(arr)


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

        board = chess.Board()
        board._clear_board()

        # Place the pieces, load en-passant
        piece_squares = arr[:64]
        print(piece_squares)
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

        white_castle_king = int(arr[68])
        if white_castle_king == 16:
            castling_fen += "K"
        elif white_castle_king == 17:
            pass
        else:
            raise (ValueError)

        white_castle_queen = int(arr[67])
        if white_castle_queen == 18:
            castling_fen += "Q"
        elif white_castle_queen == 19:
            pass
        else:
            raise (ValueError)

        black_castle_king = int(arr[66])
        if black_castle_king == 20:
            castling_fen += "k"
        elif black_castle_king == 21:
            pass
        else:
            raise (ValueError)

        black_castle_queen = int(arr[65])
        if black_castle_queen == 22:
            castling_fen += "q"
        elif black_castle_queen == 23:
            pass
        else:
            raise (ValueError)

        board.set_castling_fen(castling_fen)
        return cls(board)

    def to_fen(self):
        return self.board.fen()

    @classmethod
    def from_fen(cls, fen_str):
        board = chess.Board(fen_str)
        return cls(board)

    def to_array(self):
        fen = self.to_fen()
        return fen_to_array(fen)

def fen_to_array(fen_str):
    ffi = FFI()
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    char_arr = np.char.array(list(fen_str)).ctypes.data
    x = ffi.new(f"char[{len(fen_str)}]", bytes(fen_str, encoding="utf-8"))
    fen_to_vec(x, ffi.cast("int *", board_arr.ctypes.data))
    ffi.release(x)
    return board_arr
