import time
from dataclasses import dataclass

import chess
from cffi import FFI
import chessenv_c
import numpy as np

from typing import List

from chessenv_c.lib import (
    reset_env,
    print_board,
    get_boards,
    step_env,
    reset_env,
    step_random_move_env,
    generate_random_move,
    fen_to_vec,
    reset_boards,
)


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
            data[idx] = cls.rows.index(move[0])
            data[idx + 1] = cls.cols.index(move[1])

            data[idx + 2] = cls.rows.index(move[2])
            data[idx + 3] = cls.cols.index(move[3])

            if len(move) == 5:
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


class CChessEnv:
    def __init__(self, n):
        self.ffi = FFI()
        self.n = n
        self._env = chessenv_c.ffi.new("T *")

        self.board_arr = np.zeros(shape=(self.n * 69), dtype=np.int32)
        self.move_arr = np.zeros(shape=(self.n * 5), dtype=np.int32)

        self.done_arr = np.zeros(shape=(self.n), dtype=np.int32)

    def reset(self):
        reset_env(self._env, self.n)
        return self._get_state()

    def _get_state(self):
        get_boards(self._env, self.ffi.cast("int *", self.board_arr.ctypes.data))
        return self.board_arr.reshape(self.n, 69)

    def random_sample(self):
        generate_random_move(
            self._env, self.ffi.cast("int *", self.move_arr.ctypes.data)
        )
        return np.copy(self.move_arr)

    def step_arr(self, move_arr):
        self.move_arr = np.copy(move_arr)

        done_one = np.zeros(shape=(self.n), dtype=np.int32)
        done_two = np.zeros(shape=(self.n), dtype=np.int32)

        step_env(
            self._env,
            self.ffi.cast("int *", self.move_arr.ctypes.data),
            self.ffi.cast("int *", done_one.ctypes.data),
        )

        reward = np.copy(done_one)
        step_random_move_env(
            self._env,
            self.ffi.cast("int *", self.move_arr.ctypes.data),
            self.ffi.cast("int *", done_two.ctypes.data),
        )

        reward -= np.copy(done_two)

        total_done = (done_one + done_two) > 0
        total_done = np.int32(total_done)
        reset_boards(self._env, self.ffi.cast("int *", total_done.ctypes.data))

        return self._get_state(), reward, total_done

    def step(self, moves):
        moves = CMove.from_str(moves)
        return step_arr(moves.data)


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

        white_castle_king = int(arr[65])
        if white_castle_king == 16:
            castling_fen += "K"
        elif white_castle_king == 17:
            pass
        else:
            raise (ValueError)

        white_castle_queen = int(arr[66])
        if white_castle_queen == 18:
            castling_fen += "Q"
        elif white_castle_queen == 19:
            pass
        else:
            raise (ValueError)

        black_castle_king = int(arr[67])
        if black_castle_king == 20:
            castling_fen += "k"
        elif black_castle_king == 21:
            pass
        else:
            raise (ValueError)

        black_castle_queen = int(arr[68])
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


def fen_to_array(fen_str):
    ffi = FFI()
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    char_arr = np.char.array(list(fen_str)).ctypes.data
    x = ffi.new(f"char[{len(fen_str)}]", bytes(fen_str, encoding="utf-8"))
    fen_to_vec(x, ffi.cast("int *", board_arr.ctypes.data))
    ffi.release(x)
    return board_arr


if __name__ == "__main__":
    env = CChessEnv(1)
    states = env.reset()

    from stonefish.env import Stockfish

    eng = Stockfish(10)

    dones = np.zeros(2)
    t = 0
    while (not dones[0]) and (t < 100):
        board = CBoard.from_arr(np.copy(states[0]))
        move = str(eng(board.board))
        moves = CMove.from_str([move]).data
        states, rewards, dones = env.step_arr(moves)
        print(rewards)
        t += 1

    print(t)
    eng.quit()
