import chess
from chessenv import CChessEnv, CBoards, CMoves


def test_env():
    env = CChessEnv(16)

    states = env.reset().flatten()
    boards = CBoards.from_array(states).to_board()

    for _ in range(500):

        random_moves_arr = env.sample_opponent()
        random_moves = CMoves.from_array(random_moves_arr).to_move()

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

        moves = env.get_possible_moves()

        for (m, b) in zip(moves, boards):
            py_board = set(b.legal_moves)
            assert py_board == set(m.to_move())
