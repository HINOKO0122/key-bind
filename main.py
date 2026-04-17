import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from pynput import keyboard

# データ保存ファイルのパス
SAVE_FILE = "stats.json"

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.keys_labels = {}
        self.counts = self.load_stats() # 生涯カウントの読み込み
        self.offset = QPoint()
        self.initUI()
        
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def initUI(self):
        # 枠なし、最前面、マウス追従リサイズを有効化
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        self.setMinimumSize(500, 300)
        self.resize(800, 350)
        self.setup_layout()

    def setup_layout(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 235);
                border: 2px solid #444;
                border-radius: 15px;
            }
        """)
        self.update_keys()

    def update_keys(self):
        # 既存のラベルを削除
        for lbl in self.keys_labels.values():
            lbl.deleteLater()
        self.keys_labels = {}

        # タブ（移動用ハンドル）の作成
        self.tab_handle = QLabel("::: DRAG TO MOVE / RESIZE AT EDGES :::", self)
        self.tab_handle.setGeometry(20, 5, self.width()-40, 25)
        self.tab_handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab_handle.setStyleSheet("background: #444; color: white; border-radius: 5px; font-size: 8pt; font-weight: bold;")

        # キー配置データ
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

        padding_t = 40
        margin = 15
        base_w = (self.width() - margin*2) / 12
        base_h = (self.height() - padding_t - margin) / 5

        for text, code, x_off, w_mul, row in key_map:
            count = self.counts.get(code, 0)
            lbl = QLabel(f"{text}\n{count}", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            w = int(base_w * w_mul)
            x = int(x_off * base_w) + margin
            y = int(row * base_h) + padding_t
            
            lbl.setGeometry(x, y, w - 4, int(base_h) - 4)
            lbl.setStyleSheet("background-color: white; color: black; border: 1px solid #999; font-weight: bold; border-radius: 5px;")
            self.keys_labels[code] = (lbl, text)

    # --- 操作性（移動・リサイズ） ---
    def mousePressEvent(self, event):
        self.offset = event.position().toPoint()
        # 右下の端っこ（20px）を掴んだらリサイズ
        self.is_resizing = (event.position().x() > self.width() - 25 and event.position().y() > self.height() - 25)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.is_resizing:
                new_size = event.position().toPoint()
                self.resize(max(500, new_size.x()), max(300, new_size.y()))
                self.update_keys()
            else:
                self.move(self.pos() + event.position().toPoint() - self.offset)

    # --- カウントと保存 ---
    def load_stats(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_stats(self):
        with open(SAVE_FILE, "w") as f:
            json.dump(self.counts, f)

    def on_press(self, key):
        k = self.get_key_str(key)
        if k in self.keys_labels:
            self.counts[k] = self.counts.get(k, 0) + 1
            lbl, text = self.keys_labels[k]
            lbl.setText(f"{text}\n{self.counts[k]}")
            lbl.setStyleSheet("background-color: #ff4444; color: white; border: 1px solid darkred; font-weight: bold; border-radius: 5px;")
            self.save_stats() # 押すたびに保存

    def on_release(self, key):
        k = self.get_key_str(key)
        if k in self.keys_labels:
            lbl, text = self.keys_labels[k]
            lbl.setStyleSheet("background-color: white; color: black; border: 1px solid #999; font-weight: bold; border-radius: 5px;")

    def get_key_str(self, key):
        try: return key.char.lower()
        except AttributeError: return str(key).replace("Key.", "")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    ex.show()
    sys.exit(app.exec())
