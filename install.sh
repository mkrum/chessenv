#!/bin/bash
set -e

echo "Installing chessenv with dependencies..."

# Build the MisterQueen libraries if needed
if [ ! -d "lib" ] || [ ! -f "lib/libmisterqueen.so" ]; then
    echo "Building MisterQueen libraries..."
    ./build_lib.sh
fi

# Copy libraries to the package directory
echo "Copying libraries to package directory..."
python copy_libs.py

# Build the Python extension
echo "Building Python extension..."
python build.py

# Install the package
echo "Installing package..."
pip install -e .
