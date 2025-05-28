#!/usr/bin/env bash

# Exit on error
set -e

# Print commands
set -x

# Run pytest with coverage
pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=80 \
    --asyncio-mode=auto \
    -v \
    app/tests/

# Generate coverage report
coverage html

echo "Tests completed successfully!"
echo "Coverage report available at htmlcov/index.html"
