"""Chess rule correctness regression tests.

Parametrized tests using curated positions, each comparing CBoard legal moves
against python-chess.
"""

import chess
import pytest
from conftest import assert_legal_moves_match
from test_positions import (
    CASTLING_POSITIONS,
    CHECKMATE_POSITIONS,
    COMPLEX_POSITIONS,
    EN_PASSANT_POSITIONS,
    PROMOTION_POSITIONS,
    STALEMATE_POSITIONS,
)

from fastchessenv.rep import CBoard, CBoards

# --- En Passant ---


@pytest.mark.rules
@pytest.mark.en_passant
@pytest.mark.parametrize(
    "fen,description",
    EN_PASSANT_POSITIONS,
    ids=[desc for _, desc in EN_PASSANT_POSITIONS],
)
def test_en_passant_single_board(fen, description):
    """EP moves generated correctly by CBoard (sequential array_to_possible)."""
    assert_legal_moves_match(fen)


@pytest.mark.rules
@pytest.mark.en_passant
@pytest.mark.parametrize(
    "fen,description",
    [(f, d) for f, d in EN_PASSANT_POSITIONS if "illegal" not in d.lower()],
    ids=[d for _, d in EN_PASSANT_POSITIONS if "illegal" not in d.lower()],
)
def test_en_passant_parallel_board(fen, description):
    """EP moves generated correctly by CBoards (parallel_array_to_possible)."""
    cboards = CBoards.from_fen([fen, fen])  # Need >=2 for parallel path
    parallel_moves = set(cboards.to_possible_moves()[0].to_str())

    py_board = chess.Board(fen)
    py_moves = {str(m) for m in py_board.legal_moves}

    # This is expected to fail for EP positions in parallel mode
    assert parallel_moves == py_moves, (
        f"Parallel EP mismatch for: {description}\n"
        f"Missing: {py_moves - parallel_moves}\n"
        f"Extra: {parallel_moves - py_moves}"
    )


@pytest.mark.rules
@pytest.mark.en_passant
def test_en_passant_pinned_pawn():
    """EP should be illegal when capturing pawn is pinned along the rank."""
    fen = "8/8/8/8/k2Pp2R/8/8/4K3 b - d3"
    py_board = chess.Board(fen)
    py_moves = {str(m) for m in py_board.legal_moves}

    # EP capture d4 (exd3) should NOT be in legal moves since pawn is pinned
    assert "e4d3" not in py_moves, "python-chess confirms EP is illegal here"

    cboard = CBoard.from_fen(fen)
    c_moves = set(cboard.to_possible_moves().to_str())

    # Check CBoard also correctly excludes the EP capture
    assert c_moves == py_moves, (
        f"Pinned EP mismatch\n"
        f"Missing: {py_moves - c_moves}\n"
        f"Extra: {c_moves - py_moves}"
    )


# --- Castling ---


@pytest.mark.rules
@pytest.mark.castling
@pytest.mark.parametrize(
    "fen,description",
    CASTLING_POSITIONS,
    ids=[desc for _, desc in CASTLING_POSITIONS],
)
def test_castling_moves(fen, description):
    """Castling availability per position matches python-chess."""
    assert_legal_moves_match(fen)


@pytest.mark.rules
@pytest.mark.castling
def test_castling_through_check_is_illegal():
    """Castling through check must be rejected."""
    # White king on e1, black queen attacking f1
    fen = "rnb1kbnr/pppppppp/8/8/4q3/5N2/PPPPPPPP/RNBQKB1R w KQkq -"
    py_board = chess.Board(fen)
    py_moves = {str(m) for m in py_board.legal_moves}

    # Kingside castling (e1g1) should be illegal since f1 is attacked
    # (though e1 itself may or may not be in check)
    if "e1g1" not in py_moves:
        cboard = CBoard.from_fen(fen)
        c_moves = set(cboard.to_possible_moves().to_str())
        assert "e1g1" not in c_moves, "CBoard should also reject castling through check"


@pytest.mark.rules
@pytest.mark.castling
def test_castling_rights_encoding():
    """Different castling rights produce different legal move sets."""
    fen_all = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq -"
    fen_none = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w - -"

    moves_all = set(CBoard.from_fen(fen_all).to_possible_moves().to_str())
    moves_none = set(CBoard.from_fen(fen_none).to_possible_moves().to_str())

    # With all castling rights, should have more moves
    assert len(moves_all) > len(
        moves_none
    ), "Castling rights should produce more legal moves"
    # Specifically, e1g1 and e1c1 should be present with rights
    assert "e1g1" in moves_all
    assert "e1c1" in moves_all
    assert "e1g1" not in moves_none
    assert "e1c1" not in moves_none


# --- Promotion ---


@pytest.mark.rules
@pytest.mark.promotion
@pytest.mark.parametrize(
    "fen,description",
    PROMOTION_POSITIONS,
    ids=[desc for _, desc in PROMOTION_POSITIONS],
)
def test_promotion_moves(fen, description):
    """All 4 promotion types generated correctly."""
    assert_legal_moves_match(fen)


@pytest.mark.rules
@pytest.mark.promotion
def test_promotion_generates_all_piece_types():
    """A promoting pawn should generate queen, rook, bishop, knight promotions."""
    fen = "8/4P3/8/8/8/4k3/8/4K3 w - -"
    cboard = CBoard.from_fen(fen)
    c_moves = set(cboard.to_possible_moves().to_str())

    # Should have e7e8q, e7e8r, e7e8b, e7e8n
    assert "e7e8q" in c_moves
    assert "e7e8r" in c_moves
    assert "e7e8b" in c_moves
    assert "e7e8n" in c_moves


# --- Checkmate ---


@pytest.mark.rules
@pytest.mark.checkmate
@pytest.mark.parametrize(
    "fen,description",
    CHECKMATE_POSITIONS,
    ids=[desc for _, desc in CHECKMATE_POSITIONS],
)
def test_checkmate_no_legal_moves(fen, description):
    """Checkmate positions should have zero legal moves."""
    py_board = chess.Board(fen)
    assert py_board.is_checkmate(), f"Position should be checkmate: {description}"

    cboard = CBoard.from_fen(fen)
    c_moves = cboard.to_possible_moves().to_str()
    assert (
        len(c_moves) == 0
    ), f"Checkmate should have 0 moves but got {len(c_moves)}: {c_moves}"


# --- Stalemate ---


@pytest.mark.rules
@pytest.mark.stalemate
@pytest.mark.parametrize(
    "fen,description",
    STALEMATE_POSITIONS,
    ids=[desc for _, desc in STALEMATE_POSITIONS],
)
def test_stalemate_no_legal_moves(fen, description):
    """Stalemate positions should have zero legal moves."""
    py_board = chess.Board(fen)
    assert py_board.is_stalemate(), f"Position should be stalemate: {description}"

    cboard = CBoard.from_fen(fen)
    c_moves = cboard.to_possible_moves().to_str()
    assert (
        len(c_moves) == 0
    ), f"Stalemate should have 0 moves but got {len(c_moves)}: {c_moves}"


# --- Complex Positions ---


@pytest.mark.rules
@pytest.mark.parametrize(
    "fen,description",
    COMPLEX_POSITIONS,
    ids=[desc for _, desc in COMPLEX_POSITIONS],
)
def test_complex_position_full_match(fen, description):
    """Full legal move set comparison for complex positions."""
    assert_legal_moves_match(fen)


@pytest.mark.rules
def test_starting_position_has_20_moves():
    """Starting position should have exactly 20 legal moves."""
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    cboard = CBoard.from_fen(fen)
    c_moves = cboard.to_possible_moves().to_str()
    assert (
        len(c_moves) == 20
    ), f"Starting position should have 20 moves, got {len(c_moves)}"
