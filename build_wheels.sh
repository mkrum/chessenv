#!/bin/bash
set -e

# This script builds wheels for multiple platforms using Docker

# Directory to store wheels
WHEELHOUSE="./wheelhouse"
mkdir -p $WHEELHOUSE

# Function to build wheels for a specific platform
build_for_platform() {
    PLATFORM=$1
    DOCKER_IMAGE=$2

    echo "Building wheels for $PLATFORM using $DOCKER_IMAGE..."

    # Run the Docker container to build the wheel
    docker run --rm \
        -v $(pwd):/io \
        $DOCKER_IMAGE \
        /bin/bash -c "
            cd /io &&
            pip install -U pip build wheel &&
            python -m build --wheel &&
            mkdir -p $WHEELHOUSE/$PLATFORM &&
            cp dist/*.whl $WHEELHOUSE/$PLATFORM/
        "

    echo "Wheels for $PLATFORM built successfully!"
}

# Build source distribution (platform-independent)
echo "Building source distribution..."
uv build --sdist
mkdir -p $WHEELHOUSE/source
cp dist/*.tar.gz $WHEELHOUSE/source/

# Build wheels for various platforms
# Linux x86_64
build_for_platform "linux_x86_64" "quay.io/pypa/manylinux2014_x86_64"

# Linux aarch64 (ARM64)
build_for_platform "linux_aarch64" "quay.io/pypa/manylinux2014_aarch64"

# macOS - need to build on actual macOS machines
# This script will build the wheel for the current macOS platform
echo "Building wheel for current macOS platform..."
uv build --wheel
MACOS_ARCH=$(uname -m)
mkdir -p $WHEELHOUSE/macos_$MACOS_ARCH
cp dist/*.whl $WHEELHOUSE/macos_$MACOS_ARCH/

echo "All wheels built successfully!"
echo "Wheels are stored in the '$WHEELHOUSE' directory"
echo ""
echo "To upload all wheels to PyPI, run:"
echo "twine upload $WHEELHOUSE/**/*.whl $WHEELHOUSE/source/*.tar.gz"
