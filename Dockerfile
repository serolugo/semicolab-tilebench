FROM debian:bookworm-20250407-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV SEMICOLAB_DOCKER=1

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    iverilog \
    yosys \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    curl \
    unzip \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ────────────────────────────────────────────────────────
RUN pip3 install --no-cache-dir --break-system-packages \
    pyyaml \
    jinja2 \
    rich \
    pyfiglet \
    textual \
    terminaltexteffects \
    weasyprint \
    markdown

# ── VeriFlow ───────────────────────────────────────────────────────────────────
RUN pip3 install --no-cache-dir --break-system-packages \
    git+https://github.com/serolugo/veriflow.git

# ── TileWizard ─────────────────────────────────────────────────────────────────
RUN pip3 install --no-cache-dir --break-system-packages \
    git+https://github.com/serolugo/semicolab-ip-tile-wizard.git

# ── Surfer WASM (pre-compiled web build from GitLab CI) ───────────────────────
RUN mkdir -p /opt/surfer-web \
    && curl -L \
        "https://gitlab.com/surfer-project/surfer/-/jobs/artifacts/main/download?job=pages_build" \
        -o /tmp/surfer-web.zip \
    && unzip -q /tmp/surfer-web.zip -d /tmp/surfer-extract \
    && cp -r /tmp/surfer-extract/pages_build/. /opt/surfer-web/ \
    && rm -rf /tmp/surfer-web.zip /tmp/surfer-extract

# ── Wave server ────────────────────────────────────────────────────────────────
COPY wave_server.py /opt/wave_server.py

# ── Entrypoint ─────────────────────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ── Workspace ──────────────────────────────────────────────────────────────────
WORKDIR /workspace
VOLUME ["/workspace"]

EXPOSE 7681

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
