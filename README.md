# SemiCoLab TileBench

Docker environment with **VeriFlow** + **TileWizard** pre-installed and a browser-based waveform viewer (Surfer WASM) — no software installation required beyond Docker.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS / Linux)

## Quick start

### Linux / macOS

```bash
chmod +x semicolab-tilebench/tilebench.sh

# Start with a named project folder (recommended)
semicolab-tilebench/tilebench.sh my_chip_project

# Or use the default "workspace" folder
semicolab-tilebench/tilebench.sh
```

### Windows

```bat
semicolab-tilebench\tilebench.bat my_chip_project
```

The launcher creates the project folder and two subdirectories (`veriflow/` and `tilewizard/`) and mounts everything into the container. Your files always stay on your machine.

## Inside the container

### Interactive TUI (recommended)

```bash
# VeriFlow — navigate databases, tiles, and runs
veriflow

# TileWizard — navigate projects and generate tiles
tilewizard
```

Both tools launch a Textual TUI when run without arguments.

### CLI (direct commands)

```bash
# VeriFlow
veriflow --db ./veriflow/my_db init
veriflow --db ./veriflow/my_db create-tile
veriflow --db ./veriflow/my_db run --tile 0001 --waves

# TileWizard
tilewizard init my_project
tilewizard parse --top my_module
tilewizard wrap
```

## Workspace layout

```
your_project/
├── veriflow/        ← VeriFlow databases
│   └── my_db/
└── tilewizard/      ← TileWizard projects
    └── my_ip/
        └── src/
```

## Waveform viewer

Surfer WASM runs at **http://localhost:7681** — open it in any browser while the container is running.

## Build locally

```bash
cd semicolab-tilebench
docker build -t tilebench .
```

## Stack

| Component | Details |
|---|---|
| Base image | `debian:bookworm-20250407-slim` |
| Icarus Verilog | 11.0 (apt) |
| Yosys | 0.27 (apt) |
| VeriFlow | latest (`serolugo/veriflow`) |
| TileWizard | latest (`serolugo/semicolab-ip-tile-wizard`) |
| TUI | Textual |
| Waveform viewer | Surfer WASM |
