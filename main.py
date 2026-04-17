import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QPoint
from pynput import keyboard

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.keys_labels = {}
        self.offset = QPoint() # ドラッグ移動用
        self.initUI()
        
        # キーボード監視開始
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def initUI(self):
        # 最前面、枠なし、背景を少し透過させた白
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 220); border-radius: 8px; border: 2px solid #555;")
        
        # キーのサイズ定義
        K_W, K_H = 45, 45 # 基本サイズ
        GAP = 5           # キー同士の隙間

        # キー配置定義 [表示文字, 識別キー, 横位置オフセット, 幅の倍率]
        # オフセットを調整して「0.5マスのズレ」を再現
        key_map = [
            # 数字列
            ["1", "1", 0, 1], ["2", "2", 1, 1], ["3", "3", 2, 1], ["4", "4", 3, 1], ["5", "5", 4, 1], 
            ["6", "6", 5, 1], ["7", "7", 6, 1], ["8", "8", 7, 1], ["9", "9", 8, 1], ["0", "0", 9, 1], ["BS", "backspace", 10, 1.5],
            # 上段
            ["Q", "q", 0.2, 1], ["W", "w", 1.2, 1], ["E", "e", 2.2, 1], ["R", "r", 3.2, 1], ["T", "t", 4.2, 1], 
            ["Y", "y", 5.2, 1], ["U", "u", 6.2, 1], ["I", "i", 7.2, 1], ["O", "o", 8.2, 1], ["P", "p", 9.2, 1],
            # 中段 (0.5マスのズレ)
            ["A", "a", 0.5, 1], ["S", "s", 1.5, 1], ["D", "d", 2.5, 1], ["F", "f", 3.5, 1], ["G", "g", 4.5, 1], 
            ["H", "h", 5.5, 1], ["J", "j", 6.5, 1], ["K", "k", 7.5, 1], ["L", "l", 8.5, 1],
            # 下段
            ["Z", "z", 0.8, 1], ["X", "x", 1.8, 1], ["C", "c", 2.8, 1], ["V", "v", 3.8, 1], ["B", "b", 4.8, 1], 
            ["N", "n", 5.8, 1], ["M", "m", 6.8, 1],
            # スペース
            ["SPACE", "space", 3, 4]
        ]

        # 行ごとの高さ
        row_y = [0, 50, 100, 150, 200]
        current_row = 0
        last_idx = -1

        for text, code, x_off, w_mul in key_map:
            lbl = QLabel(text, self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 位置とサイズ計算
            w = int(K_W * w_mul)
            x = int(x_off * (K_W + GAP)) + 10
            
            # 段落の切り替え判定（簡易的）
            if x_off < last_idx: current_row += 1
            y = (current_row * (K_H + GAP)) + 10
            
            lbl.setGeometry(x, y, w, K_H)
            lbl.setStyleSheet("background-color: white; color: black; border: 1px solid gray; font-weight: bold; font-size: 10pt;")
            self.keys_labels[code] = lbl
            last_idx = x_off

        # ウィンドウ全体のサイズを調整
        self.setFixedSize(600, 260)

    # --- マウスで動かせるようにする機能 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.position().toPoint() - self.offset)

    # --- キー反応 ---
    def on_press(self, key):
        k = self.get_key_str(key)
        if k in self.keys_labels:
            self.keys_labels[k].setStyleSheet("background-color: red; color: white; border: 1px solid darkred; font-weight: bold;")

    def on_release(self, key):
        k = self.get_key_str(key)
        if k in self.keys_labels:
            self.keys_labels[k].setStyleSheet("background-color: white; color: black; border: 1px solid gray; font-weight: bold;")

    def get_key_str(self, key):
        try:
            return key.char.lower()
        except AttributeError:
            return str(key).replace("Key.", "")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    ex.show()
    sys.exit(app.exec())
