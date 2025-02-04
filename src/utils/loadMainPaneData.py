import json
import codecs # 用于解决中文乱码问题
from collections import OrderedDict # 有序字典
from ..widgets.GIFWidget import GIFButtonWidget
from ..widgets.Separator import Separator
from ..widgets import colorWidget
from ..ui import MainPaneDock
try:
    reload(MainPaneDock)
except:
    from importlib import reload
    reload(MainPaneDock)
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

def loadToolsData(toolsData):
    toolName = toolsData['ToolName']
    toolSttting = toolsData['ToolSetting']
    alignment = toolSttting['alignment']
    toolUi = MainPaneDock.mainUI(alignment=alignment)
    if alignment == 'top' or alignment == 'bottom':
        HorV = 'v'
    elif alignment == 'left' or alignment == 'right':
        HorV = 'h'
    toolData = toolsData['ToolData']
    for key in toolData.keys():
        if key == 'logo':
            pass
            # if not toolData[key]:
            #     continue
            # logoWidget = GIFButtonWidget(**toolData[key])
            # toolUi.layout1.addWidget(logoWidget)
        elif key == 'colorWidget':
            if not toolData[key]:
                continue
            for color in toolData[key]:
                colorIetm = colorWidget.ColorWidget(color=color, alignment=alignment)
                colorIetm.tranSub.hide()
                colorIetm.background_opacity = 0
                colorIetm.border_opacity = 0
                colorIetm.update()
                toolUi.layout2.addWidget(colorIetm)
                for i in toolData[key][color].keys():
                    buttonData = toolData[key][color][i]
                    if buttonData == 'separator' or buttonData == 'Separator':
                        colorIetm.addSeparator()
                    else:
                        # 确保 buttonData 是字典类型
                        if isinstance(buttonData, dict):
                            button = GIFButtonWidget(
                                icon=buttonData['image'] if 'image' in buttonData else None,
                                size=buttonData['size'] if 'size' in buttonData else 38,
                                dragMove=buttonData['dragMove'] if 'dragMove' in buttonData else True,
                                tearOff=buttonData['tearOff'] if 'tearOff' in buttonData else False,
                                alignment=HorV,
                                label=buttonData['label'] if 'label' in buttonData else None,
                                annotation=buttonData['annotation'] if 'annotation' in buttonData else None,
                                command=buttonData['command'] if 'command' in buttonData else {'click': ['python',None]}
                            )
                            colorIetm.colorLayout.addWidget(button)
                            if 'menuItem' in buttonData:
                                if buttonData['menuItem']:
                                    for j in buttonData['menuItem'].keys():
                                        menuData = buttonData['menuItem'][j]
                                        if menuData == 'Separator':
                                            button.addSeparator()
                                        else:
                                            button.addMenuItem(
                                                icon=menuData['image'] if 'image' in menuData else None,
                                                label=menuData['label'] if 'label' in menuData else None,
                                                annotation=menuData['annotation'] if 'annotation' in menuData else None,
                                                command=menuData['command'] if 'command' in menuData else {'click': ['python',None]}
                                            )
                            button.addDefaultMenuItems()
        elif key == 'Setting':
            if not toolData[key]:
                continue
            settingButton = GIFButtonWidget(**toolData[key])
            toolUi.layout3.addWidget(settingButton)
        toolUi.show()

def loadTools():
    # # 打开文件对话框
    # fileDialog = QFileDialog()
    # fileDialog.setFileMode(QFileDialog.ExistingFile)
    # fileDialog.setNameFilter("JSON Files (*.json)")
    # fileDialog.setViewMode(QFileDialog.Detail)
    # if fileDialog.exec_():
    #     filePath = fileDialog.selectedFiles()[0]
    #     with codecs.open(filePath, 'r', 'utf-8') as f:
    #         toolsData = json.load(f, object_pairs_hook=OrderedDict)
    #         self.loadToolsData(toolsData)
    filePath = 'E:/OneButtonManager/src/AniBotPro/AniBotPro.json'
    with codecs.open(filePath, 'r', 'utf-8') as f:
        toolsData = json.load(f, object_pairs_hook=OrderedDict)
        loadToolsData(toolsData)