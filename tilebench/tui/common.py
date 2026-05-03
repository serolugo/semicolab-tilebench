"""
tilebench.tui.common
────────────────────
Widgets y helpers compartidos por todos los modos (selector, veriflow, tilewizard).
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime
from pathlib import Path
from rich.text import Text

try:
    import pyfiglet
    _logo_raw = pyfiglet.figlet_format("SEMICOLAB", font="slant")
    LOGO_SLANT = "\n".join(line for line in _logo_raw.splitlines() if line.strip())
except Exception:
    LOGO_SLANT = "SEMICOLAB"

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Input, Label, Static
from textual import events


# ─── JSON helpers ─────────────────────────────────────────────────────────────

def _load_json(filename: str, fallback):
    base = Path(__file__).resolve().parent
    path = base / filename
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


PHRASES = _load_json("phrases.json", [
    "Have you checked your timing constraints today?",
    "There is no place like 0x00000000",
    "Did you commit your RTL?",
])

_THEME_FALLBACKS = {
    "dark":    {"bg":"#0d0d0d","bg2":"#111111","text":"#e0e0e0","text2":"#888888","border":"#2a2a2a","border2":"#333333","orange":"#d4633a","orange_dim":"#2a1208","orange_dim2":"#7a3820","teal":"#1a9e8f","teal_dim":"#051f1b","teal_dim2":"#1a5e52","green":"#4caf78","green_dim":"#1a3a28","green_dim2":"#2a6a3a","red":"#c0392b","cur_vf":"#5a2510","cur_vf2":"#7a3218","cur_tw":"#0a4a40","cur_tw2":"#0d6a5c","ft_bg":"#111111","ft_text":"#888888","ft_key":"#4caf78"},
    "light":   {"bg":"#f0f0f0","bg2":"#dcdcdc","text":"#1a1a1a","text2":"#444444","border":"#aaaaaa","border2":"#999999","orange":"#c0440a","orange_dim":"#f5ddd5","orange_dim2":"#a05030","teal":"#0d7a6e","teal_dim":"#c8ecea","teal_dim2":"#2a8070","green":"#1a6e3a","green_dim":"#c8ecd5","green_dim2":"#5a9a6a","red":"#b71c1c","cur_vf":"#e8a070","cur_vf2":"#d08050","cur_tw":"#80ccc0","cur_tw2":"#60b0a8","ft_bg":"#444444","ft_text":"#ffffff","ft_key":"#4caf78"},
    "fallout": {"bg":"#0a0a00","bg2":"#111100","text":"#4afe4a","text2":"#2a8a2a","border":"#1a3a1a","border2":"#2a5a2a","orange":"#4afe4a","orange_dim":"#0a1a0a","orange_dim2":"#2a6a2a","teal":"#4afe4a","teal_dim":"#0a1a0a","teal_dim2":"#2a6a2a","green":"#4afe4a","green_dim":"#0a1a0a","green_dim2":"#1a4a1a","red":"#ff4a00","cur_vf":"#1a4a1a","cur_vf2":"#2a6a2a","cur_tw":"#1a4a1a","cur_tw2":"#2a6a2a","ft_bg":"#001a00","ft_text":"#2a8a2a","ft_key":"#4afe4a"},
}

_themes_json = _load_json("themes.json", _THEME_FALLBACKS)
DARK    = _themes_json.get("dark",    _THEME_FALLBACKS["dark"])
LIGHT   = _themes_json.get("light",   _THEME_FALLBACKS["light"])
FALLOUT = _themes_json.get("fallout", _THEME_FALLBACKS["fallout"])

THEME_CYCLE = ["dark", "light", "fallout"]

THEME_COLORS = {
    "dark":    {"orange": "#d4633a", "teal": "#1a9e8f", "green": "#4caf78", "red": "#c0392b", "gray": "#888888", "dt_vf": "#d4633a", "dt_tw": "#1a9e8f", "dt_none": "#4caf78", "ft_key": "#4caf78", "ft_text": "#aaaaaa"},
    "light":   {"orange": "#c0440a", "teal": "#0d7a6e", "green": "#1a6e3a", "red": "#b71c1c", "gray": "#555555", "dt_vf": "#c0440a", "dt_tw": "#0d7a6e", "dt_none": "#1a6e3a", "ft_key": "#4caf78", "ft_text": "#ffffff"},
    "fallout": {"orange": "#4afe4a", "teal": "#4afe4a", "green": "#4afe4a", "red": "#ff4a00", "gray": "#2a8a2a", "dt_vf": "#4afe4a", "dt_tw": "#4afe4a", "dt_none": "#4afe4a", "ft_key": "#4afe4a", "ft_text": "#2a8a2a"},
}

TOOL_LABELS = {"veriflow": "VERIFLOW", "tilewizard": "TILEWIZARD", "none": "TILEBENCH"}

_ACTIVE_THEME = "dark"


# ─── CSS ──────────────────────────────────────────────────────────────────────

def _rules(p: dict) -> str:
    pre = p["pre"]
    t   = p["t"]
    return f"""
{pre}Screen {{ background: {t['bg']}; color: {t['text']}; }}
{pre}#header {{ background: {t['bg']}; }}
{pre}#header-info {{ color: {t['text']}; }}
{pre}#logo-text {{ color: {t['text']}; }}

{pre}.sep-container {{ background: {t['bg']}; }}
{pre}.sep-section-veriflow   {{ color: {t['orange']}; background: {t['bg']}; }}
{pre}.sep-section-tilewizard {{ color: {t['teal']};   background: {t['bg']}; }}
{pre}.sep-section-none       {{ color: {t['green']};  background: {t['bg']}; }}
{pre}.sep-line-veriflow   {{ color: {t['orange']}; background: {t['bg']}; }}
{pre}.sep-line-tilewizard {{ color: {t['teal']};   background: {t['bg']}; }}
{pre}.sep-line-none       {{ color: {t['green']};  background: {t['bg']}; }}
{pre}.sep-label-veriflow   {{ color: {t['orange']}; background: {t['bg']}; }}
{pre}.sep-label-tilewizard {{ color: {t['teal']};   background: {t['bg']}; }}
{pre}.sep-label-none       {{ color: {t['green']};  background: {t['bg']}; }}

{pre}#selector-body {{ background: {t['bg']}; }}
{pre}#welcome-msg {{ color: {t['green']}; }}
{pre}.tool-btn-veriflow-inactive   {{ background: {t['orange_dim']};  color: {t['orange_dim2']}; }}
{pre}.tool-btn-tilewizard-inactive {{ background: {t['teal_dim']};    color: {t['teal_dim2']};   }}
{pre}.tool-btn-veriflow-active     {{ background: {t['orange']};      color: {t['bg']};          }}
{pre}.tool-btn-tilewizard-active   {{ background: {t['teal']};        color: {t['bg']};          }}

{pre}#table-container {{ background: {t['bg']}; }}
{pre}DataTable {{ background: {t['bg']}; color: {t['text']}; }}
{pre}DataTable > .datatable--header       {{ background: {t['bg']}; color: {t['orange']}; }}
{pre}DataTable > .datatable--cursor       {{ background: {t['cur_vf']};  color: {t['text']}; }}
{pre}DataTable:focus > .datatable--cursor {{ background: {t['cur_vf2']}; color: {t['text']}; }}
{pre}#tw-table > .datatable--header        {{ color: {t['teal']}; }}
{pre}#tw-table > .datatable--cursor        {{ background: {t['cur_tw']};  color: {t['text']}; }}
{pre}#tw-table:focus > .datatable--cursor  {{ background: {t['cur_tw2']}; color: {t['text']}; }}

{pre}#tile-menu-container {{ background: {t['bg']}; }}
{pre}.menu-item          {{ background: {t['bg']};       color: {t['text']}; }}
{pre}.menu-item-selected {{ background: {t['cur_vf2']};  color: {t['text']}; }}

{pre}#split-container {{ background: {t['bg']}; }}
{pre}#left-panel  {{ background: {t['bg']}; border-right: solid {t['border2']}; }}
{pre}#right-panel {{ background: {t['bg']}; }}
{pre}.panel-title      {{ color: {t['orange']}; }}
{pre}.panel-title-teal {{ color: {t['teal']};   }}
{pre}#file-content {{ background: {t['bg2']}; color: {t['text']}; border: solid {t['border']}; }}
{pre}TabbedContent {{ background: {t['bg']}; }}
{pre}TabPane {{ background: {t['bg']}; }}
{pre}Tabs {{ background: {t['bg']}; }}
{pre}Tabs > Tab {{ background: {t['bg']}; color: {t['text2']}; }}
{pre}Tabs > Tab:hover {{ background: {t['bg2']}; color: {t['text']}; }}
{pre}Tabs > Tab.-active {{ background: {t['bg2']}; color: {t['orange']}; }}

{pre}#quit-dialog-veriflow   {{ background: {t['orange']}; }}
{pre}#quit-dialog-tilewizard {{ background: {t['teal']};   }}
{pre}#quit-dialog-none       {{ background: {t['green']};  }}
{pre}#input-dialog-veriflow  {{ background: {t['orange']}; }}
{pre}#input-dialog-tilewizard{{ background: {t['teal']};   }}
{pre}#input-dialog-none      {{ background: {t['green']};  }}
{pre}.dialog-question {{ color: {t['bg']}; }}
{pre}.dialog-input {{ background: {t['bg']}; border: solid {t['bg2']}; color: {t['text']}; }}
{pre}#quit-dialog-veriflow .modal-btn            {{ background: {t['orange_dim2']}; color: {t['orange']}; border: none; }}
{pre}#quit-dialog-veriflow .modal-btn-selected   {{ background: {t['orange_dim']};  color: {t['text2']}; border: none; }}
{pre}#quit-dialog-tilewizard .modal-btn          {{ background: {t['teal_dim2']};   color: {t['teal']}; border: none; }}
{pre}#quit-dialog-tilewizard .modal-btn-selected {{ background: {t['teal_dim']};    color: {t['text2']};  border: none; }}
{pre}#quit-dialog-none .modal-btn                {{ background: {t['green_dim2']};  color: {t['green']}; border: none; }}
{pre}#quit-dialog-none .modal-btn-selected       {{ background: {t['green_dim']};   color: {t['text2']}; border: none; }}
{pre}#input-dialog-veriflow .modal-btn           {{ background: {t['orange_dim2']}; color: {t['orange']}; border: none; }}
{pre}#input-dialog-veriflow .modal-btn-selected  {{ background: {t['orange_dim']};  color: {t['text2']}; border: none; }}
{pre}#input-dialog-tilewizard .modal-btn         {{ background: {t['teal_dim2']};   color: {t['teal']}; border: none; }}
{pre}#input-dialog-tilewizard .modal-btn-selected{{ background: {t['teal_dim']};    color: {t['text2']}; border: none; }}
{pre}#input-dialog-none .modal-btn               {{ background: {t['green_dim2']};  color: {t['green']}; border: none; }}
{pre}#input-dialog-none .modal-btn-selected      {{ background: {t['green_dim']};   color: {t['text2']}; border: none; }}

{pre}#form-container {{ background: {t['bg']}; }}
{pre}.section-label {{ color: {t['orange']}; }}
{pre}.field-label   {{ color: {t['text2']};  }}
{pre}.field-input    {{ background: {t['bg2']}; border: solid {t['border2']}; color: {t['text']}; }}
{pre}.field-textarea {{ background: {t['bg2']}; border: solid {t['border2']}; color: {t['text']}; }}

{pre}Footer {{ background: {t['ft_bg']}; color: {t['ft_text']}; }}
{pre}#footer-bar, {pre}.footer-bar {{ background: {t['ft_bg']}; color: {t['ft_text']}; }}
{pre}Footer > .footer--key           {{ background: {t['ft_bg']}; color: {t['ft_key']}; }}
{pre}Footer > .footer--highlight     {{ background: {t['ft_bg']}; color: {t['ft_key']}; }}
{pre}Footer > .footer--highlight-key {{ background: {t['ft_key']}; color: {t['ft_bg']}; }}

{pre}Tree {{ background: {t['bg']}; color: {t['text']}; }}
{pre}Tree > .tree--cursor       {{ background: {t['cur_vf']};  color: {t['text']}; }}
{pre}Tree:focus > .tree--cursor {{ background: {t['cur_vf2']}; color: {t['text']}; }}
"""

STRUCTURAL_CSS = """
#footer-bar, .footer-bar { height: 1; padding: 0 1; dock: bottom; }
#header { height: 8; padding: 0 2; }
#header-row { height: 6; }
#header-info { width: 36; padding-top: 1; height: 6; }
#logo-text { width: 1fr; text-style: bold; text-align: right; height: 5; }

.sep-container { height: 1; }
.sep-section-veriflow   { text-style: bold;        width: auto; padding-right: 1; }
.sep-section-tilewizard { text-style: bold;        width: auto; padding-right: 1; }
.sep-section-none       { text-style: bold italic; width: auto; padding-right: 1; }
.sep-line-veriflow   { width: 1fr; height: 1; overflow: hidden; }
.sep-line-tilewizard { width: 1fr; height: 1; overflow: hidden; }
.sep-line-none       { width: 1fr; height: 1; overflow: hidden; }
.sep-label-veriflow   { text-style: bold italic; width: auto; }
.sep-label-tilewizard { text-style: bold italic; width: auto; }
.sep-label-none       { text-style: italic;      width: auto; }

#selector-body { height: 1fr; align: center middle; }
#welcome-msg { text-style: bold; text-align: center; margin-bottom: 3; width: 80; }
#tools-row { height: 7; width: 80; align: center middle; }
.tool-btn-veriflow-inactive   { width: 34; height: 5; text-style: bold; border: none; margin: 0 3; content-align: center middle; }
.tool-btn-tilewizard-inactive { width: 34; height: 5; text-style: bold; border: none; margin: 0 3; content-align: center middle; }
.tool-btn-veriflow-active     { width: 34; height: 5; text-style: bold; border: none; margin: 0 3; content-align: center middle; }
.tool-btn-tilewizard-active   { width: 34; height: 5; text-style: bold; border: none; margin: 0 3; content-align: center middle; }

#table-container { height: 1fr; padding: 1 2; }
DataTable { height: 1fr; }
DataTable > .datatable--header { text-style: bold; }

#tile-menu-container { height: 1fr; padding: 2 3; }
.menu-item          { width: 46; height: 3; text-style: bold; padding: 1 2; }
.menu-item-selected { width: 46; height: 3; text-style: bold; padding: 1 2; }

#split-container { height: 1fr; }
#left-panel  { width: 35; padding: 1; }
#right-panel { width: 1fr; padding: 1 2; }
.panel-title      { text-style: bold; margin-bottom: 1; }
.panel-title-teal { text-style: bold; margin-bottom: 1; }
#file-content { height: 1fr; padding: 1; }
TabbedContent { height: 1fr; }
TabPane { padding: 1; }
Tabs > Tab.-active { text-style: bold; }

QuitModal, InputModal { align: center middle; }
#quit-dialog-veriflow, #quit-dialog-tilewizard, #quit-dialog-none,
#input-dialog-veriflow, #input-dialog-tilewizard, #input-dialog-none {
    width: 64; height: 18; border: none; align: center middle; padding: 3 4;
}
.dialog-question { text-align: center; text-style: bold; width: 1fr; height: 3; content-align: center middle; margin-bottom: 2; }
.dialog-input { width: 1fr; margin-bottom: 2; }
.dialog-buttons { align: center middle; width: 1fr; height: 5; }
.modal-btn          { width: 18; height: 3; text-style: bold; border: none; margin: 0 2; text-align: center; content-align: center middle; padding: 0; }
.modal-btn-selected { width: 18; height: 3; text-style: bold; border: none; margin: 0 2; text-align: center; content-align: center middle; padding: 0; }

#form-container { height: 1fr; padding: 1 2; overflow-y: auto; }
.section-label { text-style: bold; margin-top: 1; }
.field-label   { margin-top: 1; }
.field-input    { margin-bottom: 0; }
.field-textarea { height: 4; margin-bottom: 0; }

Tree { height: 1fr; }

.theme-light Static { color: #1a1a1a; }
.theme-light Label  { color: #1a1a1a; }
.theme-light Tree   { color: #1a1a1a; }
.theme-light Footer { background: #444444; color: #ffffff; }
.theme-light Footer > .footer--key { color: #4caf78; background: #444444; }

.theme-fallout .modal-btn          { background: #111100; color: #2a8a2a; border: none; }
.theme-fallout .modal-btn-selected { background: #4afe4a; color: #0a0a00; border: none; }
"""

APP_CSS = STRUCTURAL_CSS + _rules({"pre": "", "t": DARK}) + _rules({"pre": ".theme-light ", "t": LIGHT}) + _rules({"pre": ".theme-fallout ", "t": FALLOUT})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_separator(tool: str, section: str = "") -> Horizontal:
    tool_name = TOOL_LABELS.get(tool, "TILEBENCH")
    widgets = []
    if section:
        widgets.append(Static(section, classes=f"sep-section-{tool}"))
    widgets.append(Static("─" * 300, classes=f"sep-line-{tool}"))
    widgets.append(Static(f" {tool_name} ──", classes=f"sep-label-{tool}"))
    return Horizontal(*widgets, classes="sep-container")


def R(val: str) -> Text:
    return Text(str(val), justify="right")


def random_phrase() -> str:
    return random.choice(PHRASES)


# ─── LiveHeader ───────────────────────────────────────────────────────────────

class LiveHeader(Widget):
    DEFAULT_CSS = ""

    def __init__(self, info_lines: list, tool: str = "none",
                 show_datetime: bool = True, section: str = ""):
        super().__init__(id="header")
        self._info_lines    = info_lines
        self._tool          = tool
        self._show_datetime = show_datetime
        self._section       = section

    def _build_markup(self) -> str:
        now    = datetime.now()
        colors = THEME_COLORS.get(_ACTIVE_THEME, THEME_COLORS["dark"])
        _dt_key  = {"veriflow": "dt_vf", "tilewizard": "dt_tw"}.get(self._tool, "dt_none")
        dt_color = colors.get(_dt_key, colors["dt_none"])
        markup = ""
        if self._show_datetime:
            markup = (
                f"Date: [bold {dt_color}]{now.strftime('%d/%b/%Y')}[/]\n"
                f"Hour: [bold {dt_color}]{now.strftime('%H:%M:%S')}[/]\n"
            )
        for label, val, clr in self._info_lines:
            c = colors.get(clr, "#e0e0e0")
            markup += f"{label}[bold {c}]{val}[/]\n"
        return markup

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(self._build_markup(), id="header-info"),
            Static(LOGO_SLANT, id="logo-text"),
            id="header-row",
        )
        yield make_separator(self._tool, self._section)

    def on_mount(self) -> None:
        self.set_interval(1, self._tick)

    def _tick(self) -> None:
        try:
            self.query_one("#header-info", Static).update(self._build_markup())
        except Exception:
            pass


def make_header(info_lines: list, tool: str = "none",
                show_datetime: bool = True, section: str = "") -> LiveHeader:
    return LiveHeader(info_lines, tool, show_datetime, section)


# ─── LiveFooter ───────────────────────────────────────────────────────────────

class LiveFooter(Widget):
    DEFAULT_CSS = ""

    ACTION_MAP = {
        "esc": "back", "q": "quit", "t": "cycle_theme",
        "1": "go_veriflow", "2": "go_tilewizard",
        "ctrl+s": "save", "p": "path", "w": "waves",
        "s": "sources", "r": "run",
    }

    DESC_ACTION_MAP = {
        "new database": "new_db", "new tile": "new_tile",
        "records": "tile_records", "index": "tile_index",
        "config": "proj_config", "run index": "run_index",
        "ip config": "ip_config", "parse": "parse",
        "wrap": "wrap", "path": "path",
    }

    def __init__(self, bindings: list):
        super().__init__(id="footer-bar", classes="footer-bar")
        self._bindings = bindings
        self._slots = []
        pos = 0
        for key, desc in bindings:
            width = len(key) + 1 + len(desc)
            self._slots.append((pos, pos + width, key, desc))
            pos += width + 2

    def _build_text(self):
        colors = THEME_COLORS.get(_ACTIVE_THEME, THEME_COLORS["dark"])
        t = Text()
        for i, (key, desc) in enumerate(self._bindings):
            if i > 0:
                t.append("  ", style=colors["ft_text"])
            t.append(key,  style=f"bold {colors['ft_key']}")
            t.append(f" {desc}", style=colors["ft_text"])
        return t

    def render(self):
        return self._build_text()

    def on_mount(self) -> None:
        self.set_interval(1, self._tick)

    def _tick(self) -> None:
        self.refresh()

    async def on_click(self, event) -> None:
        x = event.x
        for (x0, x1, key, desc) in self._slots:
            if x0 <= x <= x1:
                action = (
                    self.ACTION_MAP.get(key) or
                    self.DESC_ACTION_MAP.get(desc.lower())
                )
                if action:
                    try:
                        await self.screen.run_action(action)
                    except Exception:
                        pass
                return


# ─── Modals ───────────────────────────────────────────────────────────────────

class QuitModal(ModalScreen):
    def __init__(self, tool: str = "veriflow"):
        super().__init__()
        self.tool  = tool
        self._sel  = 1

    def compose(self) -> ComposeResult:
        with Container(id=f"quit-dialog-{self.tool}"):
            yield Label("Do you want to quit?", classes="dialog-question")
            with Horizontal(classes="dialog-buttons"):
                yield Static("Yes", id="yes-btn", classes="modal-btn")
                yield Static("No",  id="no-btn",  classes="modal-btn-selected")

    def _refresh(self) -> None:
        yes = self.query_one("#yes-btn", Static)
        no  = self.query_one("#no-btn",  Static)
        if self._sel == 0:
            yes.set_classes("modal-btn-selected"); no.set_classes("modal-btn")
        else:
            yes.set_classes("modal-btn");          no.set_classes("modal-btn-selected")

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ("left", "right", "tab"):
            self._sel = 1 - self._sel; self._refresh()
        elif event.key == "enter":
            self.app.exit() if self._sel == 0 else self.dismiss()
        elif event.key in ("escape", "n"): self.dismiss()
        elif event.key == "y":             self.app.exit()

    def on_click(self, event) -> None:
        widget = event.widget
        if hasattr(widget, "id"):
            if widget.id == "yes-btn": self.app.exit()
            elif widget.id == "no-btn": self.dismiss()


class InputModal(ModalScreen):
    def __init__(self, title: str, placeholder: str = "", tool: str = "veriflow"):
        super().__init__()
        self._title       = title
        self._placeholder = placeholder
        self.tool         = tool
        self._sel         = 0

    def compose(self) -> ComposeResult:
        with Container(id=f"input-dialog-{self.tool}"):
            yield Label(self._title, classes="dialog-question")
            yield Input(placeholder=self._placeholder, id="input-field", classes="dialog-input")
            with Horizontal(classes="dialog-buttons"):
                yield Static("OK",     id="accept-btn", classes="modal-btn-selected")
                yield Static("Cancel", id="cancel-btn", classes="modal-btn")

    def on_mount(self) -> None:
        self.query_one("#input-field", Input).focus()

    def _refresh(self) -> None:
        self.query_one("#accept-btn", Static).set_classes("modal-btn-selected" if self._sel == 0 else "modal-btn")
        self.query_one("#cancel-btn", Static).set_classes("modal-btn-selected" if self._sel == 1 else "modal-btn")

    def _val(self):
        return self.query_one("#input-field", Input).value.strip() or None

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            self.dismiss(self._val()) if self._sel == 0 else self.dismiss(None)
        elif event.key in ("left", "right", "tab"):
            self._sel = 1 - self._sel; self._refresh()
