
import os
import json
import codecs
from functools import partial
from collections import OrderedDict
import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance
from maya import mel

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from ..widgets import GIFWidget
from ..widgets import Separator
from ..widgets import GIFAction
from ..ui.mayaMQT import mayaToQT
from ..ui import shelfRestoreWindow
from ..utils.switchLanguage import *
from ..utils.getBackShelfList import getBackShelfList

try:
    reload(GIFWidget)
    reload(Separator)
    reload(shelfRestoreWindow)
except:
    from importlib import reload
    reload(GIFWidget)
    reload(Separator)
    reload(shelfRestoreWindow)

ICONPATH = __file__.replace('\\', '/').replace('src/shelfManager/test.py', 'icons/')
SHELF_BACKUP_PATH = os.path.expanduser('~') + '/OneTools/data/shelf_backup/'
# 新 shelfStyle 函数增加了检索支持，不存在则不设置，不会报错
shelfStyleFuncFile = __file__.replace('\\', '/').replace('test.py', 'shelfStyle.mel')
mel.eval('source "{}"'.format(shelfStyleFuncFile))


class shelfManager():
    def __init__(self,tabName='',language=0):
        self.tabName = tabName
        self.language = language
        if self.tabName == '': 
            self.autoSetShelf()
            return
        
        mayaVersion = mel.eval('getApplicationVersionAsFloat')
        self.shelfTabWidget = None
        self.shelfTAP = mayaToQT("ShelfLayout")
        for child in self.shelfTAP.children():
            if child.__class__.__name__ == 'QTabWidget':
                self.shelfTabWidget = child
                break
        self.size = 42
        for index in range(self.shelfTabWidget.count()):
            if hasattr(self.shelfTabWidget.widget(index), 'objectName'):
                if self.shelfTabWidget.widget(index).objectName() == self.tabName:
                    self.shelfTabWidget.removeTab(index)
        self.gifTab = QWidget()
        self.gifTab.setObjectName(self.tabName)
        self.gifLayout = QHBoxLayout()
        self.gifLayout.setAlignment(Qt.AlignLeft)
        if mayaVersion == 2022:
            self.gifLayout.setContentsMargins(0, 6, 0, 0)
        else:
            self.gifLayout.setContentsMargins(0, 5, 0, 0) # layout向下移动5个像素
        self.gifLayout.setSpacing(0)

        # 添加到工具栏
        self.shelfTabWidget.addTab(self.gifTab, self.tabName)
        self.gifTab.setLayout(self.gifLayout)
        self.shelfTabWidget.setCurrentWidget(self.gifTab)
        self.menu = self.createContextMenu()

        # # test
        # self.addSeparator()
        # self.addButton(icon=ICONPATH+'siri.gif',label=sl(u'按钮',self.language),annotation=sl(u'新按钮',self.language),command='')

    # 在当前工具架添加右击菜单
    def autoSetShelf(self):
        self.currentShelf = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')
        self.mayaVersion = mel.eval('getApplicationVersionAsFloat')

        self.PATH = os.path.dirname(os.path.abspath(__file__)) 
        self.PATH = self.PATH.replace('\\', '/')
        self.iconPath = self.PATH.replace('src/shelfManager', 'icons/')

        self.OneToolsDir = mel.eval('internalVar -uad').replace('maya/','OneTools') # Documents/OneTools/
        if not os.path.exists(self.OneToolsDir): 
            os.makedirs(self.OneToolsDir)
        self.OneToolsDataDir = self.OneToolsDir + '/data/' # Documents/OneTools/data/
        if not os.path.exists(self.OneToolsDataDir):
            os.makedirs(self.OneToolsDataDir)

        self.shelfLayoutInfo = None
        self.shelfParentPtr = omui.MQtUtil.findLayout(self.currentShelf)
        self.gifTab = wrapInstance(int(self.shelfParentPtr), QWidget)

        self.menu = self.createContextMenu()
        userSetupFile = mel.eval('internalVar -usd')+'/userSetup.mel'
        setupCode = 'source "'+self.PATH+'/ShelfAutoSetup.mel";\n'
        if not os.path.exists(userSetupFile):
            with open(userSetupFile, 'w') as f:
                f.write(setupCode)
            return
        
        # 按行读取 userSetup 文件
        with codecs.open(userSetupFile, 'r', 'utf-8') as f:
            userSetup = f.readlines()
        # 删除 'ShelfAutoSetup' 行
        userSetup = [line for line in userSetup if 'ShelfAutoSetup' not in line]
        # 检查并添加 'GifButton_AutoLoad;' 行 如果有则删除
        if 'GifButton_AutoLoad' in ''.join(userSetup):
            userSetup = [line for line in userSetup if 'GifButton_AutoLoad' not in line]
            setupCode += 'GifButton_AutoLoad;\n'
        # 检查并添加 'GifButton_AutoSave;' 行
        if 'GifButton_AutoSave;' in ''.join(userSetup):
            userSetup = [line for line in userSetup if 'GifButton_AutoSave' not in line]
            setupCode += 'GifButton_AutoSave;\n'
        # 添加 setupCode 到 userSetup
        userSetup.append(setupCode)
        # 写入 userSetup 文件
        with codecs.open(userSetupFile, 'w', 'utf-8') as f:
            f.writelines(userSetup)

    def createContextMenu(self):
        if self.tabName == '': self.tabName = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')
        self.contextMenu = QMenu(self.tabName + sl(u'设置...',self.language), self.gifTab)
        self.gifTab.setContextMenuPolicy(Qt.CustomContextMenu)
        try:
            self.gifTab.customContextMenuRequested.disconnect()
        except:
            pass
        self.gifTab.customContextMenuRequested.connect(self.showMenu)
        self.contextMenu.setTearOffEnabled(True)
        # 按钮
        self.contextMenu.addAction(QIcon(ICONPATH + 'white/undetected.png'), sl(u"添加按钮",self.language), self.addNewButton).setStatusTip(sl(u"点击添加一个新按钮",self.language))
        self.contextMenu.addAction(QIcon(ICONPATH + 'white/Separator.png'), sl(u"添加分隔符",self.language), self.addSeparator).setStatusTip(sl(u"点击添加一个新分隔符",self.language))
        self.contextMenu.addAction(QIcon(ICONPATH + 'white/Paste.png'), sl(u"粘贴按钮",self.language), self.pasteButton).setStatusTip(sl(u"点击粘贴按钮",self.language))
        self.recycleAction = GIFAction.gifIconMenuAction(icon = ICONPATH + 'white/Recycle.png', label = sl(u"回收站",self.language), annotation = sl(u"删除的按钮保存在此处, 最多存放 20 个删除的按钮",self.language), parent = self.contextMenu)
        #self.recycleAction.setStatusTip(sl(u"删除的按钮保存在此处, 最多存放 20 个删除的按钮",self.language)) # 神奇的，用QAction添加子菜单后，StatusTip 不会显示出来，用 gifIconMenuAction 却可以
        self.contextMenu.addAction(self.recycleAction)
        self.recycleMenu = QMenu(sl(u"回收站",self.language))
        self.recycleAction.setMenu(self.recycleMenu)
        self.recycleMenu.setTearOffEnabled(True)
        self.recycleMenu.aboutToShow.connect(self.recycleMenuList)
        # 工具栏设置
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(QIcon(ICONPATH + 'white/Switch.png'), sl(u"转换工具栏", self.language), self.toGIF).setStatusTip(sl(u"点击转换当前工具栏", self.language))
        self.contextMenu.addAction(QIcon(ICONPATH + 'green/Restore.png'), sl(u"还原工具栏", self.language), self.toDef).setStatusTip(sl(u"点击还原当前工具栏", self.language))
        self.contextMenu.addAction(QIcon(ICONPATH + 'white/Save.png'), sl(u"保存工具栏", self.language), self.saveGifShelf).setStatusTip(sl(u"点击保存当前工具栏", self.language))
        self.contextMenu.addAction(QIcon(ICONPATH + 'white/Import.png'), sl(u"导入工具栏", self.language), self.loadGifShelf).setStatusTip(sl(u"点击导入工具栏", self.language))
        self.contextMenu.addSeparator()
        # 自动加载工具栏
        self.autoLoadAction = self.contextMenu.addAction(QIcon(':\\switchOff.png'), sl(u"自动加载工具栏", self.language), self.setAutoLoadJob)
        self.autoLoadAction.setStatusTip(sl(u"maya启动时自动加载data文件下的工具栏", self.language))
        self.autoLoadAction.switch = bool(False)
        # 自动保存工具栏
        self.autoSaveAction = self.contextMenu.addAction(QIcon(':\\switchOff.png'), sl(u"自动保存工具栏", self.language), self.setAutoSaveJob)
        self.autoSaveAction.setStatusTip(sl(u"maya关闭时自动保存当前工具栏", self.language))
        self.autoSaveAction.switch = bool(False)
        self.contextMenu.aboutToShow.connect(self.menuShowCheck) # 每次打开菜单时检查是否开启了自动加载工具栏、自动保存工具栏
        self.contextMenu.addSeparator()
        # 语言切换
        self.languageAction = self.contextMenu.addAction(QIcon(ICONPATH + 'white/Language.png'),sl(u"语言", abs(1 - self.language)))
        # 添加子菜单
        self.languageMenu = QMenu()
        self.languageAction.setMenu(self.languageMenu)
        # 两个子菜单
        self.languageMenu.addAction("简体中文").triggered.connect(partial(self.languageSwitch, 0))
        self.languageMenu.addAction("English").triggered.connect(partial(self.languageSwitch, 1))
        
        return self.contextMenu
    
    def showMenu(self, pos):
        self.menu.exec_(self.gifTab.mapToGlobal(pos))

    def addNewButton(self):
        newButton = GIFWidget.GIFButtonWidget(size=self.size, icon=ICONPATH+'white/undetected.png', dragMove=True)
        self.gifLayout.addWidget(newButton)
        newButton.addDefaultMenuItems()
        return newButton

    def addButton(self,icon=None,label=None,annotation=None,command=None):
        button = GIFWidget.GIFButtonWidget(size=self.size, icon=icon, label=label, annotation=annotation, command=command, dragMove=True)
        self.gifLayout.addWidget(button)
        #button.addDefaultMenuItems()
        return button

    def addSeparator(self):
        separator = Separator.Separator(size=self.size)
        self.gifLayout.addWidget(separator)

    def pasteButton(self): 
        pass

    def recycleMenuList(self):
        pass

    def toGIF(self):
        pass

    def toDef(self):
        # 根据保存备份的 mel 文件恢复 shelf
        fileList = getBackShelfList(SHELF_BACKUP_PATH)

        if fileList is None:
            if self.language == 0:
                mel.eval(u'warning -n "没有找到备份文件"')
            elif self.language == 1:
                mel.eval('warning -n "No backup file found"')
            return 
        try:
            self.shelf2DefUI.close()
        except:
            pass
        
        self.shelf2DefUI = shelfRestoreWindow.toDefUI(fileList=fileList, language=self.language)
        self.shelf2DefUI.show()

    def saveGifShelf(self):
        pass

    def GIFButtonJsonDataSwitch(self, data):
        newDict = {}
        if 'size' in data.keys(): newDict['size'] = data['size']
        if 'label' in data.keys(): newDict['label'] = data['label']
        if 'annotation' in data.keys(): newDict['annotation'] = data['annotation']
        if 'image' in data.keys(): newDict['image'] = data['image']
        if newDict['image'] is not None:
            # 如果文件不存在，尝试在icons文件夹下查找
            if not os.path.exists(newDict['image']) and ':\\' not in newDict['image']:
                try:
                    if mel.eval('resourceManager -nameFilter '+newDict['image']):
                        newDict['image'] = ':\\'+newDict['image']
                except:
                    pass
        newDict['command'] = {}
        sourceType = data['sourceType'] if 'sourceType' in data.keys() else 'mel'
        command = data['command'] if 'command' in data.keys() else ''
        doubleClick = data['doubleClickCommand'] if 'doubleClickCommand' in data.keys() else ''
        doubleClickSourceType = data['doubleClickCommandSourceType'] if 'doubleClickCommandSourceType' in data.keys() else 'mel'
        ctrlClick = data['ctrlCommand'] if 'ctrlCommand' in data.keys() else ''
        shiftClick = data['altCommand'] if 'altCommand' in data.keys() else ''
        altClick = data['shiftCommand'] if 'shiftCommand' in data.keys() else ''
        ctrlShiftClick = data['ctrlAltCommand'] if 'ctrlAltCommand' in data.keys() else ''
        ctrlAltClick = data['altShiftCommand'] if 'altShiftCommand' in data.keys() else ''
        shiftAltClick = data['ctrlShiftCommand'] if 'ctrlShiftCommand' in data.keys() else ''
        ctrlShiftAltClick = data['ctrlAltShiftCommand'] if 'ctrlAltShiftCommand' in data.keys() else ''
        drag = data['dragCommand'] if 'dragCommand' in data.keys() else ''
        ctrlDrag = data['ctrlDragCommand'] if 'ctrlDragCommand' in data.keys() else ''
        shiftDrag = data['altDragCommand'] if 'altDragCommand' in data.keys() else ''
        altDrag = data['shiftDragCommand'] if 'shiftDragCommand' in data.keys() else ''
        menuShowCommand = data['menuShowCommand'] if 'menuShowCommand' in data.keys() else ''
        newDict['command'] = {
            'click': [sourceType, command],
            'doubleClick': [doubleClickSourceType, doubleClick],
            'ctrlClick': ['python', ctrlClick],
            'shiftClick': ['python', shiftClick],
            'altClick': ['python', altClick],
            'ctrlShiftClick': ['python', ctrlShiftClick],
            'ctrlAltClick': ['python', ctrlAltClick],
            'shiftAltClick': ['python', shiftAltClick],
            'ctrlShiftAltClick': ['python', ctrlShiftAltClick],
            'drag': ['python', drag],
            'ctrlDrag': ['python', ctrlDrag],
            'shiftDrag': ['python', shiftDrag],
            'altDrag': ['python', altDrag],
            'menuShowCommand': ['python', menuShowCommand]
        }
        newDict['menuItem'] = {}
        if 'menuItem'  in data.keys():
            if data['menuItem'] is not None:
                for item, value  in data['menuItem'].items():
                    newDict['menuItem'][item] = {}
                    newDict['menuItem'][item]['label'] = value['label']
                    newDict['menuItem'][item]['annotation'] = value['annotation']
                    newDict['menuItem'][item]['image'] = value['image']
                    newDict['menuItem'][item]['command'] = {
                        'click': [value['sourceType'],value['command']]
                    }
        return newDict
    
    def loadGifShelf(self):
        # 打开文件对话框
        jsonPath = mel.eval(u'fileDialog2 -fm 1 -ff "*.json" -okc "导入"')[0]
        if not jsonPath:
            return
        jsonData = {}
        try:
            with codecs.open(jsonPath, 'r', encoding='utf-8') as f:
                jsonData = json.load(f, object_pairs_hook=OrderedDict)
        except:
            with open(jsonPath, 'r') as f:
                jsonData = json.load(f, object_pairs_hook=OrderedDict)
        shelfName = jsonData['shelfName']
        if shelfName in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
            # 弹出窗口
            result = ''
            if self.language == 0:
                result = mel.eval(u'confirmDialog -title "警告" -message "工具栏已存在,是否覆盖?" -button "Yes" -button "No" -defaultButton "Yes" -cancelButton "No" -dismissString "No";')
            elif self.language == 1:
                result = mel.eval('confirmDialog -title "Warning" -message "The shelf already exists, do you want to overwrite it?" -button "Yes" -button "No" -defaultButton "Yes" -cancelButton "No" -dismissString "No";')
            if result == 'No':
                return
        lgb = shelfManager(shelfName)
        lgb.loadShelfData(data=jsonData['shelfData'])

    def loadShelfData(self, data):
        for key in data.keys():
            if 'separator' in data[key] or 'Separator' in data[key]:
                self.addSeparator()
            else:
                shelfButtonData = data[key]
                shelfButtonData = self.GIFButtonJsonDataSwitch(shelfButtonData)
                
                if isinstance(shelfButtonData, dict):
                    label = shelfButtonData['label'] if 'label' in shelfButtonData.keys() else ''
                    annotation = shelfButtonData['annotation'] if 'annotation' in shelfButtonData.keys() else ''
                    icon = shelfButtonData['image'] if 'image' in shelfButtonData.keys() else ''
                    command = shelfButtonData['command'] if 'command' in shelfButtonData.keys() else ''
                    button = self.addButton(
                        label=label,
                        annotation=annotation,
                        icon=icon,
                        command=command
                    )
                    if 'menuItem' in shelfButtonData.keys():
                        if shelfButtonData['menuItem'] is not None:
                            for menuItemName in shelfButtonData['menuItem'].keys():
                                if shelfButtonData['menuItem'][menuItemName] is not None:
                                    menuItemData = shelfButtonData['menuItem'][menuItemName]
                                    if menuItemData == 'separator':
                                        button.menu.addSeparator()
                                    else:
                                        label = menuItemData['label'] if 'label' in menuItemData.keys() else ''
                                        annotation = menuItemData['annotation'] if 'annotation' in menuItemData.keys() else ''
                                        icon = menuItemData['image'] if 'image' in menuItemData.keys() else ''
                                        command = menuItemData['command'] if 'command' in menuItemData.keys() else ''

                                        button.addMenuItem(
                                            label=label,
                                            command=command,
                                            annotation=annotation,
                                            icon=icon
                                        )
                    button.addDefaultMenuItems()

    def setAutoLoadJob(self):
        pass

    def setAutoSaveJob(self):
        pass

    def menuShowCheck(self):
        pass

    def languageSwitch(self, language):
        pass

