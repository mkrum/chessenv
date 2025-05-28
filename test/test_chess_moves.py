"""
Test script to verify that various move generation approaches generate the same moves.
"""

import random

import chess
import pytest

from chessenv.env import CChessEnv
from chessenv.rep import CBoard, CBoards

# Load some test positions
with open("test/test_data.csv", "r") as test_data:
    lines = test_data.readlines()

parsed_lines = [line.rstrip().split(",") for line in lines]
fen_positions, _ = zip(*parsed_lines)


@pytest.mark.parametrize("fen", random.sample(fen_positions, 20))
def test_move_generation_consistency(fen):
    """
    Test that CBoard.to_possible_moves(), CBoards.to_possible_moves(),
    and python-chess all generate the same legal moves for the same position.
    """
    # Get moves from python-chess (reference implementation)
    py_board = chess.Board(fen)
    py_moves_set = set(str(m) for m in py_board.legal_moves)

    # Get moves from CBoard (single board)
    cboard = CBoard.from_fen(fen)
    cboard_moves_set = set(cboard.to_possible_moves().to_str())

    # Get moves from CBoards (multiple boards approach)
    cboards = CBoards.from_fen([fen])
    cboards_moves_set = set(cboards.to_possible_moves()[0].to_str())

    # Assert equality with detailed error message
    assert cboard_moves_set == py_moves_set, (
        f"CBoard moves don't match python-chess:\n"
        f"FEN: {fen}\n"
        f"Missing moves: {py_moves_set - cboard_moves_set}\n"
        f"Extra moves: {cboard_moves_set - py_moves_set}\n"
    )

    assert cboards_moves_set == py_moves_set, (
        f"CBoards moves don't match python-chess:\n"
        f"FEN: {fen}\n"
        f"Missing moves: {py_moves_set - cboards_moves_set}\n"
        f"Extra moves: {cboards_moves_set - py_moves_set}\n"
    )

    # Also check that CBoards matches CBoard
    assert cboards_moves_set == cboard_moves_set, (
        f"CBoards moves don't match CBoard moves:\n"
        f"FEN: {fen}\n"
        f"Missing moves: {cboard_moves_set - cboards_moves_set}\n"
        f"Extra moves: {cboards_moves_set - cboard_moves_set}\n"
    )


def test_cboards_consistency():
    """
    Test that CBoards.to_possible_moves() generates the same moves as CBoard.to_possible_moves()
    """
    # Sample some positions
    sample_fens = random.sample(fen_positions, 5)

    for fen in sample_fens:
        # Create individual CBoard objects
        individual_board = CBoard.from_fen(fen)
        expected_moves = set(individual_board.to_possible_moves().to_str())

        # Create CBoards object with same position
        cboards = CBoards.from_fen([fen])
        actual_moves = set(cboards.to_possible_moves()[0].to_str())

        # Verify they match
        assert actual_moves == expected_moves, (
            f"CBoards moves don't match CBoard moves:\n"
            f"FEN: {fen}\n"
            f"Missing moves: {expected_moves - actual_moves}\n"
            f"Extra moves: {actual_moves - expected_moves}\n"
        )


def test_env_vs_python_chess():
    """
    Test that CChessEnv.get_possible_moves() generates the same moves as python-chess.
    This isn't directly relevant to the CBoards.to_possible_moves fix, but is useful
    for understanding the CChessEnv behavior.
    """
    # Create a CChessEnv with one board
    env = CChessEnv(1)

    # Try with the starting position
    env.reset()

    # Get reference moves from python-chess
    py_board = chess.Board()
    py_moves = set(str(m) for m in py_board.legal_moves)

    # Get moves from the environment
    env_moves = set(env.get_possible_moves()[0].to_str())

    # CChessEnv.get_possible_moves() should match python-chess
    assert py_moves == env_moves, (
        f"CChessEnv.get_possible_moves() and python-chess return different moves (starting position):\n"
        f"Missing moves: {py_moves - env_moves}\n"
        f"Extra moves: {env_moves - py_moves}\n"
    )
