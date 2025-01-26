from maya import mel
from ..ui.mayaMQT import mayaToQT

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    
shelfTAP = mayaToQT("ShelfLayout")
shelfTabWidget = None
for child in shelfTAP.children():
    if child.__class__.__name__ == 'QTabWidget':
        shelfTabWidget = child
        break

# 新 shelfStyle 函数增加了检索支持，不存在则不设置，不会报错
shelfStyleFuncFile = __file__.replace('test.py', 'shelfStyle.mel')
mel.eval('source "{}"'.format(shelfStyleFuncFile))


menuTab = QWidget()
menuLayout = QHBoxLayout()
shelfTabWidget.addTab(menuTab, 'testssss')
menuTab.setLayout(menuLayout)