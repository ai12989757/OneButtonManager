# 根据sehlf文件生成预览窗口
# 生成预览窗口的时候，会根据shelf文件中的信息，生成对应的控件
# 生成控件的时候，会根据文件文件的类型，生成对应的窗口 mel/json
import os
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
        self.gobalLayout.setAlignment(Qt.AlignCenter)
        self.gobalLayout.setContentsMargins(5, 5, 0, 0)
        self.gobalLayout.setSpacing(0)
        self.setLayout(self.gobalLayout)
        if self.shelfType == 'mel':
            self.melShelfPreView()
        elif self.shelfType == 'json':
            self.jsonShelfPreView

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
            return cmds.warning('该shelf文件内容有误')
        # 读取文件第一行，获取函数名
        with open(self.shelfFile, 'r') as f:
            firstLine = f.readline()
        if 'global proc' not in firstLine:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return cmds.warning('该shelf文件内容有误')
        # 获取函数名
        funcName = firstLine.split('global proc ')[1].split(' ')[0]
        # 执行函数
        try:
            mel.eval('%s()' % funcName)
        except:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return cmds.warning('该shelf文件内容有误')
        numberOfChildren = cmds.shelfLayout(PreViewShelfLayout, q=True, nch=True)
        if numberOfChildren == 0:
            cmds.deleteUI(PreViewShelfLayout)
            self.close()
            return cmds.warning('该shelf文件没有内容')
        self.width = numberOfChildren*42+5
        #self.setFixedSize(self.width, self.height)
        self.setGeometry(self.pw, self.ph, self.width, self.height)
        ptr = omui.MQtUtil.findLayout(PreViewShelfLayout)
        PreViewShelfLayout = wrapInstance(int(ptr), QWidget)
        self.gobalLayout.addWidget(PreViewShelfLayout)

    def jsonShelfPreView(self):
        pass