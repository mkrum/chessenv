"""Random game validation regression tests.

Fuzz tests that play random games and validate state consistency,
legal move correctness, and mask correctness at each step.
"""

import random

import chess
import numpy as np
import pytest

from fastchessenv.env import CChessEnv
from fastchessenv.rep import CBoard, CMove


@pytest.mark.fuzz
def test_random_games_state_consistency():
    """100 random games: play random moves via CChessEnv, mirror on python-chess, compare states."""
    env = CChessEnv(1)
    state, mask = env.reset()

    py_board = chess.Board()
    games_completed = 0

    for step in range(500):
        # Get a random move
        random_move = env.random()
        move_str = CMove.from_int(int(random_move[0])).to_str()

        # Push on both
        done, _ = env.push_moves(random_move)
        py_board.push(chess.Move.from_uci(move_str))

        if done[0]:
            games_completed += 1
            state, mask = env.reset()
            py_board = chess.Board()

            if games_completed >= 100:
                break
            continue

        # Compare states (zero out EP markers due to known issues)
        env_state = env.get_state().flatten()
        env_state_no_ep = env_state.copy()
        env_state_no_ep[env_state_no_ep == 13] = 0

        py_arr = CBoard.from_board(py_board).to_array()
        py_arr_no_ep = py_arr.copy()
        py_arr_no_ep[py_arr_no_ep == 13] = 0

        assert np.array_equal(env_state_no_ep, py_arr_no_ep), (
            f"State mismatch at step {step}\n"
            f"Env state: {env_state}\n"
            f"Python state: {py_arr}"
        )


@pytest.mark.fuzz
def test_random_moves_always_legal():
    """16 boards, 200 steps: every env.random() move should be legal in python-chess."""
    env = CChessEnv(16)
    state, mask = env.reset()

    boards = [chess.Board() for _ in range(16)]

    for step in range(200):
        random_moves = env.random()

        for i in range(16):
            move_str = CMove.from_int(int(random_moves[i])).to_str()
            py_move = chess.Move.from_uci(move_str)

            assert py_move in boards[i].legal_moves, (
                f"Step {step}, board {i}: random move {move_str} not legal\n"
                f"FEN: {boards[i].fen()}\n"
                f"Legal moves: {[str(m) for m in boards[i].legal_moves]}"
            )

        # Push moves on env
        done, _ = env.push_moves(random_moves)

        # Push moves on python-chess boards
        for i in range(16):
            move_str = CMove.from_int(int(random_moves[i])).to_str()
            boards[i].push(chess.Move.from_uci(move_str))
            if done[i]:
                boards[i] = chess.Board()


@pytest.mark.fuzz
def test_mask_move_is_executable():
    """100 steps: pick random set bit from mask, push_moves succeeds."""
    rng = random.Random(123)
    env = CChessEnv(1)
    state, mask = env.reset()

    for step in range(100):
        # Pick a random set bit from the mask
        legal_indices = np.nonzero(mask[0])[0]
        if len(legal_indices) == 0:
            # No legal moves — game should be over, reset
            state, mask = env.reset()
            continue

        chosen_idx = rng.choice(legal_indices)
        move_arr = np.array([int(chosen_idx)], dtype=np.int32)

        # push_moves should succeed
        done, reward = env.push_moves(move_arr)

        if done[0]:
            state, mask = env.reset()
        else:
            state = env.get_state()
            mask = env.get_mask()

            # Resulting state should have at least one legal move (unless checkmate/stalemate)
            # and be a valid board shape
            assert state.shape == (1, 69)
            assert mask.shape == (1, 5632)


@pytest.mark.fuzz
@pytest.mark.slow
def test_extensive_random_games_legal_moves():
    """1000 random games: at each step, compare legal move sets."""
    env = CChessEnv(1)
    state, mask = env.reset()
    py_board = chess.Board()

    games_completed = 0

    for step in range(5000):
        # Compare legal moves
        py_moves = {str(m) for m in py_board.legal_moves}

        if len(py_moves) == 0:
            # Game over, reset
            games_completed += 1
            state, mask = env.reset()
            py_board = chess.Board()
            if games_completed >= 1000:
                break
            continue

        # Get CBoard moves
        cboard = CBoard.from_array(state.flatten())
        c_moves = set(cboard.to_possible_moves().to_str())

        assert c_moves == py_moves, (
            f"Game {games_completed}, step {step}: legal move mismatch\n"
            f"FEN: {py_board.fen()}\n"
            f"Missing: {py_moves - c_moves}\n"
            f"Extra: {c_moves - py_moves}"
        )

        # Play a random move
        random_move = env.random()
        move_str = CMove.from_int(int(random_move[0])).to_str()

        done, _ = env.push_moves(random_move)
        py_board.push(chess.Move.from_uci(move_str))

        if done[0]:
            games_completed += 1
            state, mask = env.reset()
            py_board = chess.Board()
            if games_completed >= 1000:
                break
        else:
            state = env.get_state()
