"""Shared test infrastructure for fastchessenv regression tests."""

import os
import shutil
import sys
from typing import Optional

import chess
import numpy as np
import pytest

# Add test/ directory to sys.path so test modules can import each other
sys.path.insert(0, os.path.dirname(__file__))

from fastchessenv.rep import CBoard, CMove

# --- Pytest markers ---


def pytest_configure(config):
    config.addinivalue_line("markers", "rules: chess rule correctness tests")
    config.addinivalue_line(
        "markers", "representation: encoding/decoding round-trip tests"
    )
    config.addinivalue_line("markers", "env_api: environment API contract tests")
    config.addinivalue_line(
        "markers", "legal_moves: comprehensive move validation tests"
    )
    config.addinivalue_line("markers", "fuzz: random game validation tests")
    config.addinivalue_line("markers", "stockfish: tests requiring Stockfish binary")
    config.addinivalue_line("markers", "slow: long-running tests")
    config.addinivalue_line(
        "markers", "known_bug: tests documenting known bugs (expected to fail)"
    )
    config.addinivalue_line("markers", "en_passant: en passant related tests")
    config.addinivalue_line("markers", "castling: castling related tests")
    config.addinivalue_line("markers", "promotion: pawn promotion related tests")
    config.addinivalue_line("markers", "checkmate: checkmate related tests")
    config.addinivalue_line("markers", "stalemate: stalemate related tests")


requires_stockfish = pytest.mark.skipif(
    not shutil.which("stockfish"),
    reason="Stockfish binary not found in PATH",
)


# --- Helpers ---


def assert_legal_moves_match(fen: str) -> None:
    """Assert that CBoard legal moves match python-chess for the given FEN."""
    cboard = CBoard.from_fen(fen)
    c_moves = set(cboard.to_possible_moves().to_str())

    py_board = chess.Board(fen)
    py_moves = {str(m) for m in py_board.legal_moves}

    assert c_moves == py_moves, (
        f"Legal move mismatch for FEN: {fen}\n"
        f"Missing (in python-chess but not CBoard): {py_moves - c_moves}\n"
        f"Extra (in CBoard but not python-chess): {c_moves - py_moves}"
    )


def assert_mask_matches_moves(fen: str) -> None:
    """Assert mask bits correspond 1:1 to legal moves from python-chess."""
    py_board = chess.Board(fen)
    py_moves = {str(m) for m in py_board.legal_moves}

    cboard = CBoard.from_fen(fen)
    c_legal = set(cboard.to_possible_moves().to_str())

    # Convert mask set bits to move strings
    mask = cboard.get_mask()
    mask_indices = np.nonzero(mask)[0]
    mask_moves = set()
    for idx in mask_indices:
        try:
            move_str = CMove.from_int(int(idx)).to_str()
            mask_moves.add(move_str)
        except Exception:
            pass

    # Every python-chess legal move should be in the mask
    for move_str in py_moves:
        move_int = CMove.from_str(move_str).to_int()
        assert (
            mask[move_int] == 1
        ), f"Legal move {move_str} (int={move_int}) not set in mask for FEN: {fen}"

    # Every set mask bit should correspond to a legal move
    for idx in mask_indices:
        move_str = CMove.from_int(int(idx)).to_str()
        assert (
            move_str in c_legal
        ), f"Mask bit {idx} ({move_str}) is set but not a legal move for FEN: {fen}"


def make_random_position(
    max_moves: int = 40, seed: Optional[int] = None
) -> chess.Board:
    """Play random moves on a python-chess Board to generate a random position."""
    import random as _random

    rng = _random.Random(seed)
    board = chess.Board()
    for _ in range(rng.randint(1, max_moves)):
        legal = list(board.legal_moves)
        if not legal:
            break
        board.push(rng.choice(legal))
    return board


# --- Fixtures ---


@pytest.fixture
def single_env():
    """A CChessEnv with N=1."""
    from fastchessenv.env import CChessEnv

    return CChessEnv(1)


@pytest.fixture
def multi_env():
    """A CChessEnv with N=16."""
    from fastchessenv.env import CChessEnv

    return CChessEnv(16)


@pytest.fixture(params=[1, 2, 16, 64, 256])
def env_n(request):
    """Parametrized CChessEnv across multiple board counts."""
    from fastchessenv.env import CChessEnv

    return CChessEnv(request.param)
