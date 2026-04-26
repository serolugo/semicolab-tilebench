@echo off
REM SemiCoLab TileBench — Windows launcher
REM
REM Usage:
REM   tilebench.bat                   uses "workspace" as project folder
REM   tilebench.bat my_chip_project   creates/opens .\my_chip_project\

set PROJECT=%~1
if "%PROJECT%"=="" set PROJECT=workspace

if not exist "%PROJECT%" (
    echo [tilebench] Creating project folder: .\%PROJECT%
    mkdir "%PROJECT%"
)

echo [tilebench] Mounting: %cd%\%PROJECT% --^> /workspace
echo [tilebench] Waveform viewer will be at: http://localhost:7681
echo.

docker run -it --rm ^
    -v "%cd%\%PROJECT%:/workspace" ^
    -w /workspace ^
    -p 7681:7681 ^
    tilebench
