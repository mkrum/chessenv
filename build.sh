#!/bin/bash
set -e

# Check if MisterQueen directory exists
if [ -d "./MisterQueen" ]; then
    echo "MisterQueen directory already exists, rebuilding..."
else
    # Clone if it doesn't exist
    git clone https://github.com/fogleman/MisterQueen.git ./MisterQueen
fi

# Build MisterQueen
cd ./MisterQueen && make clean && make && cd ..

# Create local lib directory to avoid using /usr/local
mkdir -p lib

# Build libmisterqueen.so from object files
if [[ "$(uname)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    # For macOS arm64
    clang -arch arm64 -shared -o ./lib/libmisterqueen.so ./MisterQueen/build/release/*.o -lpthread
else
    # For other platforms
    gcc -shared -o ./lib/libmisterqueen.so ./MisterQueen/build/release/*.o -lpthread
fi

# Set environment variables to use the local lib directory
export LD_LIBRARY_PATH="$PWD/lib:$LD_LIBRARY_PATH"
export LIBRARY_PATH="$PWD/lib:$LIBRARY_PATH"

# Install the package
uv pip install -e .
