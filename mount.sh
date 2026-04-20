#!/bin/bash
# SemiCoLab TileBench — Mount script for Linux/Mac

docker run -it --rm \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -p 6080:6080 \
  serolugo/tilebench
