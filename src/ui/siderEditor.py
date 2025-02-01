# -*- coding: utf-8 -*-
import os
import sys
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from collections import OrderedDict

from ..utils.KeywordHighlighter import *
from ..utils.switchLanguage import *
from ..utils import runCommand


ICONPATH = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src/ui', 'icons/')

from ..ui.mayaMQT import maya_main_window
class siderEditorWindow(QDialog):
    def __init__(self, editSider, language, parent=maya_main_window()):
        super().__init__(parent)
        self.editSider = editSider
        self.language = language if language else 0
        self.setWindowTitle(sl(u'滑块编辑器', self.language))

        self.golbalLayout = QVBoxLayout(self)
        self.setLayout(self.golbalLayout)
        self.golbalLayout.setContentsMargins(0, 0, 0, 0)
        self.golbalLayout.setSpacing(0)

    #     self.initUI()

    # def initUI(self):
    #     self.golbalLayout.addWidget(self.editSider)