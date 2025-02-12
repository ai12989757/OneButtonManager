# -*- coding: utf-8 -*-
import os
from maya import mel
import maya.cmds as cmds
from ..utils import runCommand
try:
    reload(runCommand)
except:
    from importlib import reload
    reload(runCommand)
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

iconPath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src/widgets', 'icons/')

class gifIconMenuAction(QAction):
    def __init__(self, parent=None, **kwargs):
        super(gifIconMenuAction, self).__init__(parent)
        self.movie = None
        self.current_frame = None
        self.iconPath = kwargs.get('icon', None)
        self.label = kwargs.get('label', None)
        self.annotation = kwargs.get('annotation', None)
        self.command = kwargs.get('command', {})
        self.checkable = kwargs.get('checkable', False)

        if self.checkable:
            self.setCheckable(True)
            
        if self.iconPath:
            self.setIconImage(self.iconPath)
            
        if self.label:
            self.setText(self.label)
        
        if self.annotation:
            self.setStatusTip(self.annotation)

        if self.command:
            self.triggered.connect(lambda: runCommand.runCommand(self, self.command, 'click'))

    def updateIcon(self):
        self.current_frame = self.movie.currentPixmap()
        self.setIcon(QIcon(self.current_frame))

    def setIconImage(self, image):
        if self.iconPath and not os.path.isabs(self.iconPath) and ':\\' not in self.iconPath:
            self.iconPath = os.path.join(iconPath, self.iconPath)
        if self.iconPath.lower().endswith('.gif'):
            self.movie = QMovie(self.iconPath)
            self.movie.frameChanged.connect(self.updateIcon)
            self.movie.start()
        else:
            self.setIcon(QIcon(self.iconPath))
