import os
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
    ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/ui', 'icons/')
except:
    ICONPATH = 'E:/OneButtonManager/icons/'

class mainUI(QWidget):
    def __init__(self, parent=maya_main_window(),alignment = "bottom"):
        super().__init__(parent)
    
        self.MainPane = mel.eval('string $temp = $gMainPane')
        self.MainPane = omui.MQtUtil.findLayout(self.MainPane)
        self.MainPane = wrapInstance(int(self.MainPane), QWidget)
        self.MainPane = self.MainPane.parent().parent()
        self.MainPane.removeEventFilter(self)
        self.MainPane.installEventFilter(self)
        
        self.alignment = alignment # top, bottom, left, right 窗口停靠视图位置
        self.mPos = None
        self.background_opacity = 0
        self.size = 50
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 设置窗口透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)  # 设置窗口无边框

        # 全局布局
        self.globalLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.globalLayout.setSpacing(0)
        self.globalLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.globalLayout)

        # 左侧布局
        self.layout1 = QBoxLayout(QBoxLayout.LeftToRight)
        self.globalLayout.addLayout(self.layout1)

        # 中间布局
        self.layout2 = QBoxLayout(QBoxLayout.LeftToRight)
        self.layout2.setSpacing(20)
        self.centerSpacerLeft = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.centerSpacerRight = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.globalLayout.addItem(self.centerSpacerLeft)
        self.globalLayout.addLayout(self.layout2)
        self.globalLayout.addItem(self.centerSpacerRight)

        # 右侧布局
        self.layout3 = QBoxLayout(QBoxLayout.LeftToRight)
        self.globalLayout.addLayout(self.layout3)
        self.update_window_position(self.alignment)

        # 菜单
        self.menu = QMenu()
        # 布局
        self.alignmentAction = QAction("窗口位置", self)
        self.alignmentMenu = self.menu.addMenu("窗口位置")
        self.alignmentAction.setMenu(self.alignmentMenu)
        self.alignmentMenu.addAction("Top", lambda: self.update_window_position("top"))
        self.alignmentMenu.addAction("Bottom", lambda: self.update_window_position("bottom"))
        self.alignmentMenu.addAction("Left", lambda: self.update_window_position("left"))
        self.alignmentMenu.addAction("Right", lambda: self.update_window_position("right"))
        # 添加布局
        self.addLayoutAction = QAction("添加布局", self)
        self.addLayoutMenu = self.menu.addMenu("添加布局")
        self.addLayoutAction.setMenu(self.addLayoutMenu)
        actionIcon = QPixmap(20, 20)
        actionIcon.fill(QColor(255, 127, 80))
        self.addLayoutMenu.addAction(actionIcon, 'Coral', lambda: self.addColorLayout("Coral"))
        actionIcon.fill(QColor(147, 112, 219))
        self.addLayoutMenu.addAction(actionIcon, 'MediumPurple', lambda: self.addColorLayout("MediumPurple"))
        actionIcon.fill(QColor(255, 150, 229))
        self.addLayoutMenu.addAction(actionIcon, 'Pink', lambda: self.addColorLayout("Pink"))
        # 关闭
        self.menu.addAction('关闭', self.close)

    def addNewButton(self, icon, size=32, dragMove=False):
        button = GIFButtonWidget(icon=icon, size=size, dragMove=dragMove)
        button.addDefaultMenuItems()
        return button

    def addColorLayout(self, color):
        '''
        color: str, 颜色 Coral
        '''
        colorDict = {
            "Coral": (255, 127, 80),
            "MediumPurple": (147, 112, 219),
            "Pink": (255, 150, 229)
        }
        if color not in colorDict:
            return
        color = colorDict[color]
        rgbColor = "rgb(%s, %s, %s)" % (color[0], color[1], color[2])
        opacityColor = "rgba(%s, %s, %s, 0.5)" % (color[0], color[1], color[2])
        colorWidget = QWidget()
        colorWidget.setMinimumSize(20, 42)
        colorWidget.setStyleSheet("""
            QWidget { 
                border: 2px solid %s; 
                border-radius: 8px; 
                background-color: %s; 
            }
        """ % (rgbColor, opacityColor))
        # 设置透明度
        #colorWidget.setWindowOpacity(0.5)
        # 移动角标
        tranSub = QLabel()
        tranSub.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
        tranSubImagr = QImage(ICONPATH + 'sub/tran.png')
        # 更改图片颜色
        newColor = QColor(color[0], color[1], color[2])
        for y in range(tranSubImagr.height()):
            for x in range(tranSubImagr.width()):
                color = tranSubImagr.pixelColor(x, y)
                alpha = color.alpha()
                if alpha > 0:
                    tranSubImagr.setPixelColor(x, y, newColor)
        tranSubImagr = QPixmap.fromImage(tranSubImagr)
        tranSub.setPixmap(tranSubImagr)

        if self.alignment == "top" or self.alignment == "bottom":
            colorLayout = QBoxLayout(QBoxLayout.RightToLeft)
            colorLayout.setAlignment(Qt.AlignRight|Qt.AlignCenter)
            colorWidget.setLayout(colorLayout)
            self.layout2.addWidget(colorWidget)
            #tranSub.setFixedSize(12, 38)
            colorLayout.addWidget(tranSub)
        elif self.alignment == "left" or self.alignment == "right":
            colorLayout = QBoxLayout(QBoxLayout.TopToBottom)
            colorLayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
            colorWidget.setLayout(colorLayout)
            self.layout2.addWidget(colorWidget)
            # 移动角标
            #tranSub.setFixedSize(38, 12)
            colorLayout.addWidget(tranSub)
        colorLayout.setSpacing(5)
        colorLayout.setContentsMargins(2, 2, 2, 2)
        
        colorWidget.menu = QMenu()
        colorWidget.menu.addAction('添加按钮', lambda: colorLayout.addWidget(self.addNewButton(ICONPATH + 'siri.gif', size=38, dragMove=False)))
        colorWidget.menu.addAction('删除', lambda: colorWidget.deleteLater())
        colorWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        colorWidget.customContextMenuRequested.connect(lambda: colorWidget.menu.exec_(QCursor.pos()))
        self.CoralLayout = colorLayout
        if color == "rgb(255, 127, 80)":
            self.CoralLayout = colorLayout
        elif color == "rgb(147, 112, 219)":
            self.MediumPurpleLayout = colorLayout
        elif color == "rgb(255, 150, 229)":
            self.PinkLayout = colorLayout
        return colorLayout

    # 右击显示菜单
    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def update_window_position(self, position):
        global_pos = self.MainPane.mapToGlobal(self.MainPane.rect().topLeft())
        if position == "top":
            self.setGeometry(global_pos.x() + 4, global_pos.y() + 53, self.MainPane.geometry().width() - 8, self.size)
            self.globalLayout.setDirection(QBoxLayout.LeftToRight)
            self.layout1.setDirection(QBoxLayout.LeftToRight)
            self.layout2.setDirection(QBoxLayout.LeftToRight)
            self.layout3.setDirection(QBoxLayout.LeftToRight)
            self.layout3.setAlignment(Qt.AlignRight)
        elif position == "bottom":
            self.setGeometry(global_pos.x() + 4, global_pos.y() + self.MainPane.geometry().height() - self.size - 6, self.MainPane.geometry().width() - 8, self.size)
            self.globalLayout.setDirection(QBoxLayout.LeftToRight)
            self.layout1.setDirection(QBoxLayout.LeftToRight)
            self.layout2.setDirection(QBoxLayout.LeftToRight)
            self.layout3.setDirection(QBoxLayout.LeftToRight)
            self.layout3.setAlignment(Qt.AlignRight)
        elif position == "left":
            self.setGeometry(global_pos.x() + 4, global_pos.y() + 53, self.size, self.MainPane.geometry().height() - 57)
            self.globalLayout.setDirection(QBoxLayout.TopToBottom)
            self.layout1.setDirection(QBoxLayout.TopToBottom)
            self.layout1.setAlignment(Qt.AlignTop)
            self.layout2.setDirection(QBoxLayout.TopToBottom)
            self.layout2.setAlignment(Qt.AlignCenter)
            self.layout3.setDirection(QBoxLayout.BottomToTop)
            self.layout3.setAlignment(Qt.AlignBottom)
        elif position == "right":
            self.setGeometry(global_pos.x() + self.MainPane.geometry().width() - self.size - 6, global_pos.y() + 53, self.size, self.MainPane.geometry().height() - 57)
            self.globalLayout.setDirection(QBoxLayout.TopToBottom)
            self.layout1.setDirection(QBoxLayout.TopToBottom)
            self.layout1.setAlignment(Qt.AlignTop)
            self.layout2.setDirection(QBoxLayout.TopToBottom)
            self.layout2.setAlignment(Qt.AlignCenter)
            self.layout3.setDirection(QBoxLayout.BottomToTop)
            self.layout3.setAlignment(Qt.AlignBottom)
        self.update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.update_window_position(self.alignment)
        #return super(MainPaneCtrl, self).eventFilter(obj, event)
        return False
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            if is_right_ctrl_pressed():
                self.background_opacity = 129
                self.update()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.background_opacity = 0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制半透明背景
        painter.setBrush(QColor(0, 0, 0, self.background_opacity))  # RGBA 颜色，最后一个参数是透明度
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)  # 绘制圆角矩形
        self.update()

def main():
    mainPaneCtrl = mainUI(alignment = "bottom")
    mainPaneCtrl.show()
    button1 = GIFButtonWidget(icon = ICONPATH + 'siri.gif', size=40, dragMove=False)
    button1.addDefaultMenuItems()
    mainPaneCtrl.layout1.addWidget(button1)
    button2 = GIFButtonWidget(icon = ICONPATH + 'siri.gif', size=40, dragMove=False)
    mainPaneCtrl.layout2.addWidget(button2)
    button2.addDefaultMenuItems()
    button3 = GIFButtonWidget(icon = ICONPATH + 'siri.gif', size=40, dragMove=False)
    mainPaneCtrl.layout3.addWidget(button3)
    button3.addDefaultMenuItems()