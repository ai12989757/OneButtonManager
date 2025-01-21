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
from ..utils import widgetEffect
from ..utils import imageManager
try:
    reload(widgetEffect)
    reload(imageManager)
except:
    from importlib import reload
    reload(widgetEffect)
    reload(imageManager)

ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/widgets', 'icons/') # /OneButtonManager/icons/

class GIFButtonWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(GIFButtonWidget, self).__init__(parent)

        ################## command ##################
        self.context = globals().copy()
        self.context.update({'self': self})
        self.command = kwargs.get('command', {}) # 命令
        '''
        command = {触发器: [类型, 命令]}
        tpye 类型: python, mel, function
        trigger 触发器: click, doubleClick, ctrlClick, shiftClick, altClick, ctrlShiftClick, ctrlAltClick, altShiftClick, ctrlAltShiftClick, drag, ctrlDrag, shiftDrag, altDrag, ctrlShiftDrag, ctrlAltDrag, altShiftDrag, ctrlAltShiftDrag
        命令: python: 'cmds.polyCube()', mel: 'polyCube', function: function
        '''
        ################## UI ##################
        self.alignment = kwargs.get('alignment', 'V' or 'H' or 'v' or 'h') # V: 垂直排列, H: 水平排列
        self.iconPath = kwargs.get('icon', None) # 图标路径
        self.size = kwargs.get('size', 42)  # 图标 长或宽 尺寸
        
        QApplication.instance().removeEventFilter(self) # 移除事件过滤器
        self.dragging = False        # 是否拖动按钮
        self.mouseState = ''
        '''
        鼠标状态: string
        leftPress: 左击按下
        leftRelease: 左击释放
        leftMoving: 左击拖拽
        ctrlLeftMoving: Ctrl+左击拖拽
        altLeftMoving: Alt+左击拖拽
        shiftLeftMoving: Shift+左击拖拽
        ctrlAltLeftMoving: Ctrl+Alt+左击拖拽
        ctrlShiftLeftMoving: Ctrl+Shift+左击拖拽
        altShiftLeftMoving: Alt+Shift+左击拖拽
        ctrlAltShiftLeftMoving: Ctrl+Alt+Shift+左击拖拽
        '''
        self.singleClick = 0         # 单击事件计数
        self.singleClickWait = None  # 单击事件延迟
        self.startPos = QPoint()     # 初始化鼠标位置，鼠标按下位置
        self.currentPos = QPoint()   # 初始化鼠标位置，鼠标当前位置
        self.delta = QPoint()        # 初始化鼠标移动距离，往右为正 1 ，往左为负 -1
        self.valueX = 0.00           # 初始化数值，往右为 +=1 ，往左为负 -=1
        self.valueY = 0.00           # 初始化数值，往下为 +=1 ，往上为负 -=1
        self.minValue = 0.00         # 初始化鼠标往左移动的最小值，用于判断是否拖动过按钮
        self.maxValue = 0.00         # 初始化鼠标往右移动的最大值，用于判断是否拖动过按钮
        self.value = {'self.delta': self.delta, 'self.valueX': self.valueX, 'self.valueY': self.valueY, 'self.minValue': self.minValue, 'self.maxValue': self.maxValue}
        self.initUI() # 初始化UI

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.movie = None       # GIF动画
        self.iconSub = None     # 图标角标
        self.setIconImage()     # 设置按钮外观
        self.label = None       # 用于显示角标
        self.menu = None        # 菜单
    
    # 有菜单项时，按钮右下角显示角标
    def menuSubLabel(self, width=0):
        label = QLabel(self)
        subImage = QPixmap(ICONPATH+'sub/sub.png')
        subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(subImage)
        label.setGeometry(width, 0, self.size, self.size)
        label.show()

    # 根据不同的按键组合，更新角标
    def updateSubLabel(self, sub):
        if self.label:
            self.label.setPixmap(QPixmap())
        else:
            self.label = QLabel(self) # 用于显示角标
        if sub is None:
            self.iconSub = 'default'
            return
        else:
            self.iconSub = sub
            subImage = QPixmap(ICONPATH+'sub/'+sub+'.png')
            subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(subImage)
        self.label.setGeometry(0, 0, self.size, self.size)
        self.label.show()

    def setIconImage(self):
        if not self.iconPath:
            self.iconPath = ICONPATH+'white/undetected.png'

        self.pixmap = QPixmap(self.iconPath)
        
        if self.alignment == 'H' or self.alignment == 'h':
            self.pixmap = self.pixmap.scaledToHeight(self.size, Qt.SmoothTransformation)
        elif self.alignment == 'V' or self.alignment == 'v':
            self.pixmap = self.pixmap.scaledToWidth(self.size, Qt.SmoothTransformation)
        self.setFixedSize(QSize(self.pixmap.width(), self.pixmap.height()))
        self.iconLabel = QLabel(self)
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

    def enterEvent(self, event):
        if self.iconPath.lower().endswith('.gif'):
            pass
        else:
            self.iconLabel.setPixmap(imageManager.enhanceIcon(self.pixmap, 1.3, 1.2))
        _,self.colorAnimation = widgetEffect.colorCycleEffect(self, 4000, self.alignment) # 彩色循环描边效果

        QApplication.instance().installEventFilter(self) # 安装事件过滤器, 用于监听键盘事件
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
            self.updateSubLabel('ctrlAltShift')
        elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
            self.updateSubLabel('ctrlShift')
        elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
            self.updateSubLabel('ctrlAlt')
        elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
            self.updateSubLabel('altShift')
        elif modifiers & Qt.ControlModifier:
            self.updateSubLabel('ctrl')
        elif modifiers & Qt.ShiftModifier:
            self.updateSubLabel('shift')
        elif modifiers & Qt.AltModifier:
            self.updateSubLabel('alt')
        else:
            self.updateSubLabel(None)
        #QObject.event(self, event)

    def leaveEvent(self, event):
        QApplication.instance().removeEventFilter(self) # 移除事件过滤器
        if self.iconPath.lower().endswith('.gif'):
            pass
        else:
            self.iconLabel.setPixmap(self.pixmap)
        self.updateSubLabel(None)
        self.setGraphicsEffect(None)
        if hasattr(self, 'colorAnimation'): self.colorAnimation.stop()

    def eventFilter(self, obj, event):
        if not isinstance(event, QEvent):
            return False
        if not self.underMouse():
            return False
        modifiers = QApplication.keyboardModifiers()
        if event.type() == QEvent.KeyPress:
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
            elif event.key() == Qt.Key_Menu:
                pass
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Alt:
                if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                    self.updateSubLabel('ctrlShift')
                elif modifiers & Qt.ControlModifier:
                    self.updateSubLabel('ctrl')
                elif modifiers & Qt.ShiftModifier:
                    self.updateSubLabel('shift')
                else:
                    if self.iconSub != 'default': self.updateSubLabel('default')
            elif event.key() == Qt.Key_Control:
                if modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                    self.updateSubLabel('altShift')
                elif modifiers & Qt.AltModifier:
                    self.updateSubLabel('alt')
                elif modifiers & Qt.ShiftModifier:
                    self.updateSubLabel('shift')
                else:
                    if self.iconSub != 'default': self.updateSubLabel('default')
            elif event.key() == Qt.Key_Shift:
                if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                    self.updateSubLabel('ctrlAlt')
                elif modifiers & Qt.ControlModifier:
                    self.updateSubLabel('ctrl')
                elif modifiers & Qt.AltModifier:
                    self.updateSubLabel('alt')
                else:
                    if self.iconSub != 'default': self.updateSubLabel(None)
            elif event.key() == Qt.Key_Menu:
                # show admin edit menu
                pass
        return False
        #return super(GIFButton, self).eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        self.valueX = 0.00  # 重置数值
        self.minValue = 0.00
        self.maxValue = 0.00
        self.singleClick += 1
        self.startPos = event.pos()
        if event.button() == Qt.LeftButton:
            self.executeDragCommand('leftPress')
            self.dragging = True
        # if event.button() == Qt.MiddleButton:
        #     if self.dragMove:
        #         startDrag(self, event)
           
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.eventPos = event.pos()
        if not self.rect().contains(event.pos()):
            self.setGraphicsEffect(None)
            if hasattr(self, 'colorAnimation'): self.colorAnimation.stop()
            self.updateSubLabel(None)
        if event.button() == Qt.LeftButton:
            self.executeDragCommand('leftRelease')
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
                        self.runCommand(self.command, 'doubleClick')

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
        if event.buttons() == Qt.LeftButton:
            self.executeDragCommand('leftMoving')
        #super(GIFButton, self).mouseMoveEvent(event)
        # 如果是鼠标中键拖动
        # elif event.buttons() == Qt.MiddleButton:
        #     if self.dragMove:
        #         self.move(self.mapToParent(event.pos() - self.startPos))
        #         performDrag(self, event)
        
    def singleClickEvent(self):
        self.singleClick = 0
        self.singleClickWait.stop()
        if self.rect().contains(self.eventPos):
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier and modifiers & Qt.AltModifier:
                trigger = 'ctrlAltShiftClick'
            elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                trigger = 'ctrlShiftClick'
            elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                trigger = 'ctrlAltClick'
            elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                trigger = 'altShiftClick'
            elif modifiers & Qt.ControlModifier:
                trigger = 'ctrlClick'
            elif modifiers & Qt.ShiftModifier:
                trigger = 'shiftClick'
            elif modifiers & Qt.AltModifier:
                trigger = 'altClick'
            else:
                trigger = 'click'
            self.runCommand(self.command, trigger)
    
    def executeDragCommand(self, mouseState='leftMoving'):
        if mouseState == 'leftMoving':
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier and modifiers & Qt.AltModifier:
                self.mouseState = 'ctrlAltShift'+mouseState.capitalize()
                trigger = 'ctrlAltShiftDrag'
            elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                self.mouseState = 'ctrlShift'+mouseState.capitalize()
                trigger = 'ctrlShiftDrag'
            elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                self.mouseState = 'ctrlAlt'+mouseState.capitalize()
                trigger = 'ctrlAltDrag'
            elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                self.mouseState = 'altShift'+mouseState.capitalize()
                trigger = 'altShiftDrag'
            elif modifiers & Qt.ControlModifier:
                self.mouseState = 'ctrl'+mouseState.capitalize()
                trigger = 'ctrlDrag'
            elif modifiers & Qt.ShiftModifier:
                self.mouseState = 'shift'+mouseState.capitalize()
                trigger = 'shiftDrag'
            elif modifiers & Qt.AltModifier:
                self.mouseState = 'alt'+mouseState.capitalize()
                trigger = 'altDrag'
            else:
                self.mouseState = mouseState
                trigger = 'drag'
            self.runCommand(self.command, trigger)
        else:
            self.mouseState = mouseState
            self.runCommand(self.command, mouseState)

    def runCommand(self, command, trigger='click'):
        if not command: return
        if trigger not in command: return
        if trigger not in command.keys(): return
        #print(command[trigger][0],trigger)
        if command[trigger][0] == 'python': 
            from maya.cmds import evalDeferred
            evalDeferred(lambda: exec(command[trigger][1], self.context))
        elif command[trigger][0] == 'mel':
            from maya import mel
            commendText = repr(command[trigger][1])
            commendText = "mel.eval(" + commendText + ")"
            
            if trigger in ['drag', 'ctrlDrag', 'shiftDrag', 'altDrag', 'ctrlShiftDrag', 'ctrlAltDrag', 'altShiftDrag', 'ctrlAltShiftDrag']:
                mel.eval("string $mouseState=\""+str(self.mouseState)+"\";")
                mel.eval("int $deltaX="+str(self.delta.x())+";")
                mel.eval("int $deltaY="+str(self.delta.y())+";")
            exec(commendText)
        elif command[trigger][0] == 'function': command[trigger][1]()

    def melSetIconAttr(self, iconPath, attr, value):
        # 使用mel设置按钮属性, 方便在maya中使用mel控制按钮属性
        pass
    def melSetActionAttr(self, action, attr, value):
        # 使用mel设置菜单项属性, 方便在maya中使用mel控制菜单项属性
        pass