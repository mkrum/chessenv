
import pytest
from chessenv.rep import CBoard, CBoards, CMoves, CMove
import random

with open('test/test_data.csv', 'r') as test_data:
    lines = test_data.readlines()

lines = list(map(lambda x: x.rstrip().split(','), lines))
fen, moves= zip(*lines)

def test_cmoves_rep():
    x = list(moves)
    assert x == CMoves.from_array(CMoves.from_str(x).to_array()).to_str()
    assert x == CMoves.from_move(CMoves.from_str(x).to_move()).to_str()
    assert x == CMoves.from_cmoves(CMoves.from_str(x).to_cmoves()).to_str()

@pytest.mark.parametrize("x", moves)
def test_cmove_rep(x):
    assert x == CMove.from_array(CMove.from_str(x).to_array()).to_str()
    assert x == CMove.from_move(CMove.from_str(x).to_move()).to_str()

@pytest.mark.parametrize("f", fen)
def test_board_rep(f):
    assert CBoard.from_arr(CBoard.from_fen(f).to_array()).to_fen() == f
    assert CBoard.from_board(CBoard.from_fen(f).to_board()).to_fen() == f

def test_board_rep():

    for _ in range(10):
        f = random.sample(fen, 10)
        assert CBoards.from_arr(CBoards.from_fen(f).to_array()).to_fen() == f
        assert CBoards.from_board(CBoards.from_fen(f).to_board()).to_fen() == f
