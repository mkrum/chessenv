"""Stockfish integration regression tests.

All tests require Stockfish to be installed and skip otherwise.
"""

import numpy as np
import pytest
from conftest import requires_stockfish

from fastchessenv.rep import CBoard, CMove

# --- SFArray tests ---


@requires_stockfish
@pytest.mark.stockfish
def test_sfarray_returns_legal_moves():
    """SFArray returns legal moves for starting position and middlegame positions."""
    from fastchessenv.sfa import SFArray

    sfa = SFArray(depth=1, n_threads=1)

    positions = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -",
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQK2R b KQkq -",
    ]

    for fen in positions:
        import chess

        board = CBoard.from_fen(fen)
        board_arr = board.to_array().reshape(1, 69)

        move_ints = sfa.get_move_ints(board_arr)
        assert move_ints.shape == (1,)

        # Verify the returned move is legal
        move_str = CMove.from_int(int(move_ints[0])).to_str()
        py_board = chess.Board(fen)
        py_move = chess.Move.from_uci(move_str)
        assert (
            py_move in py_board.legal_moves
        ), f"SF move {move_str} not legal for {fen}"


@requires_stockfish
@pytest.mark.stockfish
def test_sfarray_batch():
    """SFArray handles batch of 3 positions, all return legal moves."""
    import chess

    from fastchessenv.sfa import SFArray

    sfa = SFArray(depth=1, n_threads=3)

    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -",
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQK2R b KQkq -",
    ]

    board_arrs = np.array([CBoard.from_fen(f).to_array() for f in fens])
    move_ints = sfa.get_move_ints(board_arrs)

    assert move_ints.shape == (3,)

    for i, fen in enumerate(fens):
        move_str = CMove.from_int(int(move_ints[i])).to_str()
        py_board = chess.Board(fen)
        py_move = chess.Move.from_uci(move_str)
        assert (
            py_move in py_board.legal_moves
        ), f"SF batch move {move_str} not legal for {fen}"


@requires_stockfish
@pytest.mark.stockfish
def test_sfarray_depth1_deterministic():
    """Same position queried 5 times at depth-1 returns same move."""
    from fastchessenv.sfa import SFArray

    sfa = SFArray(depth=1, n_threads=1)

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    board_arr = CBoard.from_fen(fen).to_array().reshape(1, 69)

    moves = []
    for _ in range(5):
        move_int = sfa.get_move_ints(board_arr)
        moves.append(int(move_int[0]))

    # All 5 queries should return the same move
    assert len(set(moves)) == 1, f"Depth-1 should be deterministic, got: {moves}"


# --- SFCChessEnv tests ---


@requires_stockfish
@pytest.mark.stockfish
def test_sfcchessenv_plays_complete_game():
    """SFCChessEnv plays 50 steps without error."""
    from fastchessenv.env import SFCChessEnv

    env = SFCChessEnv(n=2, depth=1)
    state, mask = env.reset()

    for step in range(50):
        random_move = env.random()
        state, mask, reward, done = env.step(random_move)

    assert state.shape == (2, 69)
    assert mask.shape == (2, 5632)


@requires_stockfish
@pytest.mark.stockfish
def test_sfcchessenv_multiple_depths():
    """Depths 1, 2, 3 all produce legal moves."""
    import chess

    from fastchessenv.env import SFCChessEnv

    for depth in [1, 2, 3]:
        env = SFCChessEnv(n=1, depth=depth)
        state, mask = env.reset()

        # Get opponent move
        opponent_move = env.sample_opponent()
        move_str = CMove.from_int(int(opponent_move[0])).to_str()

        # Verify it's legal
        py_board = chess.Board()
        py_move = chess.Move.from_uci(move_str)
        assert (
            py_move in py_board.legal_moves
        ), f"SF depth {depth} move {move_str} not legal"


@requires_stockfish
@pytest.mark.stockfish
def test_sfcchessenv_cleanup():
    """Create/destroy 3 SFCChessEnv instances without crash."""
    from fastchessenv.env import SFCChessEnv

    for _ in range(3):
        env = SFCChessEnv(n=2, depth=1)
        state, mask = env.reset()
        random_move = env.random()
        env.step(random_move)
        del env


@requires_stockfish
@pytest.mark.stockfish
def test_sfarray_cleanup():
    """Create/destroy 3 SFArray instances without crash."""
    from fastchessenv.sfa import SFArray

    for _ in range(3):
        sfa = SFArray(depth=1, n_threads=1)
        board_arr = (
            CBoard.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
            .to_array()
            .reshape(1, 69)
        )
        sfa.get_move_ints(board_arr)
        del sfa
