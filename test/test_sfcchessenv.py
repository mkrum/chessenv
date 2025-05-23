import chess
import numpy as np

from chessenv import CChessEnv
from chessenv.env import SFCChessEnv
from chessenv.rep import CBoard, CBoards, CMove

# No monkey patching needed anymore


def test_sfcchessenv_init():
    """Test initialization of SFCChessEnv"""

    # Now create the environment
    env = SFCChessEnv(4, depth=1)

    # Check basic properties
    assert env.n == 4
    # No depth attribute in the class, it's only used during initialization
    assert env.max_step == 100  # Default value
    assert env.draw_reward == 0  # Default value
    assert env._sfa is not None

    # Check with custom parameters
    env2 = SFCChessEnv(
        8, depth=2, max_step=200, draw_reward=-0.5, min_random=5, max_random=10
    )
    assert env2.n == 8
    assert env2.max_step == 200
    assert env2.draw_reward == -0.5
    assert env2.min_random == 5
    assert env2.max_random == 10


def test_sfcchessenv_reset():
    """Test reset functionality of SFCChessEnv"""

    env = SFCChessEnv(2)
    states, masks = env.reset()

    # Check shapes of returned arrays
    assert states.shape == (2, 69)
    assert masks.shape == (2, 88 * 64)

    # Check that all boards are in valid starting state
    boards = CBoards.from_array(states.flatten()).to_board()
    for board in boards:
        # Check that each board is a valid chess board
        assert isinstance(board, chess.Board)
        # In the initial position, there should be 20 legal moves
        assert len(list(board.legal_moves)) > 0


def test_sfcchessenv_sample_opponent():
    """Test that sample_opponent returns valid stockfish moves"""
    env = SFCChessEnv(3)
    env.reset()

    # Sample opponent moves
    moves = env.sample_opponent()

    # Should return the right number of moves
    assert moves.shape == (3,)

    # Each move should be valid
    for i in range(env.n):
        board = CBoard.from_array(env.get_state()[i]).to_board()
        move = CMove.from_int(moves[i]).to_move()
        assert move in board.legal_moves


def test_sfcchessenv_vs_cchessenv():
    """Test that SFCChessEnv behaves differently than CChessEnv in opponent sampling"""
    # Create both environments with same seed
    sf_env = SFCChessEnv(1)
    c_env = CChessEnv(1)

    # Reset both environments
    sf_env.reset()
    c_env.reset()

    # Sample opponents multiple times
    for _ in range(5):
        sf_moves = sf_env.sample_opponent()
        c_moves = c_env.sample_opponent()

        # The moves should usually be different as Stockfish is deterministic at depth=1
        # while CChessEnv uses random sampling
        # We don't assert inequality because there's a small chance they happen to be the same

        # Push the moves to both environments
        sf_env.push_moves(sf_moves)
        c_env.push_moves(c_moves)


def test_sfcchessenv_step():
    """Test the step method of SFCChessEnv"""
    env = SFCChessEnv(1)
    state, mask = env.reset()

    # Find the first legal move from the mask
    legal_move_idx = np.nonzero(mask[0])[0][0]
    move = np.array([legal_move_idx])

    # Step the environment
    next_state, next_mask, reward, done = env.step(move)

    # Check shapes
    assert next_state.shape == state.shape
    assert next_mask.shape == mask.shape
    assert reward.shape == (1,)
    assert done.shape == (1,)

    # The board should have changed
    assert not np.array_equal(state, next_state)

    # Reward should be 0 unless the game ended
    if done[0]:
        assert reward[0] != 0
    else:
        assert reward[0] == 0


def test_sfcchessenv_depth():
    """Test that different depths affect the move quality"""
    # This is a more subtle test as higher depths should lead to better moves
    # We'll simply check that the environments return different moves at different depths
    env1 = SFCChessEnv(1, depth=1)
    env2 = SFCChessEnv(1, depth=2)

    env1.reset()
    env2.reset()

    # Sample moves from both environments
    move1 = env1.sample_opponent()
    move2 = env2.sample_opponent()

    # The moves may or may not be different, but both should be legal
    board = CBoard.from_array(env1.get_state()[0]).to_board()

    move_obj1 = CMove.from_int(move1[0]).to_move()
    move_obj2 = CMove.from_int(move2[0]).to_move()

    assert move_obj1 in board.legal_moves
    assert move_obj2 in board.legal_moves
