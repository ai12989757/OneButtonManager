# -*- coding: utf-8 -*-
import os
import sys
import json
import codecs
from maya import mel
import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

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

from switchLanguage import *
from widgets import GIFButton
try:
    reload(GIFButton)
except:
    from importlib import reload
    reload(GIFButton)

class ShelfButtonManager(QWidget):
    def __init__(self,language=0):
        super(ShelfButtonManager, self).__init__()
        self.language = language # 0 简体中文, 1 English
        self.InternalIconDict = self.getInternalIconDict()

        self.shelfManagers = {} # 添加一个字典来保存每个 shelf 的 ShelfButtonManager 实例
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
        self.shelfParent = wrapInstance(int(self.shelfParentPtr), QWidget)

        if not self.shelfParent.layout():  # 如果没有布局则创建一个
            self.shelfLayoutInfo = QHBoxLayout()
            self.shelfParent.setLayout(self.shelfLayoutInfo)
        else:
            self.shelfLayoutInfo = self.shelfParent.layout()
        self.shelfLayoutInfo.setAlignment(Qt.AlignLeft | Qt.AlignBottom) # 设置对齐方式

        self.shelfLayoutInfo.setSpacing(0) # 设置间隔
        if self.mayaVersion == 2022:
            self.shelfLayoutInfo.setContentsMargins(0, 6, 0, 0)
        else:
            self.shelfLayoutInfo.setContentsMargins(0, 5, 0, 0) # layout向下移动5个像素

        self.iconH = 42
        self.iconH = mel.eval('shelfLayout -q -h '+self.currentShelf) - 10

        self.menu = None

        # def moveYShelf(self):
        #     self.buttonList = self.getButtonList()[1]
        #     for i in self.buttonList:
        #         #i.move(i.pos().x(), 5)
        #         i.setGeometry(i.pos().x(), 5, 0, 0)
        #     #QTimer.singleShot(0, self.moveYShelf)

    def languageSwitch(self, language):
        if self.language == language:
            return
        self.language = language
        self.menu = self.createContextMenu()
        # 修改 ShelfAutoSetup.mel 文件，第二行的语言设置
        with codecs.open(self.PATH+'/ShelfAutoSetup.mel', 'r', encoding='utf-8') as f:
            data = f.readlines()
        if language == 0:
            data[1] = data[1].replace('int $Language = 1', 'int $Language = 0')
        elif language == 1:
            data[1] = data[1].replace('int $Language = 0', 'int $Language = 1')
        with codecs.open(self.PATH+'/ShelfAutoSetup.mel', 'w', encoding='utf-8') as f:
            f.writelines(data)

        currentShelf = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')
        
        # 清除所有按钮后重新添加
        self.autoSaveGifShelf()
        # mel.eval('GifButton_AutoLoad')

        # 获取 self.OneToolsDataDir 下的所有 json 文件
        self.shelfList = []
        for i in os.listdir(self.OneToolsDataDir):
            if i.endswith('.json') and ' ' not in i:
                self.shelfList.append(i)
                jsonPath = self.OneToolsDataDir + i

                try:
                    with codecs.open(jsonPath, 'r', encoding='utf-8') as f:
                        jsonData = json.load(f, object_pairs_hook=OrderedDict)
                except:
                    with open(jsonPath, 'r') as f:
                        jsonData = json.load(f, object_pairs_hook=OrderedDict)
                shelfName = jsonData['shelfName']

                # 查询 shelfName 是否存在 shelfTabLayout -q -ca $self.gShelfTopLevel
                if shelfName not in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
                    mel.eval('addNewShelfTab("'+shelfName+'")')

                evalCode = 'shelfTabLayout -e -st '+shelfName+' $gShelfTopLevel;'
                mel.eval(evalCode)
                self.shelfManagers[shelfName] = ShelfButtonManager(self.language)  # 使用字典保存每个 shelf 的 ShelfButtonManager 实例
                self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()
                if mel.eval('shelfLayout -q -ca '+shelfName) is not None:
                    for i in mel.eval('shelfLayout -q -ca '+shelfName):
                        mel.eval('deleteUI '+i)
                    try:
                        for i in self.shelfManagers[shelfName].getButtonList()[1]:
                            i.deleteLater()
                    except:
                        pass
                self.shelfManagers[shelfName].loadShelfData(jsonData)
                self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()
        evalCode = 'shelfTabLayout -e -st '+currentShelf+' $gShelfTopLevel;'

    # 工具栏右击菜单
    def createContextMenu(self):
        self.contextMenu = QMenu(self.currentShelf + sl(u'设置...',self.language), self.shelfParent)
        self.shelfParent.setContextMenuPolicy(Qt.CustomContextMenu)
        try:
            self.shelfParent.customContextMenuRequested.disconnect()
        except:
            pass
        self.shelfParent.customContextMenuRequested.connect(self.showMenu)
        self.contextMenu.setTearOffEnabled(True)
        # 按钮
        self.contextMenu.addAction(QIcon(self.iconPath + 'white/undetected.png'), sl(u"添加按钮",self.language), self.addNewButton).setStatusTip(sl(u"点击添加一个新按钮",self.language))
        self.contextMenu.addAction(QIcon(self.iconPath + 'white/Separator.png'), sl(u"添加分隔符",self.language), self.addSeparator).setStatusTip(sl(u"点击添加一个新分隔符",self.language))
        self.contextMenu.addAction(QIcon(self.iconPath + 'white/Paste.png'), sl(u"粘贴按钮",self.language), self.pasteButton).setStatusTip(sl(u"点击粘贴按钮",self.language))
        self.recycleAction = GIFButton.gifIconMenuAction(icon = self.iconPath + 'white/Recycle.png', label = sl(u"回收站",self.language), annotation = sl(u"删除的按钮保存在此处, 最多存放 20 个删除的按钮",self.language), parent = self.contextMenu)
        #self.recycleAction.setStatusTip(sl(u"删除的按钮保存在此处, 最多存放 20 个删除的按钮",self.language)) # 神奇的，用QAction添加子菜单后，StatusTip 不会显示出来，用 gifIconMenuAction 却可以
        self.contextMenu.addAction(self.recycleAction)
        self.recycleMenu = QMenu(sl(u"回收站",self.language))
        self.recycleAction.setMenu(self.recycleMenu)
        self.recycleMenu.setTearOffEnabled(True)
        self.recycleMenu.aboutToShow.connect(self.recycleMenuList)
        # 工具栏设置
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(QIcon(self.iconPath + 'white/Switch.png'), sl(u"转换工具栏", self.language), self.toGIF).setStatusTip(sl(u"点击转换当前工具栏", self.language))
        self.contextMenu.addAction(QIcon(self.iconPath + 'white/Save.png'), sl(u"保存工具栏", self.language), self.saveGifShelf).setStatusTip(sl(u"点击保存当前工具栏", self.language))
        self.contextMenu.addAction(QIcon(self.iconPath + 'white/Import.png'), sl(u"导入工具栏", self.language), self.loadGifShelf).setStatusTip(sl(u"点击导入工具栏", self.language))
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
        self.languageAction = self.contextMenu.addAction(QIcon(self.iconPath + 'white/Language.png'),sl(u"语言", abs(1 - self.language)))
        # 添加子菜单
        self.languageMenu = QMenu()
        self.languageAction.setMenu(self.languageMenu)
        # 两个子菜单
        self.languageMenu.addAction("简体中文").triggered.connect(partial(self.languageSwitch, 0))
        self.languageMenu.addAction("English").triggered.connect(partial(self.languageSwitch, 1))
        
        return self.contextMenu
    
    # 工具里右击菜单 - 回收站 的菜单
    def recycleMenuList(self):
        # 获取回收站文件夹下的所有文件
        recycleFile = self.OneToolsDataDir + 'shelf_backup/shelf_recycle.json'
        if not os.path.exists(recycleFile):
            return None
        with codecs.open(recycleFile, 'r', 'utf-8') as f:
            data = json.load(f)
        jsonData = data['shelfData']
        # 创建一个新的菜单
        self.recycleMenu.clear()
        self.recycleMenu.addAction(QIcon(self.iconPath + 'red/Recycle.png'), sl(u"清空回收站",self.language), self.recycleDeleteAllButton)
        self.recycleMenu.addSeparator()
        for i in jsonData.keys():
            action = GIFButton.gifIconMenuAction(icon = jsonData[i]['image'], label = jsonData[i]['label'], annotation = jsonData[i]['annotation'], parent = self.recycleMenu)
            buttonRecycleEdit = QMenu()
            action.setMenu(buttonRecycleEdit)
            buttonRecycleEdit.addAction(QIcon(self.iconPath + 'white/Restore.png'), sl(u"还原",self.language), self.recycleRestoreButton).setStatusTip(sl(u"将此按钮重新添加到当前工具栏",self.language))
            buttonRecycleEdit.addAction(QIcon(self.iconPath + 'red/Delete.png'), sl(u"删除",self.language), self.recycleDeleteButton).setStatusTip(sl(u"从回收站彻底删除此按钮, 注意: 不可恢复",self.language))
            self.recycleMenu.addAction(action)
   
    def pasteButton(self):
        shelf_backup = mel.eval('internalVar -uad').replace('maya','OneTools/data/shelf_backup/')
        shelf_copy = shelf_backup + 'shelf_copy.json'

        with codecs.open(shelf_copy, 'r', encoding='utf-8') as f:
            jsonData = json.load(f)
        newButtonData = jsonData['shelfData']
        if newButtonData is None:
            return
        else:
            self.addButton(
                icon=newButtonData['image'],
                label=newButtonData['label'],
                annotation=newButtonData['annotation'],
                sourceType=newButtonData['sourceType'],
                command=newButtonData['command'],
                doubleClickCommandSourceType=newButtonData['doubleClickCommandSourceType'],
                doubleClickCommand=newButtonData['doubleClickCommand'],
                ctrlCommand=newButtonData['ctrlCommand'],
                altCommand=newButtonData['altCommand'],
                shiftCommand=newButtonData['shiftCommand'],
                ctrlAltCommand=newButtonData['ctrlAltCommand'],
                altShiftCommand=newButtonData['altShiftCommand'],
                ctrlShiftCommand=newButtonData['ctrlShiftCommand'],
                ctrlAltShiftCommand=newButtonData['ctrlAltShiftCommand'],
                dragCommand=newButtonData['dragCommand'],
                altDragCommand=newButtonData['altDragCommand'],
                shiftDragCommand=newButtonData['shiftDragCommand'],
                ctrlDragCommand=newButtonData['ctrlDragCommand'],
                menuShowCommand=newButtonData['menuShowCommand']
            )
            if newButtonData['menuItem'] is not None:
                for i in newButtonData['menuItem'].keys():
                    if newButtonData['menuItem'][i] == 'separator':
                        self.gifButton.menu.addSeparator()
                    else:
                        self.gifButton.addMenuItem(
                            label=newButtonData['menuItem'][i]['label'],
                            command=newButtonData['menuItem'][i]['command'],
                            annotation=newButtonData['menuItem'][i]['annotation'],
                            icon=newButtonData['menuItem'][i]['image'],
                            sourceType=newButtonData['menuItem'][i]['sourceType']
                        )
                self.gifButton.addDefaultMenuItems()

    def recycleDeleteAllButton(self):
        shelf_recycle = self.OneToolsDataDir + 'shelf_backup/shelf_recycle.json'
        with codecs.open(shelf_recycle, 'w', encoding='utf-8') as f:
            json.dump({"shelfName": "buttonRecycle","shelfData": {}}, f)

    def getRecycleRestoreButtonIndex(self):
        # 获取当前 action 的 menu
        recycleButtonMenu = self.sender().parent()
        # 获取 self.recycleMenu 下 的 action
        recycleButton = None
        for action in self.recycleMenu.actions():
            if action.menu() == recycleButtonMenu:
                recycleButton = action
                break
        # 获取 recycleButton 的 indes
        index = self.recycleMenu.actions().index(recycleButton) - 2
        return index

    def recycleRestoreButton(self):
        # 获取按钮数据并删除在json中的数据
        restoreButtonData = self.recycleDeleteButton()
        # 添加按钮
        self.addButton4ButtonData(restoreButtonData)

    def addButton4ButtonData(self,buttonData):
        if buttonData is None:
            return
        buttonData['image'] = self.findIconImage(buttonData['image'], self.InternalIconDict)
        self.addButton(icon = buttonData['image'] if 'image' in buttonData.keys() else '',
                        label = buttonData['label'] if 'label' in buttonData.keys() else '',
                        annotation = buttonData['annotation'] if 'annotation' in buttonData.keys() else '',
                        sourceType=buttonData['sourceType'] if 'sourceType' in buttonData.keys() else 'mel',
                        command = buttonData['command'] if 'command' in buttonData.keys() else '',
                        doubleClickCommandSourceType = buttonData['doubleClickCommandSourceType'] if 'doubleClickCommandSourceType' in buttonData.keys() else 'mel',
                        doubleClickCommand = buttonData['doubleClickCommand'] if 'doubleClickCommand' in buttonData.keys() else '',
                        ctrlCommand = buttonData['ctrlCommand'] if 'ctrlCommand' in buttonData.keys() else '',
                        altCommand = buttonData['altCommand'] if 'altCommand' in buttonData.keys() else '',
                        shiftCommand = buttonData['shiftCommand'] if 'shiftCommand' in buttonData.keys() else '',
                        ctrlAltCommand = buttonData['ctrlAltCommand'] if 'ctrlAltCommand' in buttonData.keys() else '',
                        altShiftCommand = buttonData['altShiftCommand'] if 'altShiftCommand' in buttonData.keys() else '',
                        ctrlShiftCommand = buttonData['ctrlShiftCommand'] if 'ctrlShiftCommand' in buttonData.keys() else '',
                        ctrlAltShiftCommand = buttonData['ctrlAltShiftCommand'] if 'ctrlAltShiftCommand' in buttonData.keys() else '',
                        dragCommand = buttonData['dragCommand'] if 'dragCommand' in buttonData.keys() else '',
                        altDragCommand = buttonData['altDragCommand'] if 'altDragCommand' in buttonData.keys() else '',
                        shiftDragCommand = buttonData['shiftDragCommand'] if 'shiftDragCommand' in buttonData.keys() else '',
                        ctrlDragCommand = buttonData['ctrlDragCommand'] if 'ctrlDragCommand' in buttonData.keys() else '',
                        menuShowCommand = buttonData['menuShowCommand'] if 'menuShowCommand' in buttonData.keys() else ''
                        )
        if 'menuItem' in buttonData.keys():
            if buttonData['menuItem'] is not None:
                for i in buttonData['menuItem'].keys():
                    if buttonData['menuItem'][i] == 'separator':
                        self.gifButton.menu.addSeparator()
                    else:
                        self.gifButton.addMenuItem(
                            label = buttonData['menuItem'][i]['label'] if 'label' in buttonData['menuItem'][i].keys() else '',
                            command = buttonData['menuItem'][i]['command'] if 'command' in buttonData['menuItem'][i].keys() else '',
                            annotation = buttonData['menuItem'][i]['annotation'] if 'annotation' in buttonData['menuItem'][i].keys() else '',
                            icon = buttonData['menuItem'][i]['image'] if 'image' in buttonData['menuItem'][i].keys() else '',
                            sourceType = buttonData['menuItem'][i]['sourceType'] if 'sourceType' in buttonData['menuItem'][i].keys() else ''
                        )
            self.gifButton.addDefaultMenuItems()

    def recycleDeleteButton(self):
        shelf_recycle = self.OneToolsDataDir + 'shelf_backup/shelf_recycle.json'
        with codecs.open(shelf_recycle, 'r', encoding='utf-8') as f:
            jsonData = json.load(f)
        shelfData = jsonData['shelfData']
        index = self.getRecycleRestoreButtonIndex()
        restoreButtonData = list(shelfData.values())[index]
        # shelfData 里去掉这个 key
        shelfData.pop(list(shelfData.keys())[index])
        # 重新排序
        newShelfData = OrderedDict()
        for i, key in enumerate(shelfData.keys()):
            newShelfData[i] = shelfData[key]
        jsonData['shelfData'] = newShelfData
        with codecs.open(shelf_recycle, 'w', encoding='utf-8') as f:
            json.dump(jsonData, f)

        return restoreButtonData

    def showMenu(self, pos):
        self.menu.exec_(self.shelfParent.mapToGlobal(pos))

    def autoSetShelf(self):
        self.menu = self.createContextMenu()
        userSetupFile = mel.eval('internalVar -usd')+'/userSetup.mel'
        setupCode = 'source "'+self.PATH+'/ShelfAutoSetup.mel";\n'
        if not os.path.exists(userSetupFile):
            with open(userSetupFile, 'w') as f:
                f.write(setupCode)
            return
        
        with codecs.open(userSetupFile, 'r', 'utf-8') as f:
            userSetup = f.read()
        if 'ShelfAutoSetup' in userSetup:
            return
        # 写入 userSetup 文件
        with codecs.open(userSetupFile, 'a', 'utf-8') as f:
            f.write(setupCode)

    def setAutoLoadJob(self):
        userSetupFile = mel.eval('internalVar -usd')+'/userSetup.mel'
        for i in self.menu.actions():
            if i.text() == sl(u"自动加载工具栏",self.language):
                if i.switch == False:
                    i.setIcon(QIcon(':\\switchOn.png'))
                    i.switch = True
                    with open(userSetupFile, 'r') as f:
                        userSetup = f.read()
                    if 'GifButton_AutoLoad' in userSetup:
                        return
                    # 写入 userSetup 文件
                    with open(userSetupFile, 'a') as f:
                        setupCode = 'GifButton_AutoLoad;\n'
                        f.write(setupCode)
                    
                    if self.language == 0:
                        mel.eval('print("// 结果: 开启自动加载工具栏\\n")')
                    elif self.language == 1:
                        mel.eval('print("// Result: Auto load GIFShelf when Maya starts\\n")')
                    break
                elif i.switch == True:
                    i.setIcon(QIcon(':\\switchOff.png'))
                    # 删除 userSetup 文件中的自动加载工具栏代码
                    with open(userSetupFile, 'r') as f:
                        userSetup = f.read()
                    userSetup = userSetup.replace('GifButton_AutoLoad;\n', '')
                    with open(userSetupFile, 'w') as f:
                        f.write(userSetup)
                    i.switch = False
                    if self.language == 0:
                        mel.eval(u'print("// 结果: 关闭自动加载工具栏\\n")')
                    elif self.language == 1:
                        mel.eval('print("// Result: Close auto load GIFShelf\\n")')
                    break

    def setAutoSaveJob(self):
        for i in self.menu.actions():
            userSetupFile = mel.eval('internalVar -usd')+'/userSetup.mel'
            if i.text() == sl(u"自动保存工具栏",self.language):
                userSetup = ''
                with open(userSetupFile, 'r') as f:
                    userSetup = f.read()
                if i.switch == False:
                    i.setIcon(QIcon(':\\switchOn.png'))
                    if 'GifButton_AutoSave' not in userSetup:
                        with open(userSetupFile, 'a') as f:
                            setupCode = 'GifButton_AutoSave;\n'
                            f.write(setupCode)
                    for job in mel.eval('scriptJob -lj'):
                        if 'autoSaveGifShelf' in job:
                            break
                    jboCode = 'scriptJob -e "quitApplication" "python(\\"from shelfManager import ShelfButtonManager\\\\nshelf_save = ShelfButtonManager.ShelfButtonManager('+str(self.language)+')\\\\nshelf_save.autoSaveGifShelf()\\")"'
                    mel.eval(jboCode)
                    i.switch = True
                    if self.language == 0:
                        mel.eval(u'print("// 结果: 开启自动保存工具栏\\n")')
                    elif self.language == 1:
                        mel.eval('print("// Result: Auto save GIFShelf when Maya closes\\n")')
                    break
                elif i.switch == True:
                    i.setIcon(QIcon(':\\switchOff.png'))

                    if 'GifButton_AutoSave' in userSetup:
                        # 删除 userSetup 文件中的自动加载工具栏代码
                        userSetup = userSetup.replace('GifButton_AutoSave;\n', '')
                        with open(userSetupFile, 'w') as f:
                            f.write(userSetup)
                    for job in mel.eval('scriptJob -lj'):
                        if 'autoSaveGifShelf' in job:
                            job = int(job.split(': ')[0]) # 获取job的id
                            mel.eval('scriptJob -kill '+str(job))
                    i.switch = False
                    if self.language == 0:
                        mel.eval(u'print("// 结果: 关闭自动保存工具栏\\n")')
                    elif self.language == 1:
                        mel.eval('print("// Result: Close auto save GIFShelf\\n")')
                    break

    def menuShowCheck(self):
        # 查询 userSetup 文件中是否有自动加载工具栏的代码
        userSetup = ''
        userSetupFile = mel.eval('internalVar -usd')+'/userSetup.mel'
        if os.path.exists(userSetupFile):
            with open(userSetupFile, 'r') as f:
                userSetup = f.read()

        for i in self.menu.actions():
            if i.text() == sl(u"自动保存工具栏",self.language):

                for job in mel.eval('scriptJob -lj'):
                    if 'autoSaveGifShelf' in job:
                        i.setIcon(QIcon(':\\switchOn.png'))
                        i.switch = True
                        break
                else:
                    i.setIcon(QIcon(':\\switchOff.png'))
                    i.switch = False
            elif i.text() == sl(u"自动加载工具栏",self.language):

                if 'GifButton_AutoLoad' in userSetup:
                    i.setIcon(QIcon(':\\switchOn.png'))
                    i.switch = True
                else:
                    i.setIcon(QIcon(':\\switchOff.png'))
                    i.switch = False

    def addNewButton(self):
        self.addButton(icon='white/undetected.png')
        self.gifButton.addDefaultMenuItems()
            
    def addButton(self, **kwargs):
        # 检查 icon 是否为绝对路径，如果不是则添加 iconPath
        icon = kwargs.get('icon', None)
        if icon and not os.path.isabs(icon) and ':\\' not in icon:
            icon = os.path.join(self.iconPath, icon)

        self.gifButton = GIFButton.GIFButton(
            parent=self.shelfParent,
            icon=icon,
            label=kwargs.get('label', ""),
            annotation=kwargs.get('annotation', None),
            style=kwargs.get('style', "auto"),
            sourceType=kwargs.get('sourceType', "mel"),
            command=kwargs.get('command', None),
            doubleClickCommandSourceType=kwargs.get('doubleClickCommandSourceType', "mel"),
            doubleClickCommand=kwargs.get('doubleClickCommand', None),
            ctrlCommand=kwargs.get('ctrlCommand', None),
            altCommand=kwargs.get('altCommand', None),
            shiftCommand=kwargs.get('shiftCommand', None),
            ctrlAltCommand=kwargs.get('ctrlAltCommand', None),
            altShiftCommand=kwargs.get('altShiftCommand', None),
            ctrlShiftCommand=kwargs.get('ctrlShiftCommand', None),
            ctrlAltShiftCommand=kwargs.get('ctrlAltShiftCommand', None),
            dragCommand=kwargs.get('dragCommand', None),
            altDragCommand=kwargs.get('altDragCommand', None),
            shiftDragCommand=kwargs.get('shiftDragCommand', None),
            ctrlDragCommand=kwargs.get('ctrlDragCommand', None),
            menuShowCommand=kwargs.get('menuShowCommand', None),
            size=self.iconH,
            language=self.language
        )
        if self.mayaVersion < 2022:
            self.shelfLayoutInfo.addWidget(self.gifButton)
        elif self.mayaVersion >= 2022:
            # 使用winID作为按钮的名称
            self.gifButton.setObjectName('QPushButton'+str(self.gifButton.winId()))
            # 更改按钮的名字
            self.gifButtonPrt = omui.MQtUtil.findControl(self.gifButton.objectName())
            #print(self.gifButton.winId(),str(self.gifButton.winId()),self.gifButton.objectName())

            #return self.getButtonList()
            omui.MQtUtil.addWidgetToMayaLayout(int(self.gifButtonPrt), int(self.shelfParentPtr))
        self.gifButton.shelfLayoutInfo = self.shelfLayoutInfo
        self.gifButton.setFixedSize(self.gifButton.iconSizeValue)
        # self.gifButton.setContentsMargins(0, 5, 0, 0) # not work
        # self.gifButton.setGeometry(0, 5, 0, 0) # not work

    def addSeparator(self):
        self.separator = GIFButton.Separator(parent=self.shelfParent,language=self.language)
        if self.mayaVersion < 2022:
            self.shelfLayoutInfo.addWidget(self.separator)
        elif self.mayaVersion >= 2022:
            # 使用winID作为按钮的名称
            self.separator.setObjectName('QPushButton'+str(self.separator.winId()))
            # 更改按钮的名字
            self.separatorButtonPrt = omui.MQtUtil.findControl(self.separator.objectName())
            omui.MQtUtil.addWidgetToMayaLayout(int(self.separatorButtonPrt), int(self.shelfParentPtr)) 
        self.separator.shelfLayoutInfo = self.shelfLayoutInfo
        self.separator.iconSizeValue = QSize((self.iconH), self.iconH)
        self.separator.setFixedSize(self.separator.iconSizeValue)

    def getButtonList(self):
        self.buttonList = []
        for i in range(self.shelfLayoutInfo.count()):
            self.buttonList.append(self.shelfLayoutInfo.itemAt(i).widget())
        return self.shelfLayoutInfo,self.buttonList
    
    def getMayaShelfButtonData(self, mayaShelfButtonName):
        data = OrderedDict()
        data['label'] = mel.eval('shelfButton -q -label '+mayaShelfButtonName)
        data['annotation'] = mel.eval('shelfButton -q -annotation '+mayaShelfButtonName)
        data['image'] = mel.eval('shelfButton -q -image1 '+mayaShelfButtonName)
        data['sourceType'] = mel.eval('shelfButton -q -sourceType '+mayaShelfButtonName)
        data['command'] = mel.eval('shelfButton -q -command '+mayaShelfButtonName)
        data['doubleClickCommand'] = mel.eval('shelfButton -q -doubleClickCommand '+mayaShelfButtonName)
        data['doubleClickCommandSourceType'] = mel.eval('shelfButton -q -sourceType -doubleClickCommand '+mayaShelfButtonName)
        data['menuItem'] = OrderedDict()
        popupMenuName = mel.eval('shelfButton -q -popupMenuArray '+mayaShelfButtonName)[0]
        if mel.eval('shelfButton -q -numberOfPopupMenus '+mayaShelfButtonName):
            if mel.eval('popupMenu -q -itemArray '+popupMenuName):
                if len(mel.eval('popupMenu -q -itemArray '+popupMenuName)) > 4:
                    for index, menuItemName in enumerate(mel.eval('popupMenu -q -itemArray '+popupMenuName)[4:]):
                        menuData = OrderedDict()
                        menuData['label'] = mel.eval('menuItem -q -label '+menuItemName)
                        menuData['command'] = mel.eval('menuItem -q -command '+menuItemName)
                        menuData['annotation'] = mel.eval('menuItem -q -annotation '+menuItemName)
                        menuData['image'] = mel.eval('menuItem -q -image '+menuItemName)
                        menuData['sourceType'] = mel.eval('menuItem -q -sourceType '+menuItemName)
                        if menuData['label'] is not None and menuData['command'] is not None:
                            data['menuItem'][index] = menuData
            else:
                data['menuItem'] = None
            return data

    def toGIF(self):
        if mel.eval('shelfLayout -q -ca '+self.currentShelf) is not None:
            shelfMel = mel.eval('internalVar -userShelfDir') + 'shelf_'+self.currentShelf+'.mel' # 当前 shelf 的 mel 文件
            shelf_backup = self.OneToolsDataDir + 'shelf_backup/' # 备份文件夹
            if not os.path.exists(shelf_backup):
                os.makedirs(shelf_backup)
            
            mel.eval('saveShelf("'+self.currentShelf+'", "'+shelfMel.replace('.mel', '')+'")' ) # 保存当前 shelf

            # 使用robocopy备份文件 robocopy /e path file
            os.system('robocopy /e '+mel.eval('internalVar -userShelfDir')+' '+shelf_backup+' shelf_'+self.currentShelf+'.mel')
            # aveAllShelves(self.gShelfTopLevel)
            self.buttonList = self.getButtonList()[1]
            # 新建字典保存按钮数据
            data = OrderedDict()
            for index,i in enumerate(self.buttonList):
                if i.__class__.__name__ == 'GIFButton':
                    data[index] = self.getGIFButtonData(i)
                    i.deleteLater()
                elif i.__class__.__name__ == 'Separator' or i.__class__.__name__ == 'QFrame':
                    data[index] = 'separator'
                    i.deleteLater()
                elif i.__class__.__name__ == 'QFrame':
                    data[index] = 'separator'
                    mel.eval('deleteUI '+i.objectName())
                elif i.__class__.__name__ == 'QPushButton' or i.__class__.__name__ == 'QWidget':
                    if 'separator' in i.objectName() or 'Separator' in i.objectName():
                        data[index] = 'separator'
                    else:
                        data[index] = self.getMayaShelfButtonData(i.objectName())
                    mel.eval('deleteUI '+i.objectName())
                else:
                    warning(i,i.__class__.__name__)
                #print(i.__class__.__name__)

            #oldShelfButtonList = shelfLayout(self.currentShelf, q=True, ca=True)
            #print(data)
            # 重新添加GIFButton
            for i in data.keys():
                if data[i] == 'separator':
                    self.addSeparator()
                else:
                    buttonData = data[i]
                    self.addButton4ButtonData(buttonData)

            # # 删除旧按钮
            # for i in oldShelfButtonList:
            #     deleteUI(i)
            mel.eval(u'print("// 结果: 转换成功\\n")') 

    def toDef(self):
        pass

    def toJson(self):
        pass
        # filePath = internalVar(userShelfDir=True) + 'shelf_'+self.currentShelf+'.mel'
        # if not os.path.exists(filePath):
        #     return None
        # jsonPath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src', 'data/shelf_tempNeedDelete.json')
        # # 解析文件,去掉前六行和最后一行，再去掉空行,去掉\n
        # def parseFile(filePath):
        #     with codecs.open(filePath, 'r', 'gbk') as f:
        #         data = f.readlines()
        #     data = data[6:-1]
        #     data = [i for i in data if i != '\n']
        #     return data

        # # separator改为 shelfButton
        # def changeSeparator(data):
        #     data = [i.replace('separator', 'shelfButton -separator') for i in data]
        #     return data

        # # 使用 'shelfButton' 分割数据，清除空数据，如果数据里没有'annotation'或'style' 'shelf'则删除
        # def splitData(data):
        #     data = ''.join(data)
        #     data = data.split('shelfButton')
        #     for i in data:
        #         if 'separator' in i:
        #             i = 'separator'
        #     data = [i for i in data if i != '']
        #     return data

        # shelfData = parseFile(filePath)
        # shelfData = changeSeparator(shelfData)
        # shelfData = splitData(shelfData)

        # data = OrderedDict()
        # # 解析数据，使用四个空格分割数据，删除'-'
        # buttonName = 0
        # shelfDataNew = []
        # for button in shelfData:
        #     button = button.split('        -')
        #     #button = [i.replace('\n', '') for i in button]
        #     # 清除空数据
        #     button = [i for i in button if i != '']
        #     shelfDataNew.append(button)
        #     buttonData = OrderedDict()
        #     miNum = 0
            
        #     for i in button:
        #         if '-separator' in i:
        #             data[buttonName] = 'separator'
        #             break

        #         # 如果第一个字符是空格，则删除
        #         if i[0] == ' ':
        #             i = i[1:]
        #         # 以第一个空格为分割点将数据分割成两部分，
        #         # 第一部分为键，第二部分为值
        #         i = i.split(' ', 1)
        #         # 如果数据量不为2，则跳过
        #         if len(i) == 2:
        #             # if 'command' in i[0] or 'doubleClickCommand' in i[0] or 'mi' in i[0]:
        #             #     if i[1][-2:] == ' \n':
        #             #         i[1] = i[0][:-2]
        #             i[1] = i[1].replace('\\\"', '\"').replace('\\n', '\n').replace('\\t', '').replace('\\\n', '\\n').replace('\"\\\\\"', '\"\\\"').replace('\\\\\"', '\\"')
        #             if i[1][:1] == '"':
        #                 i[1] = i[1][1:]
        #             if i[1][-3:] == '" \n':
        #                 i[1] = i[1][:-3]
        #             # 如果i[0]的值在[]里,则写入buttonData
        #             if i[0] in ['annotation', 'label', 'image', 'command','sourceType','doubleClickCommand','mi']:
        #                 if i[0] == 'image':
        #                     # 如果图标不存在
        #                     if not os.path.exists(i[1]):
        #                         i[1] = ':\\'+i[1]
        #                 if i[0] == 'mi':
        #                     i[1] = i[1].replace('    ;\n    ', '')
        #                     # 使用第一个 \" 分割i[1]
        #                     i[1] = i[1].split('\"', 1)
        #                     i[1][1] = i[1][1][4:-4]
        #                     buttonData[miNum] = i[1]
        #                     miNum += 1
        #                 else:
        #                     buttonData[i[0]] = i[1]
        #                     if i[0] == 'doubleClickCommand':
        #                         # 根据 i[1] 里的数据判断是否为python语法
        #                         if 'import' in i[1] or 'from' in i[1]:
        #                             buttonData['doubleClickCommandSourceType'] = 'python'
        #                         else:
        #                             buttonData['doubleClickCommandSourceType'] = 'mel'
        #                     else:
        #                         buttonData['doubleClickCommandSourceType'] = ''
        #                         buttonData['doubleClickCommand'] = ''
        #             if 'command' not in buttonData.keys():
        #                 buttonData['command'] = ''
        #             if 'doubleClickCommand' not in buttonData.keys():
        #                 buttonData['doubleClickCommand'] = ''
        #             if 'sourceType' not in buttonData.keys():
        #                 buttonData['sourceType'] = 'mel'
        #             if 'annotation' not in buttonData.keys():
        #                 buttonData['annotation'] = ''
        #             if 'label' not in buttonData.keys():
        #                 buttonData['label'] = ''
        #             if 'image' not in buttonData.keys():
        #                 buttonData['image'] = ''
        #             if 'doubleClickCommandSourceType' not in buttonData.keys():
        #                 buttonData['doubleClickCommandSourceType'] = ''

        #     # 如果为空则
        #     if buttonData:
        #         data[buttonName] = buttonData
        #     else:
        #         data[buttonName] = 'separator'
        #     buttonName += 1

        # # 去掉第一个数据
        # data.pop(0)
        # outJson = OrderedDict()
        # outJson['shelfName'] = self.currentShelf
        # outJson['shelfData'] = data
        # # 写入json文件 D:\MELcopy\OneTools\src\shelfData.json
        # with codecs.open(jsonPath, 'w', encoding='utf-8') as f:
        #     json.dump(outJson, f, ensure_ascii=False, indent=4)
        # return jsonPath

    def codeSwitch(self,command):
        pythonVersion = int(sys.version[0:1])
        if pythonVersion < 3:
            try:
                command = command.decode('utf-8')
            except:
                pass
        return command
    
    def getGIFButtonData(self, button):
        # 获取按钮数据
        data = OrderedDict()
        data['label'] = button.label
        data['annotation'] = button.annotation
        data['image'] = button.icon
        data['sourceType'] = button.sourceType
        data['command'] = button.command
        data['doubleClickCommandSourceType'] = button.doubleClickCommandSourceType
        data['doubleClickCommand'] = button.doubleClickCommand
        data['ctrlCommand'] = button.ctrlCommand
        data['altCommand'] = button.altCommand
        data['shiftCommand'] = button.shiftCommand
        data['ctrlAltCommand'] = button.ctrlAltCommand
        data['altShiftCommand'] = button.altShiftCommand
        data['ctrlShiftCommand'] = button.ctrlShiftCommand
        data['ctrlAltShiftCommand'] = button.ctrlAltShiftCommand
        data['dragCommand'] = button.dragCommand
        data['altDragCommand'] = button.altDragCommand
        data['shiftDragCommand'] = button.shiftDragCommand
        data['ctrlDragCommand'] = button.ctrlDragCommand
        data['size'] = button.size
        data['menuShowCommand'] = button.menuShowCommand
        data['menuItem'] = OrderedDict()
    
        for index, i in enumerate(button.menu.actions()):
            menuData = OrderedDict()
            if i.__class__.__name__ == 'Separator':
                data['menuItem'][index] = 'separator'
            elif i.__class__.__name__ == 'gifIconMenuAction':
                menuData['label'] = i.label
                menuData['command'] = i.command
                menuData['annotation'] = i.annotation
                menuData['image'] = i.iconPath
                menuData['sourceType'] = i.sourceType
                data['menuItem'][index] = menuData
        return data

    def getInternalIconDict(self):
        InternalIconDict = {}
        # InternalIconDict['InternalIcon'] = {}

        # # 获取所有内部图标
        # InternalIcon = resourceManager(nameFilter="*")
        # for i in InternalIcon:
        #     InternalIconDict['InternalIcon'][i] = 1

        # 获取所有插件图标
        InternalIconDict['plugIcon'] = {}
        for module in mel.eval('moduleInfo -listModules'):
            iconsPath = mel.eval('moduleInfo -path -mn "'+module+'"') + '/icons/'
            if os.path.exists(iconsPath):
                for root, dirs, files in os.walk(iconsPath):
                    for fileName in files:
                        # 值为图片的绝对路径
                        InternalIconDict['plugIcon'][fileName] = os.path.join(root, fileName)  # 值为图片的绝对路径

        # 获取maya 安装目录下icons文件夹里的图标
        mayaIconPath = os.environ['MAYA_LOCATION'] + '/icons/'
        for root, dirs, files in os.walk(mayaIconPath):
            for fileName in files:
                InternalIconDict['plugIcon'][fileName] = os.path.join(root, fileName)

        return InternalIconDict

    def findIconImage(self, imagePath, InternalIconDict):
        if imagePath is None:
            imagePath = 'white/undetected.png'
            return imagePath
        if os.path.exists(imagePath):
            return imagePath
        # 如果imagePath不存在,则查找icons文件夹
        else:
            if ':\\' in imagePath:
                if mel.eval('resourceManager -nameFilter '+imagePath.replace(':\\', '')):
                    pass
                elif imagePath.replace(':\\', '') in InternalIconDict['plugIcon']:
                    imagePath = InternalIconDict['plugIcon'][imagePath.replace(':\\', '')]
            else:
                if mel.eval('resourceManager -nameFilter '+imagePath):
                    imagePath = ':\\'+imagePath
                elif imagePath in InternalIconDict['plugIcon']:
                    imagePath = InternalIconDict['plugIcon'][imagePath]
                else:
                    imagePath = ':\\'+imagePath 
        return imagePath

    def loadShelfData(self, shelfData):
        '''
        shelfData: dict
        '''
        data = shelfData['shelfData']

        # 获取所有图标字典
        InternalIconDict = self.getInternalIconDict()

        for shelfButtonName in data.keys():
            if 'separator' in data[shelfButtonName] or 'Separator' in data[shelfButtonName]:
                self.addSeparator()
            else:
                shelfButtonData = data[shelfButtonName]
                if isinstance(shelfButtonData, dict):
                    if 'image' in shelfButtonData.keys():
                        imagePath = shelfButtonData['image']
                        imagePath = self.findIconImage(imagePath, InternalIconDict)
                    self.addButton(
                        label=shelfButtonData['label'],
                        annotation=shelfButtonData['annotation'],
                        icon=imagePath,
                        sourceType=shelfButtonData['sourceType'],
                        command=shelfButtonData['command'],
                        doubleClickCommand=shelfButtonData['doubleClickCommand'],
                        doubleClickCommandSourceType=shelfButtonData['doubleClickCommandSourceType'],
                        menuShowCommand=shelfButtonData['menuShowCommand'] if 'menuShowCommand' in shelfButtonData.keys() else '',
                        ctrlCommand=shelfButtonData['ctrlCommand'] if 'ctrlCommand' in shelfButtonData.keys() else '',
                        altCommand=shelfButtonData['altCommand'] if 'altCommand' in shelfButtonData.keys() else '',
                        shiftCommand=shelfButtonData['shiftCommand'] if 'shiftCommand' in shelfButtonData.keys() else '',
                        ctrlAltCommand=shelfButtonData['ctrlAltCommand'] if 'ctrlAltCommand' in shelfButtonData.keys() else '',
                        altShiftCommand=shelfButtonData['altShiftCommand'] if 'altShiftCommand' in shelfButtonData.keys() else '',
                        ctrlShiftCommand=shelfButtonData['ctrlShiftCommand'] if 'ctrlShiftCommand' in shelfButtonData.keys() else '',
                        ctrlAltShiftCommand=shelfButtonData['ctrlAltShiftCommand'] if 'ctrlAltShiftCommand' in shelfButtonData.keys() else '',
                        dragCommand=shelfButtonData['dragCommand'] if 'dragCommand' in shelfButtonData.keys() else '',
                        altDragCommand=shelfButtonData['altDragCommand'] if 'altDragCommand' in shelfButtonData.keys() else '',
                        shiftDragCommand=shelfButtonData['shiftDragCommand'] if 'shiftDragCommand' in shelfButtonData.keys() else '',
                        ctrlDragCommand=shelfButtonData['ctrlDragCommand'] if 'ctrlDragCommand' in shelfButtonData.keys() else ''
                    )
                    if 'menuItem' in shelfButtonData.keys():
                        if shelfButtonData['menuItem'] is not None:
                            for menuItemName in shelfButtonData['menuItem'].keys():
                                if shelfButtonData['menuItem'][menuItemName] is not None:
                                    menuItemData = shelfButtonData['menuItem'][menuItemName]
                                    if menuItemData == 'separator':
                                        self.gifButton.menu.addSeparator()
                                    else:
                                        self.gifButton.addMenuItem(
                                            label=menuItemData['label'],
                                            command=menuItemData['command'],
                                            annotation=menuItemData['annotation'],
                                            icon=menuItemData['image'],
                                            sourceType=menuItemData['sourceType']
                                        )
                    self.gifButton.addDefaultMenuItems()

    def loadGifShelf(self):
        # 打开文件对话框
        jsonPath = mel.eval('fileDialog2 -fm 1 -ff "*.json" -okc "导入"')[0]
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

        # 查询 shelfName 是否存在 shelfTabLayout -q -ca $self.gShelfTopLevel
        if shelfName not in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
            mel.eval('addNewShelfTab("'+shelfName+'")')
        else:
            # 弹出窗口
            if self.language == 0:
                result = mel.eval('confirmDialog -title "警告" -message "工具栏已存在,是否覆盖?" -button "Yes" -button "No" -defaultButton "Yes" -cancelButton "No" -dismissString "No";')
            elif self.language == 1:
                result = mel.eval('confirmDialog -title "Warning" -message "The shelf already exists, do you want to overwrite it?" -button "Yes" -button "No" -defaultButton "Yes" -cancelButton "No" -dismissString "No";')
            # result = confirmDialog(
            #     title=u'警告',
            #     message=u'工具栏已存在,是否覆盖?',
            #     button=['Yes', 'No'],
            #     defaultButton='Yes',
            #     cancelButton='No',
            #     dismissString='No'
            # )
            if result == 'No':
                return

        evalCode = 'shelfTabLayout -e -st '+shelfName+' $gShelfTopLevel;'
        mel.eval(evalCode)
        self.shelfManagers[shelfName] = ShelfButtonManager(self.language)  # 使用字典保存每个 shelf 的 ShelfButtonManager 实例
        self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()
        if mel.eval('shelfLayout -q -ca '+shelfName) is not None:
            for i in mel.eval('shelfLayout -q -ca '+shelfName):
                mel.eval('deleteUI '+i)
            try:
                for i in self.shelfManagers[shelfName].getButtonList()[1]:
                    i.deleteLater()
            except:
                pass
        self.shelfManagers[shelfName].loadShelfData(jsonData)
        self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()
    
    def autoLoadGifShelf(self, jsonPath):
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
        # 查询 shelfName 是否存在 shelfTabLayout -q -ca $self.gShelfTopLevel
        if shelfName not in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
            mel.eval('addNewShelfTab("'+shelfName+'")')

        evalCode = 'shelfTabLayout -e -st '+shelfName+' $gShelfTopLevel;'
        mel.eval(evalCode)
        self.shelfManagers[shelfName] = ShelfButtonManager(self.language)  # 使用字典保存每个 shelf 的 ShelfButtonManager 实例
        self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()
        if mel.eval('shelfLayout -q -ca '+shelfName) is not None:
            for i in shelfLayout(shelfName, q=True, ca=True):
                mel.eval('deleteUI '+i)
            try:
                for i in self.shelfManagers[shelfName].getButtonList()[1]:
                    i.deleteLater()
            except:
                pass
        self.shelfManagers[shelfName].loadShelfData(jsonData)
        self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()

    def saveGifShelf(self):
        # 打开文件对话框
        jsonPath = self.OneToolsDataDir + 'shelf_'+self.currentShelf+'.json'
    
        self.buttonList = self.getButtonList()[1]
        data = OrderedDict()
        for index, i in enumerate(self.buttonList):
            if i.__class__.__name__ == 'GIFButton':
                data[index] = self.getGIFButtonData(i)
            elif i.__class__.__name__ == 'Separator':
                data[index] = 'separator'
        # 写入json文件
        jsonData = OrderedDict()
        jsonData['shelfName'] = self.currentShelf
        jsonData['shelfData'] = data
        with codecs.open(jsonPath, 'w', 'utf-8') as f:
            json.dump(jsonData, f, ensure_ascii=False, indent=4)
        mel.eval(u'print("// 结果: '+jsonPath+'")')

    def autoSaveGifShelf(self):
        '''
        查询所有工具架
        保存拥有仅GIFButton的工具架
        '''
        currentShelf = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')
        mayaVersion = int(mel.eval('getApplicationVersionAsFloat'))
        shelfDataDir = self.OneToolsDataDir

        for jsonName in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
            # shelfTabLayout(self.gShelfTopLevel,e=True, st=jsonName) # 切换工具栏，但使用python出错，会多出很多没用的，改用mel
            evalCode = 'shelfTabLayout -e -st '+jsonName+' $gShelfTopLevel;'
            mel.eval(evalCode)
            if mel.eval('shelfLayout -q -ca '+jsonName) is not None:
                for i in mel.eval('shelfLayout -q -ca '+jsonName):
                    if mayaVersion < 2022:
                        if i != '':
                            break
                    else:
                        if 'QPushButton' not in i: # 只要存在不是QPushButton的按钮就跳过工具栏
                            break
                else:
                    jsonPath = shelfDataDir + 'shelf_'+jsonName+'.json'
                    buttonList = ShelfButtonManager(self.language).getButtonList()[1]
                    data = OrderedDict()
                    for index, i in enumerate(buttonList):
                        if i.__class__.__name__ == 'GIFButton':
                            data[index] = self.getGIFButtonData(i)
                        elif i.__class__.__name__ == 'Separator':
                            data[index] = 'separator'
                    # 写入json文件
                    jsonData = OrderedDict()
                    jsonData['shelfName'] = jsonName
                    jsonData['shelfData'] = data
                    with codecs.open(jsonPath, 'w', 'utf-8') as f:
                        json.dump(jsonData, f, ensure_ascii=False, indent=4)
                    mel.eval(u'print("// 结果: '+jsonPath+'")')
        # 切换回当前工具栏
        mel.eval('shelfTabLayout -e -st '+currentShelf+' $gShelfTopLevel;')

def main():
    sys.dont_write_bytecode = True
    
    # mel.eval('workspaceControl -e -ih 58 -minimumHeight 58 -heightProperty "fixed" "Shelf";global string $gPlayBackSlider;timeControl -e -h 28 $gPlayBackSlider;')
    if 'Custom' in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
        mel.eval('deleteUI Custom')
    mel.eval('addNewShelfTab("Custom")')
    
    if "Custom" not in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
        mel.eval('addNewShelfTab("Custom")')
    else:
        mel.eval('shelfTabLayout -e -st Custom $gShelfTopLevel;')

    shelf_button_manager = ShelfButtonManager(0) # 切换shelf需要初始化 ShelfButtonManager
    
    # 手动添加按钮
    shelf_button_manager.addButton(
        icon="siri.gif",
        command='print("siri")',
        ctrlCommand='print("Ctrl Clicked!")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addSeparator()

    shelf_button_manager.addButton(
        icon="cat4.gif",
        command='print("cat4")',
        ctrlCommand='print("Ctrl Clicked!")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addButton(icon="cat3.gif",command='print("cat3")')
    # 添加弹出菜单
    shelf_button_manager.gifButton.addMenuItem(
        label=u"自定义菜单项",
        command=u'warning(u"自定义菜单项")',
        icon="white/Custom.png",
        annotation=u"这是一个自定义菜单项"
    )
    # 添加分隔符
    shelf_button_manager.gifButton.menu.addSeparator()
    # 添加默认菜单项
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addButton(
        icon="cat2.gif",
        annotation=u'test',
        command='print("cat2")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()

    shelf_button_manager.addButton(
        icon="cat1.gif",
        annotation=u'annotateInfo',
        command='print("cat1")'
    )
    shelf_button_manager.gifButton.addDefaultMenuItems()
