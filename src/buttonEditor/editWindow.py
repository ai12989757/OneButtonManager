# -*- coding: utf-8 -*-
import os
import sys
import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

from pymel.core import *
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from functools import partial
from collections import OrderedDict

from widgets import GIFButton
try:
    reload(GIFButton)
except:
    from importlib import reload
    reload(GIFButton)

from buttonEditor.KeywordHighlighter import *
from switchLanguage import *

iconPath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src/buttonEditor', 'icons/')

# 创建一个按钮编辑器窗口
def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class ButtonEditorWindow(QDialog):
    def __init__(self, editButton, language, parent=maya_main_window()):
        super(ButtonEditorWindow, self).__init__(parent)
        self.editButton = editButton
        self.language = language
        self.tempIcon = os.path.join(iconPath, "white/loading.gif")

        self.setWindowTitle(sl(u"OneButton编辑器", self.language))
        self.setWindowFlags(Qt.Window)
        self.setObjectName("ButtonEditorWindow")
        self.resize(800, 900)
        self.iconPathDrt = iconPath.replace('\\', '/').replace('src/../', '')

        # 创建一个整体垂直布局
        self.globalLayout = QVBoxLayout(Alignment=Qt.AlignTop)
        self.setLayout(self.globalLayout)

        # 布局第一行 图标 和 图标参数
        self.iconLayout = QHBoxLayout(Alignment=Qt.AlignTop)
        self.globalLayout.addLayout(self.iconLayout)

        # 图标
        self.buttonDict = {
            'icon': self.editButton.icon,
            'label': self.editButton.label,
            'annotation': self.editButton.annotation,
            'style': self.editButton.style,
            'sourceType': self.editButton.sourceType,
            'command': self.editButton.command,
            'doubleClickCommandSourceType': self.editButton.doubleClickCommandSourceType,
            'doubleClickCommand': self.editButton.doubleClickCommand,
            'ctrlCommand': self.editButton.ctrlCommand,
            'altCommand': self.editButton.altCommand,
            'shiftCommand': self.editButton.shiftCommand,
            'ctrlAltCommand': self.editButton.ctrlAltCommand,
            'altShiftCommand': self.editButton.altShiftCommand,
            'ctrlShiftCommand': self.editButton.ctrlShiftCommand,
            'ctrlAltShiftCommand': self.editButton.ctrlAltShiftCommand,
            'dragCommand': self.editButton.dragCommand,
            'altDragCommand': self.editButton.altDragCommand,
            'shiftDragCommand': self.editButton.shiftDragCommand,
            'ctrlDragCommand': self.editButton.ctrlDragCommand,
            'menuShowCommand': self.editButton.menuShowCommand
        }
        self.gifButton = GIFButton.GIFButton(icon=self.buttonDict['icon'], 
                                   label=self.buttonDict['label'], 
                                   annotation=self.buttonDict['annotation'], 
                                   style=self.buttonDict['style'], 
                                   sourceType=self.buttonDict['sourceType'], 
                                   command=self.buttonDict['command'], 
                                   doubleClickCommandSourceType=self.buttonDict['doubleClickCommandSourceType'], 
                                   doubleClickCommand=self.buttonDict['doubleClickCommand'], 
                                   ctrlCommand=self.buttonDict['ctrlCommand'], 
                                   altCommand=self.buttonDict['altCommand'], 
                                   shiftCommand=self.buttonDict['shiftCommand'], 
                                   ctrlAltCommand=self.buttonDict['ctrlAltCommand'], 
                                   altShiftCommand=self.buttonDict['altShiftCommand'], 
                                   ctrlShiftCommand=self.buttonDict['ctrlShiftCommand'], 
                                   ctrlAltShiftCommand=self.buttonDict['ctrlAltShiftCommand'], 
                                   dragCommand=self.buttonDict['dragCommand'], 
                                   altDragCommand=self.buttonDict['altDragCommand'], 
                                   shiftDragCommand=self.buttonDict['shiftDragCommand'], 
                                   ctrlDragCommand=self.buttonDict['ctrlDragCommand'],
                                   menuShowCommand=self.buttonDict['menuShowCommand'],
                                   size=128,
                                   language=self.language
                                   )
                                   
        # 断开所有gifIconMenuAction的movie
        for acticon in self.gifButton.menu.actions():
            if acticon.isSeparator():
                pass
            else:
                if acticon.movie:
                    pass
                    #print(acticon.movie)
                    # acticon.movie.frameChanged.disconnect(None, None, None)
                    # acticon.movie.stop()
                    # acticon.movie = None
                    
        #self.gifButton.setFixedSize(QSize(128, 128))
        self.iconLayout.addWidget(self.gifButton)
        self.menuItems =  OrderedDict()
        self.menuItemIndex = 0

        # 从当前图标获取菜单项
        for acticon in self.editButton.menu.actions():
            if acticon.isSeparator():
                pass
            else:
                label = acticon.text()
                if label not in  [sl(u'编辑',self.language), sl(u'删除',self.language)]:
                    self.menuItems[self.menuItemIndex] = {
                        "label": label if hasattr(acticon, 'text') else None,
                        "sourceType": acticon.sourceType if hasattr(acticon, 'sourceType') else "python",
                        "command": acticon.command if hasattr(acticon, 'command') else None,
                        "icon": acticon.iconPath if hasattr(acticon, 'iconPath') else None,
                        "annotation": acticon.annotation if hasattr(acticon, 'annotation') else None
                    }
                self.menuItemIndex += 1
        # 预览按钮添加菜单项
        for key in self.menuItems.keys():
            menuItem = self.menuItems[key]
            self.gifButton.addMenuItem(
                label=menuItem["label"],
                sourceType=menuItem["sourceType"],
                command=menuItem["command"],
                icon=menuItem["icon"],
                annotation=menuItem["annotation"]
            )
            
        # 图标参数布局
        self.iconParamLayout = QVBoxLayout()
        self.iconLayout.addLayout(self.iconParamLayout)

        # 图标标签 标签 输入框
        self.iconLabelLayout = QHBoxLayout()
        self.iconLabel = QLabel(sl(u"名称:", self.language))
        self.iconLabelLineEdit = QLineEdit()
        self.iconLabelLineEdit.setText(self.gifButton.label)
        self.iconLabelLayout.addWidget(self.iconLabel)
        self.iconLabelLayout.addWidget(self.iconLabelLineEdit)
        self.iconParamLayout.addLayout(self.iconLabelLayout)
        # 图标路径 图标 输入框 按钮
        self.iconPathLayout = QHBoxLayout()
        self.iconPathLabel = QLabel(sl(u"路径:", self.language))
        self.iconPathLineEdit = QLineEdit()
        # D:\MELcopy\OneTools\src\../icons/
        self.iconPathLineEdit.setText(self.gifButton.icon.replace(iconPath, '')) 
        self.iconPathButton = QPushButton()
        # 设置图标图片
        self.iconPathButton.setIcon(QIcon(iconPath+"white/OpenFile.png"))
        # 设置按钮大小
        self.iconPathButton.setIconSize(QSize(24, 24))
        self.iconPathButton.setStyleSheet("""QPushButton {background-color: rgba(0, 0, 0, 0);border: none;}""")
        self.iconPathButton.clicked.connect(self.browseIconPath)
        self.iconPathButton.enterEvent = lambda event: self.showMenuIconBorder(self.iconPathButton, event)
        self.iconPathButton.leaveEvent = lambda event: self.hideMenuIconBorder(self.iconPathButton, event)
        self.iconPathLayout.addWidget(self.iconPathLabel)
        self.iconPathLayout.addWidget(self.iconPathLineEdit)
        self.iconPathLayout.addWidget(self.iconPathButton)
        self.iconParamLayout.addLayout(self.iconPathLayout)
        # 图标风格 三个单选按钮
        self.iconStyleLayout = QHBoxLayout()
        self.iconStyleLabel = QLabel(sl(u"动画:", self.language))
        self.iconStyleAuto = QRadioButton(sl(u"循环播放", self.language))
        # 连接点击事件
        self.iconStyleAuto.clicked.connect(lambda: self.iconStyleChanged('auto'))
        if self.gifButton.style == "auto":
            self.iconStyleAuto.setChecked(True)
        self.iconStyleHover = QRadioButton(sl(u"离开停止", self.language))
        self.iconStyleHover.clicked.connect(lambda: self.iconStyleChanged('hover'))
        if self.gifButton.style == "hover":
            self.iconStyleHover.setChecked(True)
        self.iconStylePause = QRadioButton(sl(u"离开暂停", self.language))
        self.iconStylePause.clicked.connect(lambda: self.iconStyleChanged('pause'))
        if self.gifButton.style == "pause":
            self.iconStylePause.setChecked(True)
        # 如果 不是 GIF 图片，则禁用动画按钮
        if not self.gifButton.icon.lower().endswith('.gif'):
            self.iconStyleAuto.setEnabled(False)
            self.iconStyleHover.setEnabled(False)
            self.iconStylePause.setEnabled(False)
        self.iconStyleLayout.addWidget(self.iconStyleLabel)
        self.iconStyleLayout.addWidget(self.iconStyleAuto)
        self.iconStyleLayout.addWidget(self.iconStyleHover)
        self.iconStyleLayout.addWidget(self.iconStylePause)
        self.iconParamLayout.addLayout(self.iconStyleLayout)
        # 图标注释 标签 输入框
        self.iconAnnotationLayout = QHBoxLayout()
        self.iconAnnotationLabel = QLabel(sl(u"提示:", self.language))
        self.iconAnnotationLineEdit = QTextEdit()
        # 设置高度为两行
        self.iconAnnotationLineEdit.setFixedHeight(52)
        # 设置文本更改信号
        self.iconAnnotationLineEdit.textChanged.connect(self.iconAnnotationChanged)
        self.iconAnnotationLineEdit.setText(self.gifButton.annotation)
        self.iconAnnotationLayout.addWidget(self.iconAnnotationLabel, 0, Qt.AlignTop)
        self.iconAnnotationLayout.addWidget(self.iconAnnotationLineEdit)
        self.iconParamLayout.addLayout(self.iconAnnotationLayout)

        # 命令参数布局
        self.commandLayout = QHBoxLayout()
        # 向上对齐 iconLayout
        self.commandLayout.setAlignment(Qt.AlignTop)
        self.globalLayout.addLayout(self.commandLayout,stretch=1)
        self.commandTabWidget = QTabWidget()
        self.commandLayout.addWidget(self.commandTabWidget)
        # 命令布局，左边是命令列表，右边是命令输入框
        self.commandTab = QWidget()
        self.commandLayout = QHBoxLayout()
        self.commandListLayout = QVBoxLayout()
        self.commandLayout.addLayout(self.commandListLayout)
        # 命令布局
        self.commandTab.setLayout(self.commandLayout)
        self.commandTabWidget.addTab(self.commandTab, sl(u"点击命令", self.language))

        # 添加一个左右分区可以拖动调节的分区
        self.splitter = QSplitter(Qt.Horizontal)
        self.commandListLayout.addWidget(self.splitter)
        # 创建一个命令列表
        self.commandListWidget = QListWidget()
        self.splitter.addWidget(self.commandListWidget)
        self.commandListWidget.addItem(sl(u"点击命令", self.language))
        self.commandListWidget.addItem(sl(u"双击命令", self.language))
        self.commandListWidget.addItem(sl(u"Ctrl单击", self.language))
        self.commandListWidget.addItem(sl(u"Alt单击", self.language))
        self.commandListWidget.addItem(sl(u"Shift单击", self.language))
        self.commandListWidget.addItem(sl(u"Ctrl+Alt单击", self.language))
        self.commandListWidget.addItem(sl(u"Ctrl+Shift单击", self.language))
        self.commandListWidget.addItem(sl(u"Alt+Shift单击", self.language))
        self.commandListWidget.addItem(sl(u"Ctrl+Alt+Shift单击", self.language))
        self.commandListWidget.addItem(sl(u"左击拖动", self.language))
        self.commandListWidget.addItem(sl(u"Ctrl左击拖动", self.language))
        self.commandListWidget.addItem(sl(u"Alt左击拖动", self.language))
        self.commandListWidget.addItem(sl(u"Shift左击拖动", self.language))

        self.commandEditWidget = QWidget()
        self.commandEditLayout = QVBoxLayout()
        self.commandEditWidget.setLayout(self.commandEditLayout)
        self.commandTypeLayout = QHBoxLayout()
        self.commandEditLayout.addLayout(self.commandTypeLayout)
        self.commandTypeLabel = QLabel(sl(u"语言:", self.language))
        self.commandPythonRadioButton = QRadioButton(u"Python")
        self.commandPythonRadioButton.clicked.connect(self.editCommandType)
        self.commandMelRadioButton = QRadioButton(u"Mel")
        self.commandMelRadioButton.clicked.connect(self.editCommandType)
        self.commandTypeLayout.addWidget(self.commandTypeLabel)
        self.commandTypeLayout.addWidget(self.commandPythonRadioButton)
        self.commandTypeLayout.addWidget(self.commandMelRadioButton)
        
        #self.commandLayout.addLayout(self.commandEditLayout)
        # 创建一个命令输入框
        self.commandEdit = QTextEdit()
        self.commandEditLayout.addWidget(self.commandEdit)
        self.commandEdit.textChanged.connect(self.editCommand)
        # 菜单参数布局
        self.menuLayout = QHBoxLayout()
        self.globalLayout.addLayout(self.menuLayout)
        self.menuCommandEdit = QTextEdit()  # Ensure menuEdit is defined
        self.highlighter = KeywordHighlighter(self.commandEdit.document())
        # 不自动换行
        self.commandEdit.setLineWrapMode(QTextEdit.NoWrap)
        # 按下Tab键时不插入制表符，而是输入4个空格
        # 安装事件过滤器，用于代码编辑器TAB改为4个空格
        self.commandEdit.installEventFilter(self)
        #self.commandEdit.setTabChangesFocus(False)
        self.splitter.addWidget(self.commandEditWidget)
        # 当命令列表改变时，更新命令输入框
        self.commandListWidget.currentRowChanged.connect(self.updateCommandEdit)
        # splitter 左30% 右70%
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 7)

        # 菜单布局，左边是菜单图标、菜单控制按钮、菜单列表，右边是语言选择、菜单提示、菜单命令输入框
        self.menuTab = QWidget()
        self.menuLayout = QHBoxLayout()
        self.menuListLayout = QVBoxLayout()
        self.menuLayout.addLayout(self.menuListLayout)

        # 菜单布局
        self.menuTab.setLayout(self.menuLayout)
        self.commandTabWidget.addTab(self.menuTab, sl(u"右击菜单", self.language))
        # 添加一个左右分区可以拖动调节的分区
        self.menuSplitter = QSplitter(Qt.Horizontal)
        self.menuListLayout.addWidget(self.menuSplitter)
        # 创建一个菜单列表
        self.menuListLeftWidget = QWidget() # 菜单命令列表总体布局
        self.menuIconLayout = QHBoxLayout() # 菜单命令列表按钮布局
        self.menuListLeftLayout = QVBoxLayout() # 菜单命令列表总体布局
        self.menuListLeftWidget.setLayout(self.menuListLeftLayout)
        self.menuIconEditLayoutAll = QHBoxLayout() # 菜单图标编辑总体布局 左边一个图标 右边三行
        self.menuIconEditLayout = QVBoxLayout() # 菜单图标编辑布局 存放单个图标
        self.menuListLeftLayout.addLayout(self.menuIconEditLayoutAll)
        self.menuIconEditLayoutAll.addLayout(self.menuIconEditLayout)
        self.menuIconButton = QPushButton()
        self.menuIconButton.setFixedSize(QSize(42, 42))
        self.menuIconButton.setIconSize(QSize(42, 42))
        self.setMenuIcon(self.tempIcon) # 默认图标
        self.menuIconButton.setStyleSheet("""QPushButton {background-color: rgba(0, 0, 0, 0);border: none;}""")
        # 连接单击事件
        self.menuIconButton.mouseDoubleClickEvent = self.browseMenuIcon # 双击图标时更改图标
        self.menuIconButton.enterEvent = lambda event: self.showMenuIconBorder(self.menuIconButton, event)
        self.menuIconButton.leaveEvent = lambda event: self.hideMenuIconBorder(self.menuIconButton, event)
        self.menuIconButton.setStatusTip(sl(u'双击更改图标', self.language))
        self.menuIconEditLayout.addWidget(self.menuIconButton)
        self.menuIconRightLayout = QVBoxLayout() # 菜单图标布局 右侧放置三行
        self.menuIconEditLayoutAll.addLayout(self.menuIconRightLayout)

        self.menuIconLayout1 = QHBoxLayout() # 第一行菜单命令列表按钮布局 上移 下移 添加 删除
        # 设置向右对齐
        self.menuIconLayout1.setAlignment(Qt.AlignRight|Qt.AlignBottom)
        self.menuIconEditLayoutAll.addLayout(self.menuIconLayout1)
        # 添加菜单按钮 上移 下移 添加 删除
        self.menuUpButton = QPushButton()
        self.menuUpButton.setIcon(QIcon(":\\moveLayerUp.png"))
        self.menuUpButton.setFixedSize(QSize(14, 24))
        self.menuUpButton.setStyleSheet("""QPushButton {border: none;}""")
        self.menuUpButton.clicked.connect(self.moveMenuItemUp)
        self.menuUpButton.enterEvent = lambda event: self.showMenuIconBorder(self.menuUpButton, event) # 光标进入时显示描边效果
        self.menuUpButton.leaveEvent = lambda event: self.hideMenuIconBorder(self.menuUpButton,event) # 光标离开时隐藏描边效果
        self.menuDownButton = QPushButton()
        self.menuDownButton.setIcon(QIcon(":\\moveLayerDown.png"))
        self.menuDownButton.setFixedSize(QSize(14, 24))
        self.menuDownButton.setStyleSheet("""QPushButton {border: none;}""")
        self.menuDownButton.clicked.connect(self.moveMenuItemDown)
        self.menuDownButton.enterEvent = lambda event: self.showMenuIconBorder(self.menuDownButton, event)
        self.menuDownButton.leaveEvent = lambda event: self.hideMenuIconBorder(self.menuDownButton, event)
        self.menuAddButton = QPushButton()
        self.menuAddButton.setIcon(QIcon(":\\newLayerEmpty.png"))
        self.menuAddButton.setFixedSize(QSize(14, 24))
        self.menuAddButton.setStyleSheet("""QPushButton {border: none;}""")
        self.menuAddButton.clicked.connect(self.addMenuItem)
        self.menuAddButton.enterEvent = lambda event: self.showMenuIconBorder(self.menuAddButton, event)
        self.menuAddButton.leaveEvent = lambda event: self.hideMenuIconBorder(self.menuAddButton, event)
        self.menuRemoveButton = QPushButton()
        self.menuRemoveButton.setIcon(QIcon(":\\delete.png"))
        self.menuRemoveButton.setFixedSize(QSize(14, 24))
        self.menuRemoveButton.clicked.connect(self.removeMenuItem)
        self.menuRemoveButton.enterEvent = lambda event: self.showMenuIconBorder(self.menuRemoveButton, event)
        self.menuRemoveButton.leaveEvent = lambda event: self.hideMenuIconBorder(self.menuRemoveButton, event)
        self.menuRemoveButton.setStyleSheet("""QPushButton {border: none;}""")
        self.menuIconLayout1.addWidget(self.menuUpButton)
        self.menuIconLayout1.addWidget(self.menuDownButton)
        self.menuIconLayout1.addWidget(self.menuAddButton)
        self.menuIconLayout1.addWidget(self.menuRemoveButton)

        self.menuListWidget = QListWidget() # 菜单命令列表
        self.menuListLeftLayout.addWidget(self.menuListWidget)
        self.menuSplitter.addWidget(self.menuListLeftWidget)
        # 创建一个菜单输入框
        #self.menuCommandEdit = QTextEdit()
        # 高亮显示 self.keywords[] 中的关键字
        self.highlighter = KeywordHighlighter(self.menuCommandEdit.document())
        # 不自动换行
        self.menuCommandEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.menuCommandEdit.textChanged.connect(self.editMenuCommand)
        # 按下Tab键时不插入制表符，而是输入4个空格
        # 事件过滤器，用于代码编辑器TAB改为4个空格
        # 切换Tab时移除事件过滤器 commandTabWidgetChanged
        self.commandTabWidget.currentChanged.connect(self.commandTabWidgetChanged)
        #self.menuCommandEdit.setTabChangesFocus(False)
        self.menuCommandEditWidget = QWidget()
        self.menuCommandEditLayout = QVBoxLayout()

        self.menuCommandEditWidget.setLayout(self.menuCommandEditLayout)
        self.menuTypeLayout = QHBoxLayout()
        self.menuCommandEditLayout.addLayout(self.menuTypeLayout)
        self.menuTypeLabel = QLabel(sl(u"语言:", self.language))
        self.menuPythonRadioButton = QRadioButton(u"Python")
        self.menuPythonRadioButton.clicked.connect(self.editMenuCommandType)
        self.menuMelRadioButton = QRadioButton(u"Mel")
        self.menuMelRadioButton.clicked.connect(self.editMenuCommandType)
        self.menuTypeLayout.addWidget(self.menuTypeLabel)
        self.menuTypeLayout.addWidget(self.menuPythonRadioButton)
        self.menuTypeLayout.addWidget(self.menuMelRadioButton)

        self.menuAnnotationLayout = QHBoxLayout() # 第一行菜单命令列表按钮布局 存放 注释: 注释输入框
        self.menuCommandEditLayout.addLayout(self.menuAnnotationLayout)
        self.menuAnnotationLabel = QLabel(sl(u"提示:", self.language))
        self.menuAnnotationLineEdit = QLineEdit()
        self.menuAnnotationLineEdit.setPlaceholderText(sl(u"请输入菜单提示", self.language))
        # 设置文本更改信号
        self.menuAnnotationLineEdit.textChanged.connect(self.editMenuAnnotation)
        self.menuAnnotationLayout.addWidget(self.menuAnnotationLabel)
        self.menuAnnotationLayout.addWidget(self.menuAnnotationLineEdit)
        self.menuCommandEditLayout.addWidget(self.menuCommandEdit)
        self.menuSplitter.addWidget(self.menuCommandEditWidget)
        # splitter 左30% 右70%
        self.menuSplitter.setStretchFactor(0, 3)
        self.menuSplitter.setStretchFactor(1, 7)
        # # 添加菜单项
        for key in self.menuItems.keys():
            menuItem = self.menuItems[key]
            if menuItem != 'Separator':
                self.menuListWidget.addItem(menuItem["label"])
        self.menuListWidget.addItem(sl(u'菜单显示时执行的命令', self.language))

        self.menuListWidget.currentRowChanged.connect(self.updateMenuEdit)
        # 双击菜单项时更新菜单输入框，双击时编辑菜单项名称
        self.menuListWidget.itemDoubleClicked.connect(self.editMenuName)

        # 应用布局
        self.applyLayout = QHBoxLayout()
        # 应用按钮
        self.applyButton = QPushButton(sl(u"应用", self.language))
        self.applyButton.clicked.connect(lambda: self.applyEditButton(False))
        # 应用并关闭按钮
        self.applyCloseButton = QPushButton(sl(u"应用并关闭", self.language))
        self.applyCloseButton.clicked.connect(lambda: self.applyEditButton(True))
        # 关闭按钮
        self.closeButton = QPushButton(sl(u"关闭", self.language))
        self.closeButton.clicked.connect(self.close)

        self.applyLayout.addWidget(self.applyButton)
        self.applyLayout.addWidget(self.applyCloseButton)
        self.applyLayout.addWidget(self.closeButton)
        self.globalLayout.addLayout(self.applyLayout)
                                     
    def editMenuCommandType(self):
        row = self.menuListWidget.currentRow()
        if row == -1 or row not in self.menuItems:
            return
        menuItem = self.menuItems[row]
        if self.menuPythonRadioButton.isChecked():
            menuItem['sourceType'] = "python"
        elif self.menuMelRadioButton.isChecked():
            menuItem['sourceType'] = "mel"
        # 更新字典
        self.menuItems[row] = menuItem
        self.buttonDict["menuItems"] = self.menuItems

        self.updataMenuAction()

    def editMenuCommand(self):
        row = self.menuListWidget.currentRow()
        if row == -1:
            return
        
        command = self.menuCommandEdit.toPlainText()
        if row == self.menuListWidget.count() - 1:
            self.buttonDict['menuShowCommand'] = command
            self.gifButton.menuShowCommand = command
            
        try:
            menuItem = self.menuItems[row]
        except:
            return
        # 更新字典
        menuItem['command'] = command
        self.menuItems[row] = menuItem
        self.buttonDict["menuItems"] = self.menuItems

        self.updataMenuAction()
    
    def editMenuAnnotation(self):
        # 应用菜单的注释
        annotation = self.menuAnnotationLineEdit.text()
        self.menuIconButton.setStatusTip(annotation)
        # 获取当前选中的菜单项
        row = self.menuListWidget.currentRow()
        if row != -1 and row != self.menuListWidget.count() - 1:
            menuItem = self.menuItems[row]
            # 更新字典
            menuItem['annotation'] = annotation
            self.menuItems[row] = menuItem
            self.buttonDict["menuItems"] = self.menuItems
            self.updataMenuAction()

    def updateMenuEdit(self, row):
        if row == -1:
            return
        if row == self.menuListWidget.count() - 1:
            self.setMenuIcon('white/Edit_popupMenu.png')
            self.menuPythonRadioButton.setChecked(True)
            self.menuPythonRadioButton.setEnabled(False)
            self.menuMelRadioButton.setChecked(False)
            self.menuMelRadioButton.setEnabled(False)
            self.menuAnnotationLineEdit.setText(sl(u'当菜单弹出前执行命令，一般用于更新菜单项', self.language))
            self.menuAnnotationLineEdit.setEnabled(False)
            if self.buttonDict['menuShowCommand']:
                self.menuCommandEdit.setText(self.buttonDict['menuShowCommand'])
            else:
                self.menuCommandEdit.setText('')
                self.menuCommandEdit.setPlaceholderText(sl(u"请输入命令", self.language))
            return
        try:
            menuItem = self.menuItems[row]
        except:
            return
        # 设置菜单图标
        menuIcon = menuItem["icon"]
        if menuIcon:
            self.setMenuIcon(menuIcon)
        else:
            self.setMenuIcon(self.tempIcon)
        # 设置菜单注释
        self.menuAnnotationLineEdit.setEnabled(True)
        menuAnnotation = menuItem["annotation"]
        if menuAnnotation:
            self.menuAnnotationLineEdit.setText(menuAnnotation)
            self.menuIconButton.setStatusTip(menuAnnotation)
        else:
            self.menuAnnotationLineEdit.setText('')
            # 设置占位文本
            self.menuAnnotationLineEdit.setPlaceholderText(sl(u"请输入菜单提示", self.language))
            self.menuIconButton.setStatusTip('')
        
        # 设置菜单命令
        self.menuPythonRadioButton.setEnabled(True)
        self.menuMelRadioButton.setEnabled(True)
        commandType = menuItem["sourceType"]
        if commandType == "python" or commandType == "mel":
            self.menuMelRadioButton.setChecked(commandType == "mel")
            self.menuPythonRadioButton.setChecked(commandType == "python")
        
        # 获取python版本
        pythonVersion = int(sys.version[0:1])
        commandText = menuItem['command']
        if commandText != 'None' and commandText != '' and commandText is not None:
            if pythonVersion < 3:
                try:
                    commandText = commandText.decode('utf-8')
                except:
                    pass
        
            if "mel.eval(" in commandText:
                commandText = commandText.replace("mel.eval('", "")[:-2]

            self.menuCommandEdit.setText(commandText)
        else:
            self.menuCommandEdit.setText('')
            self.menuCommandEdit.setPlaceholderText(sl(u"请输入命令", self.language))

    def updataMenuAction(self):
        # 设置菜单 # 移除所有菜单后重新添加
        self.gifButton.menu.clear()
        for key in self.menuItems.keys():
            if key == 'Separator':
                self.gifButton.menu.addSeparator()
            else:
                menuItem = self.menuItems[key]
                self.gifButton.addMenuItem(
                    label=menuItem["label"],
                    sourceType=menuItem["sourceType"],
                    command=menuItem["command"],
                    icon=menuItem["icon"],
                    annotation=menuItem["annotation"]
                )
    
    def moveMenuItemUp(self):
        row = self.menuListWidget.currentRow()
        if row == -1 or row == 0 or row == self.menuListWidget.count() - 1:
            return
        # 交换两个菜单项
        self.menuItems[row], self.menuItems[row - 1] = self.menuItems[row - 1], self.menuItems[row]
        # 重新排序
        tempDict = OrderedDict()
        for key in range(len(self.menuItems.keys())):
            tempDict[key] = self.menuItems[key]
        self.menuItems = tempDict
        # 更新菜单
        self.updataMenuAction()
        self.menuListWidget.setCurrentRow(row - 1)
        # 更新菜单参数
        self.updateMenuEdit(row - 1)
        # 更新菜单显示名称
        self.menuListWidget.item(row).setText(self.menuItems[row]["label"])
        self.menuListWidget.item(row - 1).setText(self.menuItems[row - 1]["label"])

    def moveMenuItemDown(self):
        row = self.menuListWidget.currentRow()
        if row == -1 or row == self.menuListWidget.count() - 1 or row == self.menuListWidget.count() - 2:
            return
        # 交换两个菜单项
        self.menuItems[row], self.menuItems[row + 1] = self.menuItems[row + 1], self.menuItems[row]
        # 重新排序
        tempDict = OrderedDict()
        for key in range(len(self.menuItems.keys())):
            tempDict[key] = self.menuItems[key]
        self.menuItems = tempDict
        # 更新菜单
        self.updataMenuAction()
        self.menuListWidget.setCurrentRow(row + 1)
        # 更新菜单参数
        self.updateMenuEdit(row + 1)
        # 更新菜单显示名称
        self.menuListWidget.item(row).setText(self.menuItems[row]["label"])
        self.menuListWidget.item(row + 1).setText(self.menuItems[row + 1]["label"])

    def addMenuItem(self):
        # 其他菜单项的 key 递增
        for key in sorted(self.menuItems.keys(), reverse=True):
            self.menuItems[key + 1] = self.menuItems.pop(key)
        
        self.menuListWidget.insertItem(0, sl(u"双击更改名称", self.language))
        self.menuListWidget.setCurrentRow(0)  # 选择新添加的菜单项

        # 更新菜单
        self.setMenuIcon(self.tempIcon)
        #self.gifButton.menu.actions()[0].iconPath = self.tempIcon
        self.menuItems[0] = {
            "label": sl(u"双击更改名称", self.language),
            "icon": '',
            "annotation": None,
            "sourceType": "python",
            "command": None
        }

        # 重新排序
        tempDict = OrderedDict()
        for key in range(len(self.menuItems.keys())):
            tempDict[key] = self.menuItems[key]
        self.menuItems = tempDict

        self.menuListWidget.setCurrentRow(0)  # 选择新添加的菜单项
        self.updateMenuEdit(0)  # 更新菜单参数
        self.updataMenuAction()

    def removeMenuItem(self):
        row = self.menuListWidget.currentRow()
        if row == -1 or row == self.menuListWidget.count() - 1:
            return
        self.menuListWidget.takeItem(row) # 移除菜单项
        self.menuItems.pop(row) # 移除菜单项
        # 更新字典里的key的编号
        new_menuItems = OrderedDict()
        for new_key, old_key in enumerate(self.menuItems.keys()):
            new_menuItems[new_key] = self.menuItems[old_key]
        self.menuItems = new_menuItems
        
        self.updataMenuAction() # 更新菜单
        
    def showMenuIconBorder(self, setButton,event):
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(10)
        effect.setColor(QColor(255, 255, 255, 255)) # rgba(255, 255, 255, 255)
        effect.setOffset(0, 0)
        setButton.setGraphicsEffect(effect)

    def hideMenuIconBorder(self, setButton,event):
        setButton.setGraphicsEffect(None)

    def setMenuIcon(self, icon):
        if icon:
            if not os.path.exists(icon):
                icon = iconPath+icon
            self.menuIconButton.movie = None
            if icon.endswith('.gif'):
                self.menuIconButton.movie = QMovie(icon)
                self.menuIconButton.movie.frameChanged.connect(self.updateMenuIcon)
                self.menuIconButton.movie.start()
            else:
                self.menuIconButton.setIcon(QIcon(icon))
            # 更新字典
            # 查询 self.menuListWidget 是否激活
            try:
                if self.menuListWidget.currentRow() != -1:
                    row = self.menuListWidget.currentRow()
                    menuItem = self.menuItems[row]
                    if icon != self.tempIcon:
                        menuItem["icon"] = icon
            except:
                pass
            #print(self.buttonDict)

    def updateMenuIcon(self):
        self.menuIconButton.setIcon(QIcon(self.menuIconButton.movie.currentPixmap()))

    def browseMenuIcon(self, event):
        row = self.menuListWidget.currentRow()
        if row == -1:
            return
        elif row == self.menuListWidget.count() - 1:
            return
        menuItem = self.menuItems[row]
    
        # 打开文件对话框
        icon = QFileDialog.getOpenFileName(self, sl(u"选择图标", self.language), self.iconPathDrt, sl(u"图标文件 (*.PNG *.BMP *.GIF *.JPEG *.JPG *.SVG *.ICO)",self.language))[0]
        if icon:
            # 设置预览图标
            self.setMenuIcon(icon)
            menuItem['icon'] = icon
            self.updataMenuAction()

    # 更改菜单名称，双击菜单项时触发 
    def editMenuName(self):
        item = self.menuListWidget.currentItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.menuListWidget.editItem(item)
        # 编辑完成后，应用新的名称,连接编辑完成信号
        self.menuListWidget.itemChanged.connect(self.applyMenuName)
    
    # 更改菜单名称，编辑完成后触发 
    def applyMenuName(self):
        # 打印新的名称
        item = self.menuListWidget.currentItem()
        newName = item.text()
        # 获取当前选中的菜单项
        row = self.menuListWidget.currentRow()
        menuItem = self.menuItems[row]
        menuActiconItem = self.gifButton.menu.actions()[row]
        # 更改action名字
        menuActiconItem.setText(newName)
        menuActiconItem.label = newName
        # 更新菜单字典
        menuItem['label'] = newName
        # 更新按钮字典
        self.buttonDict["menuItems"] = self.menuItems
        
        # 断开连接
        self.menuListWidget.itemChanged.disconnect(self.applyMenuName)

    def commandTabWidgetChanged(self):
        index = self.commandTabWidget.currentIndex()
        if index == 0:
            self.commandEdit.installEventFilter(self)
            self.menuCommandEdit.removeEventFilter(self)
        else:
            self.commandEdit.removeEventFilter(self)
            self.menuCommandEdit.installEventFilter(self)

    def eventFilter(self, obj, event):
        if (obj == self.menuCommandEdit or obj == self.commandEdit) and event.type() == QEvent.KeyPress:
            # 按下 Tab 键时不插入制表符，而是输入 4 个空格
            if event.key() == Qt.Key_Tab:
                cursor = obj.textCursor()
                if cursor.hasSelection():
                    # 获取选中的文本
                    selected_text = cursor.selectedText()
                    # 获取选中的行数
                    start = cursor.selectionStart()
                    end = cursor.selectionEnd()
                    cursor.setPosition(start)
                    cursor.movePosition(QTextCursor.StartOfLine)
                    start_line = cursor.blockNumber()
                    cursor.setPosition(end)
                    cursor.movePosition(QTextCursor.StartOfLine)
                    end_line = cursor.blockNumber()
                    # 在每一行的前端添加 4 个空格
                    for line in range(start_line, end_line + 1):
                        cursor.movePosition(QTextCursor.StartOfLine)
                        cursor.insertText(" " * 4)
                        cursor.movePosition(QTextCursor.NextBlock)
                else:
                    cursor.insertText(" " * 4)
                return True
            # 按下 Shift + Tab 时删除 4 个空格
            elif event.key() == Qt.Key_Backtab:
                cursor = obj.textCursor()
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 4)
                selected_text = cursor.selectedText()
                if selected_text.startswith(" "):
                    if selected_text == "    ":
                        cursor.removeSelectedText()
                    else:
                        # 删除不足 4 个的空格
                        cursor.movePosition(QTextCursor.StartOfLine)
                        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, selected_text.count(" "))
                        cursor.removeSelectedText()
                return True
        return QObject.eventFilter(self, obj, event)
    
    def editCommandType(self):
        row = self.commandListWidget.currentRow()
        if row == -1:
            return
        commandList = [
            "command",
            "doubleClickCommand",
            "ctrlCommand",
            "altCommand",
            "shiftCommand",
            "ctrlAltCommand",
            "ctrlShiftCommand",
            "altShiftCommand",
            "ctrlAltShiftCommand",
            "dragCommand",
            "ctrlDragCommand",
            "altDragCommand",
            "shiftDragCommand"
        ]

        commandItem = commandList[row]
        if self.commandPythonRadioButton.isChecked():
            if commandItem == "command":
                self.buttonDict['sourceType'] = "python"
                self.gifButton.sourceType = "python"
            elif commandItem == "doubleClickCommand":
                self.buttonDict['doubleClickCommandSourceType'] = "python"
                self.gifButton.doubleClickCommandSourceType = "python"
        elif self.commandMelRadioButton.isChecked():
            if commandItem == "command":
                self.buttonDict['sourceType'] = "mel"
                self.gifButton.sourceType = "mel"
            elif commandItem == "doubleClickCommand":
                self.buttonDict['doubleClickCommandSourceType'] = "mel"
                self.gifButton.doubleClickCommandSourceType = "mel"

    def editCommand(self):
        row = self.commandListWidget.currentRow()
        if row == -1:
            return
        commandList = [
            "command",
            "doubleClickCommand",
            "ctrlCommand",
            "altCommand",
            "shiftCommand",
            "ctrlAltCommand",
            "ctrlShiftCommand",
            "altShiftCommand",
            "ctrlAltShiftCommand",
            "dragCommand",
            "ctrlDragCommand",
            "altDragCommand",
            "shiftDragCommand"
        ]

        commandItem = commandList[row]
        commandText = self.commandEdit.toPlainText()

        #command = command.replace('"', '\\"')
        #commandText = commandText.replace("\\n", "TTTTTTEMP")
        #commandText = commandText.replace("\n", "\\n")
        #commandText = commandText.replace("TTTTTTEMP", "\\\\n")
        # 更新字典
        self.buttonDict[commandItem] = commandText
        # self.gifButton 下的 commandItem 属性 = commandText
        setattr(self.gifButton, commandItem, commandText)

    def updateCommandEdit(self, row):
        if row == -1:
            # 禁用命令输入框
            self.commandEdit.setDisabled(True)
            # 禁用命令类型选择
            self.commandPythonRadioButton.setChecked(True)
            self.commandPythonRadioButton.setDisabled(True)
            self.commandMelRadioButton.setDisabled(True)
            return
        commandList = [
            "command",
            "doubleClickCommand",
            "ctrlCommand",
            "altCommand",
            "shiftCommand",
            "ctrlAltCommand",
            "ctrlShiftCommand",
            "altShiftCommand",
            "ctrlAltShiftCommand",
            "dragCommand",
            "ctrlDragCommand",
            "altDragCommand",
            "shiftDragCommand"
        ]
        commandType = ''
        if commandList[row] == "command":
            self.commandMelRadioButton.setDisabled(False)
            self.commandPythonRadioButton.setDisabled(False)
            commandType = self.editButton.sourceType
            if commandType == 'python' or commandType == 'mel':
                self.commandPythonRadioButton.setChecked(commandType == 'python')
                self.commandMelRadioButton.setChecked(commandType == 'mel')
            else:
                self.commandPythonRadioButton.setChecked(False)
                self.commandMelRadioButton.setChecked(False)

        elif commandList[row] == "doubleClickCommand":
            self.commandMelRadioButton.setDisabled(False)
            self.commandPythonRadioButton.setDisabled(False)
            commandType = self.editButton.doubleClickCommandSourceType
            if commandType == 'python' or commandType == 'mel':
                self.commandPythonRadioButton.setChecked(commandType == 'python')
                self.commandMelRadioButton.setChecked(commandType == 'mel')
            else:
                self.commandPythonRadioButton.setChecked(False)
                self.commandMelRadioButton.setChecked(False)
        else:
            commandType = 'python'
            self.commandMelRadioButton.setDisabled(True)
            self.commandPythonRadioButton.setDisabled(True)
            self.commandPythonRadioButton.setChecked(True)
            self.commandMelRadioButton.setChecked(False)
        # 获取python版本
        pythonVersion = int(sys.version[0:1])
        commandText = self.buttonDict[commandList[row]]
        if commandText != 'None' and commandText != '' and commandText is not None:
            if pythonVersion < 3:
                try:
                    commandText = commandText.decode('utf-8')
                except:
                    pass
            if "mel.eval(" in commandText:
                commandText = commandText.replace("mel.eval('", "")[:-2]
            
            self.commandEdit.setText(commandText)

        else:
            self.commandEdit.setText('')
            self.commandEdit.setPlaceholderText(sl(u"请输入命令",self.language)) # 设置占位文本
            if ('Drag' in commandList[row] or 'drag' in commandList[row]):
                self.commandEdit.setPlaceholderText(sl(u"请输入命令\n使用 print(self.value) 获取可调用的值\n例子: \n# 沿x轴移动当前选中对象，移动距离为拖动值*0.1\nmove(self.valueX*0.1,0,0)",self.language))

    # 切换命令列表时更新菜单参数
    def browseIconPath(self):
        # 打开文件对话框, 默认打开路径为 iconPath
        iconFile = QFileDialog.getOpenFileName(self, sl(u"选择图标",self.language), self.iconPathLineEdit.text(), sl(u"图标文件 (*.PNG *.BMP *.GIF *.JPEG *.JPG *.SVG *.ICO)",self.language))[0]
        if iconFile:
            self.iconPath = iconFile
            # 将路径设置到输入框
            self.iconPathLineEdit.setText(self.iconPath.replace(self.iconPathDrt, ''))
            # 更新图标
            # 如果是 GIF 图片
            if self.iconPath.lower().endswith('.gif'):
                self.gifButton.movie = QMovie(self.iconPath)
                self.gifButton.icon = self.iconPath
                self.gifButton.iconChanged('default')
                self.gifButton.movie.start()
                self.iconStyleAuto.setEnabled(True)
                self.iconStyleAuto.setChecked(True)
                self.iconStyleHover.setEnabled(True)
                self.iconStylePause.setEnabled(True)
            else:
                self.gifButton.movie = None
                self.gifButton.icon = self.iconPath
                self.gifButton.iconChanged('default')
                self.gifButton.setIcon(QIcon(self.iconPath))

        #return self.iconPath

    def iconStyleChanged(self, key):
        # 应用按钮的图标风格
        self.gifButton.style = key
        # 如果是 GIF 图片
        if self.gifButton.icon.lower().endswith('.gif'):
            if key == "auto":
                self.gifButton.movie.start()
            elif key == "hover":
                self.gifButton.movie.stop()
                self.gifButton.movie.jumpToFrame(0)
            elif key == "pause":
                self.gifButton.movie.setPaused(True)

    def iconAnnotationChanged(self):
        # 应用按钮的图标注释
        self.gifButton.annotation = self.iconAnnotationLineEdit.toPlainText()
        self.gifButton.setStatusTip(self.gifButton.annotation)
        # 更新字典
        self.buttonDict['annotation'] = self.gifButton.annotation

    def applyEditButton(self, close=False):
        # 应该修改按钮的属性
        # 设置标签
        self.editButton.label = self.iconLabelLineEdit.text()
        # 设置注释
        self.editButton.annotation = self.iconAnnotationLineEdit.toPlainText()
        self.editButton.setStatusTip(self.editButton.annotation)
        # 设置图标图片
        self.editButton.icon = self.gifButton.icon
        self.editButton.setIconStyle(icon=self.editButton.icon)
        self.editButton.iconChanged('default')
        # 设置图标风格
        self.editButton.style = self.gifButton.style
        if self.editButton.icon.lower().endswith('.gif'):
            if self.editButton.style == "auto":
                self.editButton.movie.start()
            elif self.editButton.style == "hover":
                self.editButton.movie.stop()
                self.editButton.movie.jumpToFrame(0)
            elif self.editButton.style == "pause":
                self.editButton.movie.setPaused(True)
        
        self.editButton.command = self.buttonDict["command"]
        self.editButton.sourceType = self.buttonDict["sourceType"]
        self.editButton.doubleClickCommandSourceType = self.buttonDict["doubleClickCommandSourceType"]
        self.editButton.doubleClickCommand = self.buttonDict["doubleClickCommand"]
        self.editButton.ctrlCommand = self.buttonDict["ctrlCommand"]
        self.editButton.altCommand = self.buttonDict["altCommand"]
        self.editButton.shiftCommand = self.buttonDict["shiftCommand"]
        self.editButton.ctrlAltCommand = self.buttonDict["ctrlAltCommand"]
        self.editButton.altShiftCommand = self.buttonDict["altShiftCommand"]
        self.editButton.ctrlShiftCommand = self.buttonDict["ctrlShiftCommand"]
        self.editButton.ctrlAltShiftCommand = self.buttonDict["ctrlAltShiftCommand"]
        self.editButton.dragCommand = self.buttonDict["dragCommand"]
        self.editButton.altDragCommand = self.buttonDict["altDragCommand"]
        self.editButton.shiftDragCommand = self.buttonDict["shiftDragCommand"]
        self.editButton.ctrlDragCommand = self.buttonDict["ctrlDragCommand"]
        self.editButton.doubleClickCommand = self.buttonDict["doubleClickCommand"]
        self.editButton.menuShowCommand = self.buttonDict["menuShowCommand"]

        # 断开 aboutToShow
        try:
            self.editButton.menu.aboutToShow.disconnect(None, None)
        except:
            pass
        # 重新连接 aboutToShow
        if self.editButton.menuShowCommand:
            def execute_menu_show_command():
                exec(self.editButton.menuShowCommand, globals())
            self.editButton.menu.aboutToShow.connect(execute_menu_show_command)

        # 设置菜单 # 移除所有菜单后重新添加
        self.editButton.menu.clear()
        for key in self.menuItems.keys():
            if key == 'Separator':
                self.editButton.menu.addSeparator()
            else:
                menuItem = self.menuItems[key]
                self.editButton.addMenuItem(
                    label=menuItem["label"],
                    sourceType=menuItem["sourceType"],
                    command=menuItem["command"],
                    icon=menuItem["icon"],
                    annotation=menuItem["annotation"]
            )
        self.editButton.addDefaultMenuItems()

        # 移除事件过滤器
        self.menuCommandEdit.removeEventFilter(self)
        self.commandEdit.removeEventFilter(self)
        # 关闭窗口
        if close:
            self.close()
