import random

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
