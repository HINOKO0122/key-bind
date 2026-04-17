import sys
import json
import os

# 【重要】真っ黒画面を防ぐための魔法の1行
# ソフトウェア描画を強制し、GPUとの相性問題を回避します
os.environ["QT_QUICK_BACKEND"] = "software"
os.environ["QT_API"] = "pyqt6"

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt6.QtGui import QAction
from pynput import keyboard

SAVE_FILE = "stats.json"

class KeySignal(QObject):
    pressed = pyqtSignal(str)
    released = pyqtSignal(str)

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.keys_labels = {}
        self.counts = self.load_stats()
        self.always_on_top = True
        self.signals = KeySignal()
        self.signals.pressed.connect(self.update_press_style)
        self.signals.released.connect(self.update_release_style)

        self.initUI()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def initUI(self):
        self.update_window_flags()
        # 背景の透過を一度オフにしても良いですが、まずはこれで試しましょう
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.apply_size("M")

    def update_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def apply_size(self, size_label):
        size_map = {"S": (500, 220), "M": (750, 320), "L": (1000, 420)}
        w, h = size_map[size_label]
        self.setFixedSize(w, h)
        self.update_keys()

    def update_keys(self):
        for lbl in self.keys_labels.values():
            lbl.deleteLater()
        self.keys_labels = {}

        self.tab_handle = QLabel("::: RIGHT CLICK FOR SETTINGS / DRAG TO MOVE :::", self)
        self.tab_handle.setGeometry(20, 5, self.width()-40, 25)
        self.tab_handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab_handle.setStyleSheet("background: #333; color: white; border-radius: 5px; font-size: 7pt; font-weight: bold;")

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

        padding_t, margin = 40, 15
        base_w = (self.width() - margin*2) / 12
        base_h = (self.height() - padding_t - margin) / 5

        for text, code, x_off, w_mul, row in key_map:
            count = self.counts.get(code, 0)
            lbl = QLabel(f"{text}\n{count}", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setGeometry(int(x_off * base_w) + margin, int(row * base_h) + padding_t, int(base_w * w_mul) - 4, int(base_h) - 4)
            lbl.setStyleSheet("background-color: white; color: black; border: 1px solid #999; font-weight: bold; border-radius: 5px; font-size: 8pt;")
            self.keys_labels[code] = (lbl, text)

        self.setStyleSheet("background-color: rgba(240, 240, 240, 235); border: 2px solid #444; border-radius: 15px;")

    def update_press_style(self, k):
        if k in self.keys_labels:
            self.counts[k] = self.counts.get(k, 0) + 1
            lbl, text = self.keys_labels[k]
            lbl.setText(f"{text}\n{self.counts[k]}")
            lbl.setStyleSheet("background-color: #ff4444; color: white; border: 1px solid darkred; font-weight: bold; border-radius: 5px;")
            self.save_stats()

    def update_release_style(self, k):
        if k in self.keys_labels:
            lbl, text = self.keys_labels[k]
            lbl.setStyleSheet("background-color: white; color: black; border: 1px solid #999; font-weight: bold; border-radius: 5px;")

    def on_press(self, key):
        self.signals.pressed.emit(self.get_key_str(key))

    def on_release(self, key):
        self.signals.released.emit(self.get_key_str(key))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("background-color: white; color: black; border: 1px solid gray;")
        size_menu = menu.addMenu("Size")
        for s in ["S", "M", "L"]:
            action = QAction(f"Size {s}", self)
            action.triggered.connect(lambda checked, sz=s: self.apply_size(sz))
            size_menu.addAction(action)
        top_action = QAction("Always on Top", self)
        top_action.setCheckable(True)
        top_action.setChecked(self.always_on_top)
        top_action.triggered.connect(self.toggle_on_top)
        menu.addAction(top_action)
        menu.addSeparator()
        exit_action = QAction("Exit App", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)
        menu.exec(event.globalPos())

    def toggle_on_top(self):
        self.always_on_top = not self.always_on_top
        self.update_window_flags()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.position().toPoint() - self.offset)

    def load_stats(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}

    def save_stats(self):
        with open(SAVE_FILE, "w") as f: json.dump(self.counts, f)

    def get_key_str(self, key):
        try: return key.char.lower()
        except AttributeError: return str(key).replace("Key.", "")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    sys.exit(app.exec())
