
from chessenv_c.lib import (
    fen_to_vec,
)
from chessenv.rep import CBoard
from stonefish.rep import BoardRep


def test_board_rep():

    fens = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQq - 0 1",
     "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]

    for f in fens:
        print(f)
        assert CBoard.from_arr(CBoard.from_fen(f).to_array()).to_fen() == f
