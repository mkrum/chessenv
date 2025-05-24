"""
Library loader for chessenv.

This module handles loading the required shared libraries from the package directory,
ensuring that the libraries are found regardless of where the package is installed.
"""

import ctypes
import sys
from pathlib import Path


def load_library(lib_name):
    """
    Load a shared library from the package directory.

    Args:
        lib_name: Name of the library file (e.g., 'libmisterqueen.so')

    Returns:
        The loaded library object
    """
    # Get the directory where this module is located
    module_dir = Path(__file__).parent.absolute()

    # Possible library locations to check
    lib_paths = [
        # Inside the package lib directory (for installed packages)
        module_dir / "lib" / lib_name,
        # Relative to the module (for development)
        module_dir.parent / "lib" / lib_name,
    ]

    # Try to load from each path
    for lib_path in lib_paths:
        if lib_path.exists():
            try:
                if sys.platform == "darwin":
                    # On macOS, RTLD_GLOBAL is needed to ensure symbols are globally available
                    return ctypes.CDLL(str(lib_path), ctypes.RTLD_GLOBAL)
                else:
                    return ctypes.CDLL(str(lib_path))
            except OSError as e:
                print(f"Warning: Failed to load {lib_path}: {e}")

    # If we get here, the library wasn't found
    raise ImportError(
        f"Could not find or load {lib_name}. Please ensure the library is properly installed."
    )


def initialize():
    """
    Initialize the required libraries for chessenv.

    This function should be called when the package is imported to ensure
    libraries are loaded before chessenv_c is imported.
    """
    try:
        # Load libraries in the correct order
        load_library("libtinycthread.so")
        load_library("libmisterqueen.so")
        return True
    except ImportError as e:
        print(f"Error initializing libraries: {e}")
        print("Please run 'build_lib.sh' to build the required libraries.")
        return False
