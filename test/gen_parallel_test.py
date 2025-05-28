"""
This script generates a test position that shows discrepancies between
sequential and parallel move generation.
"""

import random

import chess

from chessenv.rep import CBoard, CBoards


def check_position(fen):
    """Test a position and print detailed info if there's a discrepancy"""
    # Sequential approach
    board = CBoard.from_fen(fen)
    seq_moves = set(board.to_possible_moves().to_str())

    # Parallel approach (using CBoards with a single board)
    boards = CBoards.from_fen([fen])
    par_moves = set(boards.to_possible_moves()[0].to_str())

    if seq_moves != par_moves:
        print(f"\nDiscrepancy found for position: {fen}")
        chess_board = chess.Board(fen)
        print(f"Board:\n{chess_board}")

        missing = seq_moves - par_moves
        extra = par_moves - seq_moves

        if missing:
            print(f"\nMoves in sequential but missing in parallel ({len(missing)}):")
            for m in sorted(missing):
                print(f"  {m}")

        if extra:
            print(f"\nMoves in parallel but missing in sequential ({len(extra)}):")
            for m in sorted(extra):
                print(f"  {m}")

        # Check against python-chess
        py_moves = set(str(m) for m in chess_board.legal_moves)

        if seq_moves != py_moves:
            print("\nSequential vs python-chess:")
            print(f"  Missing in sequential: {py_moves - seq_moves}")
            print(f"  Extra in sequential: {seq_moves - py_moves}")

        if par_moves != py_moves:
            print("\nParallel vs python-chess:")
            print(f"  Missing in parallel: {py_moves - par_moves}")
            print(f"  Extra in parallel: {par_moves - py_moves}")

        return True
    return False


def generate_random_positions(count=100):
    """Generate random chess positions"""
    positions = []
    board = chess.Board()

    for _ in range(count):
        # Start from initial position
        board.reset()

        # Make random moves
        num_moves = random.randint(5, 40)
        for _ in range(num_moves):
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            board.push(random.choice(legal_moves))

        positions.append(board.fen())

    return positions


def test_known_problematic_castling_positions():
    """Test positions with complex castling rights"""
    positions = [
        # Standard starting position
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        # Positions with different castling rights
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w Kk - 0 1",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w Qq - 0 1",
        # Positions with en passant possibilities
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1",
        "rnbqkbnr/pppppp1p/8/8/6Pp/8/PPPPP1P1/RNBQKBNR b KQkq g3 0 1",
        # Positions with complex piece arrangements
        "r1bqk2r/ppp2ppp/2n2n2/2bpp3/4P3/2PP1N2/PP3PPP/RNBQKB1R w KQkq - 0 1",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 1",
    ]

    found_discrepancy = False
    for pos in positions:
        if check_position(pos):
            found_discrepancy = True

    return found_discrepancy


def test_en_passant_positions():
    """Test various en passant positions that might cause issues"""
    positions = []

    # Generate all possible en passant positions
    for file in range(8):
        # White pawn just moved from rank 2 to 4
        board = chess.Board()
        board.clear()

        # Place pawns
        square = chess.square(file, 3)  # e4
        board.set_piece_at(square, chess.Piece(chess.PAWN, chess.WHITE))

        # Add black pawn beside it
        if file > 0:
            square_left = chess.square(file - 1, 3)  # d4
            board.set_piece_at(square_left, chess.Piece(chess.PAWN, chess.BLACK))

        if file < 7:
            square_right = chess.square(file + 1, 3)  # f4
            board.set_piece_at(square_right, chess.Piece(chess.PAWN, chess.BLACK))

        # Set kings
        board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))

        # Set en passant square
        ep_square = chess.square(file, 2)  # e3
        board.ep_square = ep_square

        # Set black to move
        board.turn = chess.BLACK

        positions.append(board.fen())

        # Do the same for black pawn moving from rank 7 to 5
        board = chess.Board()
        board.clear()

        # Place pawns
        square = chess.square(file, 4)  # e5
        board.set_piece_at(square, chess.Piece(chess.PAWN, chess.BLACK))

        # Add white pawns beside it
        if file > 0:
            square_left = chess.square(file - 1, 4)  # d5
            board.set_piece_at(square_left, chess.Piece(chess.PAWN, chess.WHITE))

        if file < 7:
            square_right = chess.square(file + 1, 4)  # f5
            board.set_piece_at(square_right, chess.Piece(chess.PAWN, chess.WHITE))

        # Set kings
        board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))

        # Set en passant square
        ep_square = chess.square(file, 5)  # e6
        board.ep_square = ep_square

        # Set white to move
        board.turn = chess.WHITE

        positions.append(board.fen())

    found_discrepancy = False
    for pos in positions:
        if check_position(pos):
            found_discrepancy = True

    return found_discrepancy


if __name__ == "__main__":
    print("Testing known problematic castling positions...")
    castling_discrepancy = test_known_problematic_castling_positions()

    print("\nTesting en passant positions...")
    en_passant_discrepancy = test_en_passant_positions()

    print("\nTesting randomly generated positions...")
    random_positions = generate_random_positions(200)
    random_discrepancy = False

    for i, pos in enumerate(random_positions):
        print(f"Testing random position {i+1}/{len(random_positions)}...", end="\r")
        if check_position(pos):
            random_discrepancy = True

    if not (castling_discrepancy or en_passant_discrepancy or random_discrepancy):
        print("\nNo discrepancies found in any test positions!")
