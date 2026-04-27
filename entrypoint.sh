#!/bin/bash
# SemiCoLab TileBench — Container entrypoint

# Ensure workspace subdirs exist (safety net if launcher didn't create them)
mkdir -p /workspace/veriflow
mkdir -p /workspace/tilewizard

# Start Surfer wave server in background
python3 /opt/wave_server.py &

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            SemiCoLab TileBench Suite                    ║"
echo "║                                                          ║"
echo "║  veriflow     →  RTL verification (TUI or CLI)          ║"
echo "║  tilewizard   →  IP tile generator (TUI or CLI)         ║"
echo "║                                                          ║"
echo "║  Waveform viewer →  http://localhost:7681               ║"
echo "║  Workspace       →  /workspace                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

exec "$@"
