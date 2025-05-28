#!/bin/bash
set -e

# Directory to store packages
DIST_DIR="./dist"
rm -rf $DIST_DIR
mkdir -p $DIST_DIR

echo "Building source distribution and wheel..."
uv run python setup.py sdist bdist_wheel

# Wait for files to be completely written
sleep 1

echo "Checking built packages:"
ls -la $DIST_DIR

echo ""
echo "To upload to Test PyPI, run:"
echo "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo ""
echo "To upload to PyPI, run:"
echo "twine upload dist/*"
