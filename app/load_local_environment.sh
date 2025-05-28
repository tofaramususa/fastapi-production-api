#!/bin/bash

# Activate hatch shell first, then load environment and run uvicorn
# Load environment variables
set -o allexport
source .env
set +o allexport

# Change to app directory and run uvicorn
cd app
uvicorn main:app --reload
EOF
