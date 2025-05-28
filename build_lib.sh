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

# Create shared libraries with platform-specific naming
echo "Creating shared libraries..."

# Detect platform and architecture
OS_NAME="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

# Set file extension based on platform
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  LIB_EXT=".dylib"
  # Also create .so for backward compatibility
  COMPAT_EXT=".so"

  # macOS specific flags
  EXTRA_FLAGS=""
  ARCH_SUFFIX=""
  if [[ $ARCH == 'arm64' ]]; then
    EXTRA_FLAGS="-arch arm64"
    ARCH_SUFFIX="_arm64"
  else
    ARCH_SUFFIX="_x86_64"
  fi

  # Create platform-specific libraries
  gcc $EXTRA_FLAGS -shared -o "lib/libmisterqueen${ARCH_SUFFIX}${LIB_EXT}" MisterQueen/build/release/*.o -lpthread
  gcc $EXTRA_FLAGS -shared -o "lib/libtinycthread${ARCH_SUFFIX}${LIB_EXT}" MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread

  # Create compatibility symlinks with .so extension
  ln -sf "libmisterqueen${ARCH_SUFFIX}${LIB_EXT}" "lib/libmisterqueen${ARCH_SUFFIX}${COMPAT_EXT}"
  ln -sf "libtinycthread${ARCH_SUFFIX}${LIB_EXT}" "lib/libtinycthread${ARCH_SUFFIX}${COMPAT_EXT}"

  # Also create generic symlinks without architecture suffix
  ln -sf "libmisterqueen${ARCH_SUFFIX}${LIB_EXT}" "lib/libmisterqueen${LIB_EXT}"
  ln -sf "libtinycthread${ARCH_SUFFIX}${LIB_EXT}" "lib/libtinycthread${LIB_EXT}"
  ln -sf "libmisterqueen${ARCH_SUFFIX}${COMPAT_EXT}" "lib/libmisterqueen${COMPAT_EXT}"
  ln -sf "libtinycthread${ARCH_SUFFIX}${COMPAT_EXT}" "lib/libtinycthread${COMPAT_EXT}"
else
  # Linux
  LIB_EXT=".so"

  # Determine architecture suffix
  ARCH_SUFFIX=""
  if [[ $ARCH == 'x86_64' ]]; then
    ARCH_SUFFIX="_x86_64"
  elif [[ $ARCH == 'aarch64' || $ARCH == 'arm64' ]]; then
    ARCH_SUFFIX="_aarch64"
  fi

  # Create platform-specific libraries
  gcc -shared -o "lib/libmisterqueen${ARCH_SUFFIX}${LIB_EXT}" MisterQueen/build/release/*.o -lpthread -fopenmp
  gcc -shared -o "lib/libtinycthread${ARCH_SUFFIX}${LIB_EXT}" MisterQueen/build/release/deps/tinycthread/tinycthread.o -lpthread

  # Create generic symlinks without architecture suffix
  ln -sf "libmisterqueen${ARCH_SUFFIX}${LIB_EXT}" "lib/libmisterqueen${LIB_EXT}"
  ln -sf "libtinycthread${ARCH_SUFFIX}${LIB_EXT}" "lib/libtinycthread${LIB_EXT}"
fi

echo "Libraries built successfully!"
echo "Now you can run: python copy_libs.py && python build.py && pip install -e ."
