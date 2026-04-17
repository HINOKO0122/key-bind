import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from pynput import keyboard

class KeyVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        # ウィンドウを最前面に固定し、枠無しの「タブ」のような外見にする
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setGeometry(100, 100, 300, 80) # 表示場所(x,y)とサイズ(幅,高さ)

        # ラベル（表示部分）の作成
        self.label = QLabel("Waiting...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 初期の見た目（白背景）
        self.white_style = "background-color: white; color: black; font-size: 24pt; font-weight: bold; border: 2px solid #ccc;"
        # 押した時の見た目（赤背景）
        self.red_style = "background-color: red; color: white; font-size: 24pt; font-weight: bold;"
        
        self.label.setStyleSheet(self.white_style)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # キーボードの入力を監視する
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try:
            # 普通の文字キー
            k = key.char.upper()
        except AttributeError:
            # Shift, Ctrlなどの特殊キー
            k = str(key).replace("Key.", "").capitalize()

        # 画面の文字を更新して背景を赤くする
        self.label.setText(k)
        self.label.setStyleSheet(self.red_style)

    def on_release(self, key):
        # キーを離したら白背景に戻す
        self.label.setStyleSheet(self.white_style)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KeyVisualizer()
    window.show()
    sys.exit(app.exec())
