import numpy as np

from chessenv.rep import CBoard, CMove
from chessenv.sfa import SFArray


def test_sfarray_init():
    """Test that SFArray initializes properly"""
    sfa = SFArray(1)
    assert sfa.depth == 1
    assert sfa._sfa is not None


def test_sfarray_get_moves():
    """Test that SFArray.get_moves returns correct shape and values"""
    sfa = SFArray(1)

    # Standard starting position
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    board = CBoard.from_fen(fen)

    # Stack multiple instances for batch processing test
    N = 3
    board_arr = np.stack([np.int32(board.to_array()) for _ in range(N)])

    # Get moves from SFArray
    moves = sfa.get_moves(board_arr)

    # Check shape - should be (N, 3) for move representation
    assert moves.shape == (N, 3)

    # Check that the moves contain valid data
    for i in range(N):
        # The first column should be 0 (score placeholder)
        assert moves[i, 0] == 0

        # Move values should be populated
        assert moves[i, 1] != 0
        assert moves[i, 2] != 0


def test_sfarray_with_complex_position():
    """Test SFArray with a more complex chess position"""
    sfa = SFArray(1)

    # Complex position with several tactical opportunities
    fen = "Q1b1kbn1/2Pp1p2/2n1p3/p6p/7p/2q4P/1rP1PPP1/RNBK1BNR w KQ a6"
    board = CBoard.from_fen(fen)

    # Verify that the position was parsed correctly
    assert board.to_fen() == fen

    # Get move from Stockfish
    N = 1
    board_arr = np.stack([np.int32(board.to_array()) for _ in range(N)])
    move = sfa.get_moves(board_arr)

    # Should return a move with the expected shape
    assert move.shape == (N, 3)

    # Check structure of the move array
    assert move[0, 0] == 0  # First column is score placeholder
    assert (
        move[0, 1] != 0
    )  # Second column should be populated (from square or move type)
    assert move[0, 2] != 0  # Third column should be populated (to square or move data)


def test_sfarray_consistency():
    """Test that SFArray returns consistent results for the same position"""
    sfa = SFArray(1)

    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"
    board = CBoard.from_fen(fen)
    board_arr = np.stack([np.int32(board.to_array())])

    # Get move multiple times for the same position
    move1 = sfa.get_moves(board_arr)
    move2 = sfa.get_moves(board_arr)

    # At depth 1, Stockfish should return the same move for the same position
    # when run multiple times in succession
    np.testing.assert_array_equal(move1, move2)


def test_sfarray_get_move_ints():
    """Test that SFArray.get_move_ints returns valid move integers"""
    sfa = SFArray(1)

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    board = CBoard.from_fen(fen)

    N = 2
    board_arr = np.stack([np.int32(board.to_array()) for _ in range(N)])

    # Get move integers
    move_ints = sfa.get_move_ints(board_arr)

    # Check shape
    assert move_ints.shape == (N,)

    # Each move should be convertible to a valid chess move
    for i in range(N):
        move_obj = CMove.from_int(move_ints[i]).to_move()
        py_board = board.to_board()
        assert move_obj in py_board.legal_moves
