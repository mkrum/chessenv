# FastChessEnv

A Chess Environment for Reinforcement Learning with Stockfish integration and OpenMP support.

## Installation

### Easy Local Installation

Run the installation script:

```bash
./install.sh
```

This will:
1. Build the MisterQueen libraries
2. Copy the libraries to the package directory
3. Build the Python extension
4. Install the package in development mode

### Manual Installation

1. Build the MisterQueen libraries:

```bash
./build_lib.sh
```

2. Copy the libraries to the package directory:

```bash
python copy_libs.py
```

3. Build the Python extension and install:

```bash
python build.py
pip install -e .
```

### Remote Installation

You can install directly from the repository:

```bash
pip install git+https://github.com/yourusername/fastchessenv.git
```

Or with uv:

```bash
uv pip install git+https://github.com/yourusername/fastchessenv.git
```

### Docker Installation

To build and run with Docker:

```bash
./docker_build.sh
docker run -it --rm fastchessenv:openmp
```

## Testing

Run the tests to verify everything is working correctly:

```bash
python -m pytest
```

## Usage

### Basic Usage

```python
import fastchessenv

# Create a chess environment with 4 parallel environments
env = fastchessenv.CChessEnv(4)

# Reset the environments
state, mask = env.reset()

# Make a move
move_arr = env.random()  # Sample random moves
next_state, next_mask, reward, done = env.step(move_arr)
```

### Using Stockfish for Opponent Moves

```python
import fastchessenv

# Create a chess environment with Stockfish opponents
env = fastchessenv.SFCChessEnv(4, depth=3)

# Reset the environments
state, mask = env.reset()

# Make a move
move_arr = env.random()  # Sample random moves
next_state, next_mask, reward, done = env.step(move_arr)
```

### Using Random Opponent Moves

```python
import fastchessenv

# Create a chess environment with random opponents
env = fastchessenv.RandomChessEnv(4)

# Reset the environments
state, mask = env.reset()

# Make a move
move_arr = env.random()  # Sample random moves
next_state, next_mask, reward, done = env.step(move_arr)
```

## OpenMP Support

FastChessEnv uses OpenMP for parallelization. See [OPENMP.md](OPENMP.md) for details on how to enable and configure OpenMP support.

## Cross-Platform Support

FastChessEnv is designed to work across multiple platforms and architectures:

- macOS (Intel x86_64 and Apple Silicon arm64)
- Linux (x86_64 and aarch64)

The package includes platform-specific binary libraries that are automatically selected at runtime based on your system. If you're building from source, the build system will compile libraries optimized for your current platform.

### Building for Multiple Platforms

This package includes Docker-based tools to build wheels for multiple platforms:

#### Using Docker for Cross-Platform Builds

```bash
# Build wheels for multiple platforms using Docker
./docker_build_wheels.sh
```

This script will:
1. Build a source distribution
2. Use Docker to build wheels for Linux x86_64
3. Use Docker with buildx (if available) to build wheels for Linux aarch64/ARM64
4. Build a wheel for your current macOS platform

All wheels will be stored in the `wheelhouse` directory, organized by platform.

#### Manual Multi-Platform Building

If you prefer to build manually, you'll need to:
1. Build on each target platform (macOS arm64, macOS x86_64, Linux x86_64, Linux aarch64)
2. Collect the wheels in one place
3. Upload all wheels + the source distribution to PyPI

#### GitHub Actions

This repository includes GitHub Actions workflows that automatically build wheels for multiple platforms when a new release is created.

## Requirements

- Python 3.6+
- cffi
- numpy
- chess
- Stockfish (optional, for SFCChessEnv)
- GCC with OpenMP support (for optimal performance)
