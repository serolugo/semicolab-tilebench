# SemiCoLab TileBench

Docker environment with **VeriFlow** + **TileWizard** pre-installed and a browser-based waveform viewer (Surfer WASM) — no software installation required beyond Docker.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS / Linux)

## Quick start

### Linux / macOS

```bash
chmod +x tilebench.sh

# Start with a named project folder (recommended)
./tilebench.sh my_chip_project

# Or use the default "workspace" folder
./tilebench.sh
```

### Windows

```bat
tilebench.bat my_chip_project
```

The script creates the project folder in your current directory and mounts it into the container. Your files are always on your machine — removing the container doesn't delete them.

## Inside the container

```bash
# Initialize a new VeriFlow database
veriflow --db ./database init

# Create a new tile
veriflow --db ./database create-tile

# Run verification (with waveforms)
veriflow --db ./database run --tile 0001 --waves

# Open waveform viewer manually
# → http://localhost:7681
```

## Waveform viewer

Surfer WASM runs at **http://localhost:7681** — open it in any browser.

When you run with `--waves`, VeriFlow prints the direct URL to open the generated `.vcd` file automatically.

## Build locally

```bash
docker build -t tilebench .
```

## Stack

| Component | Version |
|---|---|
| Base image | `debian:bookworm-20250407-slim` |
| Icarus Verilog | 11.0 (apt) |
| Yosys | 0.27 (apt) |
| VeriFlow | latest (`serolugo/veriflow`) |
| TileWizard | latest (`serolugo/semicolab-ip-tile-wizard`) |
| Waveform viewer | Surfer WASM (surfer-project.org) |
