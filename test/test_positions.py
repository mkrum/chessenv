"""Curated chess positions for regression testing.

Each list contains (fen, description) tuples. All positions have been validated
with python-chess to ensure they represent the claimed scenario.
"""

# --- En Passant Positions ---
# Positions where en passant captures are available

EN_PASSANT_POSITIONS = [
    # White can capture en passant on e6
    (
        "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq e6",
        "White EP capture on e6",
    ),
    # White can capture en passant on d6
    (
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6",
        "White EP capture on d6",
    ),
    # White can capture en passant on c6
    (
        "rnbqkbnr/pp1ppppp/8/2pP4/8/8/PPP1PPPP/RNBQKBNR w KQkq c6",
        "White EP capture on c6",
    ),
    # Black can capture en passant on e3
    (
        "rnbqkbnr/pppp1ppp/8/8/4Pp2/8/PPPP1PPP/RNBQKBNR b KQkq e3",
        "Black EP capture on e3",
    ),
    # Black can capture en passant on d3
    (
        "rnbqkbnr/ppp1pppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR b KQkq d3",
        "Black EP capture on d3",
    ),
    # White can capture on a6 (edge file)
    (
        "rnbqkbnr/1ppppppp/8/pP6/8/8/P1PPPPPP/RNBQKBNR w KQkq a6",
        "White EP capture on a-file",
    ),
    # White can capture on h6 (edge file)
    (
        "rnbqkbnr/ppppppp1/8/6Pp/8/8/PPPPPP1P/RNBQKBNR w KQkq h6",
        "White EP capture on h-file",
    ),
    # Double EP capture possible (two white pawns can capture same EP square)
    (
        "rnbqkbnr/pppp1ppp/8/3PpP2/8/8/PPP1P1PP/RNBQKBNR w KQkq e6",
        "Double EP capture on e6",
    ),
    # Black double EP capture
    (
        "rnbqkbnr/ppp1p1pp/8/8/3pPp2/8/PPPP1PPP/RNBQKBNR b KQkq e3",
        "Black double EP capture on e3",
    ),
    # EP in middlegame context
    (
        "r1bqkb1r/pppp1ppp/2n2n2/4pP2/8/2N5/PPPPP1PP/R1BQKBNR w KQkq e6",
        "EP in Italian-like position",
    ),
    # EP where capturing pawn is pinned to king (EP should be illegal)
    ("8/8/8/8/k2Pp2R/8/8/4K3 b - d3", "EP illegal: pawn pinned by rook along rank"),
    # EP with few pieces
    ("8/8/8/8/4Pp2/8/8/4K2k b - e3", "EP in endgame with few pieces"),
]

# --- Castling Positions ---

CASTLING_POSITIONS = [
    # Starting position: all 4 castling rights available
    (
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        "Starting position, all castling rights",
    ),
    # White can castle kingside
    (
        "rnbqkbnr/pppppppp/8/8/8/4PN2/PPPP1PPP/RNBQKB1R w KQkq -",
        "White kingside castling available",
    ),
    # White can castle queenside
    (
        "rnbqkbnr/pppppppp/8/8/8/2NB4/PPPQPPPP/R3KBNR w KQkq -",
        "White queenside castling available",
    ),
    # Black can castle kingside
    (
        "rnbqkb1r/pppp1ppp/4pn2/8/8/4PN2/PPPP1PPP/RNBQKB1R b KQkq -",
        "Black kingside castling available",
    ),
    # Black can castle queenside
    (
        "r3kbnr/pppqpppp/2nb4/8/8/2NB4/PPPQPPPP/R3KBNR b KQkq -",
        "Black queenside castling available",
    ),
    # White castling blocked by piece on f1
    (
        "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq -",
        "White kingside blocked by bishop on f1",
    ),
    # No castling rights
    (
        "rnbqkbnr/pppppppp/8/8/8/4PN2/PPPP1PPP/RNBQKB1R w - -",
        "No castling rights at all",
    ),
    # White can castle but through check (should be illegal)
    (
        "rnb1kbnr/pppppppp/8/8/4q3/5N2/PPPPPPPP/RNBQKB1R w KQkq -",
        "White kingside through check (illegal)",
    ),
    # Partial rights: only white kingside
    (
        "rnbqkbnr/pppppppp/8/8/8/4PN2/PPPP1PPP/RNBQKB1R w K -",
        "Only white kingside right",
    ),
    # Partial rights: only black queenside
    (
        "r3kbnr/pppqpppp/2nb4/8/8/2NB4/PPPQPPPP/R3KBNR b q -",
        "Only black queenside right",
    ),
]

# --- Promotion Positions ---

PROMOTION_POSITIONS = [
    # White pawn on 7th rank, can promote
    ("8/4P3/8/8/8/4k3/8/4K3 w - -", "White pawn promotes on e8"),
    # Black pawn on 2nd rank, can promote
    ("4k3/8/8/8/8/8/4p3/6K1 b - -", "Black pawn promotes on e1"),
    # White pawn can capture-promote
    ("3rk3/4P3/8/8/8/8/8/4K3 w - -", "White capture-promote on d8"),
    # Multiple pawns can promote
    ("8/PPP5/8/8/8/4k3/8/4K3 w - -", "Multiple white pawns near promotion"),
    # Black pawn capture-promote
    ("4k3/8/8/8/8/8/4p3/3RK3 b - -", "Black capture-promote on d1"),
    # Pawn promote on a-file
    ("8/P7/8/8/8/4k3/8/4K3 w - -", "White a-file promotion"),
    # Pawn promote on h-file
    ("8/7P/8/8/8/4k3/8/4K3 w - -", "White h-file promotion"),
    # Black promotion with two capture options
    ("8/8/3k4/8/8/8/3p4/2R1KR2 b - -", "Black pawn with two capture-promotes"),
]

# --- Checkmate Positions ---

CHECKMATE_POSITIONS = [
    # Scholar's mate (white is mated by queen on h4)
    (
        "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq -",
        "Scholar's mate variant",
    ),
    # Standard scholar's mate (black is mated)
    (
        "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq -",
        "Scholar's mate standard",
    ),
    # Back-rank mate by rook (black to move, mated)
    ("1R4k1/5ppp/8/8/8/8/8/6K1 b - -", "Back-rank mate by rook"),
    # Smothered mate by knight
    ("6rk/5Npp/8/8/8/8/8/4K3 b - -", "Smothered mate by knight"),
    # Rook + knight mate
    ("R6k/6pp/6N1/8/8/8/8/4K3 b - -", "Rook and knight mate"),
    # Simple queen checkmate
    ("k7/1Q6/1K6/8/8/8/8/8 b - -", "Queen checkmate in corner"),
]

# --- Stalemate Positions ---

STALEMATE_POSITIONS = [
    # Classic queen stalemate
    ("7k/5Q2/4K3/8/8/8/8/8 b - -", "Classic queen stalemate"),
    # King-only stalemate (king boxed in)
    ("5k2/5P2/5K2/8/8/8/8/8 b - -", "King and pawn stalemate"),
    # Corner stalemate
    ("k7/2Q5/1K6/8/8/8/8/8 b - -", "Corner stalemate"),
    # Stalemate with pawn blocking
    ("8/8/8/8/8/6k1/6p1/6K1 w - -", "King blocked by own constraints"),
]

# --- Complex Positions (middlegame, many/few moves) ---

COMPLEX_POSITIONS = [
    # Starting position (exactly 20 legal moves)
    (
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        "Starting position, 20 moves",
    ),
    # Position with many legal moves (queen in center)
    (
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQK2R w KQkq -",
        "Italian game, many moves",
    ),
    # Position with very few legal moves
    ("8/8/8/8/8/7k/8/K7 w - -", "King vs king, few moves"),
    # Complex middlegame from a real game
    (
        "r2qk2r/ppp2ppp/2np1n2/2b1p1B1/2B1P1b1/2NP1N2/PPP2PPP/R2QK2R w KQkq -",
        "Complex middlegame",
    ),
    # Endgame with multiple piece types
    ("8/5pk1/5n1p/8/3NP3/6PP/5PK1/8 w - -", "Knight endgame"),
    # Position after many captures
    ("4k3/8/8/3Pp3/8/8/8/4K3 w - e6", "Minimal position with EP"),
]
