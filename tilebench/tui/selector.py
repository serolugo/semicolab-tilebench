"""
tilebench.tui.selector
──────────────────────
Punto de entrada unificado de TileBench.
Muestra el selector VeriFlow / TileWizard y lanza la herramienta elegida.

Uso directo:    python -m tilebench.tui.selector
Via tilebench:  tilebench  (sin argumentos)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, Static

from tilebench.tui.common import (
    APP_CSS, THEME_CYCLE, _ACTIVE_THEME,
    LiveFooter, QuitModal,
    make_header, random_phrase,
)
from tilebench.tui.screens.veriflow   import DatabaseScreen
from tilebench.tui.screens.tilewizard import TileWizardScreen


# ─── SelectorScreen ───────────────────────────────────────────────────────────

class SelectorScreen(Screen):
    BINDINGS = [
        Binding("1", "go_veriflow",   "VeriFlow"),
        Binding("2", "go_tilewizard", "TileWizard"),
        Binding("enter",  "select",   "Select",  show=False),
        Binding("left",   "prev",     "",        show=False),
        Binding("right",  "next",     "",        show=False),
        Binding("up",     "prev",     "",        show=False),
        Binding("down",   "next",     "",        show=False),
        Binding("q",      "quit",     "Quit"),
        Binding("t",      "cycle_theme", "Theme", show=False),
    ]

    def __init__(self, workspace: Path):
        super().__init__()
        self._workspace = workspace
        self._selected  = 0

    def compose(self) -> ComposeResult:
        user = os.environ.get("USER", "user")
        yield make_header(
            [("Version:", "0.6", "green"), ("Github:", "serolugo/tilebench", "gray")],
            tool="none",
        )
        with Vertical(id="selector-body"):
            yield Label(f"Hi {user}!!! {random_phrase()}", id="welcome-msg")
            with Horizontal(id="tools-row"):
                yield Static("VERIFLOW",   id="btn-vf", classes="tool-btn-veriflow-active")
                yield Static("TILEWIZARD", id="btn-tw", classes="tool-btn-tilewizard-inactive")
        yield LiveFooter([("1", "VeriFlow"), ("2", "TileWizard"), ("q", "Quit"), ("t", "Theme")])

    def _refresh(self) -> None:
        vf = self.query_one("#btn-vf", Static)
        tw = self.query_one("#btn-tw", Static)
        if self._selected == 0:
            vf.set_classes("tool-btn-veriflow-active")
            tw.set_classes("tool-btn-tilewizard-inactive")
        else:
            vf.set_classes("tool-btn-veriflow-inactive")
            tw.set_classes("tool-btn-tilewizard-active")

    def on_click(self, event) -> None:
        widget = event.widget
        if hasattr(widget, "id"):
            if widget.id == "btn-vf":
                self.action_go_veriflow()
            elif widget.id == "btn-tw":
                self.action_go_tilewizard()

    def action_prev(self)  -> None: self._selected = 0; self._refresh()
    def action_next(self)  -> None: self._selected = 1; self._refresh()

    def action_select(self) -> None:
        if self._selected == 0:
            self.action_go_veriflow()
        else:
            self.action_go_tilewizard()

    def action_go_veriflow(self)   -> None:
        self.app.push_screen(DatabaseScreen(workspace=self._workspace))

    def action_go_tilewizard(self) -> None:
        self.app.push_screen(TileWizardScreen(workspace=self._workspace))

    def action_quit(self)          -> None: self.app.push_screen(QuitModal("none"))
    def action_cycle_theme(self)   -> None: self.app.action_cycle_theme()


# ─── TileBenchApp ─────────────────────────────────────────────────────────────

class TileBenchApp(App):
    TITLE                  = "TileBench"
    ENABLE_COMMAND_PALETTE = False
    CSS                    = APP_CSS
    BINDINGS               = []
    _theme_idx             = 0

    def __init__(self, workspace: Path, start_screen: str = "selector"):
        super().__init__()
        self._workspace    = workspace
        self._start_screen = start_screen  # "selector" | "veriflow" | "tilewizard"

    def on_mount(self) -> None:
        if self._start_screen == "veriflow":
            self.push_screen(DatabaseScreen(workspace=self._workspace))
        elif self._start_screen == "tilewizard":
            self.push_screen(TileWizardScreen(workspace=self._workspace))
        else:
            self.push_screen(SelectorScreen(workspace=self._workspace))

    def action_cycle_theme(self) -> None:
        global _ACTIVE_THEME
        import tilebench.tui.common as _common
        old_class = f"theme-{THEME_CYCLE[self._theme_idx]}"
        self.remove_class(old_class)
        TileBenchApp._theme_idx = (self._theme_idx + 1) % len(THEME_CYCLE)
        name = THEME_CYCLE[self._theme_idx]
        _common._ACTIVE_THEME = name
        if name != "dark":
            self.add_class(f"theme-{name}")
        self.notify(f"Theme: {name}", timeout=1.5)


# ─── Entry points ─────────────────────────────────────────────────────────────

def _get_workspace() -> Path:
    """Detecta el workspace: desde env var o cwd."""
    ws = os.environ.get("HOST_WORKSPACE")
    if ws:
        return Path(ws)
    # En Docker el workspace está montado en /workspace
    if Path("/workspace").is_dir():
        return Path("/workspace")
    return Path.cwd()


def run_selector(workspace: Path | None = None) -> None:
    """Lanza TileBench con el selector de herramienta."""
    TileBenchApp(workspace or _get_workspace(), start_screen="selector").run()


def run_veriflow(workspace: Path | None = None) -> None:
    """Lanza directo en VeriFlow sin pasar por el selector."""
    TileBenchApp(workspace or _get_workspace(), start_screen="veriflow").run()


def run_tilewizard(workspace: Path | None = None) -> None:
    """Lanza directo en TileWizard sin pasar por el selector."""
    TileBenchApp(workspace or _get_workspace(), start_screen="tilewizard").run()


if __name__ == "__main__":
    run_selector()
