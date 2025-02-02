import os
import ctypes
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from ..widgets.GIFWidget import GIFButtonWidget

from maya import mel

# -*- coding: utf-8 -*-
import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

try:
    from PySide6.QtWidgets import QWidget
except ImportError:
    from PySide2.QtWidgets import QWidget


import ctypes
from ctypes import wintypes

# 定义虚拟键码
VK_RCONTROL = 0xA3

# 加载 user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 定义 GetAsyncKeyState 函数
GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = [wintypes.INT]
GetAsyncKeyState.restype = wintypes.SHORT

def is_right_ctrl_pressed():
    # 检查右 Ctrl 键是否被按下
    state = GetAsyncKeyState(VK_RCONTROL)
    return state & 0x8000 != 0

# 创建一个按钮编辑器窗口
def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

try:
    # icons/
    ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/ui', 'icons/')
except:
    ICONPATH = 'E:/OneButtonManager/icons/'

def is_caps_lock_on():
    # 使用 ctypes 检查大写锁定状态
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL) & 0x0001

class toDefUI(QWidget):
    def __init__(self, parent=maya_main_window(), fileList=None, language=0):
        self.MainPane = mel.eval('string $temp = $gMainPane')

        self.MainPane = omui.MQtUtil.findLayout(self.MainPane)
        self.MainPane = wrapInstance(int(self.MainPane), QWidget)

        self.MainPane = self.MainPane.parent().parent().parent()
        self.MainPane.resizeEvent = self.on_main_pane_resize


        super().__init__(parent)
        self.fileList = fileList
        self.language = language
        self.win = 'Shift2Default'
        self.title = 'Shift Manager'
        self.mPos = None
        self.width = 400
        self.height = 50
        self.setAttribute(Qt.WA_DeleteOnClose) # 设置窗口关闭事件
        self.createUI() # 创建UI
        self.load_settings() # 恢复上次的位置和大小

    def on_main_pane_resize(self, event):
        # 获取 MainPane 的新尺寸
        new_size = event.size()
        print(f"MainPane 窗口大小更改: 宽度={new_size.width()}, 高度={new_size.height()}")
        # 调用父类的 resizeEvent 方法
        super(QWidget, self.MainPane).resizeEvent(event)

    def createUI(self):
        self.background_opacity = 0
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle(self.title)
        self.setObjectName(self.win)
        #self.resize(self.width, self.height) # 设置窗口大小
        #self.setGeometry(0, 0, self.width, self.height)
        self.setAttribute(Qt.WA_TranslucentBackground, True) # 设置窗口透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)                  # 设置窗口无边框
        self.setFixedSize(self.width, self.height)

        self.MainPane = mel.eval('string $temp = $gMainPane')
        self.MainPane = omui.MQtUtil.findLayout(self.MainPane)
        self.MainPane = wrapInstance(int(self.MainPane), QWidget)
        self.MainPane = self.MainPane.parent().parent()
        global_pos = self.MainPane.mapToGlobal(self.MainPane.rect().topLeft())
        self.setGeometry(global_pos.x(), global_pos.y(), 400, 400)

        #self.setWindowOpacity(0)
        self.globalLayout = QHBoxLayout(self)
        self.globalLayout.setContentsMargins(5, 0, 5, 0)
        self.globalLayout.setSpacing(0)
        self.setLayout(self.globalLayout)
        self.globalLayout.setAlignment(Qt.AlignLeft)
        
        button1 = GIFButtonWidget(icon = ICONPATH + 'siri.gif', size=40, dragMove=True)
        self.globalLayout.addWidget(button1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制半透明背景
        painter.setBrush(QColor(0, 0, 0, self.background_opacity))  # RGBA 颜色，最后一个参数是透明度
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 25, 25)  # 绘制圆角矩形
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Menu:
            self.background_opacity = 129
            self.update()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Menu:
            self.background_opacity = 0
            self.update()
            

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.move(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

    def closeEvent(self, event):
        # 保存当前的位置和大小
        self.save_settings()
        event.accept()

    def save_settings(self):
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())

    def load_settings(self):
        settings = QSettings()
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    # def paintEvent(self, event):
    #     # 设置圆角
    #     path = QPainterPath()
    #     path.addRoundedRect(0, 0, self.width, self.height, 10, 10) # 设置圆角路径
    #     path.translate(0.5, 0.5) # 修复边框模糊
    #     region = QRegion(path.toFillPolygon().toPolygon())
    #     self.setMask(region)
    #     # 创建一个 QPainter 对象来绘制边框
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing) # 抗锯齿
    #     pen = QPen(Qt.darkGray, 5)  # 设置描边颜色和宽度
    #     painter.setPen(pen)
    #     painter.drawPath(path)
    #     painter.end()

if __name__ == '__main__':
    try:
        ui.close()
        ui.deleteLater()
    except:
        pass
    ui = toDefUI()
    ui.show()