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

if not exist "%PROJECT%\veriflow"    mkdir "%PROJECT%\veriflow"
if not exist "%PROJECT%\tilewizard"  mkdir "%PROJECT%\tilewizard"

echo [tilebench] Mounting: %cd%\%PROJECT% --^> /workspace
echo [tilebench] Waveform viewer: http://localhost:7681
echo.

docker run -it --rm ^
    -e TERM=xterm-256color ^
    -e HOST_WORKSPACE=%cd%\%PROJECT% ^
    -e SEMICOLAB_DOCKER=1 ^
    -v "%cd%\%PROJECT%:/workspace" ^
    -w /workspace ^
    -p 7681:7681 ^
    tilebench
