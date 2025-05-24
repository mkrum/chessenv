FROM ubuntu:20.04

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies with OpenMP support
RUN apt update && apt install -y \
    python3.8 \
    python3-pip \
    python3.8-dev \
    build-essential \
    git \
    cmake \
    gcc \
    g++ \
    libffi-dev \
    libomp-dev \
    stockfish \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workdir/

# Copy all necessary files
COPY . /workdir/

# Make scripts executable
RUN chmod +x /workdir/build_lib.sh
RUN chmod +x /workdir/install.sh

# Install Python dependencies
RUN python3.8 -m pip install --no-cache-dir --upgrade pip
RUN python3.8 -m pip install --no-cache-dir cffi numpy pytest chess

# Build libraries and install the package
RUN ./build_lib.sh
RUN python3.8 copy_libs.py
RUN python3.8 build.py
RUN python3.8 -m pip install -e .

# Install additional Python dependencies
RUN python3.8 -m pip install --no-cache-dir open_spiel || python3.8 -m pip install --no-cache-dir open_spiel

# Make sure Stockfish is available in PATH
RUN which stockfish

# Verify everything is working
RUN python3.8 -c "import chessenv; env = chessenv.CChessEnv(1); print('Basic environment working')"
RUN python3.8 -c "import chessenv; env = chessenv.SFCChessEnv(4); print('Stockfish environment working with OpenMP')"

# Set the default command
CMD ["python3.8"]
