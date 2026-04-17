import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from pynput import keyboard

class KeyBoardVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.keys_labels = {}
        self.initUI()
        
        # キーボードリスナー
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 200); border-radius: 10px;")
        
        layout = QGridLayout()
        layout.setSpacing(5)

        # キーボードの配置定義 (簡易版)
        rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]

        for r, row in enumerate(rows):
            for c, key in enumerate(row):
                lbl = QLabel(key)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setFixedSize(40, 40)
                # 初期スタイル：白背景に黒文字
                lbl.setStyleSheet("background-color: white; color: black; border: 1px solid gray; font-weight: bold;")
                layout.addWidget(lbl, r, c)
                self.keys_labels[key.lower()] = lbl

        self.setLayout(layout)
        self.show()

    def on_press(self, key):
        try:
            k = key.char.lower()
            if k in self.keys_labels:
                # 押されたら赤くする
                self.keys_labels[k].setStyleSheet("background-color: red; color: white; border: 1px solid darkred; font-weight: bold;")
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            k = key.char.lower()
            if k in self.keys_labels:
                # 離したら白に戻す
                self.keys_labels[k].setStyleSheet("background-color: white; color: black; border: 1px solid gray; font-weight: bold;")
        except AttributeError:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyBoardVisualizer()
    sys.exit(app.exec())
