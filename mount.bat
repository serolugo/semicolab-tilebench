@echo off
REM SemiCoLab TileBench — Mount script for Windows

docker run -it --rm ^
  -v "%cd%:/workspace" ^
  -w /workspace ^
  -p 6080:6080 ^
  serolugo/tilebench
