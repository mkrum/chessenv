import chess
import numpy as np

from chessenv.env import RandomChessEnv
from chessenv.rep import CBoard, CBoards, CMove


def test_randomchessenv_init():
    """Test initialization of RandomChessEnv"""

    # Create the environment
    env = RandomChessEnv(4)

    # Check basic properties
    assert env.n == 4
    assert env.max_step == 100  # Default value
    assert env.draw_reward == 0  # Default value

    # Check with custom parameters
    env2 = RandomChessEnv(
        8, max_step=200, draw_reward=-0.5, min_random=5, max_random=10, invert=True
    )
    assert env2.n == 8
    assert env2.max_step == 200
    assert env2.draw_reward == -0.5
    assert env2.min_random == 5
    assert env2.max_random == 10
    assert env2.invert is True


def test_randomchessenv_reset():
    """Test reset functionality of RandomChessEnv"""

    env = RandomChessEnv(2)
    states, masks = env.reset()

    # Check shapes of returned arrays
    assert states.shape == (2, 69)
    assert masks.shape == (2, 88 * 64)

    # Check that all boards are in valid starting state
    boards = CBoards.from_array(states.flatten()).to_board()
    for board in boards:
        # Check that each board is a valid chess board
        assert isinstance(board, chess.Board)
        # In the initial position, there should be legal moves
        assert len(list(board.legal_moves)) > 0


def test_randomchessenv_sample_opponent():
    """Test that sample_opponent returns valid random moves"""
    env = RandomChessEnv(3)
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


def test_randomchessenv_is_random():
    """Test that RandomChessEnv actually returns random moves"""
    # Create environment
    env = RandomChessEnv(1)
    env.reset()

    # Collect multiple moves from the same position
    moves = []
    for _ in range(10):  # Sample 10 times
        move = env.sample_opponent()[0]
        moves.append(move)

    # Check if there are at least 2 different moves
    # This is probabilistic but very likely to pass with 10 samples
    # There should be multiple different legal moves from the starting position
    assert (
        len(set(moves)) > 1
    ), "RandomChessEnv doesn't seem to be returning random moves"


def test_randomchessenv_vs_cchessenv():
    """Test that RandomChessEnv sample_opponent behaves the same as its random() method"""
    # Create environment
    env = RandomChessEnv(1)
    env.reset()

    # Both sample_opponent and random should return the same type of moves
    for _ in range(5):
        # Sample moves using both methods
        random_moves = env.random()
        opponent_moves = env.sample_opponent()

        # Check that both methods return arrays of the same shape
        assert random_moves.shape == opponent_moves.shape == (1,)

        # Verify both moves are legal
        board = CBoard.from_array(env.get_state()[0]).to_board()
        random_move = CMove.from_int(random_moves[0]).to_move()
        opponent_move = CMove.from_int(opponent_moves[0]).to_move()

        assert random_move in board.legal_moves
        assert opponent_move in board.legal_moves

        # Push a move to advance the game
        env.push_moves(random_moves)


def test_randomchessenv_step():
    """Test the step method of RandomChessEnv"""
    env = RandomChessEnv(1)
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


def test_randomchessenv_invert():
    """Test that the invert flag works correctly"""
    # Create environment with invert=True
    env = RandomChessEnv(1, invert=True)
    state, mask = env.reset()

    # Get initial board
    board = CBoard.from_array(state[0]).to_board()
    assert board is not None

    # Play a move
    legal_move_idx = np.nonzero(mask[0])[0][0]
    move = np.array([legal_move_idx])

    # Push the move directly (not using step, to isolate testing of invert)
    done, reward = env.push_moves(move)

    # Get new state
    new_state = env.get_state()
    new_board = CBoard.from_array(new_state[0]).to_board()

    # After push_moves with invert=True, the board should be inverted
    # This means the player to move should still be white
    assert new_board.turn == chess.WHITE


def test_randomchessenv_game_progression():
    """Test that games progress properly with the RandomChessEnv"""
    env = RandomChessEnv(1, max_step=50)
    state, mask = env.reset()

    # Play 20 moves or until the game ends
    for _ in range(20):
        # Find a legal move
        legal_move_idx = np.nonzero(mask[0])[0][0]
        move = np.array([legal_move_idx])

        # Take the move
        next_state, next_mask, reward, done = env.step(move)

        # Update for next iteration
        state, mask = next_state, next_mask

        # If game is done, break
        if done[0]:
            break

    # Check that the final state is valid
    final_board = CBoard.from_array(state[0]).to_board()
    assert isinstance(final_board, chess.Board)

    # If the game isn't over, there should still be legal moves
    if not done[0]:
        assert len(list(final_board.legal_moves)) > 0
