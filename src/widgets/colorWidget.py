import os
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from functools import partial

from ..widgets.GIFWidget import GIFButtonWidget
from ..widgets.Separator import Separator
from ..utils import dragWidgetOrder

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

try:
    ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/widgets', 'icons/')
except:
    ICONPATH = 'E:/OneButtonManager/icons/'

class ColorWidget(QWidget):
    def __init__(self, parent=None, alignment = "bottom", color = "Coral"):
        super(ColorWidget, self).__init__(parent)
        self.alignment = alignment
        self.color = color
        self.background_opacity = 100
        self.border_opacity = 255
        self.setFocusPolicy(Qt.ClickFocus)
        self.setObjectName(self.color+"Widget")
        self.colorDict = {
            "Coral": (255, 127, 80), # 珊瑚色 #FF7F50
            "MediumPurple": (147, 112, 219), # 中紫色 #9370DB
            "Pink": (255, 150, 229), # 粉红色 #FF96E5
            "Turquoise": (64, 224, 208),  # 青绿色 #40E0D0
            "LightSkyBlue": (135, 206, 250), # 亮天蓝色 #87CEFA
            "IndianRed": (205, 92, 92) # 印度红色 #CD5C5C
        }
        self.initUI()
        self.createColorWidget()
        self.careateMenu()
        dragWidgetOrder.DragWidgetOrder(self)

    def initUI(self):
        if self.alignment == "bottom" or self.alignment == "top":
            self.setMinimumSize(20, 42)
            self.mainLayout = QBoxLayout(QBoxLayout.RightToLeft)
        elif self.alignment == "left" or self.alignment == "right":
            self.setMinimumSize(42, 20)
            self.mainLayout = QBoxLayout(QBoxLayout.BottomToTop)
        self.mainLayout.setSpacing(2)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.mainLayout)

    def createColorWidget(self):
        '''
        tranSub: QLabel 移动角标
        self.colorWidget: 存放按钮的组件 self.colorWidget.layout() 获取布局
        self.colorLayout: 存放自定义按钮或其他组件的布局
        '''
        # 移动角标
        self.tranSub = QLabel()
        self.tranSub.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
        if self.alignment == "top" or self.alignment == "bottom":
            tranSubImagr = QImage(ICONPATH + 'sub/tran.png')
        elif self.alignment == "left" or self.alignment == "right":
            tranSubImagr = QImage(ICONPATH + 'sub/tranV.png')
        # 更改图片颜色
        newColor = QColor(self.colorDict[self.color][0], self.colorDict[self.color][1], self.colorDict[self.color][2])
        for y in range(tranSubImagr.height()):
            for x in range(tranSubImagr.width()):
                imageColor = tranSubImagr.pixelColor(x, y)
                alpha = imageColor.alpha()
                if alpha > 0:
                    tranSubImagr.setPixelColor(x, y, newColor)
        tranSubImagr = QPixmap.fromImage(tranSubImagr)
        self.tranSub.setPixmap(tranSubImagr)
         # 存放按钮的组件
        self.colorWidget = QWidget()
        self.colorWidget.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
        if self.alignment == "top" or self.alignment == "bottom":
            # 功能角标
            self.mainLayout.addWidget(self.tranSub)
            # 组件布局
            self.colorLayout = QHBoxLayout()
            self.colorWidget.setLayout(self.colorLayout)
            self.colorLayout.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.mainLayout.addWidget(self.colorWidget)
        elif self.alignment == "left" or self.alignment == "right":
            # 功能角标
            self.mainLayout.addWidget(self.tranSub)
            # 组件布局
            self.colorLayout = QVBoxLayout()
            self.colorWidget.setLayout(self.colorLayout)
            self.colorLayout.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
            self.mainLayout.addWidget(self.colorWidget)
        self.colorLayout.setSpacing(0)
        self.colorLayout.setContentsMargins(0, 0, 0, 0)

    def addSeparator(self):
        if self.alignment == "bottom" or self.alignment == "top":
            alignment = 'H'
        elif self.alignment == "left" or self.alignment == "right":
            alignment = 'V'
        separator = Separator(size=30, alignment=alignment, color=(self.colorDict[self.color][0], self.colorDict[self.color][1], self.colorDict[self.color][2], 255))
        self.colorLayout.addWidget(separator, 0, Qt.AlignCenter)
        if alignment == 'H': separator.setFixedSize(20, 24)
        elif alignment == 'V': separator.setFixedSize(24, 20)
        
    def careateMenu(self):
        self.menu = QMenu()
        if self.alignment == "bottom" or self.alignment == "top":
            alignment = 'H'
        elif self.alignment == "left" or self.alignment == "right":
            alignment = 'V'
        def addNewButton():
            button = GIFButtonWidget(icon=ICONPATH + 'siri.gif', size=38, dragMove=True, tearOff=False, alignment=alignment)
            button.addDefaultMenuItems()
            self.colorLayout.addWidget(button)
        self.menu.addAction('添加按钮', lambda: addNewButton())

        self.menu.addAction('添加分割线', lambda: self.addSeparator())
        self.menu.addAction('删除', lambda: self.hide())
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda: self.menu.exec_(QCursor.pos()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制半透明背景
        painter.setBrush(QColor(self.colorDict[self.color][0], self.colorDict[self.color][1], self.colorDict[self.color][2], self.background_opacity))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        # 绘制边框
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor(self.colorDict[self.color][0], self.colorDict[self.color][1], self.colorDict[self.color][2], self.border_opacity))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)