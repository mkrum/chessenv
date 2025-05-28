#!/bin/bash
set -e

# Directory to store wheels
WHEELHOUSE="./wheelhouse"
mkdir -p $WHEELHOUSE

# Build source distribution
echo "Building source distribution..."
uv run python -m build --sdist
mkdir -p $WHEELHOUSE/source
cp dist/*.tar.gz $WHEELHOUSE/source/

# Build for x86_64 Linux
echo "Building wheel for Linux x86_64..."
if [ -x "$(command -v docker)" ]; then
    docker build --no-cache -f Dockerfile.manylinux_x86_64 -t fastchessenv-manylinux-x86_64 .
    mkdir -p $WHEELHOUSE/linux_x86_64
    docker run --rm -v $(pwd)/wheelhouse:/wheelhouse fastchessenv-manylinux-x86_64 \
        bash -c "cp /io/dist/*.whl /wheelhouse/linux_x86_64/ 2>/dev/null || echo 'No wheels found to copy'"
else
    echo "Docker not available. Skipping Linux x86_64 build."
fi

# Build for aarch64 Linux (ARM64)
# Note: This requires QEMU for cross-architecture builds on x86_64 host
echo "Building wheel for Linux aarch64..."
if [ -x "$(command -v docker)" ]; then
    if docker buildx ls 2>/dev/null | grep -q linux/arm64; then
        # Use buildx for cross-platform builds if available
        docker buildx build --no-cache --platform linux/arm64 -f Dockerfile.manylinux_aarch64 -t fastchessenv-manylinux-aarch64 .
        mkdir -p $WHEELHOUSE/linux_aarch64
        docker run --platform linux/arm64 --rm -v $(pwd)/wheelhouse:/wheelhouse fastchessenv-manylinux-aarch64 \
            bash -c "cp /io/dist/*.whl /wheelhouse/linux_aarch64/ 2>/dev/null || echo 'No wheels found to copy'"
    else
        echo "Docker buildx with ARM64 support not available. Skipping aarch64 build."
        echo "To enable cross-platform builds, install Docker with buildx support."
    fi
else
    echo "Docker not available. Skipping Linux aarch64 build."
fi

# Build for current macOS platform
echo "Building wheel for current macOS platform..."
uv run python -m build --wheel
MACOS_ARCH=$(uname -m)
mkdir -p $WHEELHOUSE/macos_$MACOS_ARCH
cp dist/*.whl $WHEELHOUSE/macos_$MACOS_ARCH/

echo "All wheels built successfully!"
echo "Wheels are stored in the '$WHEELHOUSE' directory"
echo ""
echo "To upload all wheels to PyPI, run:"
echo "twine upload wheelhouse/**/*.whl wheelhouse/source/*.tar.gz"
