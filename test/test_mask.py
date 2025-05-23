import numpy as np

from chessenv.rep import CBoard, legal_mask_convert


def test_get_mask_basic():
    """Test that get_mask returns a mask of the correct shape"""
    # Test with standard starting position
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    board = CBoard.from_fen(fen)

    # Get mask
    mask = board.get_mask()

    # Check shape - should be 64*88 elements
    assert mask.shape == (64 * 88,)

    # Should be mostly zeros with some ones for legal moves
    assert np.sum(mask) > 0
    assert np.sum(mask) <= len(list(board.to_board().legal_moves))


def test_get_mask_nonzero():
    """Test that get_mask returns a mask with nonzero elements"""
    # Use a simple position to test
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    board = CBoard.from_fen(fen)
    chess_board = board.to_board()

    # Get mask
    mask = board.get_mask()

    # Get all legal moves from the chess board
    legal_moves = list(chess_board.legal_moves)

    # Verify that mask has nonzero elements
    assert np.sum(mask) > 0

    # Number of legal moves should be reasonable
    assert len(legal_moves) > 10 and len(legal_moves) < 30


def test_get_mask_specific_positions():
    """Test get_mask on specific board positions"""
    test_positions = [
        # Initial position - white to move
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        # After e4 - black to move
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3",
        # Complex middle game position
        "r1bqkb1r/pp3ppp/2n1pn2/3p4/3P4/2N1PN2/PPQ2PPP/R1B1KB1R w KQkq -",
    ]

    for fen in test_positions:
        board = CBoard.from_fen(fen)
        mask = board.get_mask()

        # Check that mask has reasonable values
        assert np.sum(mask) > 0, f"Position {fen} should have legal moves"
        assert (
            np.sum(mask) < 100
        ), f"Position {fen} should have a reasonable number of legal moves"


def test_get_mask_with_board():
    """Test that get_mask returns a mask that relates to the board position"""
    # Test with different positions
    board1 = CBoard.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
    board2 = CBoard.from_fen(
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -"
    )

    mask1 = board1.get_mask()
    mask2 = board2.get_mask()

    # Masks for different positions should be different
    assert not np.array_equal(
        mask1, mask2
    ), "Different positions should have different masks"

    # Verify mask changes when position changes
    board3 = CBoard.from_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3")
    mask3 = board3.get_mask()
    assert not np.array_equal(mask1, mask3), "After a move, mask should change"


def test_legal_mask_convert():
    """Test the legal_mask_convert function structure"""
    # Create a simple mask with a few legal moves
    # Get real masks for proper testing
    board1 = CBoard.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
    board2 = CBoard.from_fen(
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -"
    )

    mask = np.stack([board1.get_mask(), board2.get_mask()])

    # Convert the mask
    move_map = legal_mask_convert(mask)

    # Check that the move map has the right number of entries
    assert len(move_map) == 2

    # Verify that move_map has entries
    # At this point we just want to check that the function runs
    # and returns a structured result
    if len(move_map[0]) > 0:
        # If we have entries, check the format
        assert move_map[0].shape[1] == 3  # [0, from, to] format


def test_get_mask_and_possible_moves_shape():
    """Test that get_mask and to_possible_moves both produce some output"""
    # Test with multiple positions
    positions = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -",
        "r1bqk2r/ppp2ppp/2n2n2/2bpp3/2B1P3/2PP1N2/PP3PPP/RNBQK2R w KQkq -",
    ]

    for fen in positions:
        board = CBoard.from_fen(fen)

        # Get mask
        mask = board.get_mask()

        # Get possible moves
        possible_moves = board.to_possible_moves()

        # Check that the possible moves array has content
        assert len(possible_moves.data) > 0, "Should return some possible moves"

        # Check that mask has content
        assert np.sum(mask) > 0, "Mask should have some legal moves"
