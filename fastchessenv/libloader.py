"""
Library loader for fastchessenv.

This module handles loading the required shared libraries from the package directory,
ensuring that the libraries are found regardless of where the package is installed.
"""

import ctypes
import logging
import os
import platform
import sys
from pathlib import Path

# Set up logging
logger = logging.getLogger("fastchessenv.libloader")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set log level based on environment variable
log_level = os.environ.get("FASTCHESSENV_LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))


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


def find_system_lib_dirs():
    """Find additional system library directories based on platform."""
    lib_dirs = ["/usr/lib", "/usr/local/lib"]

    # Add platform-specific library paths
    if sys.platform == "linux":
        # Common Linux library paths
        arch = platform.machine()
        lib_dirs.extend(
            [
                f"/usr/lib/{arch}-linux-gnu",
                "/lib",
                f"/lib/{arch}-linux-gnu",
                "/usr/lib64",
                "/usr/local/lib64",
            ]
        )

    # Add LD_LIBRARY_PATH locations
    if "LD_LIBRARY_PATH" in os.environ:
        lib_dirs.extend(os.environ["LD_LIBRARY_PATH"].split(":"))

    # Filter out non-existent paths
    return [d for d in lib_dirs if os.path.exists(d)]


# Create a variable to store the temporary library directory
_temp_lib_dir = None


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
        # Check temporary directory if set
        global _temp_lib_dir
        if _temp_lib_dir:
            lib_paths.append(Path(os.path.join(_temp_lib_dir, filename)))
        # Also check in system library paths
        for lib_dir in find_system_lib_dirs():
            lib_paths.append(Path(os.path.join(lib_dir, filename)))

    logger.debug(f"Looking for {lib_name} in: {[str(p) for p in lib_paths]}")

    # Try to load from each path
    for lib_path in lib_paths:
        if lib_path.exists():
            try:
                logger.debug(f"Found library at {lib_path}, trying to load...")
                # On all platforms, use RTLD_GLOBAL to ensure symbols are globally available
                return ctypes.CDLL(str(lib_path), ctypes.RTLD_GLOBAL)
            except OSError as e:
                logger.warning(f"Failed to load {lib_path}: {e}")
        else:
            logger.debug(f"Path does not exist: {lib_path}")

    # If we get here, the library wasn't found
    raise ImportError(
        f"Could not find or load {lib_name}. Please ensure the library is properly installed."
    )


def initialize():
    """
    Initialize the required libraries for fastchessenv.

    This function should be called when the package is imported to ensure
    libraries are loaded before fastchessenv_c is imported.
    """
    # Print system information for debugging
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Architecture: {platform.machine()}")

    # Attempt 1: Load pre-built libraries directly
    try:
        load_library("tinycthread")
        load_library("misterqueen")
        return True
    except ImportError as e:
        logger.warning(f"Error initializing libraries: {e}")
        logger.info("Attempting to build libraries locally...")

    # Attempt 2: Build via standalone setup script
    if _try_standalone_setup():
        return True

    # Attempt 3: Build via build_lib.sh shell script
    if _try_build_script():
        return True

    logger.info("Please manually build the required libraries.")
    return False


def _try_standalone_setup() -> bool:
    """Try building libraries using the standalone setup script."""
    try:
        from fastchessenv.setup_standalone import setup_libraries
    except ImportError as imp_error:
        logger.warning(f"Standalone setup script not available: {imp_error}")
        return False

    import tempfile

    logger.info("Using standalone setup script to build libraries...")

    try:
        temp_dir = tempfile.mkdtemp(prefix="fastchessenv_libs_")
        success, lib_dir, error = setup_libraries(temp_dir)
    except OSError as e:
        logger.error(f"Failed to build libraries: {e}")
        return False

    if not success:
        logger.error(f"Failed to build libraries: {error}")
        return False

    logger.info(f"Libraries built successfully in {lib_dir}")
    global _temp_lib_dir
    _temp_lib_dir = lib_dir

    # Copy libraries to package directory if possible
    _try_copy_libs_to_package(lib_dir)

    try:
        load_library("tinycthread")
        load_library("misterqueen")
        return True
    except ImportError as e:
        logger.error(f"Failed to load built libraries: {e}")
        return False


def _try_copy_libs_to_package(lib_dir: str) -> None:
    """Try to copy built libraries into the package lib/ directory."""
    import shutil

    module_dir = os.path.dirname(os.path.abspath(__file__))
    pkg_lib_dir = os.path.join(module_dir, "lib")

    try:
        if not os.access(pkg_lib_dir, os.W_OK):
            return
        os.makedirs(pkg_lib_dir, exist_ok=True)
        for lib_file in os.listdir(lib_dir):
            if lib_file.endswith((".so", ".dylib", ".dll")):
                shutil.copy2(os.path.join(lib_dir, lib_file), pkg_lib_dir)
        logger.info(f"Copied libraries to package directory: {pkg_lib_dir}")
    except (IOError, OSError) as copy_error:
        logger.warning(f"Could not copy libraries to package directory: {copy_error}")
        logger.info("Will use libraries from temporary directory instead")


def _try_build_script() -> bool:
    """Try building libraries using the build_lib.sh shell script."""
    import subprocess

    module_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(module_dir)
    build_script = os.path.join(parent_dir, "build_lib.sh")

    if not os.path.exists(build_script):
        logger.error(f"Build script not found: {build_script}")
        return False

    logger.info(f"Running build script: {build_script}")
    try:
        subprocess.check_call(["bash", build_script])
    except subprocess.SubprocessError as subp_error:
        logger.error(f"Failed to run build script: {subp_error}")
        return False

    try:
        load_library("tinycthread")
        load_library("misterqueen")
        return True
    except ImportError as e:
        logger.error(f"Failed to load libraries after build: {e}")
        return False
