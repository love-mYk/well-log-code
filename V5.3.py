#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WellCorrelator v5.3 — 全局 Top & Zone 颜色一致版
- 相同名字的 Zone 在两口井中颜色自动一致
- 相同名字的 Top（层位线）在两口井中颜色自动一致
- 不破坏现有数据模型和保存文件格式
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import lasio
    HAS_LASIO = True
except ImportError:
    HAS_LASIO = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QInputDialog,
    QSplitter, QMessageBox, QMenu, QColorDialog,
    QGraphicsPathItem, QTextEdit, QLineEdit, QCheckBox,
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QPainter, QPen, QCursor

import pyqtgraph as pg

# ---------- 全局配置 ----------
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)

# ---------- 全局样式表 ----------
GLOBAL_QSS = """
/* ════════════════════════════════
   BASE
════════════════════════════════ */
QMainWindow {
    background: #F0F2F5;
}

/* ════════════════════════════════
   SIDEBAR SHELL
════════════════════════════════ */
QWidget#sidebar {
    background: #FFFFFF;
}

QWidget#sidebarHeader {
    background: #F5F7FA;
    border-bottom: 1px solid #E4E7ED;
}

QLabel#appTitle {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
    font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
    letter-spacing: 0.3px;
    background: transparent;
}

QLabel#appSubtitle {
    color: #3D5C7A;
    font-size: 8px;
    font-family: 'Segoe UI', Arial, sans-serif;
    letter-spacing: 2.5px;
    font-weight: 600;
    background: transparent;
}

/* ════════════════════════════════
   SCROLL AREA
════════════════════════════════ */
QScrollBar:vertical {
    background: #1A2638;
    width: 5px;
    margin: 0;
    border: none;
}
QScrollBar::handle:vertical {
    background: #2E4160;
    border-radius: 2px;
    min-height: 24px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: none; }

/* ════════════════════════════════
   SECTION HEADERS
════════════════════════════════ */
QWidget#secHeader_A {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #1B3A5C, stop:1 #1A2638);
    border-left: 3px solid #4299E1;
}
QWidget#secHeader_B {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #311A52, stop:1 #1A2638);
    border-left: 3px solid #9B72CF;
}
QWidget#secHeader_Batch {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #163325, stop:1 #1A2638);
    border-left: 3px solid #48BB78;
}

QLabel#secTitle_A {
    color: #90CDF4;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: transparent;
}
QLabel#secTitle_B {
    color: #C4A8E8;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: transparent;
}
QLabel#secTitle_Batch {
    color: #9AE6B4;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: transparent;
}

/* ════════════════════════════════
   ALL SIDEBAR LABELS (fallback)
════════════════════════════════ */
QWidget#sidebar QLabel {
    color: #8BA5BF;
    font-size: 11px;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: transparent;
}

QLabel#wellNameLabel {
    color: #B8CFEA;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #1F3248;
    border-radius: 3px;
    padding: 3px 7px;
}

QLabel#subLabel {
    color: #3D5C7A;
    font-size: 8px;
    letter-spacing: 2px;
    font-weight: 700;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding-top: 6px;
    background: transparent;
}

/* ════════════════════════════════
   BUTTONS
════════════════════════════════ */
QWidget#sidebar QPushButton {
    background: #233347;
    color: #9DBBD8;
    border: none;
    border-radius: 5px;
    padding: 6px 8px;
    font-size: 11px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-weight: 500;
}
QWidget#sidebar QPushButton:hover {
    background: #2E4562;
    color: #C8DFF0;
}
QWidget#sidebar QPushButton:pressed {
    background: #1A3050;
}

QPushButton#loadBtn_A {
    background: #1B4070;
    color: #90CDF4;
    font-weight: 600;
    border: 1px solid #2A5A94;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 11px;
}
QPushButton#loadBtn_A:hover {
    background: #25569A;
    border-color: #4299E1;
    color: #BEE3F8;
}

QPushButton#loadBtn_B {
    background: #3A1A62;
    color: #C4A8E8;
    font-weight: 600;
    border: 1px solid #5C3490;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 11px;
}
QPushButton#loadBtn_B:hover {
    background: #512880;
    border-color: #9B72CF;
    color: #DDD0F5;
}

QPushButton#loadBtn_Batch {
    background: #1A3E2A;
    color: #9AE6B4;
    font-weight: 600;
    border: 1px solid #2D6044;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 11px;
}
QPushButton#loadBtn_Batch:hover {
    background: #245236;
    border-color: #48BB78;
}

QPushButton#ghostBtn {
    background: #232F3E;
    color: #F6AD55;
    border: 1px solid #3A4A5C;
    border-radius: 5px;
    font-size: 11px;
}
QPushButton#ghostBtn:hover:!checked {
    background: #2E3E52;
    border-color: #D69E2E;
}
QPushButton#ghostBtn:checked {
    background: #5C3A0A;
    border: 1px solid #D69E2E;
    color: #F6E05E;
}

/* ════════════════════════════════
   TOGGLE BUTTON
════════════════════════════════ */
QPushButton#toggleBtn {
    background: #0F1C2A;
    color: #2E4A66;
    border: none;
    border-right: 1px solid #0A1420;
    border-radius: 0;
    padding: 0;
    min-width: 16px;
    max-width: 16px;
    font-size: 9px;
}
QPushButton#toggleBtn:hover {
    background: #162538;
    color: #4A90BF;
}

/* ════════════════════════════════
   INPUTS
════════════════════════════════ */
QWidget#sidebar QLineEdit {
    background: #1F3048;
    color: #A8C4DC;
    border: 1px solid #2E4560;
    border-radius: 4px;
    padding: 4px 6px;
    font-size: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: #2B6CB0;
}
QWidget#sidebar QLineEdit:focus {
    border-color: #4299E1;
    background: #243D58;
}

/* ════════════════════════════════
   COMBOBOX
════════════════════════════════ */
QWidget#sidebar QComboBox {
    background: #1F3048;
    color: #A8C4DC;
    border: 1px solid #2E4560;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QWidget#sidebar QComboBox:hover {
    border-color: #4A7A9A;
}
QWidget#sidebar QComboBox::drop-down {
    border: none;
    width: 16px;
    padding-right: 4px;
}
QWidget#sidebar QComboBox QAbstractItemView {
    background: #1F3048;
    color: #A8C4DC;
    border: 1px solid #3A5570;
    selection-background-color: #2B6CB0;
    outline: none;
}

/* ════════════════════════════════
   CHECKBOX
════════════════════════════════ */
QWidget#sidebar QCheckBox {
    color: #607080;
    font-size: 10px;
    font-family: 'Segoe UI', Arial, sans-serif;
    spacing: 4px;
    background: transparent;
}
QWidget#sidebar QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border: 1px solid #2E4560;
    border-radius: 3px;
    background: #1F3048;
}
QWidget#sidebar QCheckBox::indicator:checked {
    background: #2B6CB0;
    border-color: #4299E1;
}

/* ════════════════════════════════
   TEXTEDIT
════════════════════════════════ */
QWidget#sidebar QTextEdit {
    background: #1F3048;
    color: #A8C4DC;
    border: 1px solid #2E4560;
    border-radius: 4px;
    padding: 5px;
    font-size: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: #2B6CB0;
}
QWidget#sidebar QTextEdit:focus {
    border-color: #4299E1;
}

/* ════════════════════════════════
   DIVIDER & SIGNATURE
════════════════════════════════ */
QFrame#divider {
    background: #1A2E44;
    max-height: 1px;
    min-height: 1px;
    border: none;
    margin: 4px 0;
}

QLabel#signature {
    color: #1E3A54;
    font-size: 9px;
    font-family: 'Segoe UI', Arial, sans-serif;
    letter-spacing: 2px;
    padding: 6px;
    background: #0F1C2A;
    border-top: 1px solid #0A1420;
}

/* ════════════════════════════════
   STATUS BAR
════════════════════════════════ */
QStatusBar {
    background: #111C2A;
    color: #3D5C7A;
    font-size: 10px;
    font-family: 'Segoe UI', Arial, sans-serif;
    border-top: 1px solid #0A1420;
}
"""

ZONE_COLORS = [
    (255, 200, 180, 40), (180, 220, 255, 40), (200, 255, 200, 40),
    (255, 255, 180, 40), (220, 200, 255, 40), (255, 220, 180, 40),
    (180, 255, 220, 40), (240, 200, 255, 40),
]

TOP_COLORS = [
    "#FF4444", "#44FF44", "#4444FF", "#FFFF44", "#FF44FF", "#44FFFF",
    "#FF8844", "#88FF44", "#4488FF", "#FF44AA", "#AAFF44", "#44AAFF"
]

_GHOST_PALETTE = [
    (233, 30, 99), (255, 152, 0), (156, 39, 176),
    (0, 188, 212), (76, 175, 80), (255, 87, 34),
    (96, 125, 139),
]
_ghost_color_idx = 0

def _next_ghost_color():
    global _ghost_color_idx
    c = _GHOST_PALETTE[_ghost_color_idx % len(_GHOST_PALETTE)]
    _ghost_color_idx += 1
    return c

# ---------- 全局颜色管理器 ----------
class ZoneColorManager:
    """保证相同名字的 Zone 使用相同颜色"""
    def __init__(self):
        self._zone_color_map = {}
        self._next_color_idx = 0

    def get_color(self, zone_name: str):
        if zone_name not in self._zone_color_map:
            color = ZONE_COLORS[self._next_color_idx % len(ZONE_COLORS)]
            self._zone_color_map[zone_name] = color
            self._next_color_idx += 1
        return self._zone_color_map[zone_name]

    def clear(self):
        self._zone_color_map.clear()
        self._next_color_idx = 0

class TopColorManager:
    """保证相同名字的 Top 使用相同颜色"""
    def __init__(self):
        self._top_color_map = {}
        self._next_color_idx = 0

    def get_color(self, top_name: str) -> str:
        if top_name not in self._top_color_map:
            color = TOP_COLORS[self._next_color_idx % len(TOP_COLORS)]
            self._top_color_map[top_name] = color
            self._next_color_idx += 1
        return self._top_color_map[top_name]

    def register_color(self, top_name: str, color: str):
        if top_name not in self._top_color_map:
            self._top_color_map[top_name] = color

    def remove(self, top_name: str):
        self._top_color_map.pop(top_name, None)

    def clear(self):
        self._top_color_map.clear()
        self._next_color_idx = 0

# ---------- 数据模型 ----------
class Top:
    def __init__(self, name: str, md: float, color: str = "#FF4444"):
        self.name = name
        self.md = float(md)
        self.color = color
    def to_dict(self):
        return {"name": self.name, "md": self.md, "color": self.color}
    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["md"], d.get("color", "#FF4444"))

class Zone:
    def __init__(self, top_from: Top, top_to: Top):
        self._top_from = top_from
        self._top_to = top_to
    @property
    def name(self):
        return f"{self._top_from.name} → {self._top_to.name}"
    @property
    def md_from(self):
        return self._top_from.md
    @property
    def md_to(self):
        return self._top_to.md

class TopSet:
    def __init__(self, name: str = "Default", color_manager: TopColorManager = None):
        self.name = name
        self._tops: dict[str, Top] = {}
        self._color_manager = color_manager

    def __contains__(self, name):
        return name in self._tops
    def __getitem__(self, name):
        return self._tops[name]

    @property
    def Tops(self) -> list[Top]:
        return sorted(self._tops.values(), key=lambda t: t.md)

    @property
    def Zones(self) -> list[Zone]:
        s = self.Tops
        return [Zone(s[i], s[i+1]) for i in range(len(s)-1)]

    def addRow(self, name: str, md: float, color: str = None) -> Top:
        if name in self._tops:
            raise ValueError(f"Top '{name}' 已存在")
        if color is None and self._color_manager:
            color = self._color_manager.get_color(name)
        elif color is None:
            color = "#FF4444"  # fallback
        t = Top(name, md, color)
        self._tops[name] = t
        return t

    def deleteRow(self, name: str):
        del self._tops[name]

    def to_dict(self):
        return {"name": self.name, "tops": [t.to_dict() for t in self.Tops]}

    @classmethod
    def from_dict(cls, d, color_manager=None):
        ts = cls(d["name"], color_manager=color_manager)
        for td in d.get("tops", []):
            name = td["name"]
            md = td["md"]
            if color_manager:
                # 若管理器尚未记录该名称，则用文件中的颜色注册
                if name not in color_manager._top_color_map:
                    file_color = td.get("color", "#FF4444")
                    color_manager._top_color_map[name] = file_color
                color = color_manager.get_color(name)
            else:
                color = td.get("color", "#FF4444")
            t = Top(name, md, color)
            ts._tops[name] = t
        return ts

class WellData:
    def __init__(self, name: str = "", color_manager: TopColorManager = None):
        self.name = name
        self.df = None
        self.topset = TopSet(f"{name}_Tops" if name else "Default", color_manager=color_manager)
    @property
    def depth(self) -> np.ndarray:
        if self.df is not None and len(self.df) > 0:
            return self.df.index.values.astype(float)
        return np.array([])

# ---------- Ghost 模块 ----------
class GhostObject:
    _MIN_SEG = 0.5
    def __init__(self, raw_depth, raw_value, anchor_data, color=None, opacity=0.65, label="Ghost"):
        self.raw_depth = np.asarray(raw_depth, dtype=float).copy()
        self.raw_value = np.asarray(raw_value, dtype=float).copy()
        self.color = color or _next_ghost_color()
        self.opacity = float(np.clip(opacity, 0., 1.))
        self.label = label
        d_min = float(self.raw_depth.min())
        d_max = float(self.raw_depth.max())
        anchors_raw = [(float(d), name) for d, name in anchor_data if d_min + self._MIN_SEG < float(d) < d_max - self._MIN_SEG]
        anchors_raw.sort(key=lambda x: x[0])
        self.anchor_depths = [d for d, _ in anchors_raw]
        self.anchor_names = [name for _, name in anchors_raw]
        self.raw_boundaries = [d_min] + self.anchor_depths + [d_max]
        self.display_boundaries = list(self.raw_boundaries)
        self.x_offset = 0.0
    def get_display_data(self):
        y = np.interp(self.raw_depth, self.raw_boundaries, self.display_boundaries)
        x = self.raw_value + self.x_offset
        return x, y
    def move_all(self, delta):
        self.display_boundaries = [d + delta for d in self.display_boundaries]
    def move_boundary(self, idx, new_dp):
        dp = self.display_boundaries
        mn = self._MIN_SEG
        if idx > 0:
            new_dp = max(new_dp, dp[idx-1] + mn)
        if idx < len(dp)-1:
            new_dp = min(new_dp, dp[idx+1] - mn)
        dp[idx] = new_dp
    @property
    def n_boundaries(self):
        return len(self.raw_boundaries)
    def contains_depth(self, d):
        return self.display_boundaries[0] <= d <= self.display_boundaries[-1]

class GhostView:
    def __init__(self, ghost, plot_item):
        self.ghost = ghost
        self.plot_item = plot_item
        self._curve = None
        self._lines = []
        self._blocking = False
        self._build(plot_item)
    def _build(self, plot_item):
        g, n = self.ghost, self.ghost.n_boundaries
        r, gr, b = g.color
        alpha = int(g.opacity * 255)
        pen = pg.mkPen(QColor(r, gr, b, alpha), width=2.5, style=Qt.PenStyle.DashLine)
        self._curve = pg.PlotDataItem(pen=pen)
        plot_item.addItem(self._curve)
        for i in range(n):
            is_top = (i == 0)
            is_bot = (i == n-1)
            if is_top or is_bot:
                lc, lw, sty = QColor(r, gr, b, 220), 2.0, Qt.PenStyle.SolidLine
                lbl = f"↕ {g.label}" if is_top else "⇕ 拉伸底"
            else:
                lc, lw, sty = QColor(0, 0, 0, 200), 1.2, Qt.PenStyle.DashDotLine
                anchor_idx = i - 1
                if anchor_idx < len(g.anchor_names):
                    lbl = f"⚓ {g.anchor_names[anchor_idx]}"
                else:
                    lbl = "⚓ 锚点"
            line = pg.InfiniteLine(pos=g.display_boundaries[i], angle=0,
                                   pen=pg.mkPen(lc, width=lw, style=sty),
                                   movable=True, label=lbl,
                                   labelOpts={"color": lc, "position": 0.94, "fill": pg.mkBrush(255,255,255,100)})
            line.sigPositionChanged.connect(lambda obj, idx=i: self._on_drag(idx, obj))
            plot_item.addItem(line)
            self._lines.append(line)
        self._refresh()
    def _on_drag(self, idx, line_obj):
        if self._blocking:
            return
        self._blocking = True
        try:
            new_pos = float(line_obj.value())
            g = self.ghost
            if idx == 0:
                delta = new_pos - g.display_boundaries[0]
                g.move_all(delta)
                for i, ln in enumerate(self._lines):
                    ln.setValue(g.display_boundaries[i])
            else:
                g.move_boundary(idx, new_pos)
                line_obj.setValue(g.display_boundaries[idx])
            self._refresh()
        finally:
            self._blocking = False
    def _refresh(self):
        x, y = self.ghost.get_display_data()
        mask = ~(np.isnan(x) | np.isnan(y))
        if mask.sum() >= 2:
            self._curve.setData(x[mask], y[mask])
    def reattach(self, plot_item):
        self.plot_item = plot_item
        plot_item.addItem(self._curve)
        for ln in self._lines:
            plot_item.addItem(ln)
        self._refresh()
    def remove(self):
        for item in [self._curve] + self._lines:
            if item is not None:
                try:
                    self.plot_item.removeItem(item)
                except:
                    pass
        self._lines.clear()
        self._curve = None

class GhostManager:
    def __init__(self, plot_item):
        self.plot_item = plot_item
        self._entries = []
    def add_ghost(self, ghost_obj):
        view = GhostView(ghost_obj, self.plot_item)
        self._entries.append((ghost_obj, view))
    def remove_ghost(self, ghost_obj):
        for i, (g, v) in enumerate(self._entries):
            if g is ghost_obj:
                v.remove()
                self._entries.pop(i)
                return
    def clear(self):
        for _, v in self._entries:
            v.remove()
        self._entries.clear()
    def reattach(self, plot_item):
        self.plot_item = plot_item
        for _, v in self._entries:
            v.reattach(plot_item)
    def hit_test(self, depth, tol=5.0):
        for g, _ in self._entries:
            if any(abs(dp - depth) < tol for dp in g.display_boundaries):
                return g
            if g.contains_depth(depth):
                return g
        return None

class GhostSelector(QObject):
    selected = pyqtSignal(float, float)
    def __init__(self, plot_widget, plot_item, parent=None):
        super().__init__(parent)
        self._pw, self._pi, self._vb = plot_widget, plot_item, plot_item.getViewBox()
        self.active, self._step, self._d1 = False, 0, None
        self._guide, self._band = None, None
        scene = plot_widget.scene()
        scene.sigMouseClicked.connect(self._on_click)
        self._proxy = pg.SignalProxy(scene.sigMouseMoved, rateLimit=30, slot=self._on_move)
    def activate(self):
        self.active, self._step, self._d1 = True, 0, None
        self._pw.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self._clear_temp()
    def deactivate(self):
        self.active, self._step, self._d1 = False, 0, None
        self._pw.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self._clear_temp()
    def _clear_temp(self):
        for item in [self._guide, self._band]:
            if item is not None:
                try:
                    self._pi.removeItem(item)
                except:
                    pass
        self._guide, self._band = None, None
    def _on_click(self, event):
        if not self.active or event.button() != Qt.MouseButton.LeftButton:
            return
        if not self._vb.sceneBoundingRect().contains(event.scenePos()):
            return
        depth = float(self._vb.mapSceneToView(event.scenePos()).y())
        if self._step == 0:
            self._d1, self._step = depth, 1
            self._guide = pg.InfiniteLine(pos=depth, angle=0, pen=pg.mkPen('#1565c0', width=1.5, style=Qt.PenStyle.DashLine),
                                          movable=False, label=f" 起点 {depth:.1f}m")
            self._pi.addItem(self._guide)
            event.accept()
        elif self._step == 1:
            d_min, d_max = sorted([self._d1, depth])
            self.deactivate()
            if d_max - d_min >= 1.0:
                self.selected.emit(d_min, d_max)
            event.accept()
    def _on_move(self, args):
        if not self.active or self._step != 1 or self._d1 is None:
            return
        sp = args[0]
        if not self._vb.sceneBoundingRect().contains(sp):
            return
        d2 = float(self._vb.mapSceneToView(sp).y())
        d_min, d_max = sorted([self._d1, d2])
        if self._band is None:
            self._band = pg.LinearRegionItem(values=[d_min, d_max], orientation='horizontal',
                                             brush=pg.mkBrush(21, 101, 192, 35), movable=False)
            self._pi.addItem(self._band)
        else:
            self._band.setRegion([d_min, d_max])

def build_ghost(well_data, curve_name, d_min, d_max):
    if well_data is None or well_data.df is None or curve_name not in well_data.df.columns:
        return None
    depth = well_data.depth
    mask = (depth >= d_min) & (depth <= d_max)
    seg_d = depth[mask]
    if len(seg_d) < 2:
        return None
    seg_v = well_data.df[curve_name].values[mask].astype(float)
    valid = ~np.isnan(seg_v)
    if valid.sum() < 2:
        return None
    anchors = [(t.md, t.name) for t in well_data.topset.Tops if d_min < t.md < d_max]
    return GhostObject(raw_depth=seg_d[valid], raw_value=seg_v[valid], anchor_data=anchors,
                       label=f"{well_data.name}/{curve_name}")

# ---------- 文件 I/O ----------
def read_log_file(filepath: str):
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    fp = filepath.lower()
    if fp.endswith('.las') and HAS_LASIO:
        for enc in encodings:
            try:
                las = lasio.read(filepath, ignore_header_errors=True, encoding=enc)
                df = las.df()
                df.index.name = 'DEPTH'
                well_name = str(las.well['WELL'].value).strip() if las.well['WELL'].value else Path(filepath).stem
                break
            except:
                continue
    else:
        for enc in encodings:
            try:
                if fp.endswith(('.csv', '.txt')):
                    df = pd.read_csv(filepath, encoding=enc, sep=None, engine='python')
                else:
                    df = pd.read_excel(filepath)
                df, well_name = _normalize_df(df, Path(filepath).stem)
                break
            except:
                continue
    if 'df' not in locals() or df is None or df.empty:
        raise RuntimeError("数据无效或无法解析")
    df.columns = [c.strip().replace('\x00', '').replace('\ufeff', '') for c in df.columns]
    df = df.dropna(axis=1, how='all')
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df, well_name, list(df.columns)

def _normalize_df(df: pd.DataFrame, well_name: str):
    depth_col = next((c for c in df.columns if any(k in c.lower() for k in ['depth', 'dept', 'dep', '深度', 'md', 'tvd'])), None)
    if depth_col:
        df[depth_col] = pd.to_numeric(df[depth_col], errors='coerce')
        df = df.dropna(subset=[depth_col]).sort_values(depth_col).reset_index(drop=True)
        df.index = df[depth_col].values
        df.drop(columns=[depth_col], inplace=True, errors='ignore')
    else:
        df = df.reset_index(drop=True)
    df.index.name = 'DEPTH'
    return df, well_name

# ---------- 纯绘图组件 WellPanel ----------
class WellPanel(QWidget):
    topset_changed = pyqtSignal()
    send_ghost_signal = pyqtSignal(object)
    flatten_requested = pyqtSignal(str)

    def __init__(self, label: str = "井", parent=None):
        super().__init__(parent)
        self.label = label
        self.well: WellData | None = None
        self._current_curve = None
        self._curve_list = []

        self._fill_mode = 'none'
        self._fill_ref_val = None
        self._fill_color_l = QColor(100, 150, 255, 80)
        self._fill_color_r = QColor(255, 200, 60, 90)
        self._fill_ref_line = None
        self._fill_l_item = None
        self._fill_r_item = None

        self._depth_lock_enabled = False
        self._depth_locked_min = None
        self._depth_locked_max = None
        self._value_lock_enabled = False
        self._value_locked_min = None
        self._value_locked_max = None

        self.zone_color_mgr = None
        self.top_color_mgr = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widget = pg.PlotWidget(background='w')
        self.plot_widget.setLabel('left', '深度 (m)')
        self.plot_widget.invertY(True)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.plot_widget.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self.plot_widget, stretch=1)

        self.hover_label = pg.TextItem("", anchor=(0, 1), color='#1F2937', fill=pg.mkBrush(255,255,255,220), border=pg.mkPen('#D1D5DB'))
        self.hover_label.setZValue(100)
        self.hover_label.setVisible(False)
        self.plot_item.addItem(self.hover_label)
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_hover)

        self.ghost_manager = GhostManager(self.plot_item)
        self.ghost_selector = GhostSelector(self.plot_widget, self.plot_item, self)
        self.ghost_selector.selected.connect(self._on_ghost_selected)

    def _on_mouse_hover(self, pos):
        if not self.well or self.well.df is None or not self._current_curve:
            self.hover_label.setVisible(False)
            return
        vb = self.plot_item.getViewBox()
        if not vb or not vb.sceneBoundingRect().contains(pos):
            self.hover_label.setVisible(False)
            return
        point = vb.mapSceneToView(pos)
        depth = point.y()
        depths = self.well.depth
        if len(depths) == 0:
            self.hover_label.setVisible(False)
            return
        idx = np.argmin(np.abs(depths - depth))
        actual_depth = depths[idx]
        curve_values = self.well.df[self._current_curve].values
        if idx >= len(curve_values) or np.isnan(curve_values[idx]):
            self.hover_label.setVisible(False)
            return
        actual_value = curve_values[idx]
        text = f"{actual_depth:.1f} m\n{actual_value:.2f}"
        self.hover_label.setText(text)
        self.hover_label.setPos(point.x(), point.y())
        self.hover_label.setVisible(True)

    def set_curve_list(self, curves):
        self._curve_list = curves
        if curves and self._current_curve is None:
            self._current_curve = curves[0]
        self._redraw_all()

    def set_current_curve(self, curve_name):
        if curve_name in self._curve_list:
            self._current_curve = curve_name
            self._fill_ref_val = None
            self._redraw_all()

    def get_current_curve(self):
        return self._current_curve

    def get_curve_list(self):
        return self._curve_list

    def set_fill_mode(self, mode):
        self._fill_mode = mode
        self._redraw_all()

    def set_fill_color(self, side, color):
        if side == 'left':
            self._fill_color_l = color
        else:
            self._fill_color_r = color
        self._redraw_all()

    def get_fill_color(self, side):
        return self._fill_color_l if side == 'left' else self._fill_color_r

    def apply_depth_range(self, min_d, max_d, lock=False):
        self.plot_widget.getViewBox().setYRange(min_d, max_d)
        if lock:
            self.plot_widget.getViewBox().setLimits(yMin=min_d, yMax=max_d)
            self._depth_lock_enabled = True
            self._depth_locked_min = min_d
            self._depth_locked_max = max_d
        else:
            self.plot_widget.getViewBox().setLimits(yMin=None, yMax=None)
            self._depth_lock_enabled = False

    def apply_value_range(self, min_v, max_v, lock=False):
        self.plot_widget.getViewBox().setXRange(min_v, max_v)
        if lock:
            self.plot_widget.getViewBox().setLimits(xMin=min_v, xMax=max_v)
            self._value_lock_enabled = True
            self._value_locked_min = min_v
            self._value_locked_max = max_v
        else:
            self.plot_widget.getViewBox().setLimits(xMin=None, xMax=None)
            self._value_lock_enabled = False

    def reset_depth_range(self):
        if self.well is None or self.well.df is None:
            return
        dmin, dmax = self.well.depth.min(), self.well.depth.max()
        self.plot_widget.getViewBox().setYRange(dmin, dmax)
        if self._depth_lock_enabled:
            self.plot_widget.getViewBox().setLimits(yMin=dmin, yMax=dmax)
            self._depth_locked_min = dmin
            self._depth_locked_max = dmax

    def reset_value_range(self):
        if self.well is None or self.well.df is None or not self._current_curve:
            return
        vals = self.well.df[self._current_curve].values
        valid = vals[~np.isnan(vals)]
        if len(valid) == 0:
            return
        vmin, vmax = valid.min(), valid.max()
        self.plot_widget.getViewBox().setXRange(vmin, vmax)
        if self._value_lock_enabled:
            self.plot_widget.getViewBox().setLimits(xMin=vmin, xMax=vmax)
            self._value_locked_min = vmin
            self._value_locked_max = vmax

    def load_well_data(self, well_data):
        self.well = well_data
        self._fill_ref_val = None
        self._redraw_all()
        self.topset_changed.emit()

    def save_topset(self):
        if not self.well:
            QMessageBox.warning(self, "提示", "请先加载井数据")
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存分层", f"{self.well.name}_tops.json", "JSON (*.json)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.well.topset.to_dict(), f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", "分层已保存")

    def load_topset(self):
        if not self.well:
            QMessageBox.warning(self, "提示", "请先加载井数据")
            return
        path, _ = QFileDialog.getOpenFileName(self, "加载分层", "", "JSON (*.json)")
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.well.topset = TopSet.from_dict(data, color_manager=self.top_color_mgr)
            self._redraw_all()
            self.topset_changed.emit()
            QMessageBox.information(self, "成功", "分层已加载")

    def activate_ghost_selector(self, active):
        if active:
            self.ghost_selector.activate()
        else:
            self.ghost_selector.deactivate()

    def receive_ghost(self, ghost):
        self.ghost_manager.add_ghost(ghost)

    def _redraw_all(self):
        if not self.well or self.well.df is None or not self._current_curve or self._current_curve not in self.well.df.columns:
            return
        self.plot_item.clear()
        self.plot_item.addItem(self.hover_label)
        self._fill_ref_line = None
        self._fill_l_item = None
        self._fill_r_item = None

        y = self.well.depth
        x = self.well.df[self._current_curve].values.astype(float)
        mask = ~np.isnan(x)
        xc, yc = x[mask], y[mask]

        self._draw_zones()
        if self._fill_mode != 'none' and len(xc) >= 2:
            self._init_fill(xc, yc)

        self.plot_item.addItem(pg.PlotDataItem(xc, yc, pen=pg.mkPen('#1565c0', width=1.5)))
        self.plot_item.setLabel('bottom', self._current_curve)

        self._draw_tops()
        self.ghost_manager.reattach(self.plot_item)

        if self._depth_lock_enabled and self._depth_locked_min is not None:
            self.plot_widget.getViewBox().setLimits(yMin=self._depth_locked_min, yMax=self._depth_locked_max)
        if self._value_lock_enabled and self._value_locked_min is not None:
            self.plot_widget.getViewBox().setLimits(xMin=self._value_locked_min, xMax=self._value_locked_max)

    def _draw_zones(self):
        for z in self.well.topset.Zones:
            if self.zone_color_mgr is not None:
                color = self.zone_color_mgr.get_color(z.name)
            else:
                idx = self.well.topset.Zones.index(z)
                color = ZONE_COLORS[idx % len(ZONE_COLORS)]
            self.plot_item.addItem(pg.LinearRegionItem(
                values=[z.md_from, z.md_to], orientation='horizontal',
                brush=pg.mkBrush(*color), movable=False
            ))

    def _draw_tops(self):
        for t in self.well.topset.Tops:
            line = pg.InfiniteLine(
                pos=t.md, angle=0,
                pen=pg.mkPen(t.color, width=2.5, style=Qt.PenStyle.DashLine),
                label=f"{t.name} ({t.md:.1f}m)",
                labelOpts={'color': '#000000', 'fill': pg.mkBrush(255,255,255,200),
                           'position': 0.85, 'movable': True},
                movable=True
            )
            line.sigPositionChanged.connect(lambda obj, top=t: setattr(top, 'md', float(obj.value())))
            line.sigPositionChangeFinished.connect(lambda: self._redraw_all())
            self.plot_item.addItem(line)

    def _init_fill(self, xc, yc):
        if self._fill_ref_val is None:
            self._fill_ref_val = float(np.nanpercentile(xc, 25))
        ref = self._fill_ref_val

        if self._fill_mode in ('left', 'both'):
            self._fill_l_item = QGraphicsPathItem()
            self._fill_l_item.setBrush(pg.mkBrush(self._fill_color_l))
            self._fill_l_item.setPen(pg.mkPen(None))
            self.plot_item.addItem(self._fill_l_item)

        if self._fill_mode in ('right', 'both'):
            self._fill_r_item = QGraphicsPathItem()
            self._fill_r_item.setBrush(pg.mkBrush(self._fill_color_r))
            self._fill_r_item.setPen(pg.mkPen(None))
            self.plot_item.addItem(self._fill_r_item)

        self._fill_ref_line = pg.InfiniteLine(
            pos=ref, angle=90, pen=pg.mkPen(QColor(84,110,122,180), width=1.2, style=Qt.PenStyle.DashLine),
            movable=True, label=f"阈值={ref:.1f}"
        )
        self._fill_ref_line.sigPositionChanged.connect(lambda obj: self._on_fill_ref_drag(obj))
        self.plot_item.addItem(self._fill_ref_line)

        self._update_fill_paths(xc, yc, ref)

    def _create_fill_path(self, x_arr, y_arr, ref_val):
        px = np.concatenate([x_arr, [ref_val, ref_val]])
        py = np.concatenate([y_arr, [y_arr[-1], y_arr[0]]])
        return pg.arrayToQPath(px, py, connect='all')

    def _update_fill_paths(self, xc, yc, ref):
        if self._fill_l_item:
            xl = np.minimum(xc, ref)
            self._fill_l_item.setPath(self._create_fill_path(xl, yc, ref))
        if self._fill_r_item:
            xr = np.maximum(xc, ref)
            self._fill_r_item.setPath(self._create_fill_path(xr, yc, ref))

    def _on_fill_ref_drag(self, line_obj):
        if not self.well or self.well.df is None:
            return
        ref = float(line_obj.value())
        self._fill_ref_val = ref
        if not self._current_curve or self._current_curve not in self.well.df.columns:
            return
        x = self.well.df[self._current_curve].values.astype(float)
        y = self.well.depth
        mask = ~np.isnan(x)
        xc, yc = x[mask], y[mask]
        self._update_fill_paths(xc, yc, ref)
        try:
            line_obj.label.setFormat(f"阈值={ref:.1f}")
        except:
            pass

    def _on_ghost_selected(self, d_min, d_max):
        if not self.well:
            return
        ghost = build_ghost(self.well, self._current_curve, d_min, d_max)
        if ghost:
            self.send_ghost_signal.emit(ghost)
        else:
            QMessageBox.information(self, "提示", "有效数据不足")

    def _on_context_menu(self, pos):
        if not self.well:
            return
        vb = self.plot_item.getViewBox()
        scene_pos = self.plot_widget.mapToScene(pos)
        if not vb.sceneBoundingRect().contains(scene_pos):
            return
        click_depth = vb.mapSceneToView(scene_pos).y()

        menu = QMenu()
        hit_ghost = self.ghost_manager.hit_test(click_depth)
        if hit_ghost:
            act_del = menu.addAction(f"❌ 删除 Ghost: {hit_ghost.label}")
            act_del.triggered.connect(lambda: self.ghost_manager.remove_ghost(hit_ghost))
            menu.addSeparator()

        hit_top = None
        for t in self.well.topset.Tops:
            if abs(t.md - click_depth) < 5.0:
                hit_top = t
                break

        if hit_top:
            act_rename = menu.addAction(f"✏️ 重命名层位: {hit_top.name}")
            act_del_t = menu.addAction(f"🗑️ 删除层位: {hit_top.name}")
            act_rename.triggered.connect(lambda: self._rename_top(hit_top))
            act_del_t.triggered.connect(lambda: self._delete_top(hit_top))
            menu.addSeparator()
            act_flatten = menu.addAction(f"📐 层拉平（居中到该层）: {hit_top.name}")
            act_flatten.triggered.connect(lambda: self.flatten_requested.emit(hit_top.name))
        else:
            act_add = menu.addAction(f"➕ 在 {click_depth:.1f}m 处添加新 Top")
            act_add.triggered.connect(lambda: self._add_top(click_depth))

        menu.exec(self.plot_widget.mapToGlobal(pos))

    def _add_top(self, depth):
        name, ok = QInputDialog.getText(self, "添加层位", "请输入层位名称:")
        if ok and name:
            try:
                self.well.topset.addRow(name, depth)
                self._redraw_all()
                self.topset_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"层位名冲突或无效: {e}")

    def _delete_top(self, top):
        self.well.topset.deleteRow(top.name)
        self._redraw_all()
        self.topset_changed.emit()

    def _rename_top(self, top):
        new_name, ok = QInputDialog.getText(self, "重命名", "输入新名称:", text=top.name)
        if ok and new_name and new_name != top.name:
            md = top.md
            old_color = top.color
            self.well.topset.deleteRow(top.name)
            if self.top_color_mgr:
                self.top_color_mgr.remove(top.name)
                if new_name not in self.top_color_mgr._top_color_map:
                    self.top_color_mgr._top_color_map[new_name] = old_color
            self.well.topset.addRow(new_name, md)
            self._redraw_all()
            self.topset_changed.emit()

# ---------- 联井覆盖层 ----------
class CorrelationOverlay(QWidget):
    def __init__(self, panel_left, panel_right, parent=None):
        super().__init__(parent)
        self.panel_left, self.panel_right = panel_left, panel_right
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            lw, rw = self.panel_left.well, self.panel_right.well
            if not lw or not rw:
                painter.end()
                return
            common = sorted({t.name for t in lw.topset.Tops} & {t.name for t in rw.topset.Tops})
            if not common:
                painter.end()
                return
            lp, rp = self.panel_left.plot_widget, self.panel_right.plot_widget
            lvb, rvb = lp.getPlotItem().getViewBox(), rp.getPlotItem().getViewBox()
            w = self.width()
            pen = QPen(QColor(100,100,100,140), 1.2)
            pen.setStyle(Qt.PenStyle.DashLine)
            for name in common:
                lsc = lvb.mapViewToScene(pg.Point(0, lw.topset[name].md))
                rsc = rvb.mapViewToScene(pg.Point(0, rw.topset[name].md))
                lpos = self.mapFromGlobal(lp.mapToGlobal(lsc.toPoint()))
                rpos = self.mapFromGlobal(rp.mapToGlobal(rsc.toPoint()))
                painter.setPen(pen)
                painter.drawLine(0, int(lpos.y()), w, int(rpos.y()))
            painter.end()
        except:
            pass

# ---------- 主窗口 ----------
class MainWindow(QMainWindow):
    def _make_section_header(self, container_id, label_id, icon_text, title_text):
        w = QWidget()
        w.setObjectName(container_id)
        w.setFixedHeight(30)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(6)
        icon = QLabel(icon_text)
        icon.setObjectName(label_id)
        icon.setFixedWidth(14)
        lbl = QLabel(title_text)
        lbl.setObjectName(label_id)
        lay.addWidget(icon)
        lay.addWidget(lbl)
        lay.addStretch()
        return w

    def _make_sub_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("subLabel")
        return lbl

    def _make_divider(self):
        line = QFrame()
        line.setObjectName("divider")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    def _build_well_controls(self, letter):
        refs = {}
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(4, 6, 4, 4)
        lay.setSpacing(5)

        lbl_name = QLabel("  未加载")
        lbl_name.setObjectName("wellNameLabel")
        lay.addWidget(lbl_name)
        refs['lbl_name'] = lbl_name

        btn_id = f"loadBtn_{letter}"
        btn_load = QPushButton(f"⊕  加载测井文件")
        btn_load.setObjectName(btn_id)
        lay.addWidget(btn_load)
        refs['btn_load'] = btn_load

        row_curve = QHBoxLayout()
        row_curve.setSpacing(4)
        lbl_c = QLabel("曲线")
        lbl_c.setFixedWidth(26)
        cmb_curve = QComboBox()
        row_curve.addWidget(lbl_c)
        row_curve.addWidget(cmb_curve, stretch=1)
        lay.addLayout(row_curve)
        refs['cmb_curve'] = cmb_curve

        row_sl = QHBoxLayout()
        row_sl.setSpacing(4)
        btn_save = QPushButton("💾 存分层")
        btn_load_ts = QPushButton("📂 取分层")
        row_sl.addWidget(btn_save)
        row_sl.addWidget(btn_load_ts)
        lay.addLayout(row_sl)
        refs['btn_save'] = btn_save
        refs['btn_load_ts'] = btn_load_ts

        row_fill = QHBoxLayout()
        row_fill.setSpacing(4)
        lbl_f = QLabel("充填")
        lbl_f.setFixedWidth(26)
        cmb_fill = QComboBox()
        cmb_fill.addItems(["无", "左充填", "右充填", "双向"])
        row_fill.addWidget(lbl_f)
        row_fill.addWidget(cmb_fill, stretch=1)
        lay.addLayout(row_fill)
        refs['cmb_fill'] = cmb_fill

        row_color = QHBoxLayout()
        row_color.setSpacing(4)
        btn_fill_l = QPushButton("■ 左色")
        btn_fill_r = QPushButton("■ 右色")
        row_color.addWidget(btn_fill_l)
        row_color.addWidget(btn_fill_r)
        lay.addLayout(row_color)
        refs['btn_fill_l'] = btn_fill_l
        refs['btn_fill_r'] = btn_fill_r

        btn_ghost = QPushButton("👻  Ghost 选段")
        btn_ghost.setObjectName("ghostBtn")
        btn_ghost.setCheckable(True)
        lay.addWidget(btn_ghost)
        refs['btn_ghost'] = btn_ghost

        lay.addWidget(self._make_sub_label("DEPTH RANGE"))
        g_depth = QGridLayout()
        g_depth.setSpacing(3)
        g_depth.setColumnStretch(0, 1)
        g_depth.setColumnStretch(1, 1)
        le_dmin = QLineEdit(); le_dmin.setPlaceholderText("Min")
        le_dmax = QLineEdit(); le_dmax.setPlaceholderText("Max")
        btn_apply_d = QPushButton("应用")
        btn_reset_d = QPushButton("重置")
        cb_lock_d = QCheckBox("锁")
        g_depth.addWidget(le_dmin,      0, 0)
        g_depth.addWidget(le_dmax,      0, 1)
        g_depth.addWidget(btn_apply_d,  1, 0)
        g_depth.addWidget(btn_reset_d,  1, 1)
        g_depth.addWidget(cb_lock_d,    1, 2)
        lay.addLayout(g_depth)
        refs['le_dmin'] = le_dmin
        refs['le_dmax'] = le_dmax
        refs['btn_apply_d'] = btn_apply_d
        refs['btn_reset_d'] = btn_reset_d
        refs['cb_lock_d'] = cb_lock_d

        lay.addWidget(self._make_sub_label("VALUE RANGE"))
        g_val = QGridLayout()
        g_val.setSpacing(3)
        g_val.setColumnStretch(0, 1)
        g_val.setColumnStretch(1, 1)
        le_vmin = QLineEdit(); le_vmin.setPlaceholderText("Min")
        le_vmax = QLineEdit(); le_vmax.setPlaceholderText("Max")
        btn_apply_v = QPushButton("应用")
        btn_reset_v = QPushButton("重置")
        cb_lock_v = QCheckBox("锁")
        g_val.addWidget(le_vmin,     0, 0)
        g_val.addWidget(le_vmax,     0, 1)
        g_val.addWidget(btn_apply_v, 1, 0)
        g_val.addWidget(btn_reset_v, 1, 1)
        g_val.addWidget(cb_lock_v,   1, 2)
        lay.addLayout(g_val)
        refs['le_vmin'] = le_vmin
        refs['le_vmax'] = le_vmax
        refs['btn_apply_v'] = btn_apply_v
        refs['btn_reset_v'] = btn_reset_v
        refs['cb_lock_v'] = cb_lock_v

        return container, refs

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WellCorrelator v5.3 — 全局 Top & Zone 颜色一致")
        self.resize(1540, 900)

        self.zone_color_mgr = ZoneColorManager()
        self.top_color_mgr = TopColorManager()

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.panel_a = WellPanel("参考井 A")
        self.panel_b = WellPanel("目标井 B")
        self.panel_a.zone_color_mgr = self.zone_color_mgr
        self.panel_b.zone_color_mgr = self.zone_color_mgr
        self.panel_a.top_color_mgr = self.top_color_mgr
        self.panel_b.top_color_mgr = self.top_color_mgr

        self.panel_a.send_ghost_signal.connect(self.panel_b.receive_ghost)
        self.panel_b.send_ghost_signal.connect(self.panel_a.receive_ghost)
        self.panel_a.flatten_requested.connect(lambda name: self._flatten(name, self.panel_a, self.panel_b))
        self.panel_b.flatten_requested.connect(lambda name: self._flatten(name, self.panel_a, self.panel_b))

        self.corr_overlay = CorrelationOverlay(self.panel_a, self.panel_b)
        right_splitter = QSplitter(Qt.Orientation.Horizontal)
        right_splitter.addWidget(self.panel_a)
        right_splitter.addWidget(self.corr_overlay)
        right_splitter.addWidget(self.panel_b)
        right_splitter.setSizes([650, 50, 650])

        self.left_widget = QWidget()
        self.left_widget.setObjectName("sidebar")
        self.left_widget.setFixedWidth(268)

        sidebar_vbox = QVBoxLayout(self.left_widget)
        sidebar_vbox.setContentsMargins(0, 0, 0, 0)
        sidebar_vbox.setSpacing(0)

        hdr = QWidget()
        hdr.setObjectName("sidebarHeader")
        hdr.setFixedHeight(58)
        hdr_lay = QVBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 11, 14, 9)
        hdr_lay.setSpacing(2)
        t1 = QLabel("WellCorrelator")
        t1.setObjectName("appTitle")
        t2 = QLabel("v5.3  ·  TOP & ZONE COLOR SYNC")
        t2.setObjectName("appSubtitle")
        hdr_lay.addWidget(t1)
        hdr_lay.addWidget(t2)
        sidebar_vbox.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setObjectName("sidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: #F0F2F5; border: none;")
        scroll.viewport().setStyleSheet("background: #F0F2F5;")

        scroll_w = QWidget()
        scroll_w.setObjectName("scrollContent")
        scroll_w.setStyleSheet("background: #F0F2F5;")
        left_layout = QVBoxLayout(scroll_w)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(10)
        scroll.setWidget(scroll_w)
        sidebar_vbox.addWidget(scroll, stretch=1)

        left_layout.addWidget(
            self._make_section_header("secHeader_A", "secTitle_A", "◈", "REFERENCE WELL A"))
        ctr_a, ra = self._build_well_controls("A")
        left_layout.addWidget(ctr_a)

        self.lbl_a        = ra['lbl_name']
        self.cmb_curve_a  = ra['cmb_curve']
        self.cmb_fill_a   = ra['cmb_fill']
        self.btn_fill_l_a = ra['btn_fill_l']
        self.btn_fill_r_a = ra['btn_fill_r']
        self.btn_ghost_a  = ra['btn_ghost']
        self.le_depth_min_a = ra['le_dmin']
        self.le_depth_max_a = ra['le_dmax']
        self.cb_lock_depth_a = ra['cb_lock_d']
        self.le_val_min_a    = ra['le_vmin']
        self.le_val_max_a    = ra['le_vmax']
        self.cb_lock_val_a   = ra['cb_lock_v']

        ra['btn_load'].clicked.connect(
            lambda: self._load_well(self.panel_a, self.lbl_a, self.cmb_curve_a,
                                    self.le_depth_min_a, self.le_depth_max_a))
        ra['btn_save'].clicked.connect(self.panel_a.save_topset)
        ra['btn_load_ts'].clicked.connect(self.panel_a.load_topset)
        self.cmb_curve_a.currentTextChanged.connect(lambda c: self.panel_a.set_current_curve(c))
        self.cmb_fill_a.currentTextChanged.connect(lambda t: self.panel_a.set_fill_mode(
            {"无":"none","左充填":"left","右充填":"right","双向":"both"}.get(t,"none")))
        self.btn_fill_l_a.clicked.connect(
            lambda: self._pick_fill_color(self.panel_a, self.btn_fill_l_a, self.btn_fill_r_a, 'left'))
        self.btn_fill_r_a.clicked.connect(
            lambda: self._pick_fill_color(self.panel_a, self.btn_fill_l_a, self.btn_fill_r_a, 'right'))
        self.btn_ghost_a.toggled.connect(self.panel_a.activate_ghost_selector)
        ra['btn_apply_d'].clicked.connect(
            lambda: self._apply_depth(self.panel_a, self.le_depth_min_a.text(),
                                      self.le_depth_max_a.text(), self.cb_lock_depth_a.isChecked()))
        ra['btn_reset_d'].clicked.connect(self.panel_a.reset_depth_range)
        ra['btn_apply_v'].clicked.connect(
            lambda: self._apply_value(self.panel_a, self.le_val_min_a.text(),
                                      self.le_val_max_a.text(), self.cb_lock_val_a.isChecked()))
        ra['btn_reset_v'].clicked.connect(self.panel_a.reset_value_range)

        left_layout.addWidget(self._make_divider())

        left_layout.addWidget(
            self._make_section_header("secHeader_B", "secTitle_B", "◈", "TARGET WELL B"))
        ctr_b, rb = self._build_well_controls("B")
        left_layout.addWidget(ctr_b)

        self.lbl_b        = rb['lbl_name']
        self.cmb_curve_b  = rb['cmb_curve']
        self.cmb_fill_b   = rb['cmb_fill']
        self.btn_fill_l_b = rb['btn_fill_l']
        self.btn_fill_r_b = rb['btn_fill_r']
        self.btn_ghost_b  = rb['btn_ghost']
        self.le_depth_min_b = rb['le_dmin']
        self.le_depth_max_b = rb['le_dmax']
        self.cb_lock_depth_b = rb['cb_lock_d']
        self.le_val_min_b    = rb['le_vmin']
        self.le_val_max_b    = rb['le_vmax']
        self.cb_lock_val_b   = rb['cb_lock_v']

        rb['btn_load'].clicked.connect(
            lambda: self._load_well(self.panel_b, self.lbl_b, self.cmb_curve_b,
                                    self.le_depth_min_b, self.le_depth_max_b))
        rb['btn_save'].clicked.connect(self.panel_b.save_topset)
        rb['btn_load_ts'].clicked.connect(self.panel_b.load_topset)
        self.cmb_curve_b.currentTextChanged.connect(lambda c: self.panel_b.set_current_curve(c))
        self.cmb_fill_b.currentTextChanged.connect(lambda t: self.panel_b.set_fill_mode(
            {"无":"none","左充填":"left","右充填":"right","双向":"both"}.get(t,"none")))
        self.btn_fill_l_b.clicked.connect(
            lambda: self._pick_fill_color(self.panel_b, self.btn_fill_l_b, self.btn_fill_r_b, 'left'))
        self.btn_fill_r_b.clicked.connect(
            lambda: self._pick_fill_color(self.panel_b, self.btn_fill_l_b, self.btn_fill_r_b, 'right'))
        self.btn_ghost_b.toggled.connect(self.panel_b.activate_ghost_selector)
        rb['btn_apply_d'].clicked.connect(
            lambda: self._apply_depth(self.panel_b, self.le_depth_min_b.text(),
                                      self.le_depth_max_b.text(), self.cb_lock_depth_b.isChecked()))
        rb['btn_reset_d'].clicked.connect(self.panel_b.reset_depth_range)
        rb['btn_apply_v'].clicked.connect(
            lambda: self._apply_value(self.panel_b, self.le_val_min_b.text(),
                                      self.le_val_max_b.text(), self.cb_lock_val_b.isChecked()))
        rb['btn_reset_v'].clicked.connect(self.panel_b.reset_value_range)

        left_layout.addWidget(self._make_divider())

        left_layout.addWidget(
            self._make_section_header("secHeader_Batch", "secTitle_Batch", "⊕", "BATCH ADD TOPS"))

        batch_w = QWidget()
        batch_w.setStyleSheet("background: transparent;")
        batch_lay = QVBoxLayout(batch_w)
        batch_lay.setContentsMargins(4, 6, 4, 4)
        batch_lay.setSpacing(5)

        row_target = QHBoxLayout()
        row_target.setSpacing(4)
        lbl_tgt = QLabel("目标")
        lbl_tgt.setFixedWidth(26)
        self.target_well_combo = QComboBox()
        self.target_well_combo.addItems(["参考井 A", "目标井 B"])
        row_target.addWidget(lbl_tgt)
        row_target.addWidget(self.target_well_combo, stretch=1)
        batch_lay.addLayout(row_target)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("每行: 层名 深度\n示例:\n  T1  1200.5\n  T2, 1350.0")
        self.text_edit.setFixedHeight(72)
        batch_lay.addWidget(self.text_edit)

        btn_batch = QPushButton("⊕  批量添加分层")
        btn_batch.setObjectName("loadBtn_Batch")
        btn_batch.clicked.connect(self._batch_add_tops)
        batch_lay.addWidget(btn_batch)

        left_layout.addWidget(batch_w)
        left_layout.addStretch()

        sig = QLabel("by  m Y k")
        sig.setObjectName("signature")
        sig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_vbox.addWidget(sig)

        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedWidth(16)
        self.toggle_btn.clicked.connect(self._toggle_left_panel)

        main_h = QHBoxLayout()
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)
        main_h.addWidget(self.left_widget)
        main_h.addWidget(self.toggle_btn)
        main_h.addWidget(right_splitter, stretch=1)
        main_layout.addLayout(main_h, stretch=1)

        self._syncing_scale = False
        def sync_scale(source, target):
            if self._syncing_scale:
                return
            y_min, y_max = source.plot_widget.getViewBox().viewRange()[1]
            height = y_max - y_min
            y_min_t, y_max_t = target.plot_widget.getViewBox().viewRange()[1]
            center = (y_min_t + y_max_t) / 2
            new_min = center - height / 2
            new_max = center + height / 2
            if new_max > new_min:
                self._syncing_scale = True
                target.plot_widget.getViewBox().setYRange(new_min, new_max)
                self._syncing_scale = False
        self.panel_a.plot_widget.getViewBox().sigRangeChanged.connect(
            lambda: sync_scale(self.panel_a, self.panel_b))
        self.panel_b.plot_widget.getViewBox().sigRangeChanged.connect(
            lambda: sync_scale(self.panel_b, self.panel_a))

        self.panel_a.topset_changed.connect(self.corr_overlay.update)
        self.panel_b.topset_changed.connect(self.corr_overlay.update)
        self.panel_a.plot_widget.sigRangeChanged.connect(self.corr_overlay.update)
        self.panel_b.plot_widget.sigRangeChanged.connect(self.corr_overlay.update)

        self._update_fill_btn_colors(self.panel_a, self.btn_fill_l_a, self.btn_fill_r_a)
        self._update_fill_btn_colors(self.panel_b, self.btn_fill_l_b, self.btn_fill_r_b)

    def _toggle_left_panel(self):
        visible = self.left_widget.isVisible()
        self.left_widget.setVisible(not visible)
        self.toggle_btn.setText("▶" if visible else "◀")

    def _load_well(self, panel, label_widget, cmb_curve, le_depth_min, le_depth_max):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "Log Files (*.las *.csv *.xlsx *.xls);;All (*)")
        if path:
            try:
                df, well_name, cols = read_log_file(path)
                well_data = WellData(well_name, color_manager=self.top_color_mgr)
                well_data.df = df
                panel.load_well_data(well_data)
                label_widget.setText(f"  {well_name}")
                cmb_curve.blockSignals(True)
                cmb_curve.clear()
                cmb_curve.addItems(cols)
                cmb_curve.blockSignals(False)
                if cols:
                    panel.set_curve_list(cols)
                    panel.set_current_curve(cols[0])
                    cmb_curve.setCurrentText(cols[0])
                dmin, dmax = well_data.depth.min(), well_data.depth.max()
                le_depth_min.setText(f"{dmin:.2f}")
                le_depth_max.setText(f"{dmax:.2f}")
                panel.reset_value_range()
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def _apply_depth(self, panel, min_str, max_str, lock):
        try:
            panel.apply_depth_range(float(min_str), float(max_str), lock)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的深度数字")

    def _apply_value(self, panel, min_str, max_str, lock):
        try:
            panel.apply_value_range(float(min_str), float(max_str), lock)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的曲线值数字")

    def _pick_fill_color(self, panel, btn_l, btn_r, side):
        current = panel.get_fill_color(side)
        c = QColorDialog.getColor(current, self, "", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if c.isValid():
            panel.set_fill_color(side, c)
            self._update_fill_btn_colors(panel, btn_l, btn_r)

    def _update_fill_btn_colors(self, panel, btn_l, btn_r):
        c_l = panel.get_fill_color('left')
        c_r = panel.get_fill_color('right')
        btn_l.setStyleSheet(
            f"background: rgba({c_l.red()},{c_l.green()},{c_l.blue()},{c_l.alpha()}); "
            f"color: {'#fff' if c_l.lightness() < 128 else '#000'}; "
            f"border-radius: 5px; padding: 5px 8px; font-size: 11px;")
        btn_r.setStyleSheet(
            f"background: rgba({c_r.red()},{c_r.green()},{c_r.blue()},{c_r.alpha()}); "
            f"color: {'#fff' if c_r.lightness() < 128 else '#000'}; "
            f"border-radius: 5px; padding: 5px 8px; font-size: 11px;")

    def _batch_add_tops(self):
        target = self.target_well_combo.currentText()
        panel = self.panel_a if target == "参考井 A" else self.panel_b
        if panel.well is None:
            QMessageBox.warning(self, "提示", f"{target} 尚未加载井数据，请先加载。")
            return
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入层名和深度数据")
            return
        lines = text.splitlines()
        success, errors = 0, []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split(',', 1) if ',' in line else line.split(None, 1)
            if len(parts) != 2:
                errors.append(f"第{line_num}行格式错误: {line}")
                continue
            name, md_str = parts[0].strip(), parts[1].strip()
            try:
                md = float(md_str)
            except ValueError:
                errors.append(f"第{line_num}行深度无效: {md_str}")
                continue
            try:
                panel.well.topset.addRow(name, md)
                success += 1
            except ValueError as e:
                errors.append(f"第{line_num}行添加失败: {e}")
        if success > 0:
            panel._redraw_all()
            panel.topset_changed.emit()
            QMessageBox.information(self, "完成", f"成功添加 {success} 个分层。")
        if errors:
            QMessageBox.warning(self, "部分失败", "\n".join(errors[:10]))

    def _flatten(self, top_name, panel_a, panel_b):
        if not panel_a.well or not panel_b.well:
            QMessageBox.warning(self, "提示", "请先加载两口井的数据")
            return
        if top_name not in panel_a.well.topset or top_name not in panel_b.well.topset:
            QMessageBox.warning(self, "提示", f"两口井中未同时找到层位 '{top_name}'")
            return
        depth_a = panel_a.well.topset[top_name].md
        depth_b = panel_b.well.topset[top_name].md
        view_a = panel_a.plot_widget.getViewBox()
        view_b = panel_b.plot_widget.getViewBox()
        y_min_a, y_max_a = view_a.viewRange()[1]
        height_a = y_max_a - y_min_a
        y_min_b, y_max_b = view_b.viewRange()[1]
        height_b = y_max_b - y_min_b
        view_a.setYRange(depth_a - height_a/2, depth_a + height_a/2)
        view_b.setYRange(depth_b - height_b/2, depth_b + height_b/2)
        self.statusBar().showMessage(f"已居中到层位 '{top_name}'，可手动微调对齐", 3000)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()