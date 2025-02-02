from ..ui import MainPaneDock
from ..widgets.GIFWidget import GIFButtonWidget
import os
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

try:
    reload(MainPaneDock)
except:
    from importlib import reload
    reload(MainPaneDock)

try:
    ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/AniBotPro', 'icons/')
except:
    ICONPATH = 'E:/OneButtonManager/icons/'

class AniBotPro(QWidget):
    def __init__(self, parent=None, alignment='bottom'):
        super().__init__(parent)
        self.setWindowTitle('AniBotPro')
        self.UI = MainPaneDock.mainUI(alignment=alignment)
        self.layout1 = self.UI.layout1
        self.layout2 = self.UI.layout2
        self.layout3 = self.UI.layout3
        # logoButton = GIFButtonWidget(icon=ICONPATH+'logo/AniBotPo_logo.png',size=42, dragMove=False)
        # self.UI.layout1.addWidget(logoButton)
        self.UI.addColorLayout("Coral")
        # self.UI.addColorLayout("MediumPurple")
        # self.UI.addColorLayout("Pink")
        # button1 = GIFButtonWidget(icon=ICONPATH+'logo/AniBotPo_logo.png',size=42, dragMove=False)
        # self.layout3.addWidget(button1)
        