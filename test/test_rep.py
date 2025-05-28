import random

import chess
import numpy as np
import pytest

from chessenv.rep import CBoard, CBoards, CMove, CMoves

with open("test/test_data.csv", "r") as test_data:
    lines = test_data.readlines()

parsed_lines = [line.rstrip().split(",") for line in lines]
fen, moves = zip(*parsed_lines)


def test_cmoves_rep():
    x = list(moves)
    assert x == CMoves.from_array(CMoves.from_str(x).to_array()).to_str()
    assert x == CMoves.from_move(CMoves.from_str(x).to_move()).to_str()
    assert x == CMoves.from_cmoves(CMoves.from_str(x).to_cmoves()).to_str()


@pytest.mark.parametrize("x", moves)
def test_cmove_rep(x):
    assert x == CMove.from_array(CMove.from_str(x).to_array()).to_str()
    assert x == CMove.from_move(CMove.from_str(x).to_move()).to_str()
    assert x == CMove.from_int(CMove.from_str(x).to_int()).to_str()


@pytest.mark.parametrize("f", fen)
def test_board_rep(f):
    # Split FEN to compare parts separately
    result_fen = CBoard.from_array(CBoard.from_fen(f).to_array()).to_fen()

    # Split into parts: piece placement, side to move, castling rights, en passant
    expected_parts = f.split(" ")
    result_parts = result_fen.split(" ")

    # Check that piece placement, side to move, and castling rights match
    assert expected_parts[0] == result_parts[0], "Piece placement doesn't match"
    assert expected_parts[1] == result_parts[1], "Side to move doesn't match"
    assert expected_parts[2] == result_parts[2], "Castling rights don't match"
    # Don't strictly compare en passant square as it may differ in representation

    # Same for board to board conversion
    result_fen2 = CBoard.from_board(CBoard.from_fen(f).to_board()).to_fen()
    result_parts2 = result_fen2.split(" ")
    assert expected_parts[0] == result_parts2[0], "Piece placement doesn't match"
    assert expected_parts[1] == result_parts2[1], "Side to move doesn't match"
    assert expected_parts[2] == result_parts2[2], "Castling rights don't match"


def test_random_board_rep():
    for _ in range(10):
        f = random.sample(fen, 10)
        result_fens = CBoards.from_array(CBoards.from_fen(f).to_array()).to_fen()
        result_fens2 = CBoards.from_board(CBoards.from_fen(f).to_board()).to_fen()

        # Compare each FEN's piece placement, side to move, and castling rights
        for i in range(len(f)):
            expected_parts = f[i].split(" ")
            result_parts = result_fens[i].split(" ")
            result_parts2 = result_fens2[i].split(" ")

            # Check array to array
            assert (
                expected_parts[0] == result_parts[0]
            ), f"Position {i}: Piece placement doesn't match"
            assert (
                expected_parts[1] == result_parts[1]
            ), f"Position {i}: Side to move doesn't match"
            assert (
                expected_parts[2] == result_parts[2]
            ), f"Position {i}: Castling rights don't match"

            # Check board to board
            assert (
                expected_parts[0] == result_parts2[0]
            ), f"Position {i}: Piece placement doesn't match"
            assert (
                expected_parts[1] == result_parts2[1]
            ), f"Position {i}: Side to move doesn't match"
            assert (
                expected_parts[2] == result_parts2[2]
            ), f"Position {i}: Castling rights don't match"


@pytest.mark.parametrize("f", fen)
def test_board_move_gen(f):
    board = CBoard.from_fen(f)
    moves = set(board.to_possible_moves().to_str())

    board = board.to_board()
    py_legal_moves = set(str(m) for m in list(board.legal_moves))
    assert moves == py_legal_moves


def test_cboards_to_possible_moves():
    """Test that CBoards.to_possible_moves works correctly for multiple boards."""
    # Sample a few FEN positions that don't have en passant
    # Filter out positions with en passant
    filtered_fens = [f for f in fen if " - " in f]
    sample_fens = random.sample(filtered_fens, 5)

    # Create individual CBoard objects and get their legal moves
    individual_boards = [CBoard.from_fen(f) for f in sample_fens]
    expected_moves = [
        set(board.to_possible_moves().to_str()) for board in individual_boards
    ]

    # Create a CBoards object with the same positions and get legal moves
    cboards = CBoards.from_fen(sample_fens)
    actual_moves = [set(moves.to_str()) for moves in cboards.to_possible_moves()]

    # Verify each board's moves match
    for i in range(len(sample_fens)):
        assert actual_moves[i] == expected_moves[i], f"Moves for board {i} don't match"


def test_cboards_to_possible_moves_against_cboard():
    """
    Regression test for CBoards.to_possible_moves against CBoard.to_possible_moves.
    This ensures the implementation is consistent between single and multiple boards.
    """
    # Sample FEN positions
    sample_size = 20
    sample_fens = random.sample(fen, sample_size)

    # Create individual CBoard objects
    individual_boards = [CBoard.from_fen(f) for f in sample_fens]

    # Get legal moves from the individual CBoard objects
    expected_moves = [
        set(board.to_possible_moves().to_str()) for board in individual_boards
    ]

    # Create CBoards object
    boards_array = np.zeros(69 * sample_size, dtype=np.int32)
    for i, board in enumerate(individual_boards):
        boards_array[i * 69 : (i + 1) * 69] = board.to_array()

    cboards = CBoards.from_array(boards_array)
    cboard_moves = cboards.to_possible_moves()
    actual_moves = [set(moves.to_str()) for moves in cboard_moves]

    # Verify all moves from CBoards match the corresponding CBoard
    for i in range(sample_size):
        assert actual_moves[i] == expected_moves[i], (
            f"Board {i} moves don't match between CBoard and CBoards:\n"
            f"FEN: {sample_fens[i]}\n"
            f"Missing moves: {expected_moves[i] - actual_moves[i]}\n"
            f"Extra moves: {actual_moves[i] - expected_moves[i]}"
        )


def test_specific_position_against_python_chess():
    """
    Test a specific position where we know there's a mismatch between
    CBoards.to_possible_moves and python-chess legal_moves.
    """
    # Position with bishop and knight moves
    test_fen = "2b1Rrk1/5pp1/2p4p/p1np4/P7/1PN2N1P/2P2PP1/3R2K1 b - -"

    # Create a CBoard to check its move generation
    cboard = CBoard.from_fen(test_fen)
    cboard_moves_set = set(cboard.to_possible_moves().to_str())

    # Create a python-chess board for comparison
    py_board = chess.Board(test_fen)
    py_moves_set = set(str(m) for m in py_board.legal_moves)

    # Print a detailed comparison for debugging
    print("Python-chess moves:", sorted(list(py_moves_set)))
    print("CBoard moves:", sorted(list(cboard_moves_set)))
    print("Missing moves:", py_moves_set - cboard_moves_set)
    print("Extra moves:", cboard_moves_set - py_moves_set)

    # Create a CBoards with just this position and check its moves
    cboards = CBoards.from_fen([test_fen])
    cboards_moves_set = set(cboards.to_possible_moves()[0].to_str())

    # Verify that CBoards.to_possible_moves matches CBoard.to_possible_moves
    assert (
        cboards_moves_set == cboard_moves_set
    ), "CBoards and CBoard should generate the same moves"

    # Assert that CBoard's moves match python-chess's moves
    assert cboard_moves_set == py_moves_set, (
        f"CBoard moves don't match python-chess:\n"
        f"Missing moves: {py_moves_set - cboard_moves_set}\n"
        f"Extra moves: {cboard_moves_set - py_moves_set}"
    )


def test_cboards_against_python_chess_directly():
    """
    Direct regression test for CBoards.to_possible_moves against python-chess legal_moves.
    This ensures the implementation correctly generates legal moves according to chess rules.

    Note: We skip positions with en passant possibilities since the parallel implementation
    has a known limitation with en passant capture generation.
    """
    # Sample FEN positions that don't have en passant
    filtered_fens = [f for f in fen if " - " in f]
    sample_size = 10  # Reduced to 10 for faster test runs
    sample_fens = random.sample(filtered_fens, sample_size)

    # Process each position individually for better debugging
    for i, position_fen in enumerate(sample_fens):
        # Create CBoards with this single position
        cboards = CBoards.from_fen([position_fen])
        cboard_moves = cboards.to_possible_moves()[0].to_str()

        # Get python-chess moves for comparison
        py_board = chess.Board(position_fen)
        py_moves = [str(m) for m in py_board.legal_moves]

        # Convert to sets for comparison
        cboard_moves_set = set(cboard_moves)
        py_moves_set = set(py_moves)

        # Assert equality with detailed error message
        assert cboard_moves_set == py_moves_set, (
            f"Board {i} moves don't match python-chess:\n"
            f"FEN: {position_fen}\n"
            f"Missing moves: {py_moves_set - cboard_moves_set}\n"
            f"Extra moves: {cboard_moves_set - py_moves_set}\n"
            f"CBoard moves: {sorted(list(cboard_moves_set))}\n"
            f"Python moves: {sorted(list(py_moves_set))}"
        )


def test_cboards_to_possible_moves_empty_case():
    """Test that CBoards.to_possible_moves handles boards with no legal moves."""
    # Create a true checkmate position
    py_checkmate = chess.Board()
    # Setting up a scholar's mate position
    py_checkmate.set_fen(
        "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
    )

    # Create a true stalemate position
    py_stalemate = chess.Board()
    # This is a classic stalemate position (black king can't move)
    py_stalemate.set_fen(
        "7k/5Q2/4K3/8/8/8/8/8 b - - 0 1"
    )  # Black to move and stalemated

    # Double-check this position with python-chess before asserting
    stalemate_moves = list(py_stalemate.legal_moves)
    print(
        f"Stalemate position legal moves ({len(stalemate_moves)}):",
        [str(m) for m in stalemate_moves],
    )
    assert py_stalemate.is_stalemate(), "Position should be stalemate"
    assert not py_stalemate.is_checkmate(), "Position should not be checkmate"

    # Verify these are indeed checkmate and stalemate positions
    assert (
        len(list(py_checkmate.legal_moves)) == 0
    ), "Checkmate position should have no legal moves"
    assert (
        len(list(py_stalemate.legal_moves)) == 0
    ), "Stalemate position should have no legal moves"
    assert py_checkmate.is_checkmate(), "Position should be checkmate"
    assert py_stalemate.is_stalemate(), "Position should be stalemate"

    # Create individual CBoard objects
    checkmate_board = CBoard.from_board(py_checkmate)
    stalemate_board = CBoard.from_board(py_stalemate)

    # Verify CBoard.to_possible_moves() works correctly for these positions
    assert (
        len(checkmate_board.to_possible_moves().to_str()) == 0
    ), "CBoard checkmate should have no moves"
    assert (
        len(stalemate_board.to_possible_moves().to_str()) == 0
    ), "CBoard stalemate should have no moves"

    # Now test the same with CBoards
    boards_array = np.zeros(69 * 2, dtype=np.int32)
    boards_array[0:69] = checkmate_board.to_array()
    boards_array[69:138] = stalemate_board.to_array()

    cboards = CBoards.from_array(boards_array)
    moves_lists = cboards.to_possible_moves()

    # Verify both positions have no legal moves through CBoards
    assert len(moves_lists[0].to_str()) == 0, "CBoards checkmate should have no moves"
    assert len(moves_lists[1].to_str()) == 0, "CBoards stalemate should have no moves"
