#!/bin/bash
# SemiCoLab TileBench — Container entrypoint

# Start Surfer wave server in background
python3 /opt/wave_server.py &

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            SemiCoLab TileBench Suite                    ║"
echo "║                                                          ║"
echo "║  Waveform viewer →  http://localhost:7681                ║"
echo "║  Workspace       →  /workspace                          ║"
echo "║                                                          ║"
echo "║  Quick start:                                            ║"
echo "║    veriflow --db ./database init                         ║"
echo "║    veriflow --db ./database create-tile                  ║"
echo "║    veriflow --db ./database run --tile 0001 --waves      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

exec "$@"
