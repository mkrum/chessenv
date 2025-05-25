import chess
import numpy as np

from chessenv import CBoards, CChessEnv, CMove, CMoves


def test_env():
    env = CChessEnv(16)

    states, mask = env.reset()
    states = states.flatten()
    boards = CBoards.from_array(states).to_board()

    for step in range(200):

        random_moves_arr = env.sample_opponent()
        random_moves = CMoves.from_int(random_moves_arr).to_move()

        done, _ = env.push_moves(random_moves_arr)

        for b_idx in range(len(boards)):
            boards[b_idx].push(random_moves[b_idx])
            if done[b_idx]:
                boards[b_idx] = chess.Board()

        # TODO: En Passant is saved even if not possible
        states = env.get_state().flatten()
        states[states == 13] = 0

        recon_board = CBoards.from_board(boards).to_array()
        recon_board[recon_board == 13] = 0

        assert (states == recon_board).all()

        masks = env.get_mask()
        moves = env.get_possible_moves()

        for idx, (mask, m, b) in enumerate(zip(masks, moves, boards)):
            py_board = set(b.legal_moves)

            assert py_board == set(m.to_move())

            for i in np.nonzero(mask):
                assert CMove.from_int(i).to_move() in py_board

            for b in list(py_board):
                assert mask[CMove.from_move(b).to_int()] == 1
