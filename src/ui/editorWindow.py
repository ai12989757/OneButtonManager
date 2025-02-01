# -*- coding: utf-8 -*-
import os
import sys
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from collections import OrderedDict

from ..widgets import GIFWidget
from ..utils.KeywordHighlighter import *
from ..utils.switchLanguage import *
from ..utils import runCommand
try:
    reload(GIFWidget)
except:
    from importlib import reload
    reload(GIFWidget)

iconPath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src/ui', 'icons/')

from ..ui.mayaMQT import maya_main_window
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
        self.commandRriggerList = [
            "click",
            "doubleClick",
            "ctrlClick",
            "altClick",
            "shiftClick",
            "ctrlAltClick",
            "ctrlShiftClick",
            "altShiftClick",
            "ctrlAltShiftClick",
            "drag",
            "ctrlDrag",
            "altDrag",
            "shiftDrag",
            "ctrlShiftDrag",
            "ctrlAltDrag",
            "altShiftDrag",
            "ctrlAltShiftDrag",
            "leftPress",
            "leftRelease"
        ]
        # 初始化图标
        self.buttonDict = {
            'icon': self.editButton.iconPath,
            'label': self.editButton.labelText,
            'annotation': self.editButton.annotation,
            'style': self.editButton.style,
            'command': self.editButton.command,
            'size': 128,
            'language': self.language
        }

        self.menuItems =  OrderedDict()
        self.menuItemIndex = 0

        # 从当前图标获取菜单项
        self.menuItems = {
            self.menuItemIndex + i: {
                "label": acticon.text() if hasattr(acticon, 'text') else None,
                "command": acticon.command if hasattr(acticon, 'command') else {'click': ['python', '']},
                "icon": acticon.iconPath if hasattr(acticon, 'iconPath') else None,
                "annotation": acticon.annotation if hasattr(acticon, 'annotation') else None
            }
            for i, acticon in enumerate(self.editButton.menu.actions())
            if not acticon.isSeparator() and acticon.text() not in [sl(u'编辑', self.language), sl(u'删除', self.language)]
        }

        self.gifButton = GIFWidget.GIFButtonWidget(**self.buttonDict)
        # 预览按钮添加菜单项
        for key in self.menuItems.keys():
            menuItem = self.menuItems[key]
            self.gifButton.addMenuItem(
                label=menuItem["label"],
                command=menuItem["command"],
                icon=menuItem["icon"],
                annotation=menuItem["annotation"]
            )

        self.setUI()

    def setUI(self):
        # 创建一个整体垂直布局
        self.globalLayout = QVBoxLayout()
        self.setLayout(self.globalLayout)
        # 布局第一行 图标 和 图标参数
        self.createIconEditLayout()
        # 布局第二行 两个TAP页 点击命令 和 右击菜单
        self.createCommandEditLayout()
        # 布局第三行 应用按钮
        self.createApplyLayout()

    def createIconEditLayout(self):
        # 左右两个布局 左边是图标预览，右边是图标参数
        self.iconLayout = QHBoxLayout()
        self.globalLayout.addLayout(self.iconLayout)
        # 图标预览
        self.iconLayout.addWidget(self.gifButton)
        # 图标参数布局
        self.iconParamLayout = QVBoxLayout()
        self.iconLayout.addLayout(self.iconParamLayout)
        # 图标标签 名称 输入框
        self.iconLabelLayout = QHBoxLayout()
        self.iconLabel = QLabel(sl(u"名称:", self.language))
        self.iconLabelLineEdit = QLineEdit()
        self.iconLabelLineEdit.setText(self.gifButton.labelText)
        self.iconLabelLayout.addWidget(self.iconLabel)
        self.iconLabelLayout.addWidget(self.iconLabelLineEdit)
        self.iconParamLayout.addLayout(self.iconLabelLayout)
        # 图标路径 路劲 输入框 按钮 maya按钮
        self.iconPathLayout = QHBoxLayout()
        self.iconPathLabel = QLabel(sl(u"路径:", self.language))
        self.iconPathLineEdit = QLineEdit()
        self.iconPathLineEdit.setText(self.gifButton.iconPath.replace(iconPath, '')) 
        # 回车事件
        self.iconPathLineEdit.returnPressed.connect(self.iconPathChanged)
        self.iconPathButton = self.createIconButton( 20,20, iconPath + "white/OpenFile.png", self.browseIconPath)
        self.MayaIconBrowerButton = self.createIconButton( 20,20, ":\\mayaIcon.png", self.browseMayaIconPath)
        self.iconPathLayout.addWidget(self.iconPathLabel)
        self.iconPathLayout.addWidget(self.iconPathLineEdit)
        self.iconPathLayout.addWidget(self.iconPathButton)
        self.iconPathLayout.addWidget(self.MayaIconBrowerButton)
        self.iconParamLayout.addLayout(self.iconPathLayout)
        # 图标风格 三个单选按钮
        self.iconStyleLayout = QHBoxLayout()
        self.iconStyleLabel = QLabel(sl(u"动画:", self.language))
        def createRadioButton( text, style):
            radioButton = QRadioButton(text)
            radioButton.clicked.connect(lambda: self.iconStyleChanged(style))
            if self.gifButton.style == style:
                radioButton.setChecked(True)
            if not self.gifButton.iconPath.lower().endswith('.gif'):
                radioButton.setEnabled(False)
            self.iconStyleLayout.addWidget(radioButton)
        createRadioButton(sl(u"循环播放", self.language), 'auto')
        createRadioButton(sl(u"播放一次", self.language), 'once')
        createRadioButton(sl(u"点击开始", self.language), 'clickAction')
        createRadioButton(sl(u"离开停止", self.language), 'leaveStop')
        createRadioButton(sl(u"离开暂停", self.language), 'leavePause')
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

    def createCommandEditLayout(self):
        # 总命令布局
        self.commandAllLayout = QHBoxLayout()
        self.commandAllLayout.setAlignment(Qt.AlignTop)
        self.globalLayout.addLayout(self.commandAllLayout,stretch=1)
        # 命令编辑总布局 点击命令 和 右击菜单
        self.commandTabWidget = QTabWidget()
        self.commandAllLayout.addWidget(self.commandTabWidget)
        self.createClickCommandEditLayout()
        self.createMenuCommandEditLayout()
        
    def createClickCommandEditLayout(self):
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
        commandItems = [
            u"点击命令", u"双击命令", u"Ctrl单击", u"Alt单击", u"Shift单击",
            u"Ctrl+Alt单击", u"Ctrl+Shift单击", u"Alt+Shift单击", u"Ctrl+Alt+Shift单击",
            u"左击拖动", u"Ctrl左击拖动", u"Alt左击拖动", u"Shift左击拖动",u"Ctrl+Alt左击拖动",u"Ctrl+Shift左击拖动",u"Alt+Shift左击拖动",u"Ctrl+Alt+Shift左击拖动",
            u"左键按下",u"左键释放"
        ]
        for item in commandItems:
            self.commandListWidget.addItem(sl(item, self.language))

        self.commandEditWidget = QWidget()
        self.commandEditLayout = QVBoxLayout()
        self.commandEditLayout.setContentsMargins(0, 0, 0, 0)
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

    def createMenuCommandEditLayout(self):
        # 菜单TAP
        self.menuTab = QWidget()
        self.menuLayout = QHBoxLayout()
        self.commandTabWidget.addTab(self.menuTab, sl(u"右击菜单", self.language))
        self.menuTab.setLayout(self.menuLayout)
        # 菜单布局，左边是菜单图标、菜单控制按钮、菜单列表，右边是语言选择、菜单提示、菜单命令输入框
        self.menuListLayout = QVBoxLayout()
        self.menuLayout.addLayout(self.menuListLayout)

        # 添加一个左右分区可以拖动调节的分区
        self.menuSplitter = QSplitter(Qt.Horizontal)
        self.menuListLayout.addWidget(self.menuSplitter)
        # 创建一个菜单列表
        self.menuListLeftWidget = QWidget() # 菜单命令列表总体布局
        self.menuListLeftLayout = QVBoxLayout() # 菜单命令列表总体布局
        self.menuListLeftLayout.setContentsMargins(0, 0, 0, 0)
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
        # 内置图标浏览按钮
        self.menuMayaIconBrowerButton = self.createIconButton(14,14, ":\\mayaIcon.png", self.setMenuMayaIcon)
        # 添加菜单按钮 上移 下移 添加 删除
        self.menuUpButton = self.createIconButton(14,20, ":\\moveLayerUp.png", self.moveMenuItemUp)
        self.menuDownButton = self.createIconButton(14,20, ":\\moveLayerDown.png", self.moveMenuItemDown)
        self.menuAddButton = self.createIconButton(14,20, ":\\newLayerEmpty.png", self.addMenuItem)
        self.menuRemoveButton = self.createIconButton(14,20, ":\\delete.png", self.removeMenuItem)
        # 添加 menu 编辑按钮
        self.menuIconLayout1.addWidget(self.menuMayaIconBrowerButton)
        self.menuIconLayout1.addWidget(self.menuUpButton)
        self.menuIconLayout1.addWidget(self.menuDownButton)
        self.menuIconLayout1.addWidget(self.menuAddButton)
        self.menuIconLayout1.addWidget(self.menuRemoveButton)

        self.menuListWidget = QListWidget() # 菜单命令列表
        self.menuListLeftLayout.addWidget(self.menuListWidget)
        self.menuSplitter.addWidget(self.menuListLeftWidget)
        # 创建一个菜单输入框
        self.menuCommandEdit = QTextEdit()
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
        self.menuCommandEditLayout.setContentsMargins(0, 0, 0, 0)

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
        # # 添加菜单项
        for key in self.menuItems.keys():
            menuItem = self.menuItems[key]
            if menuItem != 'Separator':
                self.menuListWidget.addItem(menuItem["label"])
        self.menuListWidget.addItem(sl(u'菜单显示时执行的命令', self.language))

        self.menuListWidget.currentRowChanged.connect(self.updateMenuEdit)
        # 双击菜单项时更新菜单输入框，双击时编辑菜单项名称
        self.menuListWidget.itemDoubleClicked.connect(self.editMenuName)
        self.menuSplitter.setStretchFactor(0, 3)
        self.menuSplitter.setStretchFactor(1, 7)

    def createApplyLayout(self):
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

    def createIconButton(self, sizeW, sizeH, iconPath, clickHandler):
        button = QPushButton()
        button.setIcon(QIcon(iconPath))
        #button.setIconSize(QSize(sizeW, sizeH))
        button.setFixedSize(QSize(sizeW, sizeH))
        button.setStyleSheet("QPushButton {background-color: rgba(0, 0, 0, 0);border: none;}")
        button.clicked.connect(clickHandler)
        button.enterEvent = lambda event: self.showMenuIconBorder(button, event)
        button.leaveEvent = lambda event: self.hideMenuIconBorder(button, event)
        return button

    def editMenuCommandType(self):
        row = self.menuListWidget.currentRow()
        if row == -1 or row not in self.menuItems:
            return
        menuItem = self.menuItems[row]
        if self.menuPythonRadioButton.isChecked():
            menuItem['command']['click'][0] = "python"
        elif self.menuMelRadioButton.isChecked():
            menuItem['command']['click'][0] = "mel"
        # 更新字典
        self.menuItems[row] = menuItem
        self.buttonDict["menuItems"] = self.menuItems

        self.updataMenuAction()

    def editMenuCommand(self):
        row = self.menuListWidget.currentRow()
        if row == -1:
            return
        
        command = self.menuCommandEdit.toPlainText()
        if row == self.menuListWidget.count() - 1: # 最后一个菜单项,menuShow
            if 'menuShow' not in self.buttonDict['command'].keys():
                self.buttonDict['command']['menuShow'] = ['python', '']
            self.buttonDict['command']['menuShow'][1] = command
            self.gifButton.commend = self.buttonDict['command']
        else:
            menuItem = self.menuItems[row]
            menuItem['command']['click'][1] = command

            # 更新字典
            self.menuItems[row]['command'][1] = command
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
            self.setMenuIcon('white/Menu.png')
            self.menuPythonRadioButton.setChecked(True)
            self.menuPythonRadioButton.setEnabled(True)
            self.menuMelRadioButton.setChecked(False)
            self.menuMelRadioButton.setEnabled(True)
            self.menuAnnotationLineEdit.setText(sl(u'当菜单弹出前执行命令，一般用于更新菜单项', self.language))
            self.menuAnnotationLineEdit.setEnabled(False)
            if 'menuShow' in self.buttonDict['command'].keys():
                self.menuCommandEdit.setText(self.buttonDict['command']['menuShow'][1])
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
        commandType = menuItem["command"]['click'][0]
        if commandType == "python" or commandType == "mel":
            self.menuMelRadioButton.setChecked(commandType == "mel")
            self.menuPythonRadioButton.setChecked(commandType == "python")
        
        # 获取python版本
        pythonVersion = int(sys.version[0:1])
        commandText = menuItem["command"]['click'][1]
        if commandText != 'None' and commandText != '' and commandText is not None:
            if pythonVersion < 3:
                try:
                    commandText = commandText.decode('utf-8')
                except:
                    pass
        
            # 如果开头是 mel.eval(' 则去掉
            if commandText[:9] == "mel.eval('":
                commandText = commandText[9:-2]

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
            "command": {'click': ['python', '']}
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
        # 如果自定义菜单被完全删除，去除图标的sub下标
        if len(self.menuItems) == 0:
            self.gifButton.subIcon = None
            self.editButton.subIcon = None
            self.gifButton.menuSubLable.setPixmap(QPixmap())
            self.gifButton.menuSubLable = None
        
    def showMenuIconBorder(self, setButton,event):
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(10)
        effect.setColor(QColor(255, 255, 255, 255)) # rgba(255, 255, 255, 255)
        effect.setOffset(0, 0)
        setButton.setGraphicsEffect(effect)

    def hideMenuIconBorder(self, setButton,event):
        setButton.setGraphicsEffect(None)

    def setMenuMayaIcon(self):
        import maya.app.general.resourceBrowser as resourceBrowser
        resBrowser = resourceBrowser.resourceBrowser()
        icon = resBrowser.run()
        del resBrowser
        if icon:
            icon = ':\\'+icon
            self.setMenuIcon(icon)
            self.updataMenuAction()

    def setMenuIcon(self, icon):
        if icon:
            if ':\\' not in icon and not os.path.exists(icon):
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
        elif index == 1:
            self.commandEdit.removeEventFilter(self)
            self.menuCommandEdit.installEventFilter(self)

    def handleTabPress(self, obj):
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

    def handleShiftTabPress(self, obj):
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

    def eventFilter(self, obj, event):
        if hasattr(self, 'menuCommandEdit') and obj == self.menuCommandEdit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                return self.handleTabPress(obj)
            elif event.key() == Qt.Key_Backtab:
                return self.handleShiftTabPress(obj)
        elif hasattr(self, 'commandEdit') and obj == self.commandEdit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                return self.handleTabPress(obj)
            elif event.key() == Qt.Key_Backtab:
                return self.handleShiftTabPress(obj)
        return QObject.eventFilter(self, obj, event)
    
    def editCommandType(self):
        row = self.commandListWidget.currentRow()
        if row == -1:
            return

        if self.commandPythonRadioButton.isChecked():
            self.buttonDict['command'][self.commandRriggerList[row]][0] = "python"
        elif self.commandMelRadioButton.isChecked():
            self.buttonDict['command'][self.commandRriggerList[row]][0] = "mel"

    def editCommand(self):
        row = self.commandListWidget.currentRow()
        if row == -1:
            return

        commandText = self.commandEdit.toPlainText()

        # 更新字典
        if self.commandRriggerList[row] not in self.buttonDict['command']:
            self.buttonDict['command'][self.commandRriggerList[row]] = ['python', commandText]
        self.buttonDict['command'][self.commandRriggerList[row]][1] = commandText
        # 更新按钮
        setattr(self.gifButton, 'command', self.buttonDict['command'])

    def updateCommandEdit(self, row):
        if row == -1:
            # 禁用命令输入框
            self.commandEdit.setDisabled(True)
            # 禁用命令类型选择
            self.commandPythonRadioButton.setChecked(True)
            self.commandPythonRadioButton.setDisabled(True)
            self.commandMelRadioButton.setDisabled(True)
            return
        
        if self.commandRriggerList[row] not in self.buttonDict['command']:
            self.commandMelRadioButton.setDisabled(False)
            self.commandPythonRadioButton.setDisabled(False)
            self.commandEdit.setText('')
            return
        commandType = ''
        self.commandMelRadioButton.setDisabled(False)
        self.commandPythonRadioButton.setDisabled(False)
        commandType = self.buttonDict['command'][self.commandRriggerList[row]][0]
        if commandType == 'python' or commandType == 'mel':
            self.commandPythonRadioButton.setChecked(commandType == 'python')
            self.commandMelRadioButton.setChecked(commandType == 'mel')

        # 获取python版本
        pythonVersion = int(sys.version[0:1])
        commandText = self.buttonDict['command'][self.commandRriggerList[row]][1]
        if commandText != 'None' and commandText != '' and commandText is not None:
            if pythonVersion < 3:
                try:
                    commandText = commandText.decode('utf-8')
                except:
                    pass
            
            # 如果开头是 mel.eval(' 则去掉
            if commandText[:9] == "mel.eval('":
                commandText = commandText[9:-2]

            self.commandEdit.setText(commandText)

        else:
            self.commandEdit.setText('')
            self.commandEdit.setPlaceholderText(sl(u"请输入命令",self.language)) # 设置占位文本
            if ('Drag' in self.commandRriggerList[row] or 'drag' in self.commandRriggerList[row]):
                self.commandEdit.setPlaceholderText(sl(u"请输入命令\n使用 print(self.value) 获取可调用的值\n例子: \n# 沿x轴移动当前选中对象，移动距离为拖动值*0.1\nmove(self.valueX*0.1,0,0)",self.language))

    def browseMayaIconPath(self):
        import maya.app.general.resourceBrowser as resourceBrowser
        resBrowser = resourceBrowser.resourceBrowser()
        iconFile = resBrowser.run()
        del resBrowser
        if iconFile:
            iconFile = ':\\'+iconFile
            self.iconPath = iconFile
            # 将路径设置到输入框
            self.iconPathLineEdit.setText(self.iconPath.replace(self.iconPathDrt, ''))
            # 更新图标
            self.gifButton.movie = None
            self.gifButton.iconPath = self.iconPath
            self.gifButton.pixmap = QPixmap(self.iconPath)
            self.gifButton.pixmap = self.gifButton.pixmap.scaledToHeight(128, Qt.SmoothTransformation)
            self.gifButton.iconLabel.setPixmap(QIcon(self.gifButton.pixmap))

    # 更改图标
    def browseIconPath(self):
        # 打开文件对话框, 默认打开路径为 iconPath
        iconFile = QFileDialog.getOpenFileName(self, sl(u"选择图标",self.language), self.iconPathLineEdit.text(), sl(u"图标文件 (*.PNG *.BMP *.GIF *.JPEG *.JPG *.SVG *.ICO)",self.language))[0]
        if iconFile:
            self.iconPath = iconFile
            # 将路径设置到输入框
            self.iconPathLineEdit.setText(self.iconPath.replace(self.iconPathDrt, ''))
            # 更新图标
            # 如果是 GIF 图片
            style = 'auto'
            if self.iconPath.lower().endswith('.gif'):
                for i in range(self.iconStyleLayout.count()):
                    widget = self.iconStyleLayout.itemAt(i).widget()
                    widget.setEnabled(True)
                    if widget.isChecked():
                        style = widget.text()
                        if style == u'循环播放': style = 'auto'
                        elif style == u'播放一次': style = 'once'
                        elif style == u'点击开始': style = 'clickAction'
                        elif style == u'离开停止': style = 'leaveStop'
                        elif style == u'离开暂停': style = 'leavePause'
            else:
               for i in range(self.iconStyleLayout.count()):
                    widget = self.iconStyleLayout.itemAt(i).widget()
                    widget.setEnabled(False)
            self.gifButton.iconPath = self.iconPath
            self.gifButton.setIconImage(self.iconPath)
        #return self.iconPath

    def iconPathChanged(self):
        self.iconPath = self.iconPathLineEdit.text()
        if self.iconPath:
            style = 'auto'
            if self.iconPath.lower().endswith('.gif'):
                for i in range(self.iconStyleLayout.count()):
                    widget = self.iconStyleLayout.itemAt(i).widget()
                    widget.setEnabled(True)
                    if widget.isChecked():
                        style = widget.text()
                        if style == u'循环播放': style = 'auto'
                        elif style == u'播放一次': style = 'once'
                        elif style == u'点击开始': style = 'clickAction'
                        elif style == u'离开停止': style = 'leaveStop'
                        elif style == u'离开暂停': style = 'leavePause'
            else:
               for i in range(self.iconStyleLayout.count()):
                    widget = self.iconStyleLayout.itemAt(i).widget()
                    widget.setEnabled(False)
            self.gifButton.iconPath = self.iconPath
            self.gifButton.setIconImage(self.iconPath)

    def iconStyleChanged(self, key):
        # 应用按钮的图标风格
        self.gifButton.style = key
        self.gifButton.setGIFStyle(key)

    def iconAnnotationChanged(self):
        # 应用按钮的图标注释
        self.gifButton.annotation = self.iconAnnotationLineEdit.toPlainText()
        self.gifButton.setStatusTip(self.gifButton.annotation)
        # 更新字典
        self.buttonDict['annotation'] = self.gifButton.annotation

    def applyEditButton(self, close=False):
        # 应该修改按钮的属性
        # 设置标签
        self.editButton.labelText = self.iconLabelLineEdit.text()
        # 设置注释
        self.editButton.annotation = self.iconAnnotationLineEdit.toPlainText()
        self.editButton.setStatusTip(self.editButton.annotation)
        # 设置图标图片
        self.editButton.iconPath = self.gifButton.iconPath
        self.editButton.style = self.gifButton.style
        self.editButton.setIconImage(self.editButton.iconPath)

        # # 设置图标风格
        # self.editButton.style = self.gifButton.style
        # if self.editButton.iconPath.lower().endswith('.gif'):
        #     if self.editButton.style == "auto":
        #         self.editButton.iconLabel.movie.start()
        #     elif self.editButton.style == "hover":
        #         self.editButton.iconLabel.movie.stop()
        #         self.editButton.iconLabel.movie.jumpToFrame(0)
        #     elif self.editButton.style == "pause":
        #         self.editButton.iconLabel.movie.setPaused(True)
        
        self.editButton.command = self.buttonDict["command"]

        # 断开 aboutToShow
        try:
            self.editButton.menu.aboutToShow.disconnect(None, None)
        except:
            pass
        # 重新连接 aboutToShow
        if 'menuShow' in self.buttonDict['command'].keys():
            self.editButton.menu.aboutToShow.connect(lambda: runCommand.runCommand(self.editButton, self.editButton.command, 'menuShow'))

        # 设置菜单 # 移除所有菜单后重新添加
        self.editButton.menu.clear()
        self.editButton.subIcon = None
        if self.editButton.menuSubLable:
            #self.editButton.menuSubLable.setPixmap(QPixmap())
            self.editButton.menuSubLable.deleteLater()
            self.editButton.menuSubLable = None
        if self.menuItems:
            for key in self.menuItems.keys():
                if key == 'Separator':
                    self.editButton.menu.addSeparator()
                else:
                    menuItem = self.menuItems[key]
                    self.editButton.addMenuItem(
                        label=menuItem["label"],
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
