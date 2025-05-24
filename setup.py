import os
import shutil
import subprocess
import sys

import setuptools
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install

# Check if libraries are built
LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
MISTERQUEEN_LIB = os.path.join(LIB_DIR, "libmisterqueen.so")
TINYCTHREAD_LIB = os.path.join(LIB_DIR, "libtinycthread.so")


def build_libraries():
    """Build the MisterQueen libraries if they don't exist"""
    if not (os.path.exists(MISTERQUEEN_LIB) and os.path.exists(TINYCTHREAD_LIB)):
        print("Required libraries not found. Building MisterQueen...")
        # Run the build_lib.sh script to build libraries
        build_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "build_lib.sh"
        )
        if os.path.exists(build_script):
            subprocess.call(["bash", build_script])
        else:
            print("ERROR: build_lib.sh not found. Please run it manually.")
            sys.exit(1)


def copy_libraries():
    """Copy the built libraries to the package directory"""
    # Ensure source libraries exist
    build_libraries()

    # Create destination directory
    dst_lib_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "chessenv", "lib"
    )
    os.makedirs(dst_lib_dir, exist_ok=True)

    # Copy the libraries
    print(f"Copying libraries to {dst_lib_dir}")
    shutil.copy2(MISTERQUEEN_LIB, dst_lib_dir)
    shutil.copy2(TINYCTHREAD_LIB, dst_lib_dir)


class CustomBuildPy(build_py):
    """Custom build command to build MisterQueen libraries and copy them to the package"""

    def run(self):
        # Build and copy libraries
        build_libraries()
        copy_libraries()

        # Proceed with regular build
        build_py.run(self)


class CustomDevelop(develop):
    """Custom develop command for development mode"""

    def run(self):
        # Build and copy libraries
        build_libraries()
        copy_libraries()

        # Proceed with regular develop
        develop.run(self)


class CustomInstall(install):
    """Custom install command"""

    def run(self):
        # Build and copy libraries
        build_libraries()
        copy_libraries()

        # Proceed with regular install
        install.run(self)


setuptools.setup(
    name="chessenv",
    version="0.1.0",
    description="Chess Environment for Reinforcement Learning",
    author="Michael Krumdick",
    packages=["chessenv"],
    package_data={
        "chessenv": ["lib/*.so"],
    },
    include_package_data=True,
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "numpy", "chess"],
    cmdclass={
        "build_py": CustomBuildPy,
        "develop": CustomDevelop,
        "install": CustomInstall,
    },
    python_requires=">=3.6",
)
