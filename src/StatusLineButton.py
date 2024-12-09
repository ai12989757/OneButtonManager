'''
import sys
from pymel.core import *
from importlib import reload

sys.dont_write_bytecode = True
PATH = r'D:/MELcopy/OneTools/tools/OneButtonManager/src'
if PATH not in sys.path:
    sys.path.append(PATH)
if 'StatusLineButton' not in sys.modules:
    import StatusLineButton
reload(StatusLineButton)
StatusLineButtonInfo = StatusLineButton.StatusLineButton()
'''
import os
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
from pymel.core import *

# iconPath = 'D:/MELcopy/OneTools/tools/OneButtonManager/icons/'
iconPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../icons/')
mayaVersion = mel.eval('getApplicationVersionAsFloat')
def StatusLineButton():
    icon = iconPath.replace('\\', '/').replace('/src/..', '') + 'white/info.png'
    print(icon)
    iconPix = QPixmap(icon)
    iconW = iconPix.width() * 23 / iconPix.height()
    if layout('MainStatusLineLayout',q=True,ex=True):
        setParent(layout(layout('MainStatusLineLayout',q=True,ca=True)[0],q=True,ca=True)[0]) # 状态行左边的布局
        iconName = 'OneButtonManager_StatusLineButton'
        if not iconTextButton(iconName,q=True,ex=True):
            iconTextButton(iconName,h=23,w=iconW,image=icon,style='iconOnly',command='print("Hello World")')
    StatusLineButtonPrt = omui.MQtUtil.findControl(iconName)
    StatusLineButton = wrapInstance(int(StatusLineButtonPrt), QWidget)

    return StatusLineButton