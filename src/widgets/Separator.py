# -*- coding: utf-8 -*-
import os
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from ..utils.switchLanguage import *
from ..utils import dragWidgetOrder

ICONPATH = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src/widgets', 'icons/')
class Separator(QPushButton):
    def __init__(self, parent=None, language=0, dragMove=True, size=42, alignment='H', color=(158, 158, 158, 255)):
        super(Separator, self).__init__(parent)
        self.language = language
        self.dragMove = dragMove
        self.separatorSize = None
        if alignment == 'V' or alignment == 'v': 
            self.separatorSize = [size, 2]
        elif alignment == 'H' or alignment == 'h': 
            self.separatorSize = [2, size]
        self.setIconSize(QSize(size,size))
        self.pixmap = QPixmap(self.separatorSize[0], self.separatorSize[1])
        self.pixmap.fill(QColor(color[0],color[1],color[2],color[3])) # rgba(158, 158, 158, 255)
        self.setIcon(self.pixmap)
        self.setStyleSheet("border: none; background-color: none;")
        # 添加一个右击菜单
        self.menu = QMenu(self)
        self.deleteAction = QAction(QIcon(os.path.join(ICONPATH, "red/Delete.png")), sl(u"删除",self.language), self)
        self.deleteAction.triggered.connect(self.deleteButton)
        self.menu.addAction(self.deleteAction)

        if dragMove:
            #self.setMouseTracking(True)
            dragWidgetOrder.DragWidgetOrder(self)
        
    def deleteButton(self):
        self.menu.deleteLater()
        self.setParent(None)
        self.deleteLater()

    # 添加右键菜单
    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())