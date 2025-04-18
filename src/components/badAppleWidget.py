# -*- coding: utf-8 -*-
PYSIDE_VERSION = 2
try:
    from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMenu
    from PySide2.QtGui import QMovie
    from PySide2.QtMultimedia import QMediaPlayer, QMediaContent
    from PySide2.QtCore import Qt, QUrl
    PYSIDE_VERSION = 2
except ImportError:
    from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMenu
    from PySide6.QtGui import QMovie
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import Qt, QUrl
    PYSIDE_VERSION = 6
from ..utils import dragWidgetOrder

class ComponentWidget(QWidget):
    def __init__(self, gif_path, audio_path):
        super(ComponentWidget,self).__init__()
        dragWidgetOrder.DragWidgetOrder(self)
        self.setWindowTitle("GIF 播放器")
        self.setGeometry(100, 100, 300, 300)

        # 创建 QLabel 来显示 GIF
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # 创建 QMovie 对象
        self.movie = QMovie(gif_path)
        self.label.setMovie(self.movie)
        # 创建 QMediaPlayer 对象
        if PYSIDE_VERSION == 2:
            self.media_player = QMediaPlayer()
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
        else:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.setSource(QUrl.fromLocalFile(audio_path))

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 开始播放 GIF 和声音
        self.movie.start()
        self.media_player.play()

        # 菜单
        self.menu = QMenu(self)

    # 显示菜单
    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

if __name__ == "__main__":
    #app = QApplication([])
    gif_path = "E:/OneButtonManager/icons/components/bad_apple.gif"  # 替换为你的 GIF 文件路径
    audio_path = "E:/OneButtonManager/icons/components/bad_apple.mp3"  # 替换为你的音频文件路径
    player = ComponentWidget(gif_path, audio_path)
    player.show()
    #app.exec_()