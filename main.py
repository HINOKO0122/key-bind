import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QPoint, QSize
from pynput import keyboard

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.keys_labels = {}
        self.offset = QPoint()
        self.initUI()
        
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 枠線をつけて、右下でサイズ変更できるようにする
        self.setStyleSheet("background-color: rgba(255, 255, 255, 220); border-radius: 8px; border: 2px solid #555;")
        
        self.setup_keys()
        self.setMinimumSize(400, 200)
        self.resize(600, 260) # 初期サイズ

    def setup_keys(self):
        # 古いラベルを消去
        for lbl in self.keys_labels.values():
            lbl.deleteLater()
        self.keys_labels = {}

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

        # ウィンドウサイズに合わせてキーの大きさを計算
        padding = 10
        base_w = (self.width() - padding*2) / 12
        base_h = (self.height() - padding*2) / 5

        for text, code, x_off, w_mul, row in key_map:
            lbl = QLabel(text, self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            w = int(base_w * w_mul)
            x = int(x_off * base_w) + padding
            y = int(row * base_h) + padding
            lbl.setGeometry(x, y, w - 2, int(base_h) - 2)
            lbl.setStyleSheet("background-color: white; color: black; border: 1px solid gray; font-weight: bold;")
            self.keys_labels[code] = lbl
        self.show()

    # サイズ変更時にキーを再配置
    def resizeEvent(self, event):
        self.setup_keys()

    # マウス操作：移動とリサイズ
    def mousePressEvent(self, event):
        self.offset = event.position().toPoint()
        # 右下 30px 以内ならリサイズモード
        self.is_resizing = (event.position().x() > self.width() - 30 and event.position().y() > self.height() - 30)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if getattr(self, 'is_resizing', False):
                self.resize(event.position().x(), event.position().y())
            else:
                self.move(self.pos() + event.position().toPoint() - self.offset)

    def on_press(self, key):
        k = self.get_key_str(key)
        if k in self.keys_labels:
            self.keys_labels[k].setStyleSheet("background-color: red; color: white; border: 1px solid darkred; font-weight: bold;")

    def on_release(self, key):
        k = self.get_key_str(key)
        if k in self.keys_labels:
            self.keys_labels[k].setStyleSheet("background-color: white; color: black; border: 1px solid gray; font-weight: bold;")

    def get_key_str(self, key):
        try: return key.char.lower()
        except AttributeError: return str(key).replace("Key.", "")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    sys.exit(app.exec())
