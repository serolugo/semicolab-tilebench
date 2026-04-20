# semicolab-tilebench

Docker container for the SemiCoLab design suite. Includes VeriFlow and TileWizard with all dependencies pre-installed — no local setup required.

---

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

---

## Quick Start

### 1. Pull the image

```bash
docker pull serolugo/tilebench
```

### 2. Mount your workspace

**Linux / Mac:**
```bash
./mount.sh
```

**Windows:**
```bat
mount.bat
```

Or manually:
```bash
docker run -it --rm -v $(pwd):/workspace -w /workspace -p 6080:6080 serolugo/tilebench
```

### 3. Use the tools

Inside the container:

```bash
# VeriFlow — RTL verification
veriflow --db ./database init
veriflow --db ./database create-tile
veriflow --db ./database run --tile 0001 --waves

# TileWizard — wrap generic RTL into SemiCoLab tiles
tilewizard init my_project
tilewizard parse --top
tilewizard wrap
```

### 4. View waveforms

When you run with `--waves`, open your browser at:

```
http://localhost:6080
```

GTKWave will open automatically with your waveform file loaded.

---

## What's included

| Tool | Description |
|---|---|
| VeriFlow | RTL verification and documentation framework |
| TileWizard | Wraps generic IP RTL into SemiCoLab-compatible tiles |
| Icarus Verilog | Verilog simulator (`iverilog`, `vvp`) |
| Yosys | RTL synthesis (`yosys`) |
| GTKWave | Waveform viewer (available at `localhost:6080`) |
| OSS CAD Suite | Open source EDA toolchain |

---

## Workspace

Your current directory is mounted at `/workspace` inside the container. All files you create or modify are saved to your local machine.

---

## Updating

To get the latest version of the tools:

```bash
docker pull serolugo/tilebench
```

---

## Part of the SemiCoLab Ecosystem

```
TileWizard      → wraps generic IP RTL into a SemiCoLab-compatible tile
VeriFlow        → local RTL verification with waveforms
Precheck (CI)   → connectivity check + synthesis gate for shuttle submission
TileBench       → this container — runs TileWizard + VeriFlow locally
```
