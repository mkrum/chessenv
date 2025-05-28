"""
Test script to specifically debug en passant handling in the parallel and sequential implementations.
"""

import chess

from chessenv.rep import CBoard, CBoards, _array_to_fen


def array_to_fen_verbose(board_arr):
    """Converts a board array to fen with detailed logging"""
    print("Converting board array to FEN...")

    # Look for en passant marker (value 13) in the board array
    ep_found = False
    for i in range(64):  # First 64 elements represent the board
        if board_arr[i] == 13:
            rank = 7 - (i // 8)  # Convert from array index to chess rank (0-7)
            file = i % 8  # Convert from array index to chess file (0-7)
            print(
                f"Found en passant marker at rank={rank}, file={file} (array index {i})"
            )
            ep_found = True

            # Calculate the expected en passant square in algebraic notation
            file_letter = chr(file + ord("a"))
            rank_number = rank + 1
            ep_square = f"{file_letter}{rank_number}"
            print(f"Expected en passant square: {ep_square}")

    if not ep_found:
        print("No en passant marker found in board array")

    # Now use the standard conversion function
    fen_result = _array_to_fen(board_arr)

    print(f"Generated FEN: {fen_result}")

    # Check if the FEN contains an en passant square
    fen_parts = fen_result.split(" ")
    if len(fen_parts) >= 4:
        ep_part = fen_parts[3]
        if ep_part != "-":
            print(f"FEN contains en passant square: {ep_part}")
        else:
            print("FEN does not contain an en passant square (-)")

    return fen_result


def test_en_passant_handling():
    """Test en passant handling in detail"""
    # First, test one of the positions that showed a discrepancy
    board = chess.Board("4k3/8/8/8/Pp6/8/8/4K3 b - a3 0 1")

    print(f"Test position: {board.fen()}")
    print(f"Board:\n{board}")

    # Extract the en passant square from the FEN
    fen_parts = board.fen().split(" ")
    ep_square = fen_parts[3]
    print(f"En passant square in FEN: {ep_square}")

    # Verify that en passant is possible
    py_moves = [str(m) for m in board.legal_moves]
    ep_moves = [m for m in py_moves if m.endswith("a3")]
    print(f"En passant moves in python-chess: {ep_moves}")

    print(f"Test position: {board.fen()}")
    print(f"Board:\n{board}")

    # Verify that en passant is possible
    moves = [board.san(m) for m in board.legal_moves]
    ep_moves = [m for m in moves if "x" in m and m.endswith("3")]
    print(f"En passant moves according to python-chess: {ep_moves}")
    print(f"Test position: {board.fen()}")
    print(f"Board:\n{board}")

    # Convert to CBoard
    cboard = CBoard.from_fen(board.fen())
    board_arr = cboard.to_array()

    # Analyze the array representation
    print("\nBoard array representation:")

    # Format the board array as an 8x8 grid for visualization
    grid = []
    for i in range(8):
        row = []
        for j in range(8):
            idx = i * 8 + j
            row.append(f"{board_arr[idx]:2}")
        grid.append(" ".join(row))

    for i, row in enumerate(reversed(grid)):  # Reverse to match chess board orientation
        print(f"{8-i} {row}")

    print("  a  b  c  d  e  f  g  h")

    # Now convert back to FEN with detailed logging
    print("\nConverting back to FEN:")
    _ = array_to_fen_verbose(
        board_arr
    )  # We don't use the result, just the debug output

    # Test sequential move generation
    seq_moves = cboard.to_possible_moves().to_str()

    # Test parallel move generation
    par_moves = CBoards.from_fen([board.fen()]).to_possible_moves()[0].to_str()

    # Compare the moves
    seq_set = set(seq_moves)
    par_set = set(par_moves)

    print("\nMove generation comparison:")
    print(f"Sequential moves: {len(seq_set)}")
    print(f"Parallel moves: {len(par_set)}")

    if seq_set != par_set:
        print("\nDiscrepancy found!")
        print(f"Moves in sequential but not in parallel: {seq_set - par_set}")
        print(f"Moves in parallel but not in sequential: {par_set - seq_set}")
    else:
        print("\nNo discrepancy - move sets match exactly")

    # Check against python-chess
    py_moves = {str(m) for m in board.legal_moves}
    print(f"\nPython-chess moves: {len(py_moves)}")

    if seq_set != py_moves:
        print("Sequential vs python-chess discrepancy:")
        print(f"  Missing in sequential: {py_moves - seq_set}")
        print(f"  Extra in sequential: {seq_set - py_moves}")

    if par_set != py_moves:
        print("Parallel vs python-chess discrepancy:")
        print(f"  Missing in parallel: {py_moves - par_set}")
        print(f"  Extra in parallel: {par_set - py_moves}")


if __name__ == "__main__":
    test_en_passant_handling()
