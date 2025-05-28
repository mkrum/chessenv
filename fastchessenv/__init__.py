__version__ = "0.1.1"

# Initialize the library loader first
from fastchessenv.libloader import initialize

# Only import the rest if libraries were loaded successfully
if initialize():
    from fastchessenv.env import CChessEnv, RandomChessEnv, SFCChessEnv
    from fastchessenv.rep import CBoard, CBoards, CMove, CMoves

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
        "Failed to initialize fastchessenv libraries. "
        "Please run 'build_lib.sh' to build the required libraries."
    )
