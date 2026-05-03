"""
tilebench.tui.screens.veriflow
──────────────────────────────
Pantallas VeriFlow: Database → Tile → TileMenu → RunHistory → RunDetail / Sources / TileConfig
Conectadas al backend real via subprocess y lectura directa de archivos.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Input, Label, Static, TabbedContent, TabPane, TextArea, Tree
from textual import events

from tilebench.tui.common import (
    LiveFooter, QuitModal, InputModal,
    make_header, R,
)


# ─── Data helpers ─────────────────────────────────────────────────────────────

def _find_databases(vf_root: Path) -> list[dict]:
    """Retorna lista de dicts con info de cada database encontrada."""
    if not vf_root.is_dir():
        return []
    dbs = []
    for p in sorted(vf_root.iterdir()):
        cfg_path = p / "project_config.yaml"
        if p.is_dir() and cfg_path.exists():
            try:
                cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            except Exception:
                cfg = {}
            dbs.append({
                "path":         p,
                "name":         p.name,
                "project_name": cfg.get("project_name", "—"),
                "id_prefix":    cfg.get("id_prefix",    "—"),
            })
    return dbs


def _list_tiles(db: Path) -> list[dict]:
    """Lee tile_index.csv y retorna lista de dicts."""
    import csv
    index = db / "tile_index.csv"
    if not index.exists():
        return []
    try:
        with open(index, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _list_runs(db: Path, tile_id: str) -> list[dict]:
    """Lista runs de un tile, retorna dicts con info del manifest."""
    runs_dir = db / "tiles" / tile_id / "runs"
    if not runs_dir.exists():
        return []
    runs = []
    for d in sorted(runs_dir.iterdir(), reverse=True):
        if not (d.is_dir() and d.name.startswith("run-")):
            continue
        m = _read_manifest(d)
        runs.append({
            "path":   d,
            "name":   d.name,
            "date":   str(m.get("date", ""))[:10],
            "status": m.get("status", "?"),
            "author": m.get("author", ""),
            "manifest": m,
        })
    return runs


def _read_manifest(run_dir: Path) -> dict:
    manifest = run_dir / "manifest.yaml"
    if not manifest.exists():
        return {}
    try:
        return yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


def _tile_config_path(db: Path, tile_number: str) -> Path:
    padded = f"{int(tile_number):04d}"
    return db / "config" / f"tile_{padded}" / "tile_config.yaml"


def _tile_src_path(db: Path, tile_number: str) -> Path:
    padded = f"{int(tile_number):04d}"
    return db / "config" / f"tile_{padded}" / "src"


def _list_files(directory: Path, extensions: tuple = (".v", ".yaml", ".md", ".txt")) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.iterdir() if f.is_file() and f.suffix in extensions)


def _status_color(status: str) -> str:
    return "green" if status == "PASS" else ("red" if status == "FAIL" else "orange")


def _vf_version(db: Path) -> str:
    """Intenta leer la versión de VeriFlow del project_config."""
    try:
        cfg = _read_yaml(db / "project_config.yaml")
        return cfg.get("veriflow_version", "1.x")
    except Exception:
        return "1.x"


# ─── DatabaseScreen ───────────────────────────────────────────────────────────

class DatabaseScreen(Screen):
    BINDINGS = [
        Binding("n", "new_db",     "New Database"),
        Binding("escape", "back",  "Back"),
        Binding("q", "quit",       "Quit"),
    ]

    def __init__(self, workspace: Path):
        super().__init__()
        self._workspace = workspace
        self._vf_root   = workspace / "veriflow"
        self._dbs: list[dict] = []

    def compose(self) -> ComposeResult:
        yield make_header(
            [("Version:", "1.x", "orange"), ("Github:", "serolugo/veriflow", "gray")],
            tool="veriflow", section="DATABASE",
        )
        with Vertical(id="table-container"):
            yield DataTable(id="db-table", cursor_type="row")
        yield LiveFooter([("n", "New Database"), ("esc", "Back"), ("q", "Quit")])

    def on_mount(self) -> None:
        self._reload()

    def _reload(self) -> None:
        self._dbs = _find_databases(self._vf_root)
        t = self.query_one("#db-table", DataTable)
        t.clear(columns=True)
        t.add_columns("DATABASE", "PROJECT_NAME", "ID_PREFIX")
        for db in self._dbs:
            t.add_row(db["name"], R(db["project_name"]), R(db["id_prefix"]))
        t.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if 0 <= event.cursor_row < len(self._dbs):
            db = self._dbs[event.cursor_row]
            self.app.push_screen(TileScreen(workspace=self._workspace, db=db))

    def action_new_db(self) -> None:
        def cb(name: str | None) -> None:
            if not name:
                return
            db_path = self._vf_root / name
            with self.app.suspend():
                subprocess.run(["veriflow", "--db", str(db_path), "init"])
            self._reload()
        self.app.push_screen(InputModal("New Database", "database_name", "veriflow"), cb)

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))


# ─── TileScreen ───────────────────────────────────────────────────────────────

class TileScreen(Screen):
    BINDINGS = [
        Binding("n", "new_tile",    "New Tile"),
        Binding("escape", "back",   "Back"),
        Binding("q", "quit",        "Quit"),
    ]

    def __init__(self, workspace: Path, db: dict):
        super().__init__()
        self._workspace = workspace
        self._db        = db
        self._tiles: list[dict] = []

    def compose(self) -> ComposeResult:
        yield make_header(
            [("Version:", "1.x", "orange"), ("Database:", self._db["name"], "green")],
            tool="veriflow", section="TILE",
        )
        with Vertical(id="table-container"):
            yield DataTable(id="tile-table", cursor_type="row")
        yield LiveFooter([("n", "New Tile"), ("esc", "Back"), ("q", "Quit")])

    def on_mount(self) -> None:
        self._reload()

    def _reload(self) -> None:
        self._tiles = _list_tiles(self._db["path"])
        t = self.query_one("#tile-table", DataTable)
        t.clear(columns=True)
        t.add_columns("TILE", "TILE_NUMBER", "VERSION", "REVISION")
        for tile in self._tiles:
            t.add_row(
                tile.get("tile_name", "—"),
                R(tile.get("tile_number", "—")),
                R(str(tile.get("version",  "—")).zfill(2)),
                R(str(tile.get("revision", "—")).zfill(2)),
            )
        t.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if 0 <= event.cursor_row < len(self._tiles):
            tile = self._tiles[event.cursor_row]
            self.app.push_screen(TileMenuScreen(
                workspace=self._workspace, db=self._db, tile=tile,
            ))

    def action_new_tile(self) -> None:
        def cb(name: str | None) -> None:
            if not name:
                return
            with self.app.suspend():
                subprocess.run(["veriflow", "--db", str(self._db["path"]), "create-tile"])
            self._reload()
        self.app.push_screen(InputModal("New Tile — press Enter in terminal", "", "veriflow"), cb)

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))


# ─── TileMenuScreen ───────────────────────────────────────────────────────────

class TileMenuScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Back"), Binding("q", "quit", "Quit")]
    MENU_ITEMS = [
        ("menu-config",  "Open Tile Config"),
        ("menu-runs",    "Open Run History"),
        ("menu-sources", "Open Tile Sources"),
    ]

    def __init__(self, workspace: Path, db: dict, tile: dict):
        super().__init__()
        self._workspace = workspace
        self._db        = db
        self._tile      = tile
        self._idx       = 0

    def compose(self) -> ComposeResult:
        yield make_header(
            [("Version:", "1.x", "orange"), ("Tile:", self._tile.get("tile_name", "—"), "green")],
            tool="veriflow", section="TILE MENU",
        )
        with Vertical(id="tile-menu-container"):
            for i, (key, label) in enumerate(self.MENU_ITEMS):
                yield Static(label, id=key, classes="menu-item-selected" if i == 0 else "menu-item")
        yield LiveFooter([("esc", "Back"), ("q", "Quit")])

    def _refresh(self) -> None:
        for i, (key, _) in enumerate(self.MENU_ITEMS):
            self.query_one(f"#{key}", Static).set_classes(
                "menu-item-selected" if i == self._idx else "menu-item"
            )

    def on_key(self, event: events.Key) -> None:
        n = len(self.MENU_ITEMS)
        if event.key == "up":
            event.stop(); self._idx = max(0, self._idx - 1); self._refresh()
        elif event.key == "down":
            event.stop(); self._idx = min(n - 1, self._idx + 1); self._refresh()
        elif event.key == "enter":
            event.stop(); self._navigate(self.MENU_ITEMS[self._idx][0])

    def on_click(self, event) -> None:
        widget = event.widget
        if hasattr(widget, "id") and widget.id:
            for i, (key, _) in enumerate(self.MENU_ITEMS):
                if widget.id == key:
                    self._idx = i; self._refresh(); self._navigate(key); break

    def _navigate(self, key: str) -> None:
        if key == "menu-config":
            self.app.push_screen(TileConfigScreen(db=self._db, tile=self._tile))
        elif key == "menu-runs":
            self.app.push_screen(RunHistoryScreen(workspace=self._workspace, db=self._db, tile=self._tile))
        elif key == "menu-sources":
            self.app.push_screen(SourcesScreen(db=self._db, tile=self._tile))

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))


# ─── RunHistoryScreen ─────────────────────────────────────────────────────────

class RunHistoryScreen(Screen):
    BINDINGS = [
        Binding("r", "run",     "Run"),
        Binding("w", "waves",   "Waves"),
        Binding("s", "sources", "Sources"),
        Binding("escape", "back", "Back"),
        Binding("q", "quit",    "Quit"),
    ]

    def __init__(self, workspace: Path, db: dict, tile: dict):
        super().__init__()
        self._workspace = workspace
        self._db        = db
        self._tile      = tile
        self._runs: list[dict] = []

    def compose(self) -> ComposeResult:
        yield make_header(
            [("Version:", "1.x", "orange"), ("Tile:", self._tile.get("tile_name", "—"), "green")],
            tool="veriflow", section="RUNS",
        )
        with Vertical(id="table-container"):
            yield DataTable(id="run-table", cursor_type="row")
        yield LiveFooter([("r", "Run"), ("w", "Waves"), ("s", "Sources"), ("esc", "Back"), ("q", "Quit")])

    def on_mount(self) -> None:
        self._reload()

    def _reload(self) -> None:
        tile_id = self._tile.get("tile_id", "")
        self._runs = _list_runs(self._db["path"], tile_id)
        t = self.query_one("#run-table", DataTable)
        t.clear(columns=True)
        t.add_columns("RUN", "DATE", "AUTHOR", "STATUS")
        for run in self._runs:
            color = "#4caf78" if run["status"] == "PASS" else "#c0392b"
            t.add_row(
                run["name"],
                R(run["date"]),
                R(run["author"]),
                Text(run["status"], justify="right", style=f"bold {color}"),
            )
        t.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if 0 <= event.cursor_row < len(self._runs):
            run = self._runs[event.cursor_row]
            self.app.push_screen(RunDetailScreen(
                workspace=self._workspace, db=self._db, tile=self._tile, run=run,
            ))

    def action_run(self) -> None:
        tile_number = self._tile.get("tile_number", "")
        with self.app.suspend():
            subprocess.run(["veriflow", "--db", str(self._db["path"]), "run", "--tile", tile_number])
        self._reload()

    def action_waves(self) -> None:
        if not self._runs:
            return
        # Abre waves del último run
        run = self._runs[0]
        tile_number = self._tile.get("tile_number", "")
        with self.app.suspend():
            subprocess.run([
                "veriflow", "--db", str(self._db["path"]),
                "waves", "--tile", tile_number, "--run", run["name"],
            ])

    def action_sources(self) -> None:
        self.app.push_screen(SourcesScreen(db=self._db, tile=self._tile))

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))


# ─── RunDetailScreen ──────────────────────────────────────────────────────────

class RunDetailScreen(Screen):
    BINDINGS = [
        Binding("p", "path",   "Path"),
        Binding("w", "waves",  "Waves"),
        Binding("escape", "back", "Back"),
        Binding("q", "quit",   "Quit"),
    ]

    def __init__(self, workspace: Path, db: dict, tile: dict, run: dict):
        super().__init__()
        self._workspace = workspace
        self._db        = db
        self._tile      = tile
        self._run       = run
        self._selected_file: Path | None = None

    def compose(self) -> ComposeResult:
        status = self._run.get("status", "?")
        status_color = _status_color(status)
        yield make_header(
            [
                ("Tile:",     self._tile.get("tile_name", "—"), "green"),
                ("Database:", self._db["name"],                 "green"),
                ("Run:",      self._run["name"],                "orange"),
                ("Status:",   status,                           status_color),
            ],
            tool="veriflow", show_datetime=False, section="RUN DETAILS",
        )
        run_dir = self._run["path"]
        # Recopilar archivos reales
        docs_files  = self._get_docs(run_dir)
        src_files   = self._get_src(run_dir)

        with Horizontal(id="split-container"):
            with Vertical(id="left-panel"):
                with TabbedContent("Docs", "Src", "Logs"):
                    with TabPane("Docs"):
                        yield Static(
                            "\n".join(f.name for f in docs_files) if docs_files else "(no docs)",
                            id="docs-list",
                        )
                    with TabPane("Src"):
                        yield Static(
                            "\n".join(f.name for f in src_files) if src_files else "(no sources)",
                            id="src-list",
                        )
                    with TabPane("Logs"):
                        tree = Tree("", id="logs-tree")
                        out_dir = run_dir / "out"
                        for section in ["connectivity", "sim", "synth"]:
                            s_dir = out_dir / section
                            if s_dir.is_dir():
                                node = tree.root.add(section)
                                for sub in ["logs", "waves", "reports"]:
                                    sub_dir = s_dir / sub
                                    if sub_dir.is_dir():
                                        files = list(sub_dir.iterdir())
                                        if files:
                                            sn = node.add(sub)
                                            for f in files:
                                                sn.add_leaf(f.name)
                        tree.root.expand_all()
                        yield tree
            with Vertical(id="right-panel"):
                yield Static("[bold]File Content[/]", classes="panel-title")
                yield Static(self._load_manifest(), id="file-content")
        yield LiveFooter([("p", "Path"), ("w", "Waves"), ("esc", "Back"), ("q", "Quit")])

    def _get_docs(self, run_dir: Path) -> list[Path]:
        return [f for f in (
            run_dir / "manifest.yaml",
            run_dir / "notes.md",
            run_dir / "summary.md",
        ) if f.exists()]

    def _get_src(self, run_dir: Path) -> list[Path]:
        src = run_dir / "src"
        return _list_files(src) if src.is_dir() else []

    def _load_manifest(self) -> str:
        manifest = self._run["path"] / "manifest.yaml"
        if manifest.exists():
            return manifest.read_text(encoding="utf-8")
        return "(no manifest)"

    def action_waves(self) -> None:
        tile_number = self._tile.get("tile_number", "")
        with self.app.suspend():
            subprocess.run([
                "veriflow", "--db", str(self._db["path"]),
                "waves", "--tile", tile_number, "--run", self._run["name"],
            ])

    def action_path(self) -> None:
        host_ws = os.environ.get("HOST_WORKSPACE", str(self._workspace))
        rel = self._run["path"].relative_to(self._workspace)
        self.notify(f"{host_ws}/{rel}", timeout=8)

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))


# ─── SourcesScreen ────────────────────────────────────────────────────────────

class SourcesScreen(Screen):
    BINDINGS = [
        Binding("p", "path",      "Path"),
        Binding("escape", "back", "Back"),
        Binding("q", "quit",      "Quit"),
    ]

    def __init__(self, db: dict, tile: dict):
        super().__init__()
        self._db   = db
        self._tile = tile

    def compose(self) -> ComposeResult:
        tile_number = self._tile.get("tile_number", "0001")
        ver = str(self._tile.get("version",  "—")).zfill(2)
        rev = str(self._tile.get("revision", "—")).zfill(2)
        yield make_header(
            [
                ("Tile:",          self._tile.get("tile_name", "—"), "green"),
                ("Database:",      self._db["name"],                 "green"),
                ("Tile Version:",  ver,                              "orange"),
                ("Tile Revision:", rev,                              "orange"),
            ],
            tool="veriflow", show_datetime=False, section="SOURCES",
        )
        src_base = _tile_src_path(self._db["path"], tile_number)
        rtl_files = _list_files(src_base / "rtl")
        tb_files  = _list_files(src_base / "tb")
        doc_files = _list_files(self._db["path"] / "tiles" / self._tile.get("tile_id", "") )

        with Horizontal(id="split-container"):
            with Vertical(id="left-panel"):
                with TabbedContent("RTL", "TB", "Docs"):
                    with TabPane("RTL"):
                        yield Static(
                            "\n".join(f.name for f in rtl_files) if rtl_files else "(no RTL files)",
                            id="rtl-list",
                        )
                    with TabPane("TB"):
                        yield Static(
                            "\n".join(f.name for f in tb_files) if tb_files else "(no TB files)",
                            id="tb-list",
                        )
                    with TabPane("Docs"):
                        yield Static("README.md" if (self._db["path"] / "tiles" / self._tile.get("tile_id", "") / "README.md").exists() else "(no docs)")
            with Vertical(id="right-panel"):
                yield Static("[bold]File Content[/]", classes="panel-title")
                first = (rtl_files or tb_files or [None])[0]
                content = first.read_text(encoding="utf-8", errors="replace") if first else "(select a file)"
                yield Static(content, id="file-content")
        yield LiveFooter([("p", "Path"), ("esc", "Back"), ("q", "Quit")])

    def action_path(self) -> None:
        host_ws = os.environ.get("HOST_WORKSPACE", "")
        tile_number = self._tile.get("tile_number", "0001")
        path = _tile_src_path(self._db["path"], tile_number)
        self.notify(f"{host_ws or path}", timeout=8)

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))


# ─── TileConfigScreen ─────────────────────────────────────────────────────────

class TileConfigScreen(Screen):
    BINDINGS = [
        Binding("ctrl+s", "save",  "Save"),
        Binding("escape", "back",  "Back"),
        Binding("q", "quit",       "Quit"),
    ]

    TILE_FIELDS = [
        ("tile_name",      "tile_name",      False),
        ("tile_author",    "tile_author",     False),
        ("top_module",     "top_module",      False),
        ("description",    "description",     True),
        ("ports",          "ports",           True),
        ("usage_guide",    "usage_guide",     True),
        ("tb_description", "tb_description",  True),
    ]
    RUN_FIELDS = [
        ("run_author",  "run_author",  False),
        ("objective",   "objective",   False),
        ("tags",        "tags",        False),
        ("main_change", "main_change", True),
        ("notes",       "notes",       True),
    ]

    def __init__(self, db: dict, tile: dict):
        super().__init__()
        self._db   = db
        self._tile = tile
        self._config_path = _tile_config_path(db["path"], tile.get("tile_number", "0001"))
        self._cfg = _read_yaml(self._config_path)

    def compose(self) -> ComposeResult:
        yield make_header(
            [("Tile:", self._tile.get("tile_name", "—"), "green")],
            tool="veriflow", section="TILE CONFIG",
        )
        with Vertical(id="form-container"):
            yield Static("── TILE INFORMATION ──────────────────────", classes="section-label")
            for label, key, is_area in self.TILE_FIELDS:
                yield Label(label, classes="field-label")
                val = str(self._cfg.get(key, "") or "")
                if is_area:
                    yield TextArea(val, id=f"f-{key}", classes="field-textarea")
                else:
                    yield Input(value=val, id=f"f-{key}", classes="field-input")
            yield Static("── RUN INFORMATION ───────────────────────", classes="section-label")
            for label, key, is_area in self.RUN_FIELDS:
                yield Label(label, classes="field-label")
                val = str(self._cfg.get(key, "") or "")
                if is_area:
                    yield TextArea(val, id=f"f-{key}", classes="field-textarea")
                else:
                    yield Input(value=val, id=f"f-{key}", classes="field-input")
        yield LiveFooter([("ctrl+s", "Save"), ("esc", "Back"), ("q", "Quit")])

    def _collect(self) -> dict:
        data = dict(self._cfg)
        for label, key, is_area in self.TILE_FIELDS + self.RUN_FIELDS:
            try:
                if is_area:
                    data[key] = self.query_one(f"#f-{key}", TextArea).text
                else:
                    data[key] = self.query_one(f"#f-{key}", Input).value
            except Exception:
                pass
        return data

    def action_save(self) -> None:
        _write_yaml(self._config_path, self._collect())
        self.notify("Saved", timeout=1.5)
        self.app.pop_screen()

    def action_back(self) -> None: self.app.pop_screen()
    def action_quit(self) -> None: self.app.push_screen(QuitModal("veriflow"))
