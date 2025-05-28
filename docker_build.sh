#!/bin/bash

# Build Docker image with OpenMP support
docker build -t chessenv:openmp . --progress=plain

echo "Docker image 'chessenv:openmp' built successfully!"
echo ""
echo "You can run the image with the following command:"
echo "docker run -it --rm chessenv:openmp"
echo ""
echo "To run tests inside the container:"
echo "docker run -it --rm chessenv:openmp python3.8 -m pytest"
echo ""
echo "To benchmark with OpenMP:"
echo "docker run -it --rm chessenv:openmp python3.8 benchmark.py"
