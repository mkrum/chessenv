"""
Find the index of the en passant square in the board array
"""

import chess

from chessenv.rep import CBoard

# Test positions with en passant captures
test_position = "4k3/8/8/8/Pp6/8/8/4K3 b - a3 0 1"


def find_ep_square_in_array():
    """Find the index of the en passant square in the board array"""
    board = chess.Board(test_position)
    print(f"Testing position: {board.fen()}")
    print(f"Board:\n{board}")

    # Extract the en passant square from the FEN
    fen_parts = board.fen().split(" ")
    ep_square = fen_parts[3]
    print(f"En passant square in FEN: {ep_square}")

    # Convert to CBoard and get the array representation
    cboard = CBoard.from_fen(board.fen())
    board_arr = cboard.to_array()

    # Dump the complete board array
    print("Board array (69 elements):")
    for i in range(0, 64, 8):
        row = board_arr[i : i + 8]
        print(f"Squares {i}-{i+7}: {row}")

    print("Remaining elements (65-68):")
    print(board_arr[64:])

    # Look for code 13 (en passant marker)
    for i, val in enumerate(board_arr):
        if val == 13:
            rank = 7 - (i // 8) if i < 64 else "N/A"
            file = i % 8 if i < 64 else "N/A"
            print(f"Found en passant marker (13) at index {i}")
            if i < 64:
                print(f"This corresponds to rank {rank}, file {file}")
                print(f"In algebraic notation: {chr(file + ord('a'))}{rank + 1}")

    # Look for non-zero board.ep value
    # This would require calling into the C code


if __name__ == "__main__":
    find_ep_square_in_array()
