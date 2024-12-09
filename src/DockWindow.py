# coding: utf-8
import os
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from GIFButton import GIFButton
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from pymel.core import *

iconPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../icons/')
iconPath = iconPath.replace('\\', '/').replace('src', 'icons')

# 创建一个可以dock的窗口

class OneToolsMainWindow(MayaQWidgetDockableMixin, QWidget):
    def __init__(self, parent=None):
        super(OneToolsMainWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Window)  # 使窗口在主程序窗口内，并去除标题栏
        self.setObjectName("OneToolsWindw")  # 定义窗口名称  用于窗口管理
        self.setWindowTitle("OneTools")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)  # 设置window布局
        # 添加按钮时，从左上角开始
        self.layout.setAlignment(Qt.AlignCenter|Qt.AlignTop)
        #self.layout.setDirection(QBoxLayout.LeftToRight)
        self.layout.setSpacing(0) # 间隔为0
        self.layout.setContentsMargins(0, 1, 0, 0)

        self.winH = 34
        
    def addButton(self, 
                icon=None, 
                style="auto",
                annotation=None, 
                sourceType="python",
                command=None, 
                doubleClickCommandSourceType="python",
                doubleClickCommand=None,
                ctrlCommand=None, 
                altCommand=None,
                shiftCommand=None,
                ctrlAltCommand=None,
                altShiftCommand=None,
                ctrlShiftCommand=None,
                ctrlAltShiftCommand=None,
                dragCommand=None,
                altDragCommand=None,
                shiftDragCommand=None,
                ctrlDragCommand=None
                ):
        # 检查 icon 是否为绝对路径，如果不是则添加 iconPath
        if icon and not os.path.isabs(icon) and ':\\' not in icon:
            icon = os.path.join(iconPath, icon)

        self.gifButton = GIFButton.GIFButton(
                                icon=icon,
                                parent=self,
                                annotation=annotation, 
                                style=style, 
                                sourceType=sourceType,
                                command=command, 
                                doubleClickCommandSourceType=doubleClickCommandSourceType,
                                doubleClickCommand=doubleClickCommand,
                                ctrlCommand=ctrlCommand, 
                                altCommand=altCommand,
                                shiftCommand=shiftCommand,
                                ctrlAltCommand=ctrlAltCommand,
                                altShiftCommand=altShiftCommand,
                                ctrlShiftCommand=ctrlShiftCommand,
                                ctrlAltShiftCommand=ctrlAltShiftCommand,
                                dragCommand=dragCommand,
                                altDragCommand=altDragCommand,
                                shiftDragCommand=shiftDragCommand,
                                ctrlDragCommand=ctrlDragCommand,
                                size=self.winH
                                )
        self.layout.addWidget(self.gifButton)

        # 在不改变高度的情况下，将窗口小部件的最小和最大宽度都设置为width
        self.gifButton.setFixedSize(self.gifButton.iconSizeValue)

    def addSeparator(self):
        self.separator = GIFButton.Separator(parent=self)
        self.layout.addWidget(self.separator)
        self.separator.iconSizeValue = QSize((self.winH), self.winH)
        self.separator.setFixedSize(self.separator.iconSizeValue)

    def getButtonList(self):
        self.buttonList = []
        for i in range(self.layout.count()):
            self.buttonList.append(self.layout.itemAt(i).widget())
        return self.layout, self.buttonList
    
    def settingButton(self):
        addGifButtonCommand = '''import ShelfButtonManager
adb = ShelfButtonManager.ShelfButtonManager()
adb.addButton(icon='undetected.png')
adb.gifButton.addDefaultMenuItems()

# buttonList = []
# for i in range(self.shelfLayoutInfo.count()):
#     buttonList.append(self.shelfLayoutInfo.itemAt(i).widget())

# # buttonList 最后两项更换位置
# buttonList[-1], buttonList[-2] = buttonList[-2], buttonList[-1]
# # 重新排列按钮
# for i in buttonList:
#     i.setParent(None)
# for i in buttonList:
#     self.shelfLayoutInfo.addWidget(i)
#     try:
#         i.setFixedSize(i.iconSizeValue)
#     except:
#         pass
        '''
        addGifButtonDoubleCommand = '''import ShelfButtonManager
adb = ShelfButtonManager.ShelfButtonManager()
adb.addSeparator()

# buttonList = []
# for i in range(self.shelfLayoutInfo.count()):
#     buttonList.append(self.shelfLayoutInfo.itemAt(i).widget())

# # buttonList 最后两项更换位置
# buttonList[-1], buttonList[-2] = buttonList[-2], buttonList[-1]
# # 重新排列按钮
# for i in buttonList:
#     i.setParent(None)
# for i in buttonList:
#     self.shelfLayoutInfo.addWidget(i)
#     try:
#         i.setFixedSize(i.iconSizeValue)
#     except:
#         pass
        '''
        self.addButton(icon='siri.gif', 
                        label='Setting',
                        annotation='单击添加按钮, 双击添加分隔符, 右击工具栏设置',
                        command=addGifButtonCommand, 
                        sourceType='python', 
                        doubleClickCommand=addGifButtonDoubleCommand, 
                        doubleClickCommandSourceType='python')
        self.gifButton.addMenuItem(
            label=u"保存当前工具栏",
            icon = ":\\save.png",
            sourceType='python',
            command='import ShelfButtonManager\nadb = ShelfButtonManager.ShelfButtonManager()\nadb.saveGifShelf()',
            annotation=u"导出当前工具栏数据"
        )
        self.gifButton.addMenuItem(
            label=u"导入工具栏",
            icon = ":\\fileOpen.png",
            sourceType='python',
            command='import ShelfButtonManager\nadb = ShelfButtonManager.ShelfButtonManager()\nadb.loadGifShelf()',
            annotation=u"导入工具栏数据"
        )
        self.gifButton.addDefaultMenuItems()

def main():
    my_dock = OneToolsMainWindow()
    if workspaceControl('OneToolsWindwWorkspaceControl',q=True, exists=True):
        deleteUI('OneToolsWindwWorkspaceControl')
    my_dock.show(dockable=True)
    workspaceControl("OneToolsWindwWorkspaceControl",
                    e=True, 
                    label= "OneTools",
                    ih=34,
                    minimumHeight=34,
                    widthProperty='free',
                    heightProperty='free',
                    tp=("east",False),
                    dtc=("TimeSlider", "top" )
                    )

    # 手动添加按钮
    my_dock.addButton(
        icon="siri.gif",
        annotation=u'annotateInfo',
        command='print("siri")',
        doubleClickCommand='print("DoubleClick!")',
        ctrlCommand='print("Ctrl Clicked!")',
        altCommand='print("Alt Clicked!")',
        shiftCommand='print("Shift Clicked!")',
        ctrlAltCommand='print("Ctrl + Alt Clicked!")',
        altShiftCommand='print("Alt + Shift Clicked!")',
        ctrlShiftCommand='print("Ctrl + Shift Clicked!")',
        ctrlAltShiftCommand='print("Ctrl + Alt + Shift Clicked!")',
        dragCommand='move(self.getValue()*0.1,0,0)',
        altDragCommand='print("Alt Dragged!")',
        shiftDragCommand='print("Shift Dragged!")',
        ctrlDragCommand='print("Ctrl Dragged!")'
    )
    my_dock.gifButton.addDefaultMenuItems()

    my_dock.addSeparator()

    my_dock.addButton(
        icon="cat4.gif",
        command='print("cat4")',
        ctrlCommand='print("Ctrl Clicked!")'
    )
    my_dock.gifButton.addDefaultMenuItems()

    my_dock.addButton(icon="cat3.gif",command='print("cat3")')
    # 添加弹出菜单
    my_dock.gifButton.addMenuItem(
        label=u"自定义菜单项",
        command=lambda: warning(u"自定义菜单项"),
        icon="white/Custom.png",
        annotation=u"这是一个自定义菜单项"
    )
    my_dock.gifButton.addMenuItem(
        label=u"自定义菜单项",
        command=lambda: warning(u"自定义菜单项"),
        icon="white/Custom.png",
        annotation=u"这是一个自定义菜单项"
    )
    # 添加分隔符
    my_dock.gifButton.menu.addSeparator()
    # 添加默认菜单项
    my_dock.gifButton.addDefaultMenuItems()

    my_dock.addButton(
        icon="cat2.gif",
        annotation=u'test',
        command='mel.eval("print(\\"cat2\\")")'
    )
    my_dock.gifButton.addDefaultMenuItems()

    my_dock.addButton(
        icon="cat1.gif",
        annotation=u'annotateInfo',
        command='print("cat1")'
    )
    my_dock.gifButton.addDefaultMenuItems()

    return my_dock.getButtonList()
