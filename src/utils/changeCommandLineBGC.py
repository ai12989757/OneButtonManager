# -*- coding: utf-8 -*-
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
# -*- coding: utf-8 -*-
import maya.OpenMayaUI as omui
from maya import cmds
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

try:
    from PySide6.QtWidgets import QWidget
except ImportError:
    from PySide2.QtWidgets import QWidget

# ! 这个函数可以实现将 Maya 的 UI 转换为 Qt 的 QWidget 组件 
def mayaToQT(name):
    ptr = omui.MQtUtil.findControl(name)
    if ptr is None:
        ptr = omui.MQtUtil.findLayout(name)
    if ptr is None:
        ptr = omui.MQtUtil.findMenuItem(name)
    if ptr is not None:
        return wrapInstance(int(ptr), QWidget)

class ChangeCommandLineBGC():
    '''
    maya打开时自动加载了
    commandLineBG = changeCommandLineBGC.ChangeCommandLineBGC()
    调用时直接使用 commandLineBG.setBGColor('#ff5a5a', flicker=True)
    '''
    def __init__(self):
        
        '''
        初始化得到命令行输出控件 QLineEdit
        连接 textChanged 信号，当文本中包含特定字符时改变背景颜色
        '''
        self.outMessageUI = None
        self.init()

    # 初始化
    def init(self):
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'outMessageUI':
                self.outMessageUI = widget
                return
            
        if not self.outMessageUI:
            self.set_outMessageUI()

    def set_outMessageUI(self):
        maya_version = cmds.about(version=True)
        self.commandLineUI = mayaToQT('commandLine1')
        self.outMessageUI = None
        # 获取 commandLineUI 下的所有子控件
        for child in self.commandLineUI.children():
            if maya_version >= '2025':
                if isinstance(child, QWidget):
                    for i in child.children():
                        if isinstance(i, QLineEdit):
                            # 如果 line 是可编辑的
                            if i.isReadOnly():
                                self.outMessageUI = i
                                break
            else:
                # 如果是 QLineEdit 类型的控件
                if isinstance(child, QLineEdit):
                    # 如果 line 是可编辑的
                    if child.isReadOnly():
                        self.outMessageUI = child
                        break
        if not self.outMessageUI:
            return
        self.outMessageUI.setObjectName('outMessageUI')
        self.outMessageUI.textChanged.connect(None)
        self.outMessageUI.textChanged.connect(self.textChangedChangeBGColor)

    def flickerBG(self, color, times=2):
        '''
        闪烁背景颜色
        args:
            color: str 颜色 '#ff5a5a' or 'red' or 'rgb(255, 90, 90)' or 'rgba(255, 90, 90, 255)'
            times: int 闪烁次数 默认 2 次
        '''
        index = 0
        def flicker():
            nonlocal index, times
            if index < times:
                if self.outMessageUI.styleSheet() is None or self.outMessageUI.styleSheet() == '':
                    self.outMessageUI.setStyleSheet(f'QLineEdit {{ background-color: {color}; color: #2b2b2b;}}')
                    index += 1
                else:
                    self.outMessageUI.setStyleSheet('')
                QTimer.singleShot(200, flicker)
        flicker()

    def setBGColor(self, color, flicker=False):
        '''
        设置背景颜色
        args:
            color: str 颜色 '#ff5a5a' or 'red' or 'rgb(255, 90, 90)' or 'rgba(255, 90, 90, 255)'
            flicker: bool 是否闪烁 默认 False
        '''
        if flicker:
            self.flickerBG(color=color)
        else:
            self.outMessageUI.setStyleSheet(f'QLineEdit {{ background-color: {color}; color: #2b2b2b;}}')

    def textChangedChangeBGColor(self):
        '''
        根据文本内容改变背景颜色
        '''
        text = self.outMessageUI.text()
        if text:
            if text.startswith('// Error: ') or text.startswith(u'// 错误: ') or text.startswith('\n// Error: ') or text.startswith(u'\n// 错误: '):
                self.setBGColor('#ff5a5a')
            elif text.startswith('// Warning: ') or text.startswith(u'// 警告: ') or text.startswith('\n// Warning: ') or text.startswith(u'\n// 警告: '):
                self.setBGColor('#dcce87')
            elif text.startswith('// Info: ') or text.startswith(u'// 信息: ') or text.startswith('\n// Info: ') or text.startswith(u'\n// 信息: '):
                self.setBGColor('#00BFFF')
            elif(
                text.startswith('// Success: ') or text.startswith('\n// Success: ') or text.startswith(u'// 成功: ') or text.startswith(u'\n// 成功: ')
                or text.startswith('// Finished: ') or text.startswith('\n// Finished: ') or text.startswith(u'// 完成: ') or text.startswith(u'\n// 完成: ')
                ):
                self.setBGColor('#5aff5a')
            else:
                self.outMessageUI.setStyleSheet('')
        else:
            self.outMessageUI.setStyleSheet('')

    def OnePrint(self, message, color=None, flicker=False):
        '''
        一次性打印信息
        args:
            message: str 信息
            color: str 颜色 '#ff5a5a' or 'red' or 'rgb(255, 90, 90)' or 'rgba(255, 90, 90, 255)'
        '''
        print(message)
        self.outMessageUI.setText(message)
        if color:
            self.setBGColor(color)
        if flicker:
            if not color:
                if message.startswith('// Error: ') or message.startswith(u'// 错误: ') or message.startswith('\n// Error: ') or message.startswith(u'\n// 错误: '):
                    color = '#ff5a5a'
                elif message.startswith('// Warning: ') or message.startswith(u'// 警告: ') or message.startswith('\n// Warning: ') or message.startswith(u'\n// 警告: '):
                    color = '#dcce87'
                elif message.startswith('// Info: ') or message.startswith(u'// 信息: ') or message.startswith('\n// Info: ') or message.startswith(u'\n// 信息: '):
                    color = '#00BFFF'
                elif message.startswith('// Success: ') or message.startswith('\n// Success: ') or message.startswith(u'// 成功: ') or message.startswith(u'\n// 成功: '):
                    color = '#5aff5a'
            if color:
                self.flickerBG(color)