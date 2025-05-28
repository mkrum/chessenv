"""
Library loader for chessenv.

This module handles loading the required shared libraries from the package directory,
ensuring that the libraries are found regardless of where the package is installed.
"""

import ctypes
import platform
import sys
from pathlib import Path


def get_platform_lib_extension():
    """Get the appropriate library extension for the current platform."""
    if sys.platform == "win32":
        return ".dll"
    elif sys.platform == "darwin":
        return ".dylib"
    else:
        return ".so"


def get_platform_architecture_suffix():
    """Get the appropriate architecture suffix for the current platform."""
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":
        if machine == "arm64":
            return "_arm64"
        else:
            return "_x86_64"
    elif system == "Linux":
        if "arm" in machine or "aarch64" in machine:
            return "_aarch64"
        else:
            return "_x86_64"
    elif system == "Windows":
        if machine == "amd64" or machine == "x86_64":
            return "_x86_64"
        elif machine == "arm64":
            return "_arm64"

    # Default case - no suffix
    return ""


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

    # Get the base library name without extension
    if lib_name.startswith("lib"):
        base_name = lib_name.split(".")[0]
    else:
        base_name = f"lib{lib_name.split('.')[0]}"

    # Get platform-specific extension and architecture suffix
    ext = get_platform_lib_extension()
    arch_suffix = get_platform_architecture_suffix()

    # Generate possible library filenames with platform/architecture variants
    lib_filenames = [
        # Try platform-specific named libraries first
        f"{base_name}{arch_suffix}{ext}",
        f"{base_name}{ext}",
        # Fallback to .so for compatibility
        f"{base_name}.so",
    ]

    # Possible library locations to check
    lib_paths = []
    for filename in lib_filenames:
        # Inside the package lib directory (for installed packages)
        lib_paths.append(module_dir / "lib" / filename)
        # Relative to the module (for development)
        lib_paths.append(module_dir.parent / "lib" / filename)

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
        load_library("tinycthread")
        load_library("misterqueen")
        return True
    except ImportError as e:
        print(f"Error initializing libraries: {e}")
        print("Please run 'build_lib.sh' to build the required libraries.")
        return False
