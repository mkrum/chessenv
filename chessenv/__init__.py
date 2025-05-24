# Initialize the library loader first
from chessenv.libloader import initialize

# Only import the rest if libraries were loaded successfully
if initialize():
    from chessenv.env import CChessEnv, RandomChessEnv, SFCChessEnv
    from chessenv.rep import CBoard, CBoards, CMove, CMoves

    __all__ = [
        "SFCChessEnv",
        "CChessEnv",
        "RandomChessEnv",
        "CMove",
        "CBoard",
        "CMoves",
        "CBoards",
    ]
else:
    import warnings

    warnings.warn(
        "Failed to initialize chessenv libraries. "
        "Please run 'build_lib.sh' to build the required libraries."
    )
