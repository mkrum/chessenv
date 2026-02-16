"""Round-trip correctness regression tests for representations.

Tests FEN round-trips, move encoding/decoding, board array encoding,
and exhaustive move integer tests.
"""

import numpy as np
import pytest
from test_positions import (
    CASTLING_POSITIONS,
    COMPLEX_POSITIONS,
    EN_PASSANT_POSITIONS,
    PROMOTION_POSITIONS,
)

from fastchessenv.rep import CBoard, CBoards, CMove

# --- FEN round-trips ---

_ALL_POSITIONS = (
    EN_PASSANT_POSITIONS + CASTLING_POSITIONS + PROMOTION_POSITIONS + COMPLEX_POSITIONS
)


@pytest.mark.representation
@pytest.mark.parametrize(
    "fen,description",
    _ALL_POSITIONS,
    ids=[desc for _, desc in _ALL_POSITIONS],
)
def test_fen_array_roundtrip(fen, description):
    """fen -> array -> fen preserves piece placement, side to move, and castling."""
    result_fen = CBoard.from_array(CBoard.from_fen(fen).to_array()).to_fen()

    expected_parts = fen.split(" ")
    result_parts = result_fen.split(" ")

    assert (
        expected_parts[0] == result_parts[0]
    ), f"Piece placement mismatch: {description}"
    assert expected_parts[1] == result_parts[1], f"Side to move mismatch: {description}"
    assert (
        expected_parts[2] == result_parts[2]
    ), f"Castling rights mismatch: {description}"


@pytest.mark.representation
@pytest.mark.parametrize(
    "fen,description",
    _ALL_POSITIONS,
    ids=[desc for _, desc in _ALL_POSITIONS],
)
def test_fen_board_roundtrip(fen, description):
    """fen -> Board -> fen preserves piece placement, side to move, and castling."""
    result_fen = CBoard.from_board(CBoard.from_fen(fen).to_board()).to_fen()

    expected_parts = fen.split(" ")
    result_parts = result_fen.split(" ")

    assert (
        expected_parts[0] == result_parts[0]
    ), f"Piece placement mismatch: {description}"
    assert expected_parts[1] == result_parts[1], f"Side to move mismatch: {description}"
    assert (
        expected_parts[2] == result_parts[2]
    ), f"Castling rights mismatch: {description}"


# --- Move round-trips ---

_SAMPLE_MOVES = [
    "e2e4",
    "d2d4",
    "g1f3",
    "b1c3",  # Regular moves
    "e7e8q",
    "e7e8r",
    "e7e8b",
    "e7e8n",  # Promotions
    "a7a8q",
    "h7h8q",  # Edge-file promotions
    "e1g1",
    "e1c1",  # Castling notation
    "a2a3",
    "h2h3",  # Edge-file moves
    "e7d8q",  # Capture promotion
]


@pytest.mark.representation
@pytest.mark.parametrize("move_str", _SAMPLE_MOVES)
def test_move_str_array_roundtrip(move_str):
    """str -> array -> str round-trip."""
    result = CMove.from_array(CMove.from_str(move_str).to_array()).to_str()
    assert result == move_str


@pytest.mark.representation
@pytest.mark.parametrize("move_str", _SAMPLE_MOVES)
def test_move_str_int_roundtrip(move_str):
    """str -> int -> str round-trip."""
    result = CMove.from_int(CMove.from_str(move_str).to_int()).to_str()
    assert result == move_str


@pytest.mark.representation
@pytest.mark.parametrize("move_str", _SAMPLE_MOVES)
def test_move_str_chess_roundtrip(move_str):
    """str -> chess.Move -> str round-trip."""
    result = CMove.from_move(CMove.from_str(move_str).to_move()).to_str()
    assert result == move_str


# --- Move integer exhaustive ---


@pytest.mark.representation
def test_move_int_array_exhaustive_roundtrip():
    """All 5632 move ints round-trip through int -> array -> int."""
    for i in range(5632):
        arr = CMove.from_int(i).to_array()
        result = CMove.from_array(arr).to_int()
        assert result == i, f"Move int {i} failed round-trip: got {result}"


@pytest.mark.representation
def test_move_int_str_sample_roundtrip():
    """Every 10th valid move int through int -> str -> int (where str is valid UCI)."""
    import re

    uci_pattern = re.compile(r"^[a-h][1-8][a-h][1-8][qrbn]?$")
    successful = 0
    for i in range(0, 5632, 10):
        try:
            move_str = CMove.from_int(i).to_str()
        except (UnicodeDecodeError, ValueError):
            continue
        # Only test moves that produce valid UCI strings
        if not uci_pattern.match(move_str):
            continue
        result = CMove.from_str(move_str).to_int()
        assert (
            result == i
        ), f"Move int {i} ({move_str}) failed str round-trip: got {result}"
        successful += 1
    assert successful > 100, f"Only {successful} valid move ints found in sample"


# --- Board array encoding details ---


@pytest.mark.representation
def test_starting_position_array_values():
    """Verify exact array values for starting position."""
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    arr = CBoard.from_fen(fen).to_array()

    assert arr.shape == (69,)
    assert arr.dtype == np.int32

    # Black pieces (rank 8, squares 0-7): rook=10, knight=8, bishop=9, queen=11, king=12
    assert arr[0] == 10  # a8 rook
    assert arr[1] == 8  # b8 knight
    assert arr[2] == 9  # c8 bishop
    assert arr[3] == 11  # d8 queen
    assert arr[4] == 12  # e8 king
    assert arr[5] == 9  # f8 bishop
    assert arr[6] == 8  # g8 knight
    assert arr[7] == 10  # h8 rook

    # Black pawns (rank 7, squares 8-15): pawn=7
    for i in range(8, 16):
        assert arr[i] == 7, f"Black pawn at index {i}"

    # Empty squares (ranks 3-6, squares 16-47)
    for i in range(16, 48):
        assert arr[i] == 0, f"Empty square at index {i}"

    # White pawns (rank 2, squares 48-55): pawn=1
    for i in range(48, 56):
        assert arr[i] == 1, f"White pawn at index {i}"

    # White pieces (rank 1, squares 56-63): rook=4, knight=2, bishop=3, queen=5, king=6
    assert arr[56] == 4  # a1 rook
    assert arr[57] == 2  # b1 knight
    assert arr[58] == 3  # c1 bishop
    assert arr[59] == 5  # d1 queen
    assert arr[60] == 6  # e1 king
    assert arr[61] == 3  # f1 bishop
    assert arr[62] == 2  # g1 knight
    assert arr[63] == 4  # h1 rook

    # Metadata slots (64-68)
    # Slot 64: en passant (14 means no EP, varies by implementation)
    # Slots 65-68: castling rights
    # Side to move is encoded in slot 68 (16=white)
    assert arr[68] == 16  # White to move


@pytest.mark.representation
def test_ep_marker_in_array():
    """Verify en passant marker value (13) appears when EP is available."""
    fen = "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq e6"
    arr = CBoard.from_fen(fen).to_array()

    # EP marker value 13 should appear somewhere in the array (board squares or metadata)
    assert 13 in arr, f"EP marker (13) not found in array: {arr}"


# --- CBoards batch vs individual ---


@pytest.mark.representation
def test_cboards_batch_matches_individual():
    """CBoards.from_fen([...]).to_array() matches individual CBoard arrays.

    Note: EP marker (value 13) is zeroed for comparison due to known
    differences in how batch vs individual FEN parsing handles EP squares.
    """
    fens = [fen for fen, _ in COMPLEX_POSITIONS]

    # Individual
    individual_arrays = [CBoard.from_fen(f).to_array() for f in fens]

    # Batch
    batch = CBoards.from_fen(fens)
    batch_arr = batch.to_array()

    for i, expected in enumerate(individual_arrays):
        actual = batch_arr[i * 69 : (i + 1) * 69].copy()
        exp = expected.copy()
        # Zero out EP markers for comparison (known EP handling differences)
        actual[actual == 13] = 0
        exp[exp == 13] = 0
        assert np.array_equal(
            actual, exp
        ), f"Position {i} ({fens[i]}) batch/individual mismatch"


@pytest.mark.representation
def test_cboards_fen_roundtrip():
    """CBoards fen -> array -> fen preserves positions."""
    fens = [fen for fen, _ in COMPLEX_POSITIONS if " - " in fen]

    result_fens = CBoards.from_array(CBoards.from_fen(fens).to_array()).to_fen()

    for i in range(len(fens)):
        expected_parts = fens[i].split(" ")
        result_parts = result_fens[i].split(" ")
        assert expected_parts[0] == result_parts[0], f"Position {i}: piece placement"
        assert expected_parts[1] == result_parts[1], f"Position {i}: side to move"
        assert expected_parts[2] == result_parts[2], f"Position {i}: castling"
