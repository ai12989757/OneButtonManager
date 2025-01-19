# -*- coding: utf-8 -*-
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from ..ui.mayaMQT import maya_main_window

class sliderWidget(QWidget):
    def __init__(self, parent=maya_main_window()):
        super(sliderWidget, self).__init__(parent)

        self.setObjectName('sliderWidget')

        self.setAttribute(Qt.WA_TranslucentBackground)                           # 设置窗口背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)                  # 设置窗口无边框
        self.setGeometry(QCursor.pos().x()-80, QCursor.pos().y()+110, 200,30)        # 根据光标位置设置窗口位置
 
        layout = QVBoxLayout()
        # 设置上下左右居中
        #layout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        # 向下偏移
        layout.setContentsMargins(0, 10, 0, 0)

        # 设置间隔
        #layout.setSpacing(20)

        self.label = QLabel('0',self)
        # 设置字体
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.label.setFont(font)
        # 往右偏移
        self.label.setContentsMargins(15, 0, 0, 0)

        layout.addWidget(self.label, alignment=Qt.AlignLeft|Qt.AlignTop)

        self.label.setText(str(0.9999999))


        # 创建水平滑块
        self.h_slider = QSlider(Qt.Horizontal, self)
        # 宽度
        self.h_slider.setFixedWidth(160)
        self.h_slider.setMinimum(-100)
        self.h_slider.setMaximum(100)
        self.h_slider.setValue(0)
        self.h_slider.setTickPosition(QSlider.TicksBelow)
        self.h_slider.setTickInterval(10)

        # 设置上下左右居中
        layout.addWidget(self.h_slider, alignment=Qt.AlignTop|Qt.AlignHCenter)
        self.setLayout(layout)
        self.setWindowTitle('PySide2 滑块示例')


    # def updateLabel(self, value):
    #     self.label.setText(str(value))
    def paintEvent(self, event):
        # 圆角
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)                              # 抗锯齿 pyside6不支持
        painter.setBrush(QBrush(QColor(163, 228, 215,100)))                              # 设置画出边框的颜色,RGBA 255
        painter.setPen(QPen(QColor(20, 143, 119,255), 2))                                  # 设置画出边框的颜色,RGBA 255
        painter.drawRoundedRect( 0, 0, self.width(), self.height(), 20,20);     # 圆角设置

    def event(self, eve):
        if eve.type() == QEvent.WindowDeactivate:
            self.close()
        return QWidget.event(self, eve)
    def mouseMoveEvent(self, event):
        # 按住鼠标左键移动窗口
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.last)
            self.last = event.globalPos()
            event.accept()
    def mousePressEvent(self, event):
        # 记录鼠标左键位置
        if event.button() == Qt.LeftButton:
            self.last = event.globalPos()
            event.accept()

if __name__ == "__main__":
    try:
        olUI.close()
        olUI.deleteLater()
    except:
        pass

    olUI = sliderWidget()
    # 查看窗口是否显示
    if olUI.isVisible() is False:
        olUI.show()