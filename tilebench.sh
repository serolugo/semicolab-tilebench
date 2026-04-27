#!/bin/bash
# SemiCoLab TileBench — Linux / macOS launcher
#
# Usage:
#   ./tilebench.sh                   # uses "workspace" as project folder
#   ./tilebench.sh my_chip_project   # creates/opens ./my_chip_project/

set -e

PROJECT="${1:-workspace}"

# Create the project folder and workspace subdirectories
if [ ! -d "$PROJECT" ]; then
    echo "[tilebench] Creating project folder: ./$PROJECT"
    mkdir -p "$PROJECT"
fi

mkdir -p "$PROJECT/veriflow"
mkdir -p "$PROJECT/tilewizard"

ABS_PATH="$(cd "$PROJECT" && pwd)"

echo "[tilebench] Mounting: $ABS_PATH → /workspace"
echo "[tilebench] Waveform viewer: http://localhost:7681"
echo ""

docker run -it --rm \
    -e TERM=xterm-256color \
    -e HOST_WORKSPACE="$ABS_PATH" \
    -e SEMICOLAB_DOCKER=1 \
    -v "$ABS_PATH:/workspace" \
    -w /workspace \
    -p 7681:7681 \
    tilebench
