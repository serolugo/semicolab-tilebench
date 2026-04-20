FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV SEMICOLAB_DOCKER=1
ENV DISPLAY=:1

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y -q \
    wget curl git python3 python3-pip \
    xvfb x11vnc gtkwave \
    novnc websockify \
    libpango-1.0-0 libpangoft2-1.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── OSS CAD Suite ─────────────────────────────────────────────────────────────
RUN wget -q https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-11-26/oss-cad-suite-linux-x64-20241126.tgz \
    && tar -xf oss-cad-suite-linux-x64-20241126.tgz -C /opt \
    && rm oss-cad-suite-linux-x64-20241126.tgz

ENV PATH="/opt/oss-cad-suite/bin:/opt/oss-cad-suite/lib:${PATH}"

# ── Python tools ──────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir \
    pyyaml \
    jinja2 \
    weasyprint \
    markdown

# ── VeriFlow ──────────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir \
    git+https://github.com/serolugo/veriflow.git

# ── TileWizard ────────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir \
    git+https://github.com/serolugo/semicolab-ip-tile-wizard.git

# ── noVNC setup ───────────────────────────────────────────────────────────────
RUN ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html 2>/dev/null || true

# ── Entrypoint script ─────────────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ── Workspace ────────────────────────────────────────────────────────────────
WORKDIR /workspace
VOLUME ["/workspace"]

EXPOSE 6080

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
