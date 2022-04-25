
import pytest
from chessenv.rep import CBoard, CMoves, CMove


def test_cmoves_rep():
    x = ["e2e4", "d2d4", "g7g8q"]
    assert x == CMoves.from_array(CMoves.from_str(x).to_array()).to_str()
    assert x == CMoves.from_move(CMoves.from_str(x).to_move()).to_str()
    assert x == CMoves.from_cmoves(CMoves.from_str(x).to_cmoves()).to_str()

@pytest.mark.parametrize("x", ["e2e4", "d2d4", "g7g8q"])
def test_cmove_rep(x):
    assert x == CMove.from_array(CMove.from_str(x).to_array()).to_str()
    assert x == CMove.from_move(CMove.from_str(x).to_move()).to_str()

def test_board_rep():

    fens = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq -",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQq -",
     "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e3"]

    for f in fens:
        print(f)
        print(CBoard.from_arr(CBoard.from_fen(f).to_array()).to_fen())
        assert CBoard.from_arr(CBoard.from_fen(f).to_array()).to_fen() == f
        print(CBoard.from_arr(CBoard.from_fen(f).to_array()).to_fen())
        print()
        print(CBoard.from_arr(CBoard.from_fen(f).to_array()))
        print()
