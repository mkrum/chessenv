import numpy as np
from cffi import FFI

from chessenv import CChessEnv
from chessenv.rep import CBoard, CMove
from chessenv_c.lib import invert_array

_ffi = FFI()


def _invert_array(board_arr):
    """Helper function to invert a board array"""
    board_arr = np.int32(board_arr)
    invert_array(
        _ffi.cast("int *", board_arr.ctypes.data),
    )
    return board_arr


def test_invert_board_consistency():
    """Test that inverting a board and converting back to FEN preserves move legality"""
    # Test with a few different positions
    positions = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",  # Initial position
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -",  # After e4 e5 Nf3 Nc6
        "r1bqk2r/ppp2ppp/2n2n2/2bpp3/2B1P3/2PP1N2/PP3PPP/RNBQK2R w KQkq -",  # Italian game position
    ]

    for fen in positions:
        board = CBoard.from_fen(fen)

        # Get legal moves from original position
        original_board = board.to_board()
        original_moves = set(str(m) for m in original_board.legal_moves)

        # Invert the board
        inverted_array = _invert_array(board.to_array())
        inverted_board = CBoard.from_array(inverted_array)

        # Convert inverted board to chess.Board
        inverted_chess_board = inverted_board.to_board()

        # The inverted board should have different side to move
        assert original_board.turn != inverted_chess_board.turn

        # Re-invert to get back to original
        re_inverted_array = _invert_array(inverted_board.to_array())
        re_inverted_board = CBoard.from_array(re_inverted_array)

        # Check that the double-inverted board is the same as the original
        assert re_inverted_board.to_fen() == board.to_fen()

        # Legal moves should be preserved after double inversion
        re_inverted_chess_board = re_inverted_board.to_board()
        re_inverted_moves = set(str(m) for m in re_inverted_chess_board.legal_moves)
        assert original_moves == re_inverted_moves


def test_invert_gameplay():
    """Test that inversion works correctly during actual gameplay"""
    # Create environment with inversion enabled
    env = CChessEnv(8, invert=True)
    states, masks = env.reset()

    # Run for several steps
    for _ in range(10):
        # Get player moves
        random_moves_arr = env.sample_opponent()

        # Apply moves
        done, rewards = env.push_moves(random_moves_arr)

        # Get updated state
        new_states = env.get_state()

        # Check that after inversion, all boards have white to move
        for i in range(env.n):
            if not done[i]:  # Skip boards that are done
                board = CBoard.from_array(new_states[i]).to_board()
                # After inversion, the side to move should be white (True)
                assert (
                    board.turn is True
                ), "Board should have white to move after inversion"


def test_env_invert_flag():
    """Test that the invert flag in CChessEnv works correctly"""
    # Create two environments, one with inversion, one without
    env_with_invert = CChessEnv(4, invert=True)
    env_without_invert = CChessEnv(4, invert=False)

    # Reset both environments
    states_with_invert, _ = env_with_invert.reset()
    states_without_invert, _ = env_without_invert.reset()

    # Initial state should be the same (all start with white to move)
    for i in range(4):
        board_with = CBoard.from_array(states_with_invert[i]).to_board()
        board_without = CBoard.from_array(states_without_invert[i]).to_board()
        assert board_with.turn == board_without.turn

    # Make same moves in both environments
    moves = np.array([0, 0, 0, 0])  # Using move 0 for simplicity

    # Push moves to both environments
    env_with_invert.push_moves(moves)
    env_without_invert.push_moves(moves)

    # Get new states
    states_with_invert = env_with_invert.get_state()
    states_without_invert = env_without_invert.get_state()

    # After pushing moves, the inverted environment should have white to move
    # while the non-inverted environment should have black to move
    for i in range(4):
        board_with = CBoard.from_array(states_with_invert[i]).to_board()
        board_without = CBoard.from_array(states_without_invert[i]).to_board()

        # With inversion, turn should be white (True)
        assert board_with.turn is True

        # Without inversion, turn should be black (False)
        assert board_without.turn is False


def test_legal_moves_after_inversion():
    """Test that legal moves are correctly calculated after board inversion"""
    env = CChessEnv(1, invert=True)
    states, masks = env.reset()

    # Make a move
    moves = env.sample_opponent()
    env.push_moves(moves)

    # Get new state and mask
    new_states = env.get_state()
    new_masks = env.get_mask()

    # Get the legal moves directly from the board
    board = CBoard.from_array(new_states[0])
    chess_board = board.to_board()
    legal_chess_moves = set(str(m) for m in chess_board.legal_moves)

    # Get the legal moves from the mask
    mask_moves = set()
    for i in np.nonzero(new_masks[0])[0]:
        mask_moves.add(CMove.from_int(i).to_str())

    # The legal moves from both methods should match
    assert legal_chess_moves == mask_moves
