"""
Test en passant handling across multiple positions simultaneously
"""

import chess
import numpy as np

from chessenv.rep import CBoard, CBoards

# Test positions with en passant captures from our earlier tests
en_passant_positions = [
    "4k3/8/8/8/Pp6/8/8/4K3 b - a3 0 1",
    "4k3/8/8/pP6/8/8/8/4K3 w - a6 0 1",
    "4k3/8/8/8/pPp5/8/8/4K3 b - b3 0 1",
    "4k3/8/8/PpP5/8/8/8/4K3 w - b6 0 1",
    "4k3/8/8/8/1pPp4/8/8/4K3 b - c3 0 1",
    "4k3/8/8/1PpP4/8/8/8/4K3 w - c6 0 1",
    "4k3/8/8/8/2pPp3/8/8/4K3 b - d3 0 1",
    "4k3/8/8/2PpP3/8/8/8/4K3 w - d6 0 1",
]


def check_move_generation(fen):
    """Check and compare move generation between sequential and parallel methods for a position"""
    print(f"\nTesting position: {fen}")

    # Create a python-chess board for reference
    py_board = chess.Board(fen)
    py_moves = set(str(m) for m in py_board.legal_moves)

    # Get moves using CBoard.to_possible_moves
    cboard = CBoard.from_fen(fen)
    seq_moves = set(cboard.to_possible_moves().to_str())

    # Test the CBoards implementation manually to ensure we're using the version that was just fixed
    # First get the board array
    board_arr = cboard.to_array()

    # Create a CBoards object directly
    cboards_data = np.zeros(69, dtype=np.int32)
    cboards_data[:] = board_arr
    cboards = CBoards.from_array(cboards_data)

    # Get moves using the CBoards.to_possible_moves
    par_moves = set(cboards.to_possible_moves()[0].to_str())

    # Compare results
    print(f"Sequential moves count: {len(seq_moves)}")
    print(f"Parallel moves count: {len(par_moves)}")
    print(f"Python-chess moves count: {len(py_moves)}")

    if seq_moves != par_moves:
        print("\nDISCREPANCY BETWEEN SEQUENTIAL AND PARALLEL:")
        print(f"Missing in parallel: {seq_moves - par_moves}")
        print(f"Extra in parallel: {par_moves - seq_moves}")
    else:
        print("\nNo discrepancy between sequential and parallel")

    # Compare with python-chess for validation
    if seq_moves != py_moves:
        print("\nSequential vs python-chess discrepancy:")
        print(f"Missing in sequential: {py_moves - seq_moves}")
        print(f"Extra in sequential: {seq_moves - py_moves}")

    if par_moves != py_moves:
        print("\nParallel vs python-chess discrepancy:")
        print(f"Missing in parallel: {py_moves - par_moves}")
        print(f"Extra in parallel: {par_moves - py_moves}")

    return seq_moves == par_moves and seq_moves == py_moves


def test_all_positions():
    """Test all en passant positions"""
    results = {}
    for fen in en_passant_positions:
        results[fen] = check_move_generation(fen)

    # Summarize results
    print("\n=== SUMMARY ===")
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"Passed: {passed}/{total} positions")

    if passed < total:
        print("\nFailed positions:")
        for fen, result in results.items():
            if not result:
                print(f"- {fen}")


if __name__ == "__main__":
    test_all_positions()
