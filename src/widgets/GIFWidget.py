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

from maya import mel
from ..utils import widgetEffect
from ..utils import imageManager
from ..utils.runCommand import RunCommand
from ..utils import dragWidgetOrder
from ..utils import buttonManager
from ..utils.switchLanguage import *
from . import GIFAction
from ..utils import buttonManager
from . import BGwidget
try:
    reload(widgetEffect)
    reload(imageManager)
    reload(GIFAction)
    reload(dragWidgetOrder)
    reload(buttonManager)
    reload(BGwidget)
except:
    from importlib import reload
    reload(widgetEffect)
    reload(imageManager)
    reload(GIFAction)
    reload(dragWidgetOrder)
    reload(buttonManager)
    reload(BGwidget)

import ctypes
from ctypes import wintypes

# 定义虚拟键码
VK_RCONTROL = 0xA3

# 加载 user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 定义 GetAsyncKeyState 函数
GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = [wintypes.INT]
GetAsyncKeyState.restype = wintypes.SHORT

def is_right_ctrl_pressed():
    # 检查右 Ctrl 键是否被按下
    state = GetAsyncKeyState(VK_RCONTROL)
    return state & 0x8000 != 0

ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/widgets', 'icons/') # /OneButtonManager/icons/
SHELF_BACKUP_PATH = os.path.expanduser('~') + '/OneTools/data/shelf_backup/'

class GIFButtonWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(GIFButtonWidget, self).__init__(parent)
        self.dragMove = kwargs.get('dragMove', False)   # 是否允许拖动按钮
        if self.dragMove:
            self.dragWidgetOrder = dragWidgetOrder.DragWidgetOrder(self)
        self.mousePressEvent = self.widgetMousePressEvent
        self.mouseMoveEvent = self.widgetMouseMoveEvent
        self.mouseReleaseEvent = self.widgetMouseReleaseEvent
        ################## command ##################
        self.labelText=kwargs.get('label', "")
        self.annotation=kwargs.get('annotation', None)
        if self.annotation:
            self.setToolTip(self.annotation)
            self.setStatusTip(self.annotation)
        if self.labelText:
            self.setObjectName(self.labelText)
        self.command = kwargs.get('command', {}) # 命令
        '''
        command = {触发器: [类型, 命令]}
        tpye 类型: python, mel, function
        trigger 触发器: menuShow, click, doubleClick, ctrlClick, shiftClick, altClick, ctrlShiftClick, ctrlAltClick, altShiftClick, ctrlAltShiftClick, drag, ctrlDrag, shiftDrag, altDrag, ctrlShiftDrag, ctrlAltDrag, altShiftDrag, ctrlAltShiftDrag
        命令: python: 'cmds.polyCube()', mel: 'polyCube', function: function
        '''
        ################## UI ##################
        self.language = kwargs.get('language', 0)
        self.alignment = kwargs.get('alignment', 'H')   # V: 垂直排列, H: 水平排列
        self.iconPath = kwargs.get('icon', None)        # 图标路径
        self.bg = kwargs.get('bg', False)               # 是否显示背景
        self.bgColor = kwargs.get('bgColor', (123, 104, 238)) # 背景颜色
        self.hiIconPath = None                          # 高亮图标路径
        self.size = kwargs.get('size', 42)              # 图标 长或宽 尺寸
        self.style = kwargs.get('style', 'auto')        # 按钮样式
        self.tearOff = kwargs.get('tearOff', True)      # 是否允许撕下菜单
        
        QApplication.instance().removeEventFilter(self) # 移除事件过滤器
        self.dragging = False        # 按钮是否处于拖拽状态
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
        self.lastMoveValueX = 0
        self.lastMoveValueY = 0
        self.moveThreshold = 10
        self.value = {'self.delta': self.delta, 'self.valueX': self.valueX, 'self.valueY': self.valueY, 'self.minValue': self.minValue, 'self.maxValue': self.maxValue}
        self.iconSizeValue = QSize()    # 图标尺寸
        self.initUI() # 初始化UI

    def initUI(self):
        self.setStyleSheet("border: none; background-color: none;")
        self.golablLayout = QVBoxLayout()
        self.golablLayout.setContentsMargins(0, 0, 0, 0)
        self.golablLayout.setSpacing(0)
        self.setLayout(self.golablLayout )
        if self.bg:
            self.bgWidget = BGwidget.WidgetBG(iconPath=self.iconPath, size=self.size, color=self.bgColor)
            self.golablLayout.addWidget(self.bgWidget, 0, Qt.AlignCenter)
        self.movie = None               # GIF动画
        self.iconSub = 'default'        # 图标角标
        self.menuSubLable = None        # 菜单角标
        self.iconLabel = QLabel(self)   # 图标
        
        self.setIconImage(self.iconPath)             # 设置按钮
        self.keySubLabel = None         # 用于显示角标
        self.menu = QMenu(self)         # 菜单
        self.menu.setTearOffEnabled(self.tearOff) # 设置菜单是否可以撕下

    # 有菜单项时，按钮右下角显示角标
    def menuSubLabel(self):
        if not self.menuSubLable and not self.bg:
            self.menuSubLable = QLabel(self)
            subImage = QPixmap(ICONPATH+'sub/sub.png')
            subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.menuSubLable.setPixmap(subImage)
            self.menuSubLable.setGeometry(0, 0, self.size, self.size)
            self.golablLayout.addWidget(self.menuSubLable, 0, Qt.AlignRight)
            #self.menuSubLable.show()

    # 根据不同的按键组合，更新角标
    def updateSubLabel(self, sub):
        if self.keySubLabel:
            self.keySubLabel.setPixmap(QPixmap())
        else:
            self.keySubLabel = QLabel(self) # 用于显示角标
        if sub is None:
            sub = 'default'
        self.iconSub = sub
        iconName = self.iconPath.split('/')[-1].split('.')[0]
        if self.iconSub == 'default':
            self.setIconImage(self.iconPath)
            return

        subFile = self.iconPath.replace(iconName, iconName+'_'+sub)
        if os.path.exists(subFile):
            defaultIconPath = self.iconPath
            self.iconPath = subFile         # 更新角标图标路径
            self.setIconImage(self.iconPath)
            self.iconPath = defaultIconPath # 恢复原图标路径
            return
        subImage = QPixmap(ICONPATH+'sub/'+sub+'.png')
        subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.keySubLabel.setPixmap(subImage)
        self.keySubLabel.setGeometry(0, 0, self.size, self.size)
        self.keySubLabel.show()

    def setIconImage(self, iconPath=None):
        if not iconPath:
            iconPath = ICONPATH+'white/undetected.png'
        if not os.path.exists(iconPath) and ':\\' not in iconPath:
            self.tempPixmap = QPixmap(ICONPATH+'white/undetected.png')
            self.tempPixmap = self.tempPixmap.scaledToHeight(self.size, Qt.SmoothTransformation)
            self.iconLabel.setPixmap(self.tempPixmap)
            self.iconLabel.setGeometry(0, 0, self.size, self.size)
            self.iconSizeValue=QSize(self.size, self.size)
            self.setFixedSize(self.iconSizeValue)
            self.iconLabel.show()
            mel.eval('warning -n "图标不存在: ' + iconPath + '"')
            return
        self.pixmap = QPixmap(iconPath)
        
        if self.alignment == 'H' or self.alignment == 'h':
            self.pixmap = self.pixmap.scaledToHeight(self.size, Qt.SmoothTransformation)
        elif self.alignment == 'V' or self.alignment == 'v':
            self.pixmap = self.pixmap.scaledToWidth(self.size, Qt.SmoothTransformation)
        self.iconSizeValue = QSize(self.pixmap.width(), self.pixmap.height())
        self.setFixedSize(self.iconSizeValue)
        
        if iconPath.lower().endswith('.gif'):
            if self.movie:
                # 获取 QMovie 使用的图片
                self.movie.stop()

            self.movie = QMovie(iconPath)
            self.movie.setCacheMode(QMovie.CacheAll)
            self.movie.setScaledSize(self.iconSizeValue)
            self.iconLabel.setMovie(self.movie)
            self.movie.start()
            self.setGIFStyle(self.style)
        else:
            if self.movie:
                self.movie.stop()
                self.movie = None
            self.iconLabel.setPixmap(self.pixmap)
        self.iconLabel.setGeometry(0, 0, self.pixmap.width(), self.pixmap.height())
        self.iconLabel.show()

    def setGIFStyle(self, style='auto'):
        if not os.path.exists(self.iconPath) or not self.iconPath.lower().endswith('.gif'):
            return
        try:
            self.movie.frameChanged.disconnect(None, None)
        except:
            pass
        if style == 'auto' or style == 'loop': # 默认循环播放
            if self.movie.state() != QMovie.Running: self.movie.start()
        elif style == 'once': # 播放一次
            def gifFrameChanged(self):
                # 如果当前帧数等于总帧数-1，说明已经播放到最后一帧
                if self.movie.currentFrameNumber() == self.movie.frameCount()-1:
                    self.movie.stop()
                    try:
                        self.movie.frameChanged.disconnect(None, None)
                    except:
                        pass
                return
            if not self.underMouse():
                if self.movie.currentFrameNumber() != self.movie.frameCount()-1:
                    self.movie.frameChanged.connect(lambda: gifFrameChanged(self))
            else:
                if self.movie.state() != QMovie.Running: self.movie.start()
                self.movie.frameChanged.connect(lambda: gifFrameChanged(self))
        elif style == 'leaveStop': # 鼠标离开停止播放  回到第一帧
            if not self.underMouse():
                self.movie.jumpToFrame(0)
                self.movie.stop()
            else:
                if self.movie.state() != QMovie.Running: self.movie.start()
        elif style == 'leavePause': # 鼠标离开暂停播放
            if self.underMouse():
                self.movie.setPaused(False)
            else:
                self.movie.setPaused(True)

    def enterEvent(self, event):
        if not hasattr(self, 'pixmap'): return
        self.setGIFStyle(self.style)
        imageName = self.iconPath.split('/')[-1].split('.')[0]
        self.hiIconPath = self.iconPath.replace(imageName, imageName+'_hi') if self.iconPath else None
        # 如果 self.hiIconPath 存在
        if self.hiIconPath and not os.path.exists(self.hiIconPath): self.hiIconPath = None
        if self.hiIconPath:
            self.setIconImage(self.hiIconPath)
        if self.iconPath.lower().endswith('.gif'):
            pass
        else:
            self.iconLabel.setPixmap(imageManager.enhanceIcon(self.pixmap, 1.3, 1.2))
        _,self.colorAnimation = widgetEffect.colorCycleEffect(self.iconLabel, 4000, self.alignment) # 彩色循环描边效果

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
            if is_right_ctrl_pressed():
                return
            self.updateSubLabel('ctrl')
        elif modifiers & Qt.ShiftModifier:
            self.updateSubLabel('shift')
        elif modifiers & Qt.AltModifier:
            self.updateSubLabel('alt')
        # else:
        #     self.updateSubLabel(None)
        #QObject.event(self, event)

    def leaveEvent(self, event):
        if not hasattr(self, 'pixmap'): return
        if self.hiIconPath:
            self.setIconImage(self.iconPath)
        self.setGIFStyle(self.style)
        QApplication.instance().removeEventFilter(self) # 移除事件过滤器
        if self.iconPath.lower().endswith('.gif'):
            pass
        else:
            self.iconLabel.setPixmap(self.pixmap)
        if self.iconSub != 'default': self.updateSubLabel(None)
        self.iconLabel.setGraphicsEffect(None)
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
                if is_right_ctrl_pressed():
                    return False
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
                    if self.iconSub != 'default': self.updateSubLabel('default')
            elif event.key() == Qt.Key_Menu:
                # show admin edit menu
                pass
        return False
        #return super(GIFButton, self).eventFilter(obj, event)
    
    def widgetMousePressEvent(self, event):
        self.lastMoveValueX = 0
        self.lastMoveValueY = 0
        self.moveThreshold = 10
        self.valueX = 0.00  # 重置数值
        self.valueY = 0.00  # 重置数值
        self.minValue = 0.00
        self.maxValue = 0.00
        self.singleClick += 1
        self.startPos = event.pos()
        self.raise_() # 置顶
        if event.button() == Qt.LeftButton:
            self.mouseState = 'leftPress'
            RunCommand(self, self.command, 'leftPress').leftPR()
            self.dragging = True
            if self.style == 'clickAction': # 点击播放/暂停
                if self.movie.state() == QMovie.Running:
                    self.movie.setPaused(True)
                elif self.movie.state() == QMovie.Paused or self.movie.state() == QMovie.NotRunning:
                    self.movie.setPaused(False)
        if event.button() == Qt.MiddleButton:
            if self.dragMove:
                self.dragWidgetOrder.startDrag(event)
           
    def widgetMouseReleaseEvent(self, event):
        self.iconDragEffect('back')
        self.dragging = False
        self.eventPos = event.pos()
        if not self.rect().contains(event.pos()):
            self.setGraphicsEffect(None)
            if hasattr(self, 'colorAnimation'): self.colorAnimation.stop()
            self.updateSubLabel(None)
        if event.button() == Qt.LeftButton:
            self.mouseState = 'leftRelease'
            RunCommand(self, self.command, 'leftRelease').leftPR()
        if event.button() == Qt.MiddleButton:
            if self.dragMove:
                self.singleClick = 0
                self.dragWidgetOrder.endDrag(event)
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
                        self.singleClickWait.setInterval(150)
                        self.singleClickWait.timeout.connect(self.singleClickEvent)
                        self.singleClickWait.start() 

    def widgetMouseMoveEvent(self, event):
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
            self.iconDragEffect('move')
        #super(GIFButton, self).mouseMoveEvent(event)
        # 如果是鼠标中键拖动
        elif event.buttons() == Qt.MiddleButton:
            if self.dragMove:
                #self.move(self.mapToParent(event.pos() - self.startPos))
                self.dragWidgetOrder.performDrag(event)
        
    def singleClickEvent(self):
        self.singleClick = 0
        self.singleClickWait.stop()
        if self.rect().contains(self.eventPos):
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier and modifiers & Qt.AltModifier:
                trigger = 'ctrlAltShiftClick'
                self.mouseState = 'ctrlAltShiftClick'
            elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                trigger = 'ctrlShiftClick'
                self.mouseState = 'ctrlShiftClick'
            elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                trigger = 'ctrlAltClick'
                self.mouseState = 'ctrlAltClick'
            elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                trigger = 'altShiftClick'
                self.mouseState = 'altShiftClick'
            elif modifiers & Qt.ControlModifier:
                trigger = 'ctrlClick'
                self.mouseState = 'ctrlClick'
            elif modifiers & Qt.ShiftModifier:
                trigger = 'shiftClick'
                self.mouseState = 'shiftClick'
            elif modifiers & Qt.AltModifier:
                trigger = 'altClick'
                self.mouseState = 'altClick'
            else:
                trigger = 'click'
                self.mouseState = 'click'
            RunCommand(self, self.command, trigger).runCommand()
    
    def mouseDoubleClickEvent(self, event):
        RunCommand(self, self.command, 'leftPress').leftPR() # 双击事件会覆盖掉一次鼠标按下事件，所有需要在执行双击事件之前补偿一次鼠标按下命令 
        if self.singleClickWait:
            self.singleClickWait.stop()
        # 双击事件
        self.singleClick = 0
        self.mouseState = 'doubleClick'
        RunCommand(self, self.command, 'doubleClick').runCommand()

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
            RunCommand(self, self.command, trigger).runDragCommand()
            

    def melSetIconAttr(self, iconPath, attr, value):
        # 使用mel设置按钮属性, 方便在maya中使用mel控制按钮属性
        pass
    def melSetActionAttr(self, action, attr, value):
        # 使用mel设置菜单项属性, 方便在maya中使用mel控制菜单项属性
        pass

    def iconDragEffect(self,mode='move'):
        if mode=='move':
            # 根据 self.valueX 和 self.valueY 的值，设置按钮的图标的移动
            # 制作出拖拽时图标有被拉扯的效果
            # 鼠标每移动10px，图标移动1px
            # 计算当前的移动值
            #self.moveThreshold = 10
            moveValueX = round(self.valueX / self.moveThreshold)
            moveValueY = round(self.valueY / self.moveThreshold)
            # 限制移动值的范围在 -10 到 10 之间
            moveValueX = max(min(moveValueX, 5), -5)
            moveValueY = max(min(moveValueY, 5), -5)
            # 只有当移动值发生变化时才移动图标
            if moveValueX != self.lastMoveValueX or moveValueY != self.lastMoveValueY:
                self.iconLabel.move(self.iconLabel.x() + (moveValueX - self.lastMoveValueX),
                        self.iconLabel.y() + (moveValueY - self.lastMoveValueY))
            # 更新最后的移动值
            self.lastMoveValueX = moveValueX
            self.lastMoveValueY = moveValueY
            # 增加移动阈值
            self.moveThreshold += 0.1
        elif mode == 'back':
            # 设置回弹动画
            start_pos = self.iconLabel.pos()
            end_pos = QPoint(self.iconLabel.x() - self.lastMoveValueX, self.iconLabel.y() - self.lastMoveValueY)
            self.animation = QPropertyAnimation(self.iconLabel, b"pos")
            self.animation.setDuration(200)
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(end_pos)
            self.animation.setEasingCurve(QEasingCurve.OutBounce)
            self.animation.start()

    # 添加右键菜单,没有这个方法，右键菜单不会显示
    def contextMenuEvent(self, event):
        if self.menu.isEmpty():
            return
        self.menu.exec_(event.globalPos())

    def addMenuItem(self, label=None, command=None, icon=None, annotation=None, checkable=False):
        menu_item = GIFAction.gifIconMenuAction(parent=self, icon=icon, label=label, annotation=annotation, command=command, checkable=checkable)
        self.menu.addAction(menu_item)
        
        if not self.bg:
            self.menuSubLabel() # 菜单项角标
        else:
            self.bgWidget.menuSub = True
            #self.bgWidget.setSub()
            self.bgWidget.update()
            
        # 菜单出现前命令
        try:
            self.menu.aboutToShow.disconnect(None, None)
        except:
            pass
        self.menu.aboutToShow.connect(lambda: RunCommand(self, self.command, 'menuShow').runCommand())

    def addDefaultMenuItems(self):
        self.menu.addSeparator()

        editAction = QAction(QIcon(os.path.join(ICONPATH, "white/Edit_popupMenu.png")), sl(u"编辑",self.language), self)
        self.menu.addAction(editAction)

        editMenu = QMenu(sl(u"编辑",self.language), self)
        editAction.setMenu(editMenu)
        editMenu.addAction(QIcon(os.path.join(ICONPATH, "white/Edit.png")), sl(u"编辑",self.language), self.buttonEditor).setStatusTip(sl(u"点击打开编辑窗口",self.language))
        editMenu.addSeparator()
        editMenu.addAction(QIcon(os.path.join(ICONPATH, "white/Copy.png")), sl(u"复制",self.language), self.copyButton).setStatusTip(sl(u"复制按钮",self.language))
        editMenu.addAction(QIcon(os.path.join(ICONPATH, "white/Cut.png")), sl(u"剪切",self.language), self.cutButton).setStatusTip(sl(u"剪切按钮",self.language))
        editMenu.addAction(QIcon(os.path.join(ICONPATH, "white/Paste.png")), sl(u"粘贴",self.language), self.pasteButton).setStatusTip(sl(u"粘贴按钮",self.language))

        self.menu.addAction(QIcon(os.path.join(ICONPATH, "red/Delete.png")), sl(u"删除",self.language), self.deleteButton).setStatusTip(sl(u"删除按钮",self.language))

    def buttonEditor(self):
        from ..ui import editorWindow
        editButton = self
        if mel.eval('window -exists ButtonEditorWindow'):
            mel.eval('deleteUI ButtonEditorWindow')
        btw = editorWindow.ButtonEditorWindow(editButton=editButton,language=self.language)
        btw.show()

    def copyButton(self):
        buttonManager.copyButton(button=self,path=SHELF_BACKUP_PATH)

    def cutButton(self):
        buttonManager.cutButton(button=self,path=SHELF_BACKUP_PATH)

    def pasteButton(self):
        buttonManager.pasteButton(button=self,path=SHELF_BACKUP_PATH)

    def deleteButton(self):
        buttonManager.deleteButton(button=self,path=SHELF_BACKUP_PATH)