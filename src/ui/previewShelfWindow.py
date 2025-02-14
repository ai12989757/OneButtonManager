# -*- coding: utf-8 -*-
# 根据sehlf文件生成预览窗口
# 生成预览窗口的时候，会根据shelf文件中的信息，生成对应的控件
# 生成控件的时候，会根据文件文件的类型，生成对应的窗口 mel/json
import os
import json
import codecs
from collections import OrderedDict

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except:
    from shiboken2 import wrapInstance
from maya import mel, cmds
from ..widgets import GIFWidget, Separator

def GIFButtonJsonDataSwitch(data):
    if 'sourceType' not in data.keys():
        return data
    newDict = {}
    if 'size' in data.keys(): newDict['size'] = data['size']
    if 'label' in data.keys(): newDict['label'] = data['label']
    if 'annotation' in data.keys(): newDict['annotation'] = data['annotation']
    if 'image' in data.keys(): newDict['image'] = data['image']
    if not os.path.exists(data['image']) and ':\\' not in newDict['image']:
        try:
            if mel.eval('resourceManager -nameFilter "'+newDict['image']+'"'):
                newDict['image'] = ':\\'+newDict['image']
        except:
            pass
    newDict['command'] = {}
    sourceType = data['sourceType'] if 'sourceType' in data.keys() else 'mel'
    command = data['command'] if 'command' in data.keys() else ''
    doubleClick = data['doubleClickCommand'] if 'doubleClickCommand' in data.keys() else ''
    doubleClickSourceType = data['doubleClickCommandSourceType'] if 'doubleClickCommandSourceType' in data.keys() else 'mel'
    newDict['command'] = {
        'click': [sourceType, command],
        'doubleClick': [doubleClickSourceType, doubleClick],
    }
    newDict['menuItem'] = {}
    if 'menuItem'  in data.keys():
        if data['menuItem'] is not None:
            for item, value  in data['menuItem'].items():
                newDict['menuItem'][item] = {}
                newDict['menuItem'][item]['label'] = value['label']
                newDict['menuItem'][item]['annotation'] = value['annotation']
                newDict['menuItem'][item]['image'] = value['image']
                newDict['menuItem'][item]['command'] = {'click': [value['sourceType'],value['command']]}
    return newDict


def returnShelfData(shelfFile):
    """
    Returns the shelf data from the shelf file.
    """
    shelfFile = shelfFile.replace('\\', '/')
    shelfType = ''
    if '.mel' in shelfFile:
        shelfType = 'mel'
    elif '.json' in shelfFile:
        shelfType = 'json'
    else:
        return mel.eval('print("\\n// 错误: 不支持的文件类型 //")')

    if shelfType == 'mel':
        returnMelShelfData(shelfFile)
    elif shelfType == 'json':
        returnJsonShelfData(shelfFile)

def returnMelShelfData(shelfFile):
    shelfName = shelfFile.split('.mel')[0].split('/')[-1].replace('shelf_', '')
    if shelfName not in mel.eval('shelfTabLayout -q -ca $gShelfTopLevel'):
        mel.eval('addNewShelfTab("'+shelfName+'")')
    if mel.eval('shelfLayout -q -ca '+shelfName) is not None:
        for i in mel.eval('shelfLayout -q -ca '+shelfName):
            mel.eval('deleteUI '+i)
    mel.eval('setParent("'+shelfName+'")')
    mel.eval('source "'+shelfFile+'"')
    with open(shelfFile, 'r') as f:
        firstLine = f.readline()
    if 'global proc' not in firstLine:
        return mel.eval('ptint "// 错误: 该shelf文件内容有误 //"')
    funcName = firstLine.split('global proc ')[1].split(' ')[0]
    try:
        mel.eval('%s()' % funcName)
        return mel.eval('print("// 成功: '+shelfName+' 还原成功")')
    except:
        return mel.eval('ptint "// 错误: 该shelf文件内容有误 //"')
    
def returnJsonShelfData(shelfFile):
    data = {}
    try:
        with codecs.open(shelfFile, 'r', encoding='utf-8') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
    except:
        with open(shelfFile, 'r') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

    shelfName = data['shelfName']
    shelfData = data['shelfData']
    
    if cmds.shelfLayout(shelfName, ex=True):
        layoutChildren = cmds.shelfLayout(shelfName, q=True, fullPathName=True, ca=True)
        if layoutChildren:
            for child in layoutChildren:
                cmds.deleteUI(child)
    else:
        mel.eval('addNewShelfTab("'+shelfName+'")')
        #cmds.shelfTabLayout('gShelfTopLevel', e=True, selectTab=shelfName)
    cmds.setParent(shelfName)
    for value in shelfData.values():
        if value == 'separator':
            cmds.separator(style='shelf', visible=True)
        else:
            value = GIFButtonJsonDataSwitch(value)
            if ':\\' in value['image']:
                value['image'] = value['image'].replace(':\\', '')
            tempShelfButton = cmds.shelfButton(
                label=value['label'],
                annotation=value['annotation'],
                image=value['image'],
                sourceType=value['command']['click'][0],
                command=value['command']['click'][1]
            )
            if 'doubleClick' in value['command'].keys():
                cmds.shelfButton(
                    tempShelfButton,
                    edit=True,
                    sourceType=value['command']['doubleClick'][0],
                    doubleClickCommand=value['command']['doubleClick'][1]
                )
            if 'menuItem' in value.keys():
                if value['menuItem'] is not None:
                    pMenu = cmds.shelfButton(tempShelfButton,q=True, popupMenuArray=True)[0]
                    for item, itemValue in value['menuItem'].items():
                        cmds.menuItem(
                            parent=pMenu,
                            label=itemValue['label'],
                            annotation=itemValue['annotation'],
                            image=itemValue['image'],
                            command=itemValue['command']['click'][1],
                            sourceType=itemValue['command']['click'][0]
                        )
    from ..shelfManager import ShelfButtonManager
    ShelfButtonManager.ShelfButtonManager().autoSetShelf()

# 创建一个按钮编辑器窗口
def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class PreviewShelfWindow(QWidget):
    def __init__(self, parent=maya_main_window(), shelfFile=''):
        super(PreviewShelfWindow, self).__init__(parent)
        self.shelfFile = shelfFile.replace('\\', '/')
        self.shelfType = ''
        if '.mel' in shelfFile:
            self.shelfName = shelfFile.split('.mel')[0].split('/')[-1].replace('shelf_', '')
            self.shelfType = 'mel'
        elif '.json' in shelfFile:
            self.shelfName = shelfFile.split('.json')[0].split('/')[-1].replace('shelf_', '')
            self.shelfType = 'json'
        self.mPos = None
        self.setObjectName('PreviewShelfWindow')
        self.setWindowTitle('Shelf PreView')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)                  # 设置窗口无边框
        self.setAttribute(Qt.WA_DeleteOnClose) # 设置窗口关闭事件
        self.width = 800
        self.height = 54
        self.pw = QCursor.pos().x()-200
        self.ph = QCursor.pos().y()-60
        self.gobalLayout = QHBoxLayout()
        self.gobalLayout.setAlignment(Qt.AlignLeft|Qt.AlignCenter)
        self.gobalLayout.setContentsMargins(0, 0, 0, 0)
        self.gobalLayout.setSpacing(0)
        self.setLayout(self.gobalLayout)
        if self.shelfType == 'mel':
            self.melShelfPreView()
        elif self.shelfType == 'json':
            self.jsonShelfPreView()

    def paintEvent(self, event):
        # 设置圆角
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 10, 10) # 设置圆角路径
        path.translate(0.5, 0.5) # 修复边框模糊
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        # 创建一个 QPainter 对象来绘制边框
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # 抗锯齿
        pen = QPen(Qt.darkGray, 5)  # 设置描边颜色和宽度
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

    def event(self, eve):
        if eve.type() == QEvent.WindowDeactivate:
            self.close()
        return QWidget.event(self, eve)
    
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

    def melShelfPreView(self):
        cmds.setParent('Shelf')
        PreViewShelfLayout = cmds.shelfLayout()
        cmds.setParent(PreViewShelfLayout)
        try:
            mel.eval('source "%s"' % self.shelfFile)
        except:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return mel.eval('print "\\n// 错误: 该shelf文件内容有误 //"')
        # 读取文件第一行，获取函数名
        with open(self.shelfFile, 'r') as f:
            firstLine = f.readline()
        if 'global proc' not in firstLine:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return mel.eval('print "\\n// 错误: 该shelf文件内容有误 //"')
        # 获取函数名
        funcName = firstLine.split('global proc ')[1].split(' ')[0]
        # 执行函数
        try:
            mel.eval('%s()' % funcName)
        except:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return mel.eval('print "\\n// 错误: 该shelf文件内容有误 //"')
        layoutChildren = cmds.shelfLayout(PreViewShelfLayout, q=True, fullPathName=True, ca=True)
        if not layoutChildren:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return mel.eval('print "\\n// 错误: 该shelf文件内容有误 //"')
        self.width = 15
        for child in layoutChildren:
            if 'separator' in child or 'Separator' in child:
                self.width += 43
            else:
                self.width += cmds.shelfButton(child, q=True, width=True)
        #self.setFixedSize(self.width, self.height)
        self.gobalLayout.setContentsMargins(5, 5, 5, 0)
        self.setGeometry(self.pw, self.ph, self.width, self.height)
        ptr = omui.MQtUtil.findLayout(PreViewShelfLayout)
        PreViewShelfLayout = wrapInstance(int(ptr), QWidget)
        self.gobalLayout.addWidget(PreViewShelfLayout)

    def jsonShelfPreView(self):
        def addButton(**kwargs):
            button = GIFWidget.GIFButtonWidget(**kwargs)
            self.gobalLayout.addWidget(button)
            return button
        def addSeparator(**kwargs):
            separator = Separator.Separator(**kwargs)
            self.gobalLayout.addWidget(separator)

        data = {}
        try:
            with codecs.open(self.shelfFile, 'r', encoding='utf-8') as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
        except:
            with open(self.shelfFile, 'r') as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
        shelfData = data['shelfData']
        self.width = 52
        for data in shelfData.values():
            if data == 'separator':
                addSeparator(size=42)
                self.width += 42
            else:
                data = GIFButtonJsonDataSwitch(data)
                button = addButton(
                    icon=data['image'],
                    label=data['label'],
                    annotation=data['annotation'],
                    command=data['command'],
                    size=42,
                    dragMove=True
                )
                if 'menuItem' in data.keys():
                    if data['menuItem'] is not None:
                        for item, value in data['menuItem'].items():
                            button.addMenuItem(
                                icon=value['image'],
                                label=value['label'],
                                annotation=value['annotation'],
                                command=value['command']
                            )
                #print(button.width())
                self.width += button.width()
        self.gobalLayout.setContentsMargins(15, 3, 5, 0)
        self.setGeometry(self.pw, self.ph, self.width, self.height)

