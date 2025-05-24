# ChessEnv

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
pip install git+https://github.com/yourusername/chessenv.git
```

Or with uv:

```bash
uv pip install git+https://github.com/yourusername/chessenv.git
```

### Docker Installation

To build and run with Docker:

```bash
./docker_build.sh
docker run -it --rm chessenv:openmp
```

## Testing

Run the tests to verify everything is working correctly:

```bash
python -m pytest
```

## Usage

### Basic Usage

```python
import chessenv

# Create a chess environment with 4 parallel environments
env = chessenv.CChessEnv(4)

# Reset the environments
state, mask = env.reset()

# Make a move
move_arr = env.random()  # Sample random moves
next_state, next_mask, reward, done = env.step(move_arr)
```

### Using Stockfish for Opponent Moves

```python
import chessenv

# Create a chess environment with Stockfish opponents
env = chessenv.SFCChessEnv(4, depth=3)

# Reset the environments
state, mask = env.reset()

# Make a move
move_arr = env.random()  # Sample random moves
next_state, next_mask, reward, done = env.step(move_arr)
```

### Using Random Opponent Moves

```python
import chessenv

# Create a chess environment with random opponents
env = chessenv.RandomChessEnv(4)

# Reset the environments
state, mask = env.reset()

# Make a move
move_arr = env.random()  # Sample random moves
next_state, next_mask, reward, done = env.step(move_arr)
```

## OpenMP Support

ChessEnv uses OpenMP for parallelization. See [OPENMP.md](OPENMP.md) for details on how to enable and configure OpenMP support.

## Requirements

- Python 3.6+
- cffi
- numpy
- chess
- Stockfish (optional, for SFCChessEnv)
- GCC with OpenMP support (for optimal performance)
