"""
Test script to find and analyze differences between sequential and parallel move generation.
"""

import random

import chess

from chessenv.rep import CBoard, CBoards

# Read test data
with open("test/test_data.csv", "r") as test_data:
    lines = test_data.readlines()

parsed_lines = [line.rstrip().split(",") for line in lines]
fen_positions, _ = zip(*parsed_lines)


def analyze_position(fen):
    """
    Analyze a specific position for move generation differences
    between sequential and parallel implementations.
    """
    print(f"\nAnalyzing position: {fen}")

    # Generate moves using sequential approach
    board = CBoard.from_fen(fen)
    sequential_moves = set(board.to_possible_moves().to_str())

    # Generate moves using parallel approach
    boards = CBoards.from_fen([fen])
    parallel_moves = set(boards.to_possible_moves()[0].to_str())

    # Check if the move sets match
    if sequential_moves == parallel_moves:
        print("✅ Moves match! No differences found.")
        return True

    # Display the board
    chess_board = chess.Board(fen)
    print(f"Board:\n{chess_board}")

    # Display the differences
    missing_in_parallel = sequential_moves - parallel_moves
    extra_in_parallel = parallel_moves - sequential_moves

    print("❌ Move mismatch found!")
    print(f"Sequential moves: {len(sequential_moves)}")
    print(f"Parallel moves: {len(parallel_moves)}")

    if missing_in_parallel:
        print(f"\nMissing in parallel ({len(missing_in_parallel)} moves):")
        for move in sorted(missing_in_parallel):
            uci_move = chess.Move.from_uci(move)
            print(f"  - {move} ({chess_board.san(uci_move)})")

    if extra_in_parallel:
        print(f"\nExtra in parallel ({len(extra_in_parallel)} moves):")
        for move in sorted(extra_in_parallel):
            uci_move = chess.Move.from_uci(move)
            print(f"  - {move} ({chess_board.san(uci_move)})")

    # Analyze legality of the differing moves using python-chess as reference
    legal_moves = set(str(m) for m in chess_board.legal_moves)

    if missing_in_parallel:
        missing_legal = missing_in_parallel.intersection(legal_moves)
        missing_illegal = missing_in_parallel - legal_moves
        print("\nOf the missing moves:")
        print(f"  - Legal according to python-chess: {len(missing_legal)}")
        print(f"  - Illegal according to python-chess: {len(missing_illegal)}")

    if extra_in_parallel:
        extra_legal = extra_in_parallel.intersection(legal_moves)
        extra_illegal = extra_in_parallel - legal_moves
        print("\nOf the extra moves:")
        print(f"  - Legal according to python-chess: {len(extra_legal)}")
        print(f"  - Illegal according to python-chess: {len(extra_illegal)}")

    return False


def find_discrepancies(num_positions=100):
    """
    Find positions where move generation differs between
    sequential and parallel implementations.
    """
    print(
        f"Searching for move generation discrepancies across {num_positions} positions..."
    )

    discrepancies = []
    sampled_fens = random.sample(fen_positions, min(num_positions, len(fen_positions)))

    for i, fen in enumerate(sampled_fens):
        print(f"Testing position {i+1}/{len(sampled_fens)}...", end="\r")

        # Generate moves using sequential approach
        board = CBoard.from_fen(fen)
        sequential_moves = set(board.to_possible_moves().to_str())

        # Generate moves using parallel approach
        boards = CBoards.from_fen([fen])
        parallel_moves = set(boards.to_possible_moves()[0].to_str())

        # Check if the move sets match
        if sequential_moves != parallel_moves:
            discrepancies.append(fen)
            print(f"\nDiscrepancy found in position {i+1}: {fen}")

    print(f"\nFound {len(discrepancies)} positions with move generation discrepancies.")
    return discrepancies


def test_specific_positions():
    """Test positions that are known to cause discrepancies."""
    known_problem_positions = [
        # Add specific positions that showed discrepancies here
        "r2qkb1r/pp3ppp/2p1pn2/8/3Pn3/5N2/PPP1BPPP/RNBQ1RK1 b kq -",
        "r3kb1r/ppqn1ppp/2p1pn2/8/3P4/2N2N2/PPP1BPPP/R1BQK2R w KQkq -",
        "rnbqk2r/pp2bppp/3ppn2/8/3NPP2/2N5/PPP3PP/R1BQKB1R b KQkq -",
        # Add more positions as you find them
    ]

    for fen in known_problem_positions:
        analyze_position(fen)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--find":
        # Find discrepancies in random positions
        num_positions = 100
        if len(sys.argv) > 2:
            num_positions = int(sys.argv[2])
        discrepancies = find_discrepancies(num_positions)

        # Analyze the first few discrepancies
        for i, fen in enumerate(discrepancies[:5]):
            print(f"\n{'='*80}")
            print(f"Detailed analysis of discrepancy {i+1}:")
            analyze_position(fen)
    else:
        # Test specific known problem positions
        test_specific_positions()
