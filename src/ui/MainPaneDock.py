import os
import json
import codecs # 用于解决中文乱码问题
from collections import OrderedDict # 有序字典
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
from ..widgets import colorWidget
from ..utils import dragWidgetOrder
try:
    reload(colorWidget)
except:
    from importlib import reload
    reload(colorWidget)

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

from maya import cmds
class mainUI(QWidget):
    def __init__(self, parent=maya_main_window(),alignment = "bottom"):
        super().__init__(parent)
        # 检查是否已经创建了窗口
        if cmds.window('MainPaneCtrl', exists=True):
            cmds.deleteUI('MainPaneCtrl')
            if hasattr(self, 'MainPane'):
                self.MainPane.removeEventFilter(self)
        self.MainPane = mel.eval('string $temp = $gMainPane')
        self.MainPane = omui.MQtUtil.findLayout(self.MainPane)
        self.MainPane = wrapInstance(int(self.MainPane), QWidget)
        self.MainPane = self.MainPane.parent().parent()
        self.MainPane.installEventFilter(self)
        self.alignment = alignment # top, bottom, left, right 窗口停靠视图位置
        self.mPos = None
        self.background_opacity = 0
        self.size = 50
        self.setObjectName('MainPaneCtrl')
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 设置窗口透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)  # 设置窗口无边框
        self.setFocusPolicy(Qt.ClickFocus)
        self.colorWidgetDict = {}
        self.initUI(self.alignment)

    def initUI(self, position="bottom"):
        global_pos = self.MainPane.mapToGlobal(self.MainPane.rect().topLeft())
        # 设置按钮
        self.settingButton = GIFButtonWidget(icon = ICONPATH + 'white/Setting.png', size=38, dragMove=False)
        self.addSettingButton()
        if position == "top":
            self.alignment = "top"
            self.setGeometry(global_pos.x() + 4, global_pos.y() + 53, self.MainPane.geometry().width() - 8, self.size)
            # 全局布局
            self.globalLayout = QBoxLayout(QBoxLayout.LeftToRight)
            self.globalLayout.setSpacing(0)
            self.globalLayout.setContentsMargins(5, 5, 5, 5)
            self.setLayout(self.globalLayout)
            # 1
            self.layout1 = QBoxLayout(QBoxLayout.LeftToRight)
            self.layout1.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.globalLayout.addLayout(self.layout1)
            # 2
            self.layout2Widget = QWidget()
            self.layout2Widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout2Widget.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
            self.layout2 = QHBoxLayout()
            self.layout2Widget.setLayout(self.layout2)
            self.layout2.setAlignment(Qt.AlignCenter)
            self.layout2.setSpacing(20)
            self.layout2.setContentsMargins(0, 0, 0, 0)
            self.centerSpacerLeft = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.centerSpacerRight = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.globalLayout.addItem(self.centerSpacerLeft)
            self.globalLayout.addWidget(self.layout2Widget)
            self.globalLayout.addItem(self.centerSpacerRight)
            # 3
            self.layout3 = QBoxLayout(QBoxLayout.LeftToRight)
            self.layout3.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.globalLayout.addLayout(self.layout3)
            self.layout3.addWidget(self.settingButton)
        elif position == "bottom":
            self.alignment = "bottom"
            self.setGeometry(global_pos.x() + 4, global_pos.y() + self.MainPane.geometry().height() - self.size - 6, self.MainPane.geometry().width() - 8, self.size)
            # 全局布局
            self.globalLayout = QBoxLayout(QBoxLayout.LeftToRight)
            self.globalLayout.setSpacing(0)
            self.globalLayout.setContentsMargins(5, 5, 5, 5)
            self.setLayout(self.globalLayout)
            # 1
            self.layout1 = QBoxLayout(QBoxLayout.LeftToRight)
            self.layout1.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.globalLayout.addLayout(self.layout1)
            # 2
            self.layout2Widget = QWidget()
            self.layout2Widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout2Widget.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
            self.layout2 = QHBoxLayout()
            self.layout2Widget.setLayout(self.layout2)
            self.layout2.setAlignment(Qt.AlignCenter)
            self.layout2.setSpacing(20)
            self.layout2.setContentsMargins(0, 0, 0, 0)
            self.centerSpacerLeft = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.centerSpacerRight = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.globalLayout.addItem(self.centerSpacerLeft)
            self.globalLayout.addWidget(self.layout2Widget)
            self.globalLayout.addItem(self.centerSpacerRight)
            # 3
            self.layout3 = QBoxLayout(QBoxLayout.LeftToRight)
            self.layout3.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.globalLayout.addLayout(self.layout3)
            self.layout3.addWidget(self.settingButton)
        elif position == "left":
            self.alignment = "left"
            self.setGeometry(global_pos.x() + 4, global_pos.y() + 53, self.size, self.MainPane.geometry().height() - 57)
            # 全局布局
            self.globalLayout = QBoxLayout(QBoxLayout.TopToBottom)
            self.globalLayout.setSpacing(0)
            self.globalLayout.setContentsMargins(5, 5, 5, 5)
            self.setLayout(self.globalLayout)
            # 1
            self.layout1 = QBoxLayout(QBoxLayout.TopToBottom)
            self.layout1.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
            self.globalLayout.addLayout(self.layout1)
            self.layout1.addWidget(self.settingButton)
            # 2
            self.layout2Widget = QWidget()
            self.layout2Widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout2Widget.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
            self.layout2 = QVBoxLayout()
            self.layout2Widget.setLayout(self.layout2)
            self.layout2.setAlignment(Qt.AlignCenter|Qt.AlignHCenter)
            self.layout2.setSpacing(20)
            self.layout2.setContentsMargins(0, 0, 0, 0)
            self.centerSpacerTop = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.centerSpacerBottom = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.globalLayout.addItem(self.centerSpacerTop)
            self.globalLayout.addWidget(self.layout2Widget)
            self.globalLayout.addItem(self.centerSpacerBottom)
            # 3
            self.layout3 = QBoxLayout(QBoxLayout.BottomToTop)
            self.layout3.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)
            self.globalLayout.addLayout(self.layout3)
        elif position == "right":
            self.alignment = "right"
            self.setGeometry(global_pos.x() + self.MainPane.geometry().width() - self.size - 6, global_pos.y() + 53, self.size, self.MainPane.geometry().height() - 57)
            # 全局布局
            self.globalLayout = QBoxLayout(QBoxLayout.TopToBottom)
            self.globalLayout.setSpacing(0)
            self.globalLayout.setContentsMargins(5, 5, 5, 5)
            self.setLayout(self.globalLayout)
            # 1
            self.layout1 = QBoxLayout(QBoxLayout.TopToBottom)
            self.layout1.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
            self.globalLayout.addLayout(self.layout1)
            self.layout1.addWidget(self.settingButton)
            # 2
            self.layout2Widget = QWidget()
            self.layout2Widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout2Widget.setStyleSheet("background-color: rgba(0,0,0,0); border: none;")
            self.layout2 = QVBoxLayout()
            self.layout2Widget.setLayout(self.layout2)
            self.layout2.setAlignment(Qt.AlignCenter|Qt.AlignHCenter)
            self.layout2.setSpacing(20)
            self.layout2.setContentsMargins(0, 0, 0, 0)
            self.centerSpacerTop = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.centerSpacerBottom = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.globalLayout.addItem(self.centerSpacerTop)
            self.globalLayout.addWidget(self.layout2Widget)
            self.globalLayout.addItem(self.centerSpacerBottom)
            # 3
            self.layout3 = QBoxLayout(QBoxLayout.BottomToTop)
            self.layout3.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)
            self.globalLayout.addLayout(self.layout3)
        
        # 设置窗口透明
        self.background_opacity = 0
        self.settingButton.hide()

    def setAlignment(self, alignment):
        self.alignment = alignment
        self.close()
        see = mainUI(alignment = alignment)
        see.loadTools()
        see.show()
        
    def addSettingButton(self):
        # 菜单
        self.menu = QMenu()
        # 布局
        self.alignmentAction = QAction("窗口位置", self)
        self.alignmentMenu = self.menu.addMenu("窗口位置")
        self.alignmentAction.setMenu(self.alignmentMenu)
        self.alignmentMenu.addAction("Top", lambda: self.setAlignment("top"))
        self.alignmentMenu.addAction("Bottom", lambda: self.setAlignment("bottom"))
        self.alignmentMenu.addAction("Left", lambda: self.setAlignment("left"))
        self.alignmentMenu.addAction("Right", lambda: self.setAlignment("right"))
        # 添加布局
        self.addLayoutAction = QAction("添加布局", self)
        self.addLayoutMenu = self.menu.addMenu("添加布局")
        self.addLayoutAction.setMenu(self.addLayoutMenu)
        self.colorDict = {
            "Coral": (255, 127, 80), # 珊瑚色 #FF7F50
            "MediumPurple": (147, 112, 219), # 中紫色 #9370DB
            "Pink": (255, 150, 229), # 粉红色 #FF96E5
            "Turquoise": (64, 224, 208),  # 青绿色 #40E0D0
            "LightSkyBlue": (135, 206, 250), # 亮天蓝色 #87CEFA
            "IndianRed": (205, 92, 92) # 印度红色 #CD5C5C
        }
        for color in self.colorDict.keys():
            actionIcon = QPixmap(20, 20)
            actionIcon.fill(QColor(self.colorDict[color][0], self.colorDict[color][1], self.colorDict[color][2]))
            self.addLayoutMenu.addAction(actionIcon, color, lambda color=color: self.addColorLayout(color))
        # 关闭
        self.menu.addAction('关闭', self.close)
        # 按钮右击弹出菜单
        self.settingButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.settingButton.customContextMenuRequested.connect(self.showMenu)

    def showMenu(self, pos):
        self.menu.exec_(self.settingButton.mapToGlobal(pos))

    def addColorLayout(self, color):
        '''
        color: str, 颜色 Coral
        '''
        # 查询是否存在
        for i in range(self.layout2.count()):
            item = self.layout2.itemAt(i)
            if item.widget() is not None:
                if item.widget().objectName() == color+"Widget":
                    item.widget().show()
                    return
        if color not in self.colorDict:
            return
        self.colorWidgetDict[color] = colorWidget.ColorWidget(color=color, alignment=self.alignment)
        self.layout2.addWidget(self.colorWidgetDict[color])
        return self.colorWidgetDict[color]

    def update_window_position(self, alignment):
        global_pos = self.MainPane.mapToGlobal(self.MainPane.rect().topLeft())
        if alignment == "top":
            self.setGeometry(global_pos.x() + 4, global_pos.y() + 53, self.MainPane.geometry().width() - 8, self.size)
        elif alignment == "bottom":
            self.setGeometry(global_pos.x() + 4, global_pos.y() + self.MainPane.geometry().height() - self.size - 6, self.MainPane.geometry().width() - 8, self.size)
        elif alignment == "left":
            self.setGeometry(global_pos.x() + 4, global_pos.y() + 53, self.size, self.MainPane.geometry().height() - 57)
        elif alignment == "right":
            self.setGeometry(global_pos.x() + self.MainPane.geometry().width() - self.size - 6, global_pos.y() + 53, self.size, self.MainPane.geometry().height() - 57)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.update_window_position(self.alignment)
        #return super(MainPaneCtrl, self).eventFilter(obj, event)
        return False
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            if is_right_ctrl_pressed():
                if self.background_opacity == 0:
                    self.background_opacity = 100
                    self.settingButton.show()
                    self.update()
                    for i in range(self.layout2.count()):
                        item = self.layout2.itemAt(i)
                        if item.widget() is not None:
                            if "Widget" in item.widget().objectName():
                                item.widget().tranSub.show()
                                item.widget().background_opacity = 100
                                item.widget().border_opacity = 255
                                item.widget().update()
                else:
                    self.background_opacity = 0
                    self.update()
                    for i in range(self.layout2.count()):
                        item = self.layout2.itemAt(i)
                        self.settingButton.hide()
                        if item.widget() is not None:
                            if "Widget" in item.widget().objectName():
                                item.widget().tranSub.hide()
                                item.widget().background_opacity = 0
                                item.widget().border_opacity = 0
                                item.widget().update()

    # def keyReleaseEvent(self, event):
    #     for i in range(self.layout2.count()):
    #         item = self.layout2.itemAt(i)
    #         if item.widget() is not None:
    #             if "Widget" in item.widget().objectName():
    #                 item.widget().keyReleaseEvent(event)
    #     if event.key() == Qt.Key_Control:
    #         self.background_opacity = 0
    #         self.update()

    # def focusOutEvent(self, event):
    #     self.background_opacity = 0
    #     self.update()

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     # 绘制半透明背景
    #     painter.setBrush(QColor(0, 0, 0, self.background_opacity))  # RGBA 颜色，最后一个参数是透明度
    #     painter.setPen(Qt.NoPen)
    #     painter.drawRoundedRect(self.rect(), 15, 15)  # 绘制圆角矩形
    #     self.update()

    

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