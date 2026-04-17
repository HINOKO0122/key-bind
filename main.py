import sys
import json
import os
import winreg
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt6.QtGui import QAction
from pynput import keyboard

# 保存用ファイル
STATS_FILE = "stats.json"
CONFIG_FILE = "config.json"
APP_NAME = "MyKeyVisualizer"

class KeySignal(QObject):
    pressed = pyqtSignal(str)
    released = pyqtSignal(str)

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        # 設定と統計の読み込み
        self.config = self.load_config()
        self.counts = self.load_stats()
        
        # 変数のセットアップ
        self.keys_labels = {}
        self.is_moving = False
        self.signals = KeySignal()
        self.signals.pressed.connect(self.update_press_style)
        self.signals.released.connect(self.update_release_style)

        # ウィンドウ初期設定
        self.always_on_top = self.config.get("always_on_top", True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        if self.always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # サイズと位置の適用
        current_size = self.config.get("size_label", "M")
        self.apply_size(current_size, save=False)
        
        if "pos" in self.config:
            self.move(self.config["pos"][0], self.config["pos"][1])

        self.show()
        
        # キー監視開始
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.daemon = True
        self.listener.start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: pass
        return {"size_label": "M", "always_on_top": True}

    def save_config(self):
        self.config["pos"] = [self.x(), self.y()]
        self.config["always_on_top"] = self.always_on_top
        with open(CONFIG_FILE, "w") as f: json.dump(self.config, f)

    def apply_size(self, size_label, save=True):
        size_map = {"S": (600, 300), "M": (850, 400), "L": (1100, 500)}
        w, h = size_map[size_label]
        self.setFixedSize(w, h)
        self.config["size_label"] = size_label
        if save: self.save_config()
        self.update_keys()

    def update_keys(self):
        for lbl, _ in self.keys_labels.values(): lbl.deleteLater()
        self.keys_labels = {}
        self.setStyleSheet("background-color: rgba(20, 20, 20, 210); border: 2px solid #666; border-radius: 12px;")

        self.tab_height = 35
        self.handle = QLabel("::: DRAG TO MOVE / RIGHT CLICK FOR SETTINGS :::", self)
        self.handle.setGeometry(10, 5, self.width()-20, self.tab_height)
        self.handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.handle.setStyleSheet("background: rgba(255, 255, 255, 20); color: #ccc; border: none; font-size: 8pt;")
        self.handle.show()

        # キーマップ（Shift, Ctrl, Alt, Tab, Enter追加）
        key_map = [
            ["1", "1", 0, 1, 0], ["2", "2", 1, 1, 0], ["3", "3", 2, 1, 0], ["4", "4", 3, 1, 0], ["5", "5", 4, 1, 0], 
            ["6", "6", 5, 1, 0], ["7", "7", 6, 1, 0], ["8", "8", 7, 1, 0], ["9", "9", 8, 1, 0], ["0", "0", 9, 1, 0], ["BS", "backspace", 10, 1.5, 0],
            ["Tab", "tab", 0, 1.3, 1], ["Q", "q", 1.3, 1, 1], ["W", "w", 2.3, 1, 1], ["E", "e", 3.3, 1, 1], ["R", "r", 4.3, 1, 1], ["T", "t", 5.3, 1, 1], 
            ["Y", "y", 6.3, 1, 1], ["U", "u", 7.3, 1, 1], ["I", "i", 8.3, 1, 1], ["O", "o", 9.3, 1, 1], ["P", "p", 10.3, 1, 1],
            ["Ctrl", "ctrl_l", 0, 1.5, 2], ["A", "a", 1.5, 1, 2], ["S", "s", 2.5, 1, 2], ["D", "d", 3.5, 1, 2], ["F", "f", 4.5, 1, 2], ["G", "g", 4.5, 1, 2], 
            ["H", "h", 6.5, 1, 2], ["J", "j", 7.5, 1, 2], ["K", "k", 8.5, 1, 2], ["L", "l", 9.5, 1, 2], ["Enter", "enter", 10.5, 1.2, 2],
            ["Shift", "shift", 0, 1.8, 3], ["Z", "z", 1.8, 1, 3], ["X", "x", 2.8, 1, 3], ["C", "c", 3.8, 1, 3], ["V", "v", 4.8, 1, 3], ["B", "b", 5.8, 1, 3], 
            ["N", "n", 6.8, 1, 3], ["M", "m", 7.8, 1, 3], ["Alt", "alt_l", 8.8, 1.2, 3],
            ["SPACE", "space", 3, 5, 4]
        ]

        p_t, m = 50, 20
        b_w, b_h = (self.width() - m*2) / 12, (self.height() - p_t - m) / 5

        for text, code, x_off, w_mul, row in key_map:
            count = self.counts.get(code, 0)
            lbl = QLabel(f"{text}\n{count}", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setGeometry(int(x_off * b_w) + m, int(row * b_h) + p_t, int(b_w * w_mul) - 6, int(b_h) - 6)
            lbl.setStyleSheet("background-color: rgba(240, 240, 240, 220); color: black; border-radius: 6px; font-weight: bold; font-size: 9pt;")
            lbl.show()
            self.keys_labels[code] = (lbl, text)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        # 設定画面が見えるようにダークテーマを適用
        menu.setStyleSheet("""
            QMenu { background-color: #222; color: white; border: 1px solid #555; }
            QMenu::item { padding: 8px 25px; }
            QMenu::item:selected { background-color: #444; }
            QMenu::separator { background-color: #555; height: 1px; }
        """)
        
        size_m = menu.addMenu("Resize")
        for s in ["S", "M", "L"]:
            a = QAction(f"Size {s}", self)
            a.triggered.connect(lambda chk, sz=s: self.apply_size(sz))
            size_m.addAction(a)

        top_a = QAction("Always On Top", self, checkable=True, checked=self.always_on_top)
        top_a.triggered.connect(self.toggle_on_top)
        menu.addAction(top_a)

        start_a = QAction("Launch on Startup", self, checkable=True, checked=self.is_startup_enabled())
        start_a.triggered.connect(self.toggle_startup)
        menu.addAction(start_a)

        menu.addSeparator()
        exit_a = QAction("Exit", self)
        exit_a.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_a)
        menu.exec(event.globalPos())

    def toggle_on_top(self):
        self.always_on_top = not self.always_on_top
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowType.WindowStaysOnTopHint)
        self.save_config()
        self.show()

    def toggle_startup(self, checked):
        path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
            if checked: winreg.SetValueEx(reg, APP_NAME, 0, winreg.REG_SZ, os.path.abspath(sys.argv[0]))
            else: winreg.DeleteValue(reg, APP_NAME)
            winreg.CloseKey(reg)
        except: pass

    def is_startup_enabled(self):
        try:
            reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(reg, APP_NAME)
            return True
        except: return False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= self.tab_height + 15:
            self.is_moving = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.is_moving:
            self.move(self.pos() + event.position().toPoint() - self.offset)
            self.save_config() # 移動するたびに位置を保存

    def mouseReleaseEvent(self, event): self.is_moving = False

    def on_press(self, key): self.signals.pressed.emit(self.get_key_str(key))
    def on_release(self, key): self.signals.released.emit(self.get_key_str(key))
    
    def get_key_str(self, key):
        try: return key.char.lower()
        except:
            k = str(key).replace("Key.", "")
            if "shift" in k: return "shift"
            if "ctrl" in k: return "ctrl_l"
            if "alt" in k: return "alt_l"
            return k

    def update_press_style(self, k):
        if k in self.keys_labels:
            self.counts[k] = self.counts.get(k, 0) + 1
            lbl, text = self.keys_labels[k]
            lbl.setText(f"{text}\n{self.counts[k]}")
            lbl.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold; border-radius: 6px;")
            self.save_stats()

    def update_release_style(self, k):
        if k in self.keys_labels:
            lbl, _ = self.keys_labels[k]
            lbl.setStyleSheet("background-color: rgba(240, 240, 240, 220); color: black; border-radius: 6px; font-weight: bold;")

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f: return json.load(f)
            except: pass
        return {}
    def save_stats(self):
        with open(STATS_FILE, "w") as f: json.dump(self.counts, f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    sys.exit(app.exec())
