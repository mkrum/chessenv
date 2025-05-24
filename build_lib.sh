#!/bin/bash
set -e

# Create lib directory if it doesn't exist
mkdir -p lib

# Check if MisterQueen exists, clone if not
if [ ! -d "MisterQueen" ]; then
  echo "Cloning MisterQueen repository..."
  git clone https://github.com/fogleman/MisterQueen.git
fi

# Set compile flags based on platform
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS - Clang doesn't support OpenMP by default
  COMPILE_FLAGS="-std=c99 -Wall -O3 -fPIC"

  # Check for arm64 architecture
  if [[ $(uname -m) == 'arm64' ]]; then
    COMPILE_FLAGS="$COMPILE_FLAGS -arch arm64"
  fi
else
  # Linux - gcc with OpenMP
  COMPILE_FLAGS="-std=c99 -Wall -O3 -fPIC -fopenmp"
fi

# Build MisterQueen with appropriate flags
echo "Building MisterQueen with compile flags: $COMPILE_FLAGS"
cd MisterQueen
make clean || true
make COMPILE_FLAGS="$COMPILE_FLAGS"
cd ..

# Create shared libraries
echo "Creating shared libraries..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS specific flags
  EXTRA_FLAGS=""
  if [[ $(uname -m) == 'arm64' ]]; then
    EXTRA_FLAGS="-arch arm64"
  fi
  gcc $EXTRA_FLAGS -shared -o lib/libmisterqueen.so MisterQueen/build/release/*.o -lpthread
  gcc $EXTRA_FLAGS -shared -o lib/libtinycthread.so MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread
else
  # Linux flags
  gcc -shared -o lib/libmisterqueen.so MisterQueen/build/release/*.o -lpthread -fopenmp
  gcc -shared -o lib/libtinycthread.so MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread
fi

echo "Libraries built successfully!"
echo "Now you can run: python copy_libs.py && python build.py && pip install -e ."
