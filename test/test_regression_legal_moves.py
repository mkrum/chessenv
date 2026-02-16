"""Comprehensive legal move validation regression tests.

Tests that validate CBoard/CBoards legal moves against python-chess across
many positions, including mask bijection tests.
"""

import chess
import numpy as np
import pytest
from conftest import assert_legal_moves_match

from fastchessenv.env import CChessEnv
from fastchessenv.rep import CBoard, CBoards, CMove

# Load test data
with open("test/test_data.csv", "r") as f:
    _lines = f.readlines()
_parsed = [line.rstrip().split(",") for line in _lines]
_fens, _moves = zip(*_parsed)


# --- Deterministic position tests ---


@pytest.mark.legal_moves
@pytest.mark.parametrize("fen", _fens[:100], ids=[f"pos{i}" for i in range(100)])
def test_deterministic_positions_legal_moves(fen):
    """CBoard legal moves match python-chess for 100 positions from test_data.csv."""
    assert_legal_moves_match(fen)


# --- Mask bijection ---


@pytest.mark.legal_moves
@pytest.mark.parametrize("fen", _fens[:100], ids=[f"pos{i}" for i in range(100)])
def test_mask_bijection(fen):
    """Every set mask bit maps to a legal move, and every legal move maps to a set bit."""
    cboard = CBoard.from_fen(fen)
    c_moves = set(cboard.to_possible_moves().to_str())

    py_board = chess.Board(fen)
    py_moves = {str(m) for m in py_board.legal_moves}

    # Get mask from CBoard
    mask = cboard.get_mask()
    mask_indices = np.nonzero(mask)[0]

    # Every set bit should correspond to a legal move
    mask_move_strs = set()
    for idx in mask_indices:
        move_str = CMove.from_int(int(idx)).to_str()
        mask_move_strs.add(move_str)
        assert (
            move_str in c_moves
        ), f"Mask bit {idx} ({move_str}) set but not in legal moves for {fen}"

    # Every legal move from python-chess should have its bit set
    for move_str in py_moves:
        move_int = CMove.from_str(move_str).to_int()
        assert (
            mask[move_int] == 1
        ), f"Legal move {move_str} (int={move_int}) not set in mask for {fen}"


# --- CBoards parallel vs CBoard sequential ---


@pytest.mark.legal_moves
def test_cboards_parallel_vs_sequential_no_ep():
    """50 non-EP positions: parallel CBoards matches sequential CBoard."""
    # Filter out positions with en passant
    no_ep_fens = [f for f in _fens if " - " in f][:50]

    for fen in no_ep_fens:
        # Sequential (single board)
        cboard = CBoard.from_fen(fen)
        expected = set(cboard.to_possible_moves().to_str())

        # Parallel (via CBoards with 2+ boards to trigger parallel path)
        cboards = CBoards.from_fen([fen, fen])
        actual = set(cboards.to_possible_moves()[0].to_str())

        assert actual == expected, (
            f"Parallel vs sequential mismatch for {fen}\n"
            f"Missing: {expected - actual}\n"
            f"Extra: {actual - expected}"
        )


@pytest.mark.legal_moves
@pytest.mark.known_bug
@pytest.mark.xfail(reason="Parallel move gen has known EP bug", strict=False)
def test_cboards_parallel_ep_known_bug():
    """EP positions in parallel mode — documents known discrepancy."""
    ep_fens = [f for f in _fens if " - " not in f][:20]

    for fen in ep_fens:
        cboard = CBoard.from_fen(fen)
        expected = set(cboard.to_possible_moves().to_str())

        cboards = CBoards.from_fen([fen, fen])
        actual = set(cboards.to_possible_moves()[0].to_str())

        assert actual == expected, (
            f"Parallel EP mismatch for {fen}\n"
            f"Missing: {expected - actual}\n"
            f"Extra: {actual - expected}"
        )


# --- Env mask matches python-chess ---


@pytest.mark.legal_moves
def test_env_mask_matches_python_chess():
    """Play 50 steps of a single-board game, validate mask at each step."""
    env = CChessEnv(1)
    state, mask = env.reset()

    py_board = chess.Board()

    for step in range(50):
        # Validate mask against python-chess
        py_moves = {str(m) for m in py_board.legal_moves}

        if len(py_moves) == 0:
            break

        # Check that all python-chess legal moves are in the mask
        for move_str in py_moves:
            move_int = CMove.from_str(move_str).to_int()
            assert (
                mask[0, move_int] == 1
            ), f"Step {step}: legal move {move_str} not in mask"

        # Get a random move from the env
        random_moves = env.random()
        move_str = CMove.from_int(int(random_moves[0])).to_str()

        # Push move on both sides
        done, _ = env.push_moves(random_moves)

        # Push on python-chess board
        py_board.push(chess.Move.from_uci(move_str))

        if done[0]:
            # Reset both
            state, mask = env.reset()
            py_board = chess.Board()
        else:
            _ = env.get_state()
            mask = env.get_mask()
