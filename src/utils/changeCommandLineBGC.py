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
        
commandLineUI = mayaToQT('commandLine1')
outMessageUI = None
# 获取 commandLineUI 下的所有子控件
for child in commandLineUI.children():
    # 如果是 QLineEdit 类型的控件
    if isinstance(child, QLineEdit):
        # 如果 line 是可编辑的
        if child.isReadOnly():
            outMessageUI = child
            break

def textChangedChangeBGColor():
    # 获取控件文本
    text = outMessageUI.text()
    # 如果文本包含 'Error'，则设置控件样式
    if text.startswith('// Error: ') or text.startswith('// 错误: ') or text.startswith('\n// Error: ') or text.startswith('\n// 错误: '):
        outMessageUI.setStyleSheet('QLineEdit { background-color: #ff5a5a; color: #2b2b2b; }')
    else:
        outMessageUI.setStyleSheet('')

outMessageUI.textChanged.connect(textChangedChangeBGColor)