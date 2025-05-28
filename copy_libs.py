#!/usr/bin/env python
"""
Copy built libraries to the chessenv package directory for distribution.
This script ensures the libraries are bundled with the package.
"""

import os
import shutil
import sys


def copy_libs():
    # Directory paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_lib_dir = os.path.join(script_dir, "lib")
    dst_lib_dir = os.path.join(script_dir, "fastchessenv", "lib")

    # Create destination directory if it doesn't exist
    os.makedirs(dst_lib_dir, exist_ok=True)

    # Check if source libraries exist
    misterqueen_lib = os.path.join(src_lib_dir, "libmisterqueen.so")
    tinycthread_lib = os.path.join(src_lib_dir, "libtinycthread.so")

    if not os.path.exists(misterqueen_lib) or not os.path.exists(tinycthread_lib):
        print("ERROR: Libraries not found in the lib directory.")
        print("Please run build_lib.sh first to build the libraries.")
        sys.exit(1)

    # Copy libraries
    print("Copying libraries to package directory...")
    shutil.copy2(misterqueen_lib, dst_lib_dir)
    shutil.copy2(tinycthread_lib, dst_lib_dir)

    print(f"Libraries copied to {dst_lib_dir}")


if __name__ == "__main__":
    copy_libs()
