import sys
import json
import os
import winreg

# 真っ黒対策（念のため残しますが、不透明設定にしています）
os.environ["QT_QUICK_BACKEND"] = "software"

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt6.QtGui import QAction
from pynput import keyboard

SAVE_FILE = "stats.json"
APP_NAME = "MyKeyVisualizer"

class KeySignal(QObject):
    pressed = pyqtSignal(str)
    released = pyqtSignal(str)

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.keys_labels = {}
        self.counts = self.load_stats()
        self.always_on_top = True
        self.is_moving = False
        self.signals = KeySignal()
        
        # 信号の接続
        self.signals.pressed.connect(self.update_press_style)
        self.signals.released.connect(self.update_release_style)

        # 1. まずフラグを設定（表示する前に設定するのが鉄則です）
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # 2. UIの初期化
        self.initUI()
        
        # 3. リスナー開始
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.setDaemon(True) # アプリ終了時に一緒に消えるように
        self.listener.start()

    def initUI(self):
        # 背景を白に固定（真っ黒対策）
        self.setStyleSheet("background-color: white; border: 2px solid #444; border-radius: 10px;")
        self.apply_size("M")

    def apply_size(self, size_label):
        size_map = {"S": (500, 220), "M": (750, 320), "L": (1000, 420)}
        w, h = size_map[size_label]
        self.setFixedSize(w, h)
        self.update_keys() # キーを再配置

    def update_keys(self):
        # 古いラベルを完全に消去
        for lbl, _ in self.keys_labels.values():
            lbl.setParent(None)
            lbl.deleteLater()
        self.keys_labels = {}

        # タブハンドル
        self.tab_height = 30
        self.handle = QLabel("::: RIGHT CLICK FOR SETTINGS / DRAG TO MOVE :::", self)
        self.handle.setGeometry(10, 5, self.width()-20, self.tab_height)
        self.handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.handle.setStyleSheet("background: #333; color: white; border-radius: 5px; font-weight: bold;")
        self.handle.show()

        # キーボードのデータ（省略なし）
        key_map = [
            ["1", "1", 0, 1, 0], ["2", "2", 1, 1, 0], ["3", "3", 2, 1, 0], ["4", "4", 3, 1, 0], ["5", "5", 4, 1, 0], 
            ["6", "6", 5, 1, 0], ["7", "7", 6, 1, 0], ["8", "8", 7, 1, 0], ["9", "9", 8, 1, 0], ["0", "0", 9, 1, 0], ["BS", "backspace", 10, 1.5, 0],
            ["Q", "q", 0.2, 1, 1], ["W", "w", 1.2, 1, 1], ["E", "e", 2.2, 1, 1], ["R", "r", 3.2, 1, 1], ["T", "t", 4.2, 1, 1], 
            ["Y", "y", 5.2, 1, 1], ["U", "u", 6.2, 1, 1], ["I", "i", 7.2, 1, 1], ["O", "o", 8.2, 1, 1], ["P", "p", 9.2, 1, 1],
            ["A", "a", 0.5, 1, 2], ["S", "s", 1.5, 1, 2], ["D", "d", 2.5, 1, 2], ["F", "f", 3.5, 1, 2], ["G", "g", 4.5, 1, 2], 
            ["H", "h", 5.5, 1, 2], ["J", "j", 6.5, 1, 2], ["K", "k", 7.5, 1, 2], ["L", "l", 8.5, 1, 2],
            ["Z", "z", 0.8, 1, 3], ["X", "x", 1.8, 1, 3], ["C", "c", 2.8, 1, 3], ["V", "v", 3.8, 1, 3], ["B", "b", 4.8, 1, 3], 
            ["N", "n", 5.8, 1, 3], ["M", "m", 6.8, 1, 3],
            ["SPACE", "space", 3, 4, 4]
        ]

        padding_t, margin = 45, 15
        base_w = (self.width() - margin*2) / 12
        base_h = (self.height() - padding_t - margin) / 5

        for text, code, x_off, w_mul, row in key_map:
            count = self.counts.get(code, 0)
            lbl = QLabel(f"{text}\n{count}", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setGeometry(int(x_off * base_w) + margin, int(row * base_h) + padding_t, int(base_w * w_mul) - 4, int(base_h) - 4)
            lbl.setStyleSheet("background-color: #f0f0f0; color: black; border: 1px solid #999; border-radius: 5px;")
            lbl.show() # 明示的に表示
            self.keys_labels[code] = (lbl, text)

    # --- 右クリックメニュー ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # サイズ変更
        size_m = menu.addMenu("サイズ変更")
        for s in ["S", "M", "L"]:
            a = QAction(f"サイズ {s}", self)
            a.triggered.connect(lambda chk, sz=s: self.apply_size(sz))
            size_m.addAction(a)

        # 最前面設定
        top_a = QAction("最前面に表示", self, checkable=True, checked=self.always_on_top)
        top_a.triggered.connect(self.toggle_on_top)
        menu.addAction(top_a)

        # 自動起動
        start_a = QAction("Windows起動時に開始", self, checkable=True, checked=self.is_startup_enabled())
        start_a.triggered.connect(self.toggle_startup)
        menu.addAction(start_a)

        menu.addSeparator()
        exit_a = QAction("終了", self)
        exit_a.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_a)
        
        menu.exec(event.globalPos())

    def toggle_on_top(self):
        self.always_on_top = not self.always_on_top
        if self.always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show() # フラグ変更後にこれがないと消える場合がある

    # --- 自動起動 (Registry) ---
    def toggle_startup(self, checked):
        path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
            if checked:
                winreg.SetValueEx(reg_key, APP_NAME, 0, winreg.REG_SZ, os.path.abspath(sys.argv[0]))
            else:
                try: winreg.DeleteValue(reg_key, APP_NAME)
                except: pass
            winreg.CloseKey(reg_key)
        except: pass

    def is_startup_enabled(self):
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(reg_key, APP_NAME)
            return True
        except: return False

    # --- 基本動作 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 40:
            self.is_moving = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.is_moving: self.move(self.pos() + event.position().toPoint() - self.offset)

    def mouseReleaseEvent(self, event): self.is_moving = False

    def on_press(self, key): self.signals.pressed.emit(self.get_key_str(key))
    def on_release(self, key): self.signals.released.emit(self.get_key_str(key))
    def get_key_str(self, key):
        try: return key.char.lower()
        except: return str(key).replace("Key.", "")

    def update_press_style(self, k):
        if k in self.keys_labels:
            self.counts[k] = self.counts.get(k, 0) + 1
            lbl, text = self.keys_labels[k]
            lbl.setText(f"{text}\n{self.counts[k]}")
            lbl.setStyleSheet("background-color: red; color: white; font-weight: bold; border-radius: 5px;")
            self.save_stats()

    def update_release_style(self, k):
        if k in self.keys_labels:
            lbl, _ = self.keys_labels[k]
            lbl.setStyleSheet("background-color: #f0f0f0; color: black; border: 1px solid #999; border-radius: 5px;")

    def load_stats(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}
    def save_stats(self):
        with open(SAVE_FILE, "w") as f: json.dump(self.counts, f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    ex.show()
    sys.exit(app.exec())
