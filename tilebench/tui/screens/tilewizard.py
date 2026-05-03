"""
tilebench.tui.screens.tilewizard
─────────────────────────────────
Pantallas TileWizard: TileWizardScreen → TileWizardSourcesScreen
Conectadas al backend real via subprocess y lectura directa de archivos.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Static, TabbedContent, TabPane

from tilebench.tui.common import (
    LiveFooter, QuitModal, InputModal,
    make_header, R,
)


# ─── Data helpers ─────────────────────────────────────────────────────────────

def _tw_root(workspace: Path) -> Path:
    tw_dir = workspace / "tilewizard"
    return tw_dir if tw_dir.is_dir() else workspace


def _find_projects(tw_dir: Path) -> list[dict]:
    """Retorna lista de dicts con info de cada proyecto TileWizard."""
    if not tw_dir.is_dir():
        return []
    projects = []
    for p in sorted(tw_dir.iterdir()):
        if not p.is_dir():
            continue
        has_src    = (p / "src").is_dir()
        has_config = (p / "ip_config.yaml").exists()
        has_output = (p / "ip_tile").is_dir()
        if not (has_src or has_config):
            continue

        cfg = {}
        if has_config:
            try:
                cfg = yaml.safe_load((p / "ip_config.yaml").read_text(encoding="utf-8")) or {}
            except Exception:
                pass

        rtl_count = len(list((p / "src").glob("*.v"))) if has_src else 0

        projects.append({
            "path":       p,
            "name":       p.name,
            "top":        cfg.get("top_module", "—"),
            "version":    cfg.get("version",    "—"),
            "author":     cfg.get("author",     "—"),
            "has_src":    has_src,
            "has_config": has_config,
            "has_output": has_output,
            "rtl_count":  rtl_count,
        })
    return projects


def _list_files(directory: Path, extensions: tuple = (".v", ".yaml", ".md", ".txt", ".j2")) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.iterdir() if f.is_file() and f.suffix in extensions)


# ─── TileWizardScreen ────────────────────────────────────────────────────────

class TileWizardScreen(Screen):
    BINDINGS = [
        Binding("n", "new_tile",    "New Tile"),
        Binding("escape", "back",   "Back"),
        Binding("q", "quit",        "Quit"),
    ]

    def __init__(self, workspace: Path):
        super().__init__()
        self._workspace = workspace
        self._tw_dir    = _tw_root(workspace)
        self._projects: list[dict] = []

    def compose(self) -> ComposeResult:
        yield make_header(
            [("Version:", "1.x", "teal"), ("Github:", "serolugo/tilewizard", "gray")],
            tool="tilewizard", section="TILE",
        )
        with Vertical(id="table-container"):
            yield DataTable(id="tw-table", cursor_type="row")
        yield LiveFooter([("n", "New Tile"), ("esc", "Back"), ("q", "Quit")])

    def on_mount(self) -> None:
        self._reload()

    def _reload(self) -> None:
        self._projects = _find_projects(self._tw_dir)
        t = self.query_one("#tw-table", DataTable)
        t.clear(columns=True)
        t.add_columns("TILE", "TOP MODULE", "VERSION")
        for p in self._projects:
            t.add_row(p["name"], R(p["top"]), R(p["version"]))
        t.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if 0 <= event.cursor_row < len(self._projects):
            proj = self._projects[event.cursor_row]
            self.app.push_screen(TileWizardSourcesScreen(
                workspace=self._workspace, project=proj,
            ))

    def action_new_tile(self) -> None:
        def cb(name: str | None) -> None:
            if not name:
                return
            with self.app.suspend():
                subprocess.run(["tilewizard", "init", name], cwd=str(self._tw_dir))
            self._reload()
        self.app.push_screen(InputModal("New Tile", "tile_name", "tilewizard"), cb)

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("tilewizard"))


# ─── TileWizardSourcesScreen ──────────────────────────────────────────────────

class TileWizardSourcesScreen(Screen):
    BINDINGS = [
        Binding("p", "parse",     "Parse"),
        Binding("w", "wrap",      "Wrap"),
        Binding("r", "path",      "Path"),
        Binding("escape", "back", "Back"),
        Binding("q", "quit",      "Quit"),
    ]

    def __init__(self, workspace: Path, project: dict):
        super().__init__()
        self._workspace = workspace
        self._project   = project
        self._selected_file: Path | None = None

    def compose(self) -> ComposeResult:
        proj = self._project
        yield make_header(
            [
                ("Tile:",    proj["name"],    "green"),
                ("Top:",     proj["top"],     "teal"),
                ("Author:",  proj["author"],  "teal"),
                ("Version:", proj["version"], "teal"),
            ],
            tool="tilewizard", show_datetime=False, section="SOURCES",
        )
        proj_dir = proj["path"]
        src_files = _list_files(proj_dir / "src")
        rtl_files = _list_files(proj_dir / "ip_tile" / "output" / "rtl")
        doc_files = _list_files(proj_dir / "ip_tile" / "output" / "docs")
        vf_files  = _list_files(proj_dir / "ip_tile" / "veriflow")

        with Horizontal(id="split-container"):
            with Vertical(id="left-panel"):
                with TabbedContent("Src", "Rtl", "Docs", "Veriflow"):
                    with TabPane("Src"):
                        yield Static(
                            "\n".join(f.name for f in src_files) if src_files else "(no source files)",
                            id="src-list",
                        )
                    with TabPane("Rtl"):
                        yield Static(
                            "\n".join(f.name for f in rtl_files) if rtl_files else "(run Wrap first)",
                            id="rtl-list",
                        )
                    with TabPane("Docs"):
                        yield Static(
                            "\n".join(f.name for f in doc_files) if doc_files else "(run Wrap first)",
                            id="doc-list",
                        )
                    with TabPane("Veriflow"):
                        yield Static(
                            "\n".join(f.name for f in vf_files) if vf_files else "(run Wrap first)",
                            id="vf-list",
                        )
            with Vertical(id="right-panel"):
                yield Static("[bold]File Content[/]", classes="panel-title-teal")
                # Mostrar ip_config.yaml si existe, sino el primer src
                first = None
                config_path = proj_dir / "ip_config.yaml"
                if config_path.exists():
                    first = config_path
                elif src_files:
                    first = src_files[0]
                content = first.read_text(encoding="utf-8", errors="replace") if first else "(no files)"
                yield Static(content, id="file-content")
        yield LiveFooter([("p", "Parse"), ("w", "Wrap"), ("r", "Path"), ("esc", "Back"), ("q", "Quit")])

    def action_parse(self) -> None:
        from textual.screen import Screen as _S
        from tilebench.tui.common import InputModal as _IM
        def cb(top: str | None) -> None:
            if not top:
                return
            with self.app.suspend():
                subprocess.run(
                    ["tilewizard", "parse", "--top", top],
                    cwd=str(self._project["path"]),
                )
            # Recargar la pantalla
            self.app.pop_screen()
            self.app.push_screen(TileWizardSourcesScreen(
                workspace=self._workspace, project=self._project,
            ))
        self.app.push_screen(_IM("Top module name (without .v)", "my_module", "tilewizard"), cb)

    def action_wrap(self) -> None:
        with self.app.suspend():
            subprocess.run(["tilewizard", "wrap"], cwd=str(self._project["path"]))
        # Recargar
        self.app.pop_screen()
        self.app.push_screen(TileWizardSourcesScreen(
            workspace=self._workspace, project=self._project,
        ))

    def action_path(self) -> None:
        host_ws = os.environ.get("HOST_WORKSPACE", str(self._workspace))
        rel = self._project["path"].relative_to(self._workspace)
        self.notify(f"{host_ws}/{rel}", timeout=8)

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("tilewizard"))
