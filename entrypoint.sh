#!/bin/bash
# SemiCoLab TileBench — Container entrypoint

# Ensure workspace subdirs exist
mkdir -p /workspace/veriflow
mkdir -p /workspace/tilewizard

# Start Surfer wave server in background
python3 /opt/wave_server.py &

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            SemiCoLab TileBench Suite                    ║"
echo "║                                                          ║"
echo "║  tilebench    →  TUI unificada (selector)               ║"
echo "║  veriflow     →  RTL verification (TUI o CLI)           ║"
echo "║  tilewizard   →  IP tile generator (TUI o CLI)          ║"
echo "║                                                          ║"
echo "║  Waveform viewer →  http://localhost:7681               ║"
echo "║  Workspace       →  /workspace                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

exec "$@"
