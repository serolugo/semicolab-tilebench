#!/bin/bash
# SemiCoLab TileBench — Linux / macOS launcher
#
# Usage:
#   ./tilebench.sh                   # uses "workspace" as project folder
#   ./tilebench.sh my_chip_project   # creates/opens ./my_chip_project/

set -e

PROJECT="${1:-workspace}"

# Create the project folder if it doesn't exist
if [ ! -d "$PROJECT" ]; then
    echo "[tilebench] Creating project folder: ./$PROJECT"
    mkdir -p "$PROJECT"
fi

ABS_PATH="$(cd "$PROJECT" && pwd)"

echo "[tilebench] Mounting: $ABS_PATH → /workspace"
echo "[tilebench] Waveform viewer will be at: http://localhost:7681"
echo ""

docker run -it --rm \
    -v "$ABS_PATH:/workspace" \
    -w /workspace \
    -p 7681:7681 \
    tilebench
