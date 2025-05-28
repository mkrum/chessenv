from dataclasses import dataclass

import chess
import numpy as np
from cffi import FFI

from chessenv_c.lib import (
    array_to_fen,
    array_to_move_str,
    array_to_possible,
    board_arr_to_mask,
    fen_to_array,
    int_to_move_arr,
    legal_mask_to_move_arr_mask,
    move_arr_to_int,
    move_str_to_array,
    parallel_array_to_possible,
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
        # Check if array contains floats - if so, convert to int32 or raise error
        arr_np = np.asarray(arr)
        if not np.issubdtype(arr_np.dtype, np.integer):
            # If all values are effectively integers (no decimal part), convert them
            if np.all(np.equal(arr_np, arr_np.astype(np.int32))):
                arr_np = arr_np.astype(np.int32)
            else:
                raise ValueError(
                    f"Moves array must contain integer values, received {arr_np.dtype}. "
                    "Values must be convertible to integers without loss of information."
                )
        return cls(arr_np)

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
        # Check if array contains floats - if so, convert to int32 or raise error
        arr_np = np.asarray(arr)
        if not np.issubdtype(arr_np.dtype, np.integer):
            # If all values are effectively integers (no decimal part), convert them
            if np.all(np.equal(arr_np, arr_np.astype(np.int32))):
                arr_np = arr_np.astype(np.int32)
            else:
                raise ValueError(
                    f"Board array must contain integer values, received {arr_np.dtype}. "
                    "Values must be convertible to integers without loss of information."
                )
        return cls(arr_np)

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
        """
        Get all possible moves for the board using C library only.

        Returns
        -------
        CMoves:
         CMoves object containing all legal moves
        """
        return _get_board_legal_moves(self.data)

    def __str__(self):
        board = self.to_board()
        return str(board)

    def __repr__(self):
        board = self.to_board()
        return repr(board)

    def get_mask(self):
        return _board_arr_to_mask(self.data)


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
        # Handle empty move_ints array (no legal moves)
        if len(move_ints) == 0:
            return cls(np.zeros((0,), dtype=np.int32))
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
        for i, move in enumerate(move_list):
            data[5 * i : 5 * (i + 1)] = _move_str_to_array(move)

        return cls(data)

    def to_str(self):
        moves = []
        # Handle empty data array (no moves)
        if self.data.size == 0:
            return moves

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
        # Check if array contains floats - if so, convert to int32 or raise error
        arr_np = np.asarray(arr)
        if not np.issubdtype(arr_np.dtype, np.integer):
            # If all values are effectively integers (no decimal part), convert them
            if np.all(np.equal(arr_np, arr_np.astype(np.int32))):
                arr_np = arr_np.astype(np.int32)
            else:
                raise ValueError(
                    f"Moves array must contain integer values, received {arr_np.dtype}. "
                    "Values must be convertible to integers without loss of information."
                )
        return cls(arr_np)

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
        """
        Get all possible moves for each board in the stack using parallelized C implementation.

        This method uses OpenMP to parallelize move generation across all boards.

        NOTE: The parallel implementation has a known limitation: en passant captures are not
        correctly generated. If your application depends on accurate en passant move generation,
        you should process boards individually using CBoard.to_possible_moves instead.

        Returns
        -------
        list:
            List of CMoves objects, one for each board
        """
        # Count how many boards we have
        num_boards = self.data.shape[0] // 69

        if num_boards == 0:
            return []

        # For a single board, just use the non-parallel version
        if num_boards == 1:
            board_array = self.data[:69]
            return [_get_board_legal_moves(board_array)]

        # Allocate a buffer for all possible moves for all boards
        # Each board can have a maximum of MAX_MOVES (256) moves, and each move is 5 integers
        max_moves = 256
        moves_buffer = np.zeros(num_boards * max_moves * 5, dtype=np.int32)

        # Use the parallelized C function to generate all legal moves
        parallel_array_to_possible(
            _ffi.cast("int *", moves_buffer.ctypes.data),
            _ffi.cast("int *", self.data.ctypes.data),
            num_boards,
        )

        # Process the results into a list of CMoves objects
        moves = []
        for i in range(num_boards):
            # Calculate the offset for this board's moves in the buffer
            offset = i * max_moves * 5

            # Count how many moves were generated for this board
            num_moves = 0
            for j in range(max_moves):
                # Check if all elements in this move are zero (no more moves)
                if np.sum(moves_buffer[offset + j * 5 : offset + j * 5 + 5]) == 0:
                    break
                num_moves += 1

            # Extract the moves for this board
            if num_moves == 0:
                # No legal moves
                moves.append(CMoves(np.zeros(0, dtype=np.int32)))
            else:
                # Extract the valid moves
                board_moves = moves_buffer[offset : offset + num_moves * 5].copy()
                moves.append(CMoves(board_moves))

        return moves

    @classmethod
    def from_array(cls, arr):
        # Check if array contains floats - if so, convert to int32 or raise error
        arr_np = np.asarray(arr)
        if not np.issubdtype(arr_np.dtype, np.integer):
            # If all values are effectively integers (no decimal part), convert them
            if np.all(np.equal(arr_np, arr_np.astype(np.int32))):
                arr_np = arr_np.astype(np.int32)
            else:
                raise ValueError(
                    f"Boards array must contain integer values, received {arr_np.dtype}. "
                    "Values must be convertible to integers without loss of information."
                )
        return cls(arr_np)

    def to_fen(self):
        fens = []
        for idx in range(0, self.data.shape[0], 69):
            fens.append(_array_to_fen(self.data[idx : idx + 69]))
        return fens

    @classmethod
    def from_fen(cls, fen_str_list):

        data = np.zeros(69 * len(fen_str_list), dtype=np.int32)
        for i, idx in enumerate(range(0, data.shape[0], 69)):
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
    """Converts a fen to a board array"""
    board_arr = np.zeros(shape=(69), dtype=np.int32)
    x = _ffi.new(f"char[{len(fen_str) + 10}]", bytes(fen_str, encoding="utf-8"))
    fen_to_array(_ffi.cast("int *", board_arr.ctypes.data), _ffi.cast("char *", x))
    _ffi.release(x)
    return board_arr


def _array_to_fen(board_arr):
    """Converts a board array to fen"""
    x = _ffi.new("char[512]", bytes("\0" * 512, encoding="utf-8"))
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
    """Converts string representation of a move ("e2e4") to an array"""
    move_arr = np.zeros(shape=(5), dtype=np.int32)
    x = _ffi.new("char[10]", bytes(move_str, encoding="utf-8"))
    move_str_to_array(_ffi.cast("int *", move_arr.ctypes.data), _ffi.cast("char *", x))
    _ffi.release(x)
    return move_arr


def _array_to_move_str(move_arr):
    """Converts move array to a string representation of a move ("e2e4")"""
    x = _ffi.new("char[10]", bytes("\0" * 10, encoding="utf-8"))
    array_to_move_str(x, _ffi.cast("int *", move_arr.ctypes.data))
    x_str = _ffi.string(x).decode("utf-8")

    # remove possible trailing space
    if x_str[-1] == " ":
        x_str = x_str[:-1]

    _ffi.release(x)
    return x_str


def _get_board_legal_moves(board_array):
    """
    Get legal moves for a board array using C library.

    Parameters
    ----------
    board_array : numpy.ndarray
        The board array to get legal moves for

    Returns
    -------
    CMoves
        CMoves object containing all legal moves
    """
    # We'll call array_to_possible, which calls fen_to_possible internally
    # This uses the C function gen_legal_moves to generate all legal moves

    # Maximum number of legal moves in chess (practical limit)
    max_moves = 256

    # Allocate space for the moves (5 elements per move)
    move_buffer = np.zeros(max_moves * 5, dtype=np.int32)

    # Make sure the board array is a copy and int32
    board_arr = np.array(board_array, dtype=np.int32)

    # Call the C function to fill the buffer with moves
    array_to_possible(
        _ffi.cast("int *", move_buffer.ctypes.data),
        _ffi.cast("int *", board_arr.ctypes.data),
    )

    # Count how many moves were generated (non-zero entries)
    num_moves = 0
    for i in range(0, move_buffer.shape[0], 5):
        if np.sum(move_buffer[i : i + 5]) > 0:  # If any element is non-zero
            num_moves += 1
        else:
            break  # Stop at first all-zero entry

    # If no moves were found, return empty CMoves
    if num_moves == 0:
        return CMoves(np.zeros(0, dtype=np.int32))

    # Extract just the moves that were generated
    valid_moves = move_buffer[: num_moves * 5]

    # Return as CMoves object
    return CMoves(valid_moves)


def _move_arr_to_int(move_arr):
    """Converts a move array to a move id"""
    move_int = np.zeros(shape=(1,), dtype=np.int32)
    move_arr_to_int(
        _ffi.cast("int *", move_int.ctypes.data),
        _ffi.cast("int*", move_arr.ctypes.data),
    )
    return move_int[0]


def _int_to_move_arr(move_int):
    """Converts a move id to a move array"""
    move_int = np.array([move_int])
    move_arr = np.zeros(shape=(5,), dtype=np.int32)
    int_to_move_arr(
        _ffi.cast("int*", move_arr.ctypes.data),
        _ffi.cast("int *", move_int.ctypes.data),
    )
    return move_arr


def legal_mask_convert(legal_mask):
    """Converts the id version of the move mask into an array based version"""
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


def _board_arr_to_mask(board_arr):
    """
    Converts a board array to a move mask.

    NOTE: This function on its own only generates pawn moves, castling moves, and some
    other basic moves, but may not generate all knight, bishop, rook, and queen moves.
    For reliable move generation, use CBoard.to_possible_moves, CBoards.to_possible_moves,
    or CChessEnv.get_possible_moves which access the native C chess engine correctly.
    """
    board_arr = np.int32(board_arr)
    move_mask = np.zeros(shape=(64 * 88), dtype=np.int32)
    board_arr_to_mask(
        _ffi.cast("int *", board_arr.ctypes.data),
        _ffi.cast("int *", move_mask.ctypes.data),
    )
    return move_mask
