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
from functools import partial
from collections import OrderedDict

ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/widgets', 'icons/') # /OneButtonManager/icons/

class GIFButtonWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(GIFButtonWidget, self).__init__(parent)

        ################## command ##################
        self.sourceType = kwargs.get('sourceType', "mel" or "python" or "function") 
        self.command = kwargs.get('command', None)
        self.doubleClickCommandSourceType = kwargs.get('doubleClickCommandSourceType', "mel" or "python" or "function")
        self.doubleClickCommand = kwargs.get('doubleClickCommand', None)
        self.ctrlCommand = kwargs.get('ctrlCommand', None)
        self.altCommand = kwargs.get('altCommand', None)
        self.shiftCommand = kwargs.get('shiftCommand', None)
        self.ctrlAltCommand = kwargs.get('ctrlAltCommand', None)
        self.altShiftCommand = kwargs.get('altShiftCommand', None)
        self.ctrlShiftCommand = kwargs.get('ctrlShiftCommand', None)
        self.ctrlAltShiftCommand = kwargs.get('ctrlAltShiftCommand', None)
        self.dragCommand = kwargs.get('dragCommand', None)
        self.altDragCommand = kwargs.get('altDragCommand', None)
        self.shiftDragCommand = kwargs.get('shiftDragCommand', None)
        self.ctrlDragCommand = kwargs.get('ctrlDragCommand', None)
        self.menuShowCommand = kwargs.get('menuShowCommand', '')
        ################## UI ##################
        self.alignment = kwargs.get('alignment', 'V' or 'H' or 'v' or 'h') # V: 垂直排列, H: 水平排列
        self.iconPath = kwargs.get('icon', None)
        self.size = kwargs.get('size', 42)

        self.dragging = False
        self.mouseState = ''         # 鼠标状态: 左击按下 leftPress, 左击释放 leftRelease, 左击拖拽 leftMoving
        self.singleClick = 0         # 单击事件计数
        self.singleClickWait = None  # 单击事件延迟
        self.startPos = QPoint()     # 初始化鼠标位置，鼠标按下位置
        self.currentPos = QPoint()   # 初始化鼠标位置，鼠标当前位置
        self.delta = QPoint()        # 初始化鼠标移动距离，往右为正 1 ，往左为负 -1
        self.valueX = 0.00           # 初始化数值，往右为 +=1 ，往左为负 -=1
        self.valueY = 0.00           # 初始化数值，往下为 +=1 ，往上为负 -=1
        self.minValue = 0.00         # 初始化鼠标往左移动的最小值，用于判断是否拖动过按钮
        self.maxValue = 0.00         # 初始化鼠标往右移动的最大值，用于判断是否拖动过按钮

        self.initUI() # 初始化UI

    def initUI(self):
        self.setFocusPolicy(Qt.StrongFocus)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.movie = None
        self.setIconImage()  # 设置按钮外观
        self.menuSubLabel(self.pixmap.width()-self.size) # 有菜单项时，按钮右下角显示角标
        self.label = None
    
    # 有菜单项时，按钮右下角显示角标
    def menuSubLabel(self, width=0):
        label = QLabel(self)
        subImage = QPixmap(ICONPATH+'sub/sub.png')
        subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(subImage)
        label.setGeometry(width, 0, self.size, self.size)
        label.show()

    def updateSubLabel(self, sub):
        #sub = 'alt'
        if self.label:
            self.label.setPixmap(QPixmap())
        if not sub:
            return
        self.label = QLabel(self) # 用于显示角标
        subImage = QPixmap(ICONPATH+'sub/'+sub+'.png')
        subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(subImage)
        self.label.setGeometry(0, 0, self.size, self.size)
        self.label.show()
        
    def setIconImage(self):
        if not self.iconPath:
            self.iconPath = ICONPATH+'white/undetected.png'

        self.pixmap = QPixmap(self.iconPath)
        self.iconLabel = QLabel(self)
        self.setFixedSize(QSize(self.pixmap.width(), self.pixmap.height()))
        if self.alignment == 'H' or self.alignment == 'h':
            self.pixmap = self.pixmap.scaledToHeight(self.size, Qt.SmoothTransformation)
        elif self.alignment == 'V' or self.alignment == 'v':
            self.pixmap = self.pixmap.scaledToWidth(self.size, Qt.SmoothTransformation)

        if self.iconPath.lower().endswith('.gif'):
            self.movie = QMovie(self.iconPath)
            self.movie.setScaledSize(QSize(self.pixmap.width(), self.pixmap.height()))
            self.iconLabel.setMovie(self.movie)
            self.movie.start()
        else:
            if self.movie:
                self.movie.stop()
                self.movie.deleteLater()
            self.iconLabel.setPixmap(self.pixmap)
        self.iconLabel.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.iconLabel.show()

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_Alt:
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                self.updateSubLabel('ctrlAltShift')
            elif modifiers & Qt.ControlModifier:
                self.updateSubLabel('ctrlAlt')
            elif modifiers & Qt.ShiftModifier:
                self.updateSubLabel('altShift')
            else:
                self.updateSubLabel('alt')
        elif event.key() == Qt.Key_Control:
            if modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                self.updateSubLabel('ctrlAltShift')
            elif modifiers & Qt.AltModifier:
                self.updateSubLabel('ctrlAlt')
            elif modifiers & Qt.ShiftModifier:
                self.updateSubLabel('ctrlShift')
            else:
                self.updateSubLabel('ctrl')
        elif event.key() == Qt.Key_Shift:
            if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                self.updateSubLabel('ctrlAltShift')
            elif modifiers & Qt.ControlModifier:
                self.updateSubLabel('ctrlShift')
            elif modifiers & Qt.AltModifier:
                self.updateSubLabel('altShift')
            else:
                self.updateSubLabel('shift')
        
    def keyReleaseEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_Alt:
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                self.updateSubLabel('ctrlShift')
            elif modifiers & Qt.ControlModifier:
                self.updateSubLabel('ctrl')
            elif modifiers & Qt.ShiftModifier:
                self.updateSubLabel('shift')
            else:
                self.updateSubLabel('default')
        elif event.key() == Qt.Key_Control:
            if modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                self.updateSubLabel('altShift')
            elif modifiers & Qt.AltModifier:
                self.updateSubLabel('alt')
            elif modifiers & Qt.ShiftModifier:
                self.updateSubLabel('shift')
            else:
                self.updateSubLabel('default')
        elif event.key() == Qt.Key_Shift:
            if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                self.updateSubLabel('ctrlAlt')
            elif modifiers & Qt.ControlModifier:
                self.updateSubLabel('ctrl')
            elif modifiers & Qt.AltModifier:
                self.updateSubLabel('alt')
            else:
                self.updateSubLabel('default')

    def mousePressEvent(self, event):
        self.valueX = 0.00  # 重置数值
        self.minValue = 0.00
        self.maxValue = 0.00
        self.singleClick += 1
        self.startPos = event.pos()
        if event.button() == Qt.LeftButton:
            self.executeDragCommand(event,'leftPress')
            self.dragging = True
            
        # if event.button() == Qt.MiddleButton:
        #     if self.dragMove:
        #         startDrag(self, event)
           
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.eventPos = event.pos()

        if hasattr(self, 'colorAnimation'): self.colorAnimation.stop()
        if event.button() == Qt.LeftButton:
            self.executeDragCommand(event,'leftRelease')
        # if event.button() == Qt.MiddleButton:
        #     if self.dragMove:
        #         self.singleClick = 0
        #         endDrag(self, event)
        if self.minValue < -10 or self.maxValue > 10: # 说明按钮被拖动了，不执行单击事件
            self.minValue = 0.00
            self.maxValue = 0.00
            self.singleClick = 0
            if self.singleClickWait:
                self.singleClickWait.stop()
        else:  
            if event.button() == Qt.RightButton:
                self.singleClick = 0
            if event.button() == Qt.LeftButton:
                # 如果释放时光标不在按钮上，不执行单击事件
                if self.rect().contains(event.pos()):
                    if self.singleClick == 1:
                        # 延迟30ms,进入等待执行状态
                        self.singleClickWait = QTimer(self)
                        self.singleClickWait.setInterval(200)
                        self.singleClickWait.timeout.connect(self.singleClickEvent)
                        self.singleClickWait.start() 
                    elif self.singleClick == 2:
                        # 停止正在延迟等待的单击事件 singleClickWait
                        # 禁用self.singleClickWait
                        if self.singleClickWait:
                            self.singleClickWait.stop()
                        # 双击事件
                        self.singleClick = 0
                        self.doubleClickCommandText()

    def singleClickEvent(self):
        self.singleClick = 0
        self.singleClickWait.stop()
        if self.rect().contains(self.eventPos):
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier and modifiers & Qt.AltModifier:
                if self.ctrlAltShiftCommand: print('ctrlAltShiftCommand')
            elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                if self.ctrlShiftCommand: print('ctrlShiftCommand')
            elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                if self.ctrlAltCommand: print('ctrlAltCommand')
            elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                if self.altShiftCommand: print('altShiftCommand')
            elif modifiers & Qt.ControlModifier:
                if self.ctrlCommand: print('ctrlCommand')
            elif modifiers & Qt.ShiftModifier:
                if self.shiftCommand: print('shiftCommand')
            elif modifiers & Qt.AltModifier:
                if self.altCommand: print('altCommand')
            else:
                print('singleClick')
                if not self.command: return
                if self.sourceType == 'python': exec(self.command, dict(globals(), **{'self': self}))
                elif self.sourceType == 'mel':
                    commendText = repr(self.command)
                    commendText = "mel.eval(" + commendText + ")"
                    exec(commendText)
        return False

    def doubleClickCommandText(self):
        print('doubleClickCommandText')
        if not self.doubleClickCommand:
            return
        if self.doubleClickCommandSourceType == 'python':
            commendText = self.doubleClickCommand
        elif self.doubleClickCommandSourceType == 'mel':
            commendText = repr(self.doubleClickCommand)
            commendText = "mel.eval(" + commendText + ")"
        if commendText and self.doubleClickCommandSourceType == 'python': cmds.evalDeferred(lambda: self.execute_python_command(commendText, self.context))
        elif commendText and self.doubleClickCommandSourceType == 'mel': cmds.evalDeferred(lambda: self.execute_mel_command(commendText))

    def mouseMoveEvent(self, event):
        # 更改光标样式
        # QApplication.setOverrideCursor(Qt.SizeHorCursor)
        #setToolTo('moveSuperContext')
        #om.MGlobal.displayWarning("Changing cursor shape")
        # om.MGlobal.displayWarning("Changing cursor shape")
        # omui.MGlobal.setCursor(omui.MCursor.kSizeHor)
        self.currentPos = event.pos()
        self.delta = self.currentPos - self.startPos
        #print(self.delta.x())
        self.valueX += self.delta.x()
        self.valueY += self.delta.y()
        self.startPos = self.currentPos
        # 初始化最小值和最大值
        if not hasattr(self, 'minValue') or not hasattr(self, 'maxValue'):
            self.minValue = self.valueX
            self.maxValue = self.valueX

        # 更新最小值和最大值
        if self.valueX < self.minValue:
            self.minValue = self.valueX
        if self.valueX > self.maxValue:
            self.maxValue = self.valueX
        #print(f"Current Value: {self.valueX}, Min Value: {self.minValue}, Max Value: {self.maxValue}")
        if event.buttons() == Qt.LeftButton:
            self.executeDragCommand(event,'leftMoving')
        #super(GIFButton, self).mouseMoveEvent(event)
        # 如果是鼠标中键拖动
        # elif event.buttons() == Qt.MiddleButton:
        #     if self.dragMove:
        #         self.move(self.mapToParent(event.pos() - self.startPos))
        #         performDrag(self, event)
         
    def executeDragCommand(self, event,mouseState='leftMoving'):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            self.mouseState = 'ctrl'+mouseState.capitalize()
            print('ctrlDragCommand')
        elif modifiers & Qt.ShiftModifier:
            self.mouseState = 'shift'+mouseState.capitalize()
            print('shiftDragCommand')
        elif modifiers & Qt.AltModifier:
            self.mouseState = 'alt'+mouseState.capitalize()
            print('altDragCommand')
        else:
            self.mouseState = mouseState
            print('dragCommand')
