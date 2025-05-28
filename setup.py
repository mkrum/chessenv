import os
import platform
import shutil
import subprocess

import setuptools

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None
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
            try:
                subprocess.call(["bash", build_script])
            except Exception as e:
                print(f"Warning: Could not build libraries using build_lib.sh: {e}")
                print("This is normal when installing from source distribution.")
                # Create empty lib files to allow installation to proceed
                # These will be replaced by the platform-specific ones at runtime
                os.makedirs(os.path.dirname(MISTERQUEEN_LIB), exist_ok=True)
                if not os.path.exists(MISTERQUEEN_LIB):
                    with open(MISTERQUEEN_LIB, "wb") as f:
                        f.write(b"")
                if not os.path.exists(TINYCTHREAD_LIB):
                    with open(TINYCTHREAD_LIB, "wb") as f:
                        f.write(b"")
        else:
            print(
                "WARNING: build_lib.sh not found. Creating empty placeholder libraries."
            )
            # Create empty lib files to allow installation to proceed
            os.makedirs(os.path.dirname(MISTERQUEEN_LIB), exist_ok=True)
            if not os.path.exists(MISTERQUEEN_LIB):
                with open(MISTERQUEEN_LIB, "wb") as f:
                    f.write(b"")
            if not os.path.exists(TINYCTHREAD_LIB):
                with open(TINYCTHREAD_LIB, "wb") as f:
                    f.write(b"")


def copy_libraries():
    """Copy the built libraries to the package directory"""
    # Ensure source libraries exist
    build_libraries()

    # Create destination directory
    dst_lib_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fastchessenv", "lib"
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


if bdist_wheel is not None:

    class CustomBdistWheel(bdist_wheel):
        """Custom wheel building command that tags wheels as platform-specific"""

        def finalize_options(self):
            bdist_wheel.finalize_options(self)
            # Mark this package as platform-specific (not pure Python)
            self.root_is_pure = False

        def get_tag(self):
            # Get the platform tag
            python_tag, abi_tag, platform_tag = bdist_wheel.get_tag(self)

            # Use a specific platform tag based on the system and architecture
            system = platform.system().lower()
            machine = platform.machine().lower()

            if system == "darwin":
                # macOS - arm64 or x86_64
                if machine == "arm64":
                    platform_tag = "macosx_11_0_arm64"
                else:
                    platform_tag = "macosx_10_9_x86_64"
            elif system == "linux":
                # Linux - x86_64 or aarch64
                if "arm" in machine or "aarch64" in machine:
                    platform_tag = "manylinux2014_aarch64"
                else:
                    platform_tag = "manylinux2014_x86_64"

            return python_tag, abi_tag, platform_tag

    # Create a dictionary to hold command classes
    cmdclass = {
        "build_py": CustomBuildPy,
        "develop": CustomDevelop,
        "install": CustomInstall,
        "bdist_wheel": CustomBdistWheel,
    }
else:
    # Without wheel, use standard command classes
    cmdclass = {
        "build_py": CustomBuildPy,
        "develop": CustomDevelop,
        "install": CustomInstall,
    }


setuptools.setup(
    name="fastchessenv",
    version="0.1.1",
    description="Chess Environment for Reinforcement Learning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chessenv",  # Update with your GitHub repo
    packages=["fastchessenv", "fastchessenv.lib"],
    package_data={
        "fastchessenv": ["lib/*.so"],
    },
    include_package_data=True,
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "numpy", "python-chess"],
    cmdclass=cmdclass,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="chess, reinforcement-learning, openmp",
)
