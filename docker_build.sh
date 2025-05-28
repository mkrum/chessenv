#!/bin/bash

# Default to building the standard image
BUILD_TYPE=${1:-standard}

if [ "$BUILD_TYPE" == "slim" ]; then
    # Build slim Docker image with Python 3.10
    echo "Building slim Python 3.10 image for testing..."
    docker build -t fastchessenv:slim-test -f Dockerfile.slim . --progress=plain

    echo "Docker image 'fastchessenv:slim-test' built successfully!"
    echo ""
    echo "You can run the image with the following command:"
    echo "docker run -it --rm fastchessenv:slim-test"
    echo ""
    echo "To run tests inside the container:"
    echo "docker run -it --rm fastchessenv:slim-test python -m pytest"
    echo ""
    echo "To benchmark with OpenMP:"
    echo "docker run -it --rm fastchessenv:slim-test python benchmark.py"
else
    # Build standard Docker image with OpenMP support
    echo "Building standard Ubuntu 20.04 image with OpenMP support..."
    docker build -t fastchessenv:openmp . --progress=plain

    echo "Docker image 'fastchessenv:openmp' built successfully!"
    echo ""
    echo "You can run the image with the following command:"
    echo "docker run -it --rm fastchessenv:openmp"
    echo ""
    echo "To run tests inside the container:"
    echo "docker run -it --rm fastchessenv:openmp python3.8 -m pytest"
    echo ""
    echo "To benchmark with OpenMP:"
    echo "docker run -it --rm fastchessenv:openmp python3.8 benchmark.py"
fi
