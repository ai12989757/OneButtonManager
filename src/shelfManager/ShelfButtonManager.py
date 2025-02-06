# -*- coding: utf-8 -*-
import os
import sys
import json
import codecs
import datetime
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

from ..utils.switchLanguage import *
from ..utils.getBackShelfList import getBackShelfList
from ..widgets import GIFWidget, GIFAction, Separator
from ..ui import shelfRestoreWindow

try:
    reload(GIFWidget)
    reload(shelfRestoreWindow)
except:
    from importlib import reload
    reload(GIFWidget)
    reload(shelfRestoreWindow)

ICONPATH = __file__.replace('\\','/').replace('src/shelfManager/ShelfButtonManager.py', 'icons/')

class ShelfButtonManager(QWidget):
    mel.eval('int $sjkhs = `shelfTabLayout -q -h $gShelfTopLevel`;')
    mel.eval('workspaceControl -e -heightProperty "free" "Shelf"')
    def __init__(self,language=0):
        super(ShelfButtonManager, self).__init__()
        self.language = language # 0 简体中文, 1 English
        self.InternalIconDict = self.getInternalIconDict()

        self.shelfManagers = {} # 添加一个字典来保存每个 shelf 的 ShelfButtonManager 实例
        self.currentShelf = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')

        self.mayaVersion = mel.eval('getApplicationVersionAsFloat')

        self.PATH = os.path.dirname(os.path.abspath(__file__)) 
        self.PATH = self.PATH.replace('\\', '/')
        

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

        self.menu = None # 右击菜单
        self.shelf2DefUI = None # 还原工具栏的UI
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
        self.autoSetShelf()
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
                        try:
                            mel.eval('deleteUI '+i)
                        except:
                            pass
                    for i in self.shelfManagers[shelfName].getButtonList()[1]:
                        try:
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
        # 组件
        self.contextMenu.addSeparator()
        self.shelfComponentsAction = self.contextMenu.addAction(QIcon(ICONPATH + 'components/components.png'),sl(u"组件", abs(1 - self.language)))
        self.shelfComponentsMenu = QMenu()
        self.shelfComponentsAction.setMenu(self.shelfComponentsMenu)
        self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'components/clock.png'), sl(u"时钟", self.language), lambda: self.addComponent('clock')).setStatusTip(sl(u"时钟", self.language))
        self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'components/timing.png'), sl(u"秒表", self.language), lambda: self.addComponent('timing')).setStatusTip(sl(u"秒表", self.language))
        self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'components/stopwatch.png'), sl(u"倒计时", self.language), lambda: self.addComponent('countdown')).setStatusTip(sl(u"倒计时", self.language))
        self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'components/woodenFish.png'), sl(u"功德", self.language), lambda: self.addComponent('meritsVirtues')).setStatusTip(sl(u"功德", self.language))
        self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'components/DinoJump.png'), sl(u"小恐龙", self.language), lambda: self.addComponent('dinoGame')).setStatusTip(sl(u"小恐龙", self.language))
        self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'components/bilibili.png'), sl(u"bilibili粉丝", self.language), lambda: self.addComponent('bilibiliFans')).setStatusTip(sl(u"bilibili粉丝", self.language))
        #self.shelfComponentsMenu.addAction(QIcon(ICONPATH + 'siri.gif'), sl(u"Bad Apple", self.language), self.toGIF).setStatusTip(sl(u"敢试吗", self.language))
        badAppleAction = GIFAction.gifIconMenuAction(
            icon = ICONPATH + 'components/bad_apple.gif', 
            label = sl(u"Bad Apple",self.language), annotation = sl(u"敢试吗",self.language), 
            parent = self.shelfComponentsMenu,
            command = {'click':['function', lambda: self.addComponent('badApple')]}
            )
        self.shelfComponentsMenu.addAction(badAppleAction)
        # 工具栏设置
        self.contextMenu.addSeparator()
        self.shelfManagerAction = self.contextMenu.addAction(QIcon(ICONPATH + 'white/Setting.png'),sl(u"工具栏管理", abs(1 - self.language)))
        self.shelfManagerMenu = QMenu()
        self.shelfManagerAction.setMenu(self.shelfManagerMenu)
        self.shelfManagerMenu.addAction(QIcon(ICONPATH + 'white/Switch.png'), sl(u"转换工具栏", self.language), self.toGIF).setStatusTip(sl(u"点击转换当前工具栏", self.language))
        self.shelfManagerMenu.addAction(QIcon(ICONPATH + 'green/Restore.png'), sl(u"还原工具栏", self.language), self.toDef).setStatusTip(sl(u"点击还原当前工具栏", self.language))
        self.shelfManagerMenu.addAction(QIcon(ICONPATH + 'white/Save.png'), sl(u"保存工具栏", self.language), self.saveGifShelf).setStatusTip(sl(u"点击保存当前工具栏", self.language))
        self.shelfManagerMenu.addAction(QIcon(ICONPATH + 'white/Import.png'), sl(u"导入工具栏", self.language), self.loadGifShelf).setStatusTip(sl(u"点击导入工具栏", self.language))
        # 自动加载工具栏
        self.contextMenu.addSeparator()
        self.autoLoadAction = self.contextMenu.addAction(QIcon(':\\switchOff.png'), sl(u"自动加载工具栏", self.language), self.setAutoLoadJob)
        self.autoLoadAction.setStatusTip(sl(u"maya启动时自动加载data文件下的工具栏", self.language))
        self.autoLoadAction.switch = bool(False)
        # 自动保存工具栏
        self.autoSaveAction = self.contextMenu.addAction(QIcon(':\\switchOff.png'), sl(u"自动保存工具栏", self.language), self.setAutoSaveJob)
        self.autoSaveAction.setStatusTip(sl(u"maya关闭时自动保存当前工具栏", self.language))
        self.autoSaveAction.switch = bool(False)
        self.contextMenu.aboutToShow.connect(self.menuShowCheck) # 每次打开菜单时检查是否开启了自动加载工具栏、自动保存工具栏
        # 语言切换
        self.contextMenu.addSeparator()
        self.languageAction = self.contextMenu.addAction(QIcon(ICONPATH + 'white/Language.png'),sl(u"语言", abs(1 - self.language)))
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
        self.recycleMenu.addAction(QIcon(ICONPATH + 'red/Recycle.png'), sl(u"清空回收站",self.language), self.recycleDeleteAllButton)
        self.recycleMenu.addSeparator()
        for i in jsonData.keys():
            action = GIFAction.gifIconMenuAction(icon = jsonData[i]['image'], label = jsonData[i]['label'], annotation = jsonData[i]['annotation'], parent = self.recycleMenu)
            buttonRecycleEdit = QMenu()
            action.setMenu(buttonRecycleEdit)
            buttonRecycleEdit.addAction(QIcon(ICONPATH + 'green/Restore.png'), sl(u"还原",self.language), self.recycleRestoreButton).setStatusTip(sl(u"将此按钮重新添加到当前工具栏",self.language))
            buttonRecycleEdit.addAction(QIcon(ICONPATH + 'red/Delete.png'), sl(u"删除",self.language), self.recycleDeleteButton).setStatusTip(sl(u"从回收站彻底删除此按钮, 注意: 不可恢复",self.language))
            self.recycleMenu.addAction(action)
   
    def pasteButton(self):
        shelf_backup = mel.eval('internalVar -uad').replace('maya','OneTools/data/shelf_backup/')
        shelf_copy = shelf_backup + 'shelf_copy.json'

        with codecs.open(shelf_copy, 'r', encoding='utf-8') as f:
            jsonData = json.load(f)
        newButtonData = jsonData['shelfData']
        if newButtonData is None: return
        self.addButton(
            icon=newButtonData['image'],
            label=newButtonData['label'],
            annotation=newButtonData['annotation'],
            command=newButtonData['command']
        )
        
        if newButtonData['menuItem'] is not None and newButtonData['menuItem'] != {}:
            print(newButtonData['menuItem'])
            for i in newButtonData['menuItem'].keys():
                if newButtonData['menuItem'][i] == 'separator':
                    self.gifButton.menu.addSeparator()
                else:
                    self.gifButton.addMenuItem(
                        label=newButtonData['menuItem'][i]['label'],
                        command=newButtonData['menuItem'][i]['command'],
                        annotation=newButtonData['menuItem'][i]['annotation'],
                        icon=newButtonData['menuItem'][i]['image']
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
        buttonData = self.GIFButtonJsonDataSwitch(buttonData)
        buttonData['image'] = self.findIconImage(buttonData['image'], self.InternalIconDict)
        self.addButton(
            icon = buttonData['image'] if 'image' in buttonData.keys() else '',
            label = buttonData['label'] if 'label' in buttonData.keys() else '',
            annotation = buttonData['annotation'] if 'annotation' in buttonData.keys() else '',
            command = buttonData['command'] if 'command' in buttonData.keys() else ''
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
                            icon = buttonData['menuItem'][i]['image'] if 'image' in buttonData['menuItem'][i].keys() else ''
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
        currShelf = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')
        for shelf in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
            evalCode = 'shelfTabLayout -e -st '+shelf+' $gShelfTopLevel;'
            mel.eval(evalCode)
            self.shelfManagers[shelf] = ShelfButtonManager(self.language)
            self.shelfManagers[shelf].menu = self.shelfManagers[shelf].createContextMenu()
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
        mel.eval('shelfTabLayout -e -st '+currShelf+' $gShelfTopLevel')

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
                        mel.eval(u'print("// 结果: 开启自动加载工具栏\\n")')
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
                    if not any('autoSaveGifShelf' in job for job in mel.eval('scriptJob -lj')):
                        jboCode = 'scriptJob -e "quitApplication" "python(\\"from OneButtonManager.src.shelfManager import ShelfButtonManager\\\\nshelf_save = ShelfButtonManager.ShelfButtonManager('+str(self.language)+')\\\\nshelf_save.autoSaveGifShelf()\\")"'
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
                    if 'autoSaveGifShelf' in job and 'GifButton_AutoSave' in userSetup:
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
        self.addButton(
            icon='white/undetected.png',
            label='',
            annotation='',
            command={'click': ['python', '']}
            )
        self.gifButton.addDefaultMenuItems()
            
    def addButton(self, **kwargs):
        # 检查 icon 是否为绝对路径，如果不是则添加 iconPath
        icon = kwargs.get('icon', None)
        if icon and not os.path.isabs(icon) and ':\\' not in icon:
            icon = ICONPATH+icon
        size = kwargs.get('size', self.iconH)
        self.gifButton = GIFWidget.GIFButtonWidget(
            parent=self.shelfParent,
            icon=icon,
            label=kwargs.get('label', ""),
            annotation=kwargs.get('annotation', None),
            style=kwargs.get('style', "auto"),
            command=kwargs.get('command', None),
            size=size,
            dragMove=True,
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
        self.separator = Separator.Separator(parent=self.shelfParent,language=self.language,size=self.iconH)
        if self.mayaVersion < 2022:
            self.shelfLayoutInfo.addWidget(self.separator)

        elif self.mayaVersion >= 2022:
            # 使用winID作为按钮的名称
            self.separator.setObjectName('QPushButton'+str(self.separator.winId()))
            # 更改按钮的名字
            self.separatorButtonPrt = omui.MQtUtil.findControl(self.separator.objectName())
            omui.MQtUtil.addWidgetToMayaLayout(int(self.separatorButtonPrt), int(self.shelfParentPtr)) 
        self.separator.shelfLayoutInfo = self.shelfLayoutInfo
        self.separator.iconSizeValue = QSize(self.iconH, self.iconH)
        self.separator.setFixedSize(self.iconH, self.iconH)

    def getButtonList(self):
        self.buttonList = []
        for i in range(self.shelfLayoutInfo.count()):
            self.buttonList.append(self.shelfLayoutInfo.itemAt(i).widget())
        return self.shelfLayoutInfo,self.buttonList
    
    def getMayaShelfButtonData(self, mayaShelfButtonName):
        data = OrderedDict()
        try:
            data['label'] = mel.eval('shelfButton -q -label '+mayaShelfButtonName)
        except:
            data['label'] = None
        try:
            data['annotation'] = mel.eval('shelfButton -q -annotation '+mayaShelfButtonName)
        except:
            data['annotation'] = None
        data['image'] = mel.eval('shelfButton -q -image '+mayaShelfButtonName)
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
        if mel.eval('shelfLayout -q -ca '+self.currentShelf) is None:
            return
        shelfMel = mel.eval('internalVar -userShelfDir') + 'shelf_'+self.currentShelf+'.mel' # 当前 shelf 的 mel 文件
        shelf_backup = self.OneToolsDataDir + 'shelf_backup/' # 备份文件夹
        if not os.path.exists(shelf_backup):
            os.makedirs(shelf_backup)
        
        mel.eval('saveShelf("'+self.currentShelf+'", "'+shelfMel.replace('.mel','')+'")' ) # 保存当前 shelf

        # 使用robocopy备份文件 robocopy /e path file
        # 获取当前日期和时间
        current_datetime = datetime.datetime.now()
        # 格式化日期和时间
        formatted_datetime = current_datetime.strftime('%Y%m%d_%H%M%S')
        # 在文件名后添加日期时间
        shelf_backupFile = shelf_backup + 'shelf_' + self.currentShelf + '.mel.' + formatted_datetime
        os.system('robocopy /e '+mel.eval('internalVar -userShelfDir')+' '+shelf_backup+' shelf_'+self.currentShelf+'.mel')
        os.rename(shelf_backup + 'shelf_' + self.currentShelf + '.mel', shelf_backupFile)
        # aveAllShelves(self.gShelfTopLevel)
        self.buttonList = self.getButtonList()[1]
        # 新建字典保存按钮数据
        data = OrderedDict()
        for index,i in enumerate(self.buttonList):
            if i.__class__.__name__ == 'GIFButton' or i.__class__.__name__ == 'GIFButtonWidget':
                data[index] = self.getGIFButtonData(i)
            elif i.__class__.__name__ == 'Separator':
                data[index] = 'separator'
            elif i.__class__.__name__ == 'QFrame':
                data[index] = 'separator'
            elif i.__class__.__name__ == 'QPushButton' or i.__class__.__name__ == 'QWidget':
                if not i.objectName():
                    continue
                if 'separator' in i.objectName() or 'Separator' in i.objectName():
                    data[index] = 'separator'
                else:
                    if mel.eval('shelfButton -q -ex '+i.objectName()):
                        data[index] = self.getMayaShelfButtonData(i.objectName())
            else:
                if self.language == 0:
                    mel.eval(u'warning -n "未知类型: ' + i.__class__.__name__ + ', 请联系开发者"')
                elif self.language == 1:
                    mel.eval('warning -n "Unknown type: ' + i.__class__.__name__ + ', please contact the developer"')
                return

        # 保存按钮数据到json文件
        shelfData = OrderedDict()
        shelfData['shelfName'] = self.currentShelf
        shelfData['shelfData'] = data
        
        jsonPath = self.OneToolsDataDir + 'shelf_backup/shelf_'+self.currentShelf+'.json'
        with codecs.open(jsonPath, 'w', encoding='utf-8') as f:
            json.dump(shelfData, f, ensure_ascii=False, indent=4)
        os.rename(jsonPath,jsonPath+'.'+formatted_datetime)
        # 删除当前shelf的所有按钮
        for index,i in enumerate(self.buttonList):
            if i.__class__.__name__ == 'GIFButton' or i.__class__.__name__ == 'Separator' or i.__class__.__name__ == 'GIFButtonWidget':
                i.deleteLater()
            elif i.__class__.__name__ == 'QFrame':
                data[index] = 'separator'
                mel.eval('deleteUI '+i.objectName())
            elif i.__class__.__name__ == 'QPushButton' or i.__class__.__name__ == 'QWidget':
                try:
                    mel.eval('deleteUI '+i.objectName())
                except:
                    i.deleteLater()
        #oldShelfButtonList = shelfLayout(self.currentShelf, q=True, ca=True)
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
        # 根据保存备份的 mel 文件恢复 shelf
        shelf_backup = self.OneToolsDataDir + 'shelf_backup/' # 备份文件夹
        fileList = getBackShelfList(shelf_backup)

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
        
    def toJson(self):
        pass

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
        data['label'] = button.labelText
        data['annotation'] = button.annotation
        data['image'] = button.iconPath
        data['command'] = button.command
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
            imagePath = ICONPATH+'white/undetected.png'
            return imagePath
        if imagePath.lower().endswith('.gif'):
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
                try:
                    if mel.eval('resourceManager -nameFilter '+imagePath):
                        imagePath = ':\\'+imagePath
                    elif imagePath in InternalIconDict['plugIcon']:
                        imagePath = InternalIconDict['plugIcon'][imagePath]
                    # else:
                    #     imagePath = ':\\'+imagePath 
                except:
                    pass
        return imagePath
    
    def GIFButtonJsonDataSwitch(self, data):
        if 'sourceType' not in data.keys():
            return data
        newDict = {}
        if 'size' in data.keys(): newDict['size'] = data['size']
        if 'label' in data.keys(): newDict['label'] = data['label']
        if 'annotation' in data.keys(): newDict['annotation'] = data['annotation']
        if 'image' in data.keys(): newDict['image'] = data['image']
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
            'menuShow': ['python', menuShowCommand]
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
            elif 'Component' in data[shelfButtonName]:
                self.addComponent(data[shelfButtonName][1])
            else:
                shelfButtonData = data[shelfButtonName]
                shelfButtonData = self.GIFButtonJsonDataSwitch(shelfButtonData)
                if isinstance(shelfButtonData, dict):
                    if 'image' in shelfButtonData.keys():
                        imagePath = shelfButtonData['image']
                        imagePath = self.findIconImage(imagePath, InternalIconDict)
                    self.addButton(
                        label=shelfButtonData['label'],
                        annotation=shelfButtonData['annotation'],
                        icon=imagePath,
                        size=self.iconH,
                        command=shelfButtonData['command']
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
                                            icon=menuItemData['image']
                                        )
                    self.gifButton.addDefaultMenuItems()

    def loadGifShelf(self):
        # 打开文件对话框
        jsonPath = QFileDialog.getOpenFileName(self, u"打开文件", self.OneToolsDataDir, u"JSON文件(*.json)")[0]
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
            result = ''
            if self.language == 0:
                result = mel.eval(u'confirmDialog -title "警告" -message "工具栏已存在,是否覆盖?" -button "Yes" -button "No" -defaultButton "Yes" -cancelButton "No" -dismissString "No";')
            elif self.language == 1:
                result = mel.eval('confirmDialog -title "Warning" -message "The shelf already exists, do you want to overwrite it?" -button "Yes" -button "No" -defaultButton "Yes" -cancelButton "No" -dismissString "No";')
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
            for i in mel.eval('shelfLayout -q -ca '+shelfName):
                mel.eval('deleteUI '+i)
            try:
                for i in self.shelfManagers[shelfName].getButtonList()[1]:
                    i.deleteLater()
            except:
                pass
            
        self.shelfManagers[shelfName].loadShelfData(jsonData)
        self.shelfManagers[shelfName].menu = self.shelfManagers[shelfName].createContextMenu()

    def saveGifShelf(self):
        jsonPath = self.OneToolsDataDir + 'shelf_'+self.currentShelf+'.json'
    
        self.buttonList = self.getButtonList()[1]
        data = OrderedDict()
        for index, i in enumerate(self.buttonList):
            if i.__class__.__name__ == 'GIFButton' or i.__class__.__name__ == 'GIFButtonWidget':
                data[index] = self.getGIFButtonData(i)
            elif i.__class__.__name__ == 'Separator':
                data[index] = 'separator'
            elif i.__class__.__name__ == 'ComponentWidget':
                data[index] = ['Component', i.objectName().split('_')[-2]]
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
                        if i.__class__.__name__ == 'GIFButton' or i.__class__.__name__ == 'GIFButtonWidget':
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

    def addComponent(self, component):
        if component == 'badApple':
            self.addBadAppleComponent()
        elif component == 'clock':
            self.addClockComponent()
        elif component == 'timing':
            self.addTimingComponent()
        elif component == 'countdown':
            self.addCountdownComponent()
        elif component == 'meritsVirtues':
            self.addMeritsVirtuesComponent()
        elif component == 'dinoGame':
            self.addDinoGameComponent()
        elif component == 'bilibiliFans':
            self.addBilibiliFansComponent()

    # bad apple
    def addBadAppleComponent(self):
        mel.eval('int $sjkhs = `shelfTabLayout -q -h $gShelfTopLevel`;')
        mel.eval('workspaceControl -e -heightProperty "free" "Shelf"')
        mel.eval('workspaceControl -e -ih ($sjkhs+225) "Shelf"')

        from ..components import badAppleWidget
        gif_path = ICONPATH + 'components/bad_apple.gif'
        audio_path = ICONPATH + 'components/bad_apple.mp3'

        self.badAppleComponent = badAppleWidget.ComponentWidget(gif_path, audio_path)
        def closeBadAppleComponent():
            mel.eval('workspaceControl -e -ih ($sjkhs-20) "Shelf"')
            self.badAppleComponent.movie.stop()
            self.badAppleComponent.media_player.stop()
            self.badAppleComponent.deleteLater()
        self.badAppleComponent.menu.addAction(QIcon(ICONPATH + 'red/Delete.png'), u'关闭', closeBadAppleComponent)

        self.badAppleComponent.setObjectName('Component_badApple_'+str(self.badAppleComponent.winId()))
        self.badAppleComponentPrt = omui.MQtUtil.findControl(self.badAppleComponent.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(self.badAppleComponentPrt), int(self.shelfParentPtr))
        self.badAppleComponent.setFixedSize(QSize(400, 300))

    # 时钟
    def addClockComponent(self):
        from ..components import clockWidget
        self.clockComponent = clockWidget.ComponentWidget()
        self.clockComponent.setObjectName('Component_clock_'+str(self.clockComponent.winId()))
        self.clockComponentPrt = omui.MQtUtil.findControl(self.clockComponent.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(self.clockComponentPrt), int(self.shelfParentPtr))
        fact = 150/42
        self.clockComponent.setFixedSize(QSize(int(self.iconH*fact), self.iconH))
    
    # 计时器
    def addTimingComponent(self):
        from ..components import timingWidget
        self.timingComponent = timingWidget.ComponentWidget()
        self.timingComponent.setObjectName('Component_timing_'+str(self.timingComponent.winId()))
        self.timingComponentPrt = omui.MQtUtil.findControl(self.timingComponent.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(self.timingComponentPrt), int(self.shelfParentPtr))
        fact = 235/42
        self.timingComponent.setFixedSize(QSize(int(self.iconH*fact), self.iconH))

    # 倒计时
    def addCountdownComponent(self):
        from ..components import countdownWidget
        self.countdownComponent = countdownWidget.ComponentWidget()
        self.countdownComponent.setObjectName('Component_countdown_'+str(self.countdownComponent.winId()))
        self.countdownComponentPrt = omui.MQtUtil.findControl(self.countdownComponent.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(self.countdownComponentPrt), int(self.shelfParentPtr))
        fact = 235/42
        self.countdownComponent.setFixedSize(QSize(int(self.iconH*fact), self.iconH))
        self.countdownComponent.lcd_hours.setFixedSize(self.iconH, self.iconH)
        self.countdownComponent.lcd_minutes.setFixedSize(self.iconH, self.iconH)
        self.countdownComponent.lcd_seconds.setFixedSize(self.iconH, self.iconH)
        self.countdownComponent.lcd_ms.setFixedSize(int(self.iconH/42*63), self.iconH)

    # 功德
    def addMeritsVirtuesComponent(self):
        mel.eval('int $gongDe = 1;')
        self.addButton(
            icon=ICONPATH + 'components/woodenFish.png', 
            command={
                'leftPress': ['python','self.setIconImage("'+ICONPATH + 'components/woodenFishClicked.png")\nmel.eval(u\'print("\\\\n// 结果: 功德+"+$gongDe)\')\nmel.eval(\'$gongDe += 1;\')'],
                'leftRelease': ['python','self.setIconImage("'+ICONPATH + 'components/woodenFish.png")']
                }
            )
        self.gifButton.addDefaultMenuItems()

    # 谷歌恐龙游戏
    def addDinoGameComponent(self, size=42):
        def setWidgetSize(size):
            self.addDinoGameComponent(size=size)
            if size < 47:
                mel.eval('workspaceControl -e -ih ($sjkhs-20) "Shelf"')
            else:
                mel.eval('workspaceControl -e -ih ($sjkhs+{}) "Shelf"'.format(size-25))
        def closeDinoGameComponent():
            mel.eval('workspaceControl -e -ih ($sjkhs-20) "Shelf"')
            self.dinoGameComponent.close()
        from ..components.dinoGame import pysideMain
        self.dinoGameComponent = pysideMain.ComponentWidget(size=self.iconH)
        self.dinoGameComponent.menu.addAction(QIcon(), u'原始尺寸', lambda: setWidgetSize(size=300))
        self.dinoGameComponent.menu.addAction(QIcon(), u'小窗口', lambda: setWidgetSize(size=42))
        self.dinoGameComponent.menu.addAction(QIcon(ICONPATH+'red/Delete.png'), u'关闭', closeDinoGameComponent)
        self.dinoGameComponent.setObjectName('Component_dinoGame_'+str(self.dinoGameComponent.winId()))
        self.dinoGameComponentPrt = omui.MQtUtil.findControl(self.dinoGameComponent.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(self.dinoGameComponentPrt), int(self.shelfParentPtr))
        self.dinoGameComponent.setFixedSize(QSize(pysideMain.SCREEN_WIDTH, pysideMain.SCREEN_HEIGHT))

    # bilibili 粉丝
    def addBilibiliFansComponent(self):
        if self.mayaVersion < 2022:
            return
        from ..components import bilibiliFansWidget
        self.bilibiliFansComponent = bilibiliFansWidget.ComponentWidget(size=self.iconH)
        self.bilibiliFansComponent.setObjectName('Component_bilibiliFans_'+str(self.bilibiliFansComponent.winId()))
        self.bilibiliFansComponentPrt = omui.MQtUtil.findControl(self.bilibiliFansComponent.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(self.bilibiliFansComponentPrt), int(self.shelfParentPtr))
        self.bilibiliFansComponent.setFixedSize(QSize(self.bilibiliFansComponent.WIDTH, self.bilibiliFansComponent.SIZE))

    def addShelfWidget(self, widget):
        if widget is None:
            return
        if self.mayaVersion < 2022:
            self.shelfLayoutInfo.addWidget(widget)
        elif self.mayaVersion >= 2022:
            widget.setObjectName('OneShelf_'+widget.__class__.__name__+'_'+str(widget.winId()))
            widgetPrt = omui.MQtUtil.findControl(widget.objectName())
            omui.MQtUtil.addWidgetToMayaLayout(int(widgetPrt), int(self.shelfParentPtr))
        if hasattr(widget, 'SCREEN_WIDTH') and hasattr(widget, 'SCREEN_HEIGHT'):
            fact = widget.SCREEN_WIDTH/widget.SCREEN_HEIGHT
            widget.setFixedSize(QSize(int(self.iconH*fact), self.iconH))
        
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
