#!/bin/bash
# SemiCoLab TileBench — Container entrypoint
# Starts Xvfb + x11vnc + noVNC in background, then runs the user command

# Start virtual display
Xvfb :1 -screen 0 1280x800x24 &
sleep 1

# Start VNC server on virtual display
x11vnc -display :1 -nopw -listen localhost -xkb -forever -quiet &
sleep 1

# Start noVNC web interface
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         SemiCoLab TileBench Suite            ║"
echo "║                                              ║"
echo "║  GTKWave available at: http://localhost:6080 ║"
echo "║  Workspace: /workspace                       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Run the user command (default: bash)
exec "$@"
