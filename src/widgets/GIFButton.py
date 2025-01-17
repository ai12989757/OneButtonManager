# -*- coding: utf-8 -*-
import os
import json
import codecs # 用于python2.7中读取json文件encoding问题
from maya import mel
import maya.cmds as cmds

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

from switchLanguage import *

iconPath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').replace('src/widgets', 'icons/')

def startDrag(self, event):
    # 获取光标移动的距离
    self.startPos = event.pos()
    self.buttonParent = self.parent()
    # 列出所有的按钮
    self.buttonList = []
    if self.buttonParent.__class__.__name__ == 'ButtonEditorWindow':
        self.buttonList = [self]
        self.buttonIndex = 0
        return
    elif self.buttonParent.__class__.__name__ == 'OneToolsMainWindow':
        shelfLayoutInfo = self.buttonParent.layout
    else:
        shelfLayoutInfo = self.buttonParent.layout()

    for i in range(shelfLayoutInfo.count()):
        self.buttonList.append(shelfLayoutInfo.itemAt(i).widget())
    # 获取按钮的索引
    self.buttonIndex = self.buttonList.index(self)
    
def performDrag(self, event):
    # 将当前拖拽的按钮显示在最前面
    self.raise_()

    # 移动按钮
    self.move(self.pos() + QPoint(self.valueX, 0))

    # 求出当前按钮移动的距离
    movePos = self.pos()

    # 判断按钮移动方向
    if len(self.buttonList) != 1: # 如果不止一个按钮
        if self.valueX > 0: # 如果按钮向右移动
            # 判断当前按钮是否是最后一个按钮
            if self.buttonIndex != len(self.buttonList) - 1:
                # 获取右边按钮的位置
                rightButton = self.buttonList[self.buttonIndex + 1]
                rightButtonPos = rightButton.pos()
                if movePos.x()+self.width() > rightButtonPos.x()+(rightButton.width()/2): # 如果按钮最右边的位置大于右边按钮的一半宽度
                    rightButton.move(QPoint(rightButtonPos.x() - self.width(), rightButtonPos.y()))
                    # 将当前按钮的的索引与右边按钮的索引交换
                    self.buttonList[self.buttonIndex], self.buttonList[self.buttonIndex + 1] = self.buttonList[self.buttonIndex + 1], self.buttonList[self.buttonIndex]
                    # 交换按钮的索引
                    self.buttonIndex += 1
        else: # 如果按钮向左移动
            if self.buttonIndex != 0:
                # 获取左边按钮的位置
                leftButton = self.buttonList[self.buttonIndex - 1]
                leftButtonPos = leftButton.pos()
                if movePos.x() < leftButtonPos.x()+(leftButton.width()/2): # 如果按钮最左边的位置小于左边按钮的一半宽度
                    leftButton.move(QPoint(leftButtonPos.x() + self.width(), leftButtonPos.y()))
                    # 将当前按钮的的索引与左边按钮的索引交换
                    self.buttonList[self.buttonIndex], self.buttonList[self.buttonIndex - 1] = self.buttonList[self.buttonIndex - 1], self.buttonList[self.buttonIndex]
                    # 交换按钮的索引
                    self.buttonIndex -= 1

def endDrag(self, event):
    animationDuration = 100
    animationEasingCurve = QEasingCurve.Linear
    # 中键释放后，将按钮的位置依附到相邻的按钮边上
    # 判断要依附的按钮是左边的还是右边的
    if len(self.buttonList) != 1:
        # 根据button在list中的位置，获取按钮是否在最前面或最后面
        if self.buttonIndex == 0: # 如果是第一个按钮
            # 获取右边按钮的位置
            rightButton = self.buttonList[self.buttonIndex + 1]
            rightButtonPos = rightButton.pos()
            target_x = rightButtonPos.x() - self.width()
            # 将 button 移动到右边按钮的左边
            if target_x - self.pos().x() > self.width():
                animationDuration = 1000
                animationEasingCurve = QEasingCurve.OutBounce
        elif self.buttonIndex == len(self.buttonList) - 1: # 如果是最后一个按钮
            # 获取左边按钮的位置
            leftButton = self.buttonList[self.buttonIndex - 1]
            leftButtonPos = leftButton.pos()
            # 获取左边按钮的宽度
            leftButtonWidth = leftButton.width()
            # 将 button 移动到左边按钮的右边
            target_x = leftButtonPos.x() + leftButtonWidth
            if self.pos().x() - target_x > self.width():
                animationDuration = 1000
                animationEasingCurve = QEasingCurve.OutBounce
        else:
            animationDuration = 100
            # 根据button在list中的位置，获取左右两个按钮的位置
            leftButton = self.buttonList[self.buttonIndex - 1]
            rightButton = self.buttonList[self.buttonIndex + 1]
            # 获取 button leftButton rightButton 的位置
            buttonPos = self.pos()
            leftButtonPos = leftButton.pos()
            rightButtonPos = rightButton.pos()
            # 获取 button leftButton rightButton 的宽度
            buttonWidth = self.width()
            leftButtonWidth = leftButton.width()
            rightButtonWidth = rightButton.width()
            # 判断 button 与 leftButton 的距离
            distanceToLeftButton = abs(buttonPos.x() - leftButtonPos.x() - leftButtonWidth)
            # 判断 button 与 rightButton 的距离
            distanceToRightButton = abs(buttonPos.x() + buttonWidth - rightButtonPos.x())
            # 判断 button 与 leftButton 的距离是否小于 button 与 rightButton 的距离
            if distanceToLeftButton < distanceToRightButton:
                # 将 button 移动到 leftButton 的右边
                target_x = leftButtonPos.x() + leftButtonWidth
            else:
                # 将 button 移动到 rightButton 的左边
                target_x = rightButtonPos.x() - buttonWidth
    else:
        target_x = 0
        animationDuration = 1000
        animationEasingCurve = QEasingCurve.OutBounce

    animation = QPropertyAnimation(self, b"pos")
    animation.setDuration(animationDuration)
    animation.setEasingCurve(animationEasingCurve)
    animation.setStartValue(self.pos())
    animation.setEndValue(QPoint(target_x, self.pos().y()))
    animation.start()
    self.animation = animation
    # 当动画结束时，更新按钮列表
    self.animation.finished.connect(partial(updateButtonList, self))

def updateButtonList(self):
    # 获取新的按钮列表
    self.buttonListNew = []
    if self.buttonParent.__class__.__name__ == 'ButtonEditorWindow':
        return
    elif self.buttonParent.__class__.__name__ == 'OneToolsMainWindow':
        shelfLayoutInfo = self.parent().layout
    else:
        shelfLayoutInfo = self.parent().layout()

    for i in range(shelfLayoutInfo.count()):
        self.buttonListNew.append(shelfLayoutInfo.itemAt(i).widget())
    # 如果按钮列表不一样，则说明按钮的位置发生了变化
    if self.buttonList != self.buttonListNew:
        # 将layout上的widget全部移除后，重新添加，这样就可以保证按钮的顺序是正确的
        for i in self.buttonList:
            i.setParent(None)
        for i in self.buttonList:
            shelfLayoutInfo.addWidget(i)

class menuSeparator(QAction):
    def __init__(self, parent=None,  label=None):
        super(menuSeparator, self).__init__(parent)

        self.setText(label+'—'*20) # 设置分隔符的文本
        # 字体颜色
        self.setTextColor(QColor(150, 150, 150)) # rgb(150, 150, 150)
        # 不可选中
        self.setSelectable(False)
        # 不可用
        self.setEnabled(False)

class gifIconMenuAction(QAction):
    def __init__(self, parent=None, **kwargs):
        super(gifIconMenuAction, self).__init__(parent)
        self.movie = None
        self.current_frame = None
        self.iconPath = kwargs.get('icon', None)
        self.label = kwargs.get('label', None)
        self.annotation = kwargs.get('annotation', None)
        self.sourceType = kwargs.get('sourceType', None)
        self.command = kwargs.get('command', None)
        self.checkable = kwargs.get('checkable', False)

        self.context = globals().copy()
        self.context.update({'self': self})

        if self.checkable:
            self.setCheckable(True)
            
        if self.iconPath:
            if self.iconPath and not os.path.isabs(self.iconPath) and ':\\' not in self.iconPath:
                self.iconPath = os.path.join(iconPath, self.iconPath)
            if self.iconPath.lower().endswith('.gif'):
                self.movie = QMovie(self.iconPath)
                self.movie.frameChanged.connect(self.updateIcon)
                self.movie.start()
            else:
                self.setIcon(QIcon(self.iconPath))
            
        if self.label:
            self.setText(self.label)
        
        if self.annotation:
            self.setStatusTip(self.annotation)

        if self.command:
            self.triggered.connect(self.execute_command)

    def execute_python_command(self, command, context):
        exec(command, context)
    def execute_mel_command(self, command):
        exec(command)

    def execute_command(self):
        actions = self.parent().menu.actions()
        self.row = -1
        for index, action in enumerate(actions):
            if action == self:
                self.row = index
                break
        if self.sourceType == 'python':
            cmds.evalDeferred(lambda: self.execute_python_command(self.command, self.context))

        elif self.sourceType == 'mel':
            command = 'mel.eval(' + repr(self.command) + ')'
            cmds.evalDeferred(lambda: self.execute_mel_command(command))

    def updateIcon(self):
        self.current_frame = self.movie.currentPixmap()
        self.setIcon(QIcon(self.current_frame))

class Separator(QPushButton):
    def __init__(self, parent=None, language=0):
        super(Separator, self).__init__(parent)
        self.language = language
        self.setIconSize(QSize(2, 42))
        # 绘制分隔符
        self.pixmap = QPixmap(2, 42)
        self.pixmap.fill(QColor(158, 158, 158, 255)) # rgba(158, 158, 158, 255)
        self.setIcon(self.pixmap)
        self.setStyleSheet("""QPushButton {background-color: rgba(0, 0, 0, 0);border: none;}""")
        self.iconSizeValue = QSize(21, 42)
        # 添加一个右击菜单
        self.menu = QMenu(self)
        self.deleteAction = QAction(QIcon(os.path.join(iconPath, "red/Delete.png")), sl(u"删除",self.language), self)
        self.deleteAction.triggered.connect(self.deleteButton)
        self.menu.addAction(self.deleteAction)

        self.dragging = False
        self.startPos = QPoint()
        self.valueX = 0.00  # 初始化数值
        self.currentPos = QPoint()
        self.delta = QPoint()
        
    def deleteButton(self):
        self.menu.deleteLater()
        self.setParent(None)
        self.deleteLater()

    def mousePressEvent(self, event):
        self.valueX = 0.00  # 重置数值
        if event.button() == Qt.MiddleButton:
            self.dragging = True
            startDrag(self, event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.currentPos = event.pos()
            self.delta = self.currentPos - self.startPos
            self.valueX += self.delta.x()
            self.startPos = self.currentPos
            if event.buttons() == Qt.MiddleButton:
                performDrag(self, event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        if event.button() == Qt.MiddleButton:
            endDrag(self, event)
    # 添加右键菜单
    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

class GIFButton(QPushButton):
    def __init__(self, parent=None, **kwargs):    
        super(GIFButton, self).__init__(parent)
        # 初始化代码
        self.icon = kwargs.get('icon', None)
        self.label = kwargs.get('label', "")
        self.annotation = kwargs.get('annotation', "")
        self.style = kwargs.get('style', "auto")
        self.iconImage = 'default'
        self.sourceType = kwargs.get('sourceType', "mel")
        self.command = kwargs.get('command', None)
        self.doubleClickCommandSourceType = kwargs.get('doubleClickCommandSourceType', "mel")
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
        self.size = kwargs.get('size', 42)
        self.language = kwargs.get('language', 0)

        self.context = globals().copy()
        self.context.update({'self': self})

        self.dragging = False
        self.mouseState = ''         # 鼠标状态: 左击按下 leftPress, 左击释放 leftRelease, 左击拖拽 leftMoving
        self.singleClick = 0         # 单击事件计数
        self.singleClickWait = None  # 单击事件延迟
        self.setAcceptDrops(True)    # 设置接受拖拽

        self.startPos = QPoint()     # 初始化鼠标位置，鼠标按下位置
        self.currentPos = QPoint()   # 初始化鼠标位置，鼠标当前位置
        self.delta = QPoint()        # 初始化鼠标移动距离，往右为正 1 ，往左为负 -1 
        self.valueX = 0.00           # 初始化数值，往右为 +=1 ，往左为负 -=1
        self.valueY = 0.00           # 初始化数值，往下为 +=1 ，往上为负 -=1
        self.minValue = 0.00         # 初始化鼠标往左移动的最小值，用于判断是否拖动过按钮
        self.maxValue = 0.00         # 初始化鼠标往右移动的最大值，用于判断是否拖动过按钮
        self.buttonList = []
        self.buttonIndex = 0
        self.menuIndex = 0
        
        self.value = [('startPos:'+str(self.startPos)+' Type:'+str(type(self.startPos))),
                            ('currentPos:'+str(self.currentPos)+' Type:'+str(type(self.currentPos))),
                            ('delta:'+str(self.delta)+' Type:'+str(type(self.delta))),
                            ('valueX:'+str(self.valueX)+' Type:'+str(type(self.valueX))),
                            ('valueY:'+str(self.valueY)+' Type:'+str(type(self.valueY))),
                            ('minValue:'+str(self.minValue)+' Type:'+str(type(self.minValue))),
                            ('maxValue:'+str(self.maxValue)+' Type:'+str(type(self.maxValue))),
                            ('mouseState: "leftPress" "leftRelease" "leftMoving" "ctrlLeftMoving" "shiftLeftMoving" "altLeftMoving" Type:'+str(type(self.mouseState))),
                            ('buttonList:'+str(self.buttonList)+' Type:'+str(type(self.buttonList)))
                         ]
        
        # 设置注释
        if self.annotation:
            self.setStatusTip(self.annotation)

        # 设置按钮外观
        self.iconKey = self.icon 
        self.setIconStyle(self.icon)

        self.menu = QMenu(self.label,self)  # 初始化右键菜单
        self.menu.setTearOffEnabled(True) # 设置菜单可拖动

        # 移除事件过滤器
        QApplication.instance().removeEventFilter(self)
        # 安装事件过滤器, 用于监听键盘事件,但是导致maya内部窗口异常卡顿，改为在鼠标进入时安装，鼠标离开时卸载
        #QApplication.instance().installEventFilter(self)

    def execute_python_command(self, command, context):
        exec(command, context)
    def execute_mel_command(self, command):
        exec(command)

    def eventFilter(self, obj, event):
        if isinstance(event, QEvent):
            if self.underMouse():
                modifiers = QApplication.keyboardModifiers()
                if event.type() == QEvent.KeyPress:
                    if event.key() == Qt.Key_Alt:
                        if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                            self.iconChanged('ctrlAltShift')
                        elif modifiers & Qt.ControlModifier:
                            self.iconChanged('ctrlAlt')
                        elif modifiers & Qt.ShiftModifier:
                            self.iconChanged('altShift')
                        else:
                            self.iconChanged('alt')
                    elif event.key() == Qt.Key_Control:
                        if modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                            self.iconChanged('ctrlAltShift')
                        elif modifiers & Qt.AltModifier:
                            self.iconChanged('ctrlAlt')
                        elif modifiers & Qt.ShiftModifier:
                            self.iconChanged('ctrlShift')
                        else:
                            self.iconChanged('ctrl')
                    elif event.key() == Qt.Key_Shift:
                        if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                            self.iconChanged('ctrlAltShift')
                        elif modifiers & Qt.ControlModifier:
                            self.iconChanged('ctrlShift')
                        elif modifiers & Qt.AltModifier:
                            self.iconChanged('altShift')
                        else:
                            self.iconChanged('shift')
                elif event.type() == QEvent.KeyRelease:
                    if event.key() == Qt.Key_Alt:
                        if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                            self.iconChanged('ctrlShift')
                        elif modifiers & Qt.ControlModifier:
                            self.iconChanged('ctrl')
                        elif modifiers & Qt.ShiftModifier:
                            self.iconChanged('shift')
                        else:
                            self.iconChanged('default')
                    elif event.key() == Qt.Key_Control:
                        if modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                            self.iconChanged('altShift')
                        elif modifiers & Qt.AltModifier:
                            self.iconChanged('alt')
                        elif modifiers & Qt.ShiftModifier:
                            self.iconChanged('shift')
                        else:
                            self.iconChanged('default')
                    elif event.key() == Qt.Key_Shift:
                        if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                            self.iconChanged('ctrlAlt')
                        elif modifiers & Qt.ControlModifier:
                            self.iconChanged('ctrl')
                        elif modifiers & Qt.AltModifier:
                            self.iconChanged('alt')
                        else:
                            self.iconChanged('default')
        return False
        #return super(GIFButton, self).eventFilter(obj, event)
    
    def setIconStyle(self, icon=None):
        # 设置按钮外观
        # 检查文件扩展名是否为 GIF
        icon = self.icon
        self.movie = None
        if self.icon.lower().endswith('.gif'):
            self.movie = QMovie(icon)  # 初始化 QMovie
            self.iconImage = 'default'
            self.movie.frameChanged.connect(self.updateIcon)  # 连接帧更新信号到槽函数
            if self.style == "auto":
                self.movie.start()  # 自动播放 GIF
            else:
                self.movie.stop()  # 停止播放 GIF

        mel.eval('$temp=$gShelfTopLevel')
        getHLayout = mel.eval('shelfTabLayout -q -st $gShelfTopLevel')
        getH = mel.eval('layout -q -h "'+getHLayout+'"') - 8

        self.pixmap = QPixmap(icon)
        self.pixmap = self.pixmap.scaledToHeight(self.size, Qt.SmoothTransformation)
        self.setIcon(self.pixmap)
        
        if self.pixmap.height() != 0:
            self.iconSizeValue = QSize(float(self.pixmap.width())/float(self.pixmap.height())*self.size, self.size)
            self.original_size = QSize(float(self.pixmap.width())/float(self.pixmap.height())*self.size-2, self.size-2)
        else:
            self.iconSizeValue = QSize(self.size, self.size)
            self.original_size = QSize(self.size-2, self.size-2)
        
        self.setIconSize(self.iconSizeValue)
        # 绘制时将图标缩放到指定大小
        # 保持纵横比例缩放

        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
        """)
        self.setFixedSize(self.iconSizeValue)
    
    def updateIcon(self):
        if self.movie:
            self.current_frame = self.movie.currentPixmap()
            self.setIcon(QIcon(self.current_frame))

    def iconChanged(self, key = 'ctrl' or 'default' or 'shift' or 'alt' or 'ctrlAlt' or 'ctrlShift' or 'altShift' or 'ctrlAltShift' or 'hi'):
        iconName = self.icon.split('/')[-1].split('.')[0]
        self.iconKey = self.icon if key == 'default' else self.icon.replace(iconName, iconName + '_' +key)
        # 检查iconKey是否存在
        if os.path.exists(self.iconKey):
            self.iconImage = key
            if self.icon.lower().endswith('.gif'):
                self.setIcon(QIcon(self.iconKey))
                self.movie = QMovie(self.iconKey)  # 初始化 QMovie
                self.movie.frameChanged.connect(self.updateIcon)  # 连接帧更新信号到槽函数
                if self.style == "auto":
                    self.movie.start()  # 自动播放 GIF
                else:
                    self.movie.stop()  # 停止播放 GIF
            else:
                self.movie = None
                self.setIcon(QIcon(self.iconKey))
        
    def enterEvent(self, event):
        self.iconChanged('hi')
        if not self.dragging:
            effect = QGraphicsDropShadowEffect(self)
            effect.setColor(QColor(255, 255, 255))
            # 设置描边大小为自身大小的 6%
            effect.setBlurRadius(self.height() * 0.2)
            effect.setOffset(0, 0)
            self.setGraphicsEffect(effect)
            self.colorAnimation = QPropertyAnimation(effect, b"color")
            self.colorAnimation.setStartValue(QColor(127, 179, 213))
            self.colorAnimation.setKeyValueAt(0.07, QColor(133, 193, 233))
            self.colorAnimation.setKeyValueAt(0.14, QColor(118, 215, 196))
            self.colorAnimation.setKeyValueAt(0.21, QColor(115, 198, 182))
            self.colorAnimation.setKeyValueAt(0.28, QColor(125, 206, 160))
            self.colorAnimation.setKeyValueAt(0.35, QColor(130, 224, 170))
            self.colorAnimation.setKeyValueAt(0.42, QColor(247, 220, 111))
            self.colorAnimation.setKeyValueAt(0.49, QColor(248, 196, 113))
            self.colorAnimation.setKeyValueAt(0.56, QColor(240, 178, 122))
            self.colorAnimation.setKeyValueAt(0.63, QColor(229, 152, 102))
            self.colorAnimation.setKeyValueAt(0.70, QColor(217, 136, 128))
            self.colorAnimation.setKeyValueAt(0.77, QColor(241, 148, 138))
            self.colorAnimation.setKeyValueAt(0.84, QColor(195, 155, 211))
            self.colorAnimation.setKeyValueAt(0.91, QColor(187, 143, 206))
            self.colorAnimation.setEndValue(QColor(127, 179, 213))
            self.colorAnimation.setDuration(4000)
            self.colorAnimation.setLoopCount(-1)
            self.colorAnimation.start()

            QApplication.instance().installEventFilter(self) # 安装事件过滤器, 用于监听键盘事件
            if self.style == "hover" and self.movie:
                self.movie.start()
            elif self.style == "pause" and self.movie:
                self.movie.setPaused(False)

            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                self.iconChanged('ctrlAltShift')
            elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                self.iconChanged('ctrlShift')
            elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                self.iconChanged('ctrlAlt')
            elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                self.iconChanged('altShift')
            elif modifiers & Qt.ControlModifier:
                self.iconChanged('ctrl')
            elif modifiers & Qt.ShiftModifier:
                self.iconChanged('shift')
            elif modifiers & Qt.AltModifier:
                self.iconChanged('alt')
            
        #QObject.event(self, event)

    def leaveEvent(self, event):
        if not self.dragging:
            self.setGraphicsEffect(None)
            if hasattr(self, 'colorAnimation'): self.colorAnimation.stop()
            QApplication.instance().removeEventFilter(self) # 移除事件过滤器
            if self.style == "hover" and self.movie:
                self.movie.stop()  # 鼠标离开时停止播放 GIF
                self.movie.jumpToFrame(0)  # 恢复到第一帧
            elif self.style == "pause" and self.movie:
                self.movie.setPaused(True)  # 暂停播放 GIF
            
        # 如果iconImage 不是 default，说明图标被更改了，需要恢复原图标
        if self.iconImage != 'default':
            self.iconChanged('default')
            #QObject.event(self, event)

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
        elif event.buttons() == Qt.MiddleButton:
            self.move(self.mapToParent(event.pos() - self.startPos))
            performDrag(self, event)
         
    def executeDragCommand(self, event,mouseState='leftMoving'):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            self.mouseState = 'ctrl'+mouseState.capitalize()
            if self.ctrlDragCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.ctrlDragCommand, self.context))
        elif modifiers & Qt.ShiftModifier:
            self.mouseState = 'shift'+mouseState.capitalize()
            if self.shiftDragCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.shiftDragCommand, self.context))
        elif modifiers & Qt.AltModifier:
            self.mouseState = 'alt'+mouseState.capitalize()
            if self.altDragCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.altDragCommand, self.context))
        else:
            self.mouseState = mouseState
            if self.dragCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.dragCommand, self.context))

    def mousePressEvent(self, event):
        self.valueX = 0.00  # 重置数值
        self.minValue = 0.00
        self.maxValue = 0.00
        self.singleClick += 1
        self.startPos = event.pos()
        if event.button() == Qt.LeftButton:
            # 开启撤回快
            cmds.undoInfo(openChunk=True)
            self.executeDragCommand(event,'leftPress')
            self.setIconSize(self.iconSizeValue*1.05*0.9)
            self.dragging = True
            
        if event.button() == Qt.MiddleButton:
            startDrag(self, event)
           
    def mouseReleaseEvent(self, event):
        self.setIconSize(self.iconSizeValue)
        self.dragging = False
        self.eventPos = event.pos()
        # 清除effect
        self.setGraphicsEffect(None)
        if hasattr(self, 'colorAnimation'): self.colorAnimation.stop()
        if event.button() == Qt.LeftButton:
            self.executeDragCommand(event,'leftRelease')
            cmds.undoInfo(closeChunk=True)
        if event.button() == Qt.MiddleButton:
            self.singleClick = 0
            endDrag(self, event)
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
                self.setIconSize(self.iconSizeValue * 1.05)
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
                        if self.doubleClickCommand: self.doubleClickCommandText()

    def singleClickEvent(self):
        self.singleClick = 0
        self.singleClickWait.stop()
        if self.rect().contains(self.eventPos):
            modifiers = QApplication.keyboardModifiers()
            if self.sourceType == 'python':
                commendText = self.command
            elif self.sourceType == 'mel':
                commendText = repr(self.command)
                commendText = "mel.eval(" + commendText + ")"
            if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier and modifiers & Qt.AltModifier:
                if self.ctrlAltShiftCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.ctrlAltShiftCommand, self.context))
            elif modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
                if self.ctrlShiftCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.ctrlShiftCommand, self.context))
            elif modifiers & Qt.ControlModifier and modifiers & Qt.AltModifier:
                if self.ctrlAltCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.ctrlAltCommand, self.context))
            elif modifiers & Qt.AltModifier and modifiers & Qt.ShiftModifier:
                if self.altShiftCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.altShiftCommand, self.context))
            elif modifiers & Qt.ControlModifier:
                if self.ctrlCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.ctrlCommand, self.context))
            elif modifiers & Qt.ShiftModifier:
                if self.shiftCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.shiftCommand, self.context))
            elif modifiers & Qt.AltModifier:
                if self.altCommand: cmds.evalDeferred(lambda: self.execute_python_command(self.altCommand, self.context))
            else:
                if commendText and self.sourceType == 'python': 
                    cmds.evalDeferred(lambda: self.execute_python_command(commendText, self.context))
                elif commendText and self.sourceType == 'mel': 
                    cmds.evalDeferred(lambda: self.execute_mel_command(commendText))
        return False

    def doubleClickCommandText(self):
        if self.doubleClickCommandSourceType == 'python':
            commendText = self.doubleClickCommand
        elif self.doubleClickCommandSourceType == 'mel':
            commendText = repr(self.doubleClickCommand)
            commendText = "mel.eval(" + commendText + ")"
        if commendText and self.doubleClickCommandSourceType == 'python': cmds.evalDeferred(lambda: self.execute_python_command(commendText, self.context))
        elif commendText and self.doubleClickCommandSourceType == 'mel': cmds.evalDeferred(lambda: self.execute_mel_command(commendText))

    def getGIFButtonData(self,button):
        # 获取按钮数据
        data = OrderedDict()
        data['label'] = button.label
        data['annotation'] = button.annotation
        data['image'] = button.icon
        data['sourceType'] = button.sourceType
        data['command'] = button.command
        data['doubleClickCommandSourceType'] = button.doubleClickCommandSourceType
        data['doubleClickCommand'] = button.doubleClickCommand
        data['ctrlCommand'] = button.ctrlCommand
        data['altCommand'] = button.altCommand
        data['shiftCommand'] = button.shiftCommand
        data['ctrlAltCommand'] = button.ctrlAltCommand
        data['altShiftCommand'] = button.altShiftCommand
        data['ctrlShiftCommand'] = button.ctrlShiftCommand
        data['ctrlAltShiftCommand'] = button.ctrlAltShiftCommand
        data['dragCommand'] = button.dragCommand
        data['altDragCommand'] = button.altDragCommand
        data['shiftDragCommand'] = button.shiftDragCommand
        data['ctrlDragCommand'] = button.ctrlDragCommand
        data['size'] = button.size
        data['menuShowCommand'] = button.menuShowCommand
        data['menuItem'] = OrderedDict()
    
        for index, i in enumerate(button.menu.actions()):
            menuData = OrderedDict()
            if i.__class__.__name__ == 'Separator':
                data['menuItem'][index] = 'separator'
            elif i.__class__.__name__ == 'gifIconMenuAction':
                menuData['label'] = i.label
                menuData['command'] = i.command
                menuData['annotation'] = i.annotation
                menuData['image'] = i.iconPath
                menuData['sourceType'] = i.sourceType
                data['menuItem'][index] = menuData
        return data
    
    def copyButton(self):
        shelf_backup = mel.eval('internalVar -uad').replace('maya','OneTools/data/shelf_backup/')
        shelf_copy = shelf_backup + 'shelf_copy.json'
        # 在 Python 2.7 中，open 函数不支持 encoding 参数。你需要使用 codecs 模块来处理文件的编码。
        if not os.path.exists(shelf_copy):
            with codecs.open(shelf_copy, 'w', 'utf-8') as f:
                json.dump({"shelfName": "buttonEdit", "shelfData": {}}, f, indent=4, ensure_ascii=False)

        buttonData = self.getGIFButtonData(self)
        jsonData = {"shelfName": "buttonEdit", "shelfData": buttonData}

        with codecs.open(shelf_copy, 'w', 'utf-8') as f:
            json.dump(jsonData, f, indent=4, ensure_ascii=False)

    def cutButton(self):
        self.copyButton()
        self.menu.deleteLater()
        self.setParent(None)
        self.deleteLater()

    def pasteButton(self):
        oldButtonData = self.getGIFButtonData(self)

        shelf_backup = mel.eval('internalVar -uad').replace('maya','OneTools/data/shelf_backup/')
        shelf_copy = shelf_backup + 'shelf_copy.json'
        # 在 Python 2.7 中，open 函数不支持 encoding 参数。你需要使用 codecs 模块来处理文件的编码。
        with codecs.open(shelf_copy, 'r', 'utf-8') as f:
            jsonData = json.load(f)
        newButtonData = jsonData['shelfData']
        if newButtonData is None:
            return
        elif newButtonData == oldButtonData:
            return
        else:
            self.label = newButtonData['label']
            self.annotation = newButtonData['annotation']
            self.icon = newButtonData['image']
            self.sourceType = newButtonData['sourceType']
            self.command = newButtonData['command']
            self.doubleClickCommandSourceType = newButtonData['doubleClickCommandSourceType']
            self.doubleClickCommand = newButtonData['doubleClickCommand']
            self.ctrlCommand = newButtonData['ctrlCommand']
            self.altCommand = newButtonData['altCommand']
            self.shiftCommand = newButtonData['shiftCommand']
            self.ctrlAltCommand = newButtonData['ctrlAltCommand']
            self.altShiftCommand = newButtonData['altShiftCommand']
            self.ctrlShiftCommand = newButtonData['ctrlShiftCommand']
            self.ctrlAltShiftCommand = newButtonData['ctrlAltShiftCommand']
            self.dragCommand = newButtonData['dragCommand']
            self.altDragCommand = newButtonData['altDragCommand']
            self.shiftDragCommand = newButtonData['shiftDragCommand']
            self.ctrlDragCommand = newButtonData['ctrlDragCommand']
            self.size = newButtonData['size']
            self.menuShowCommand = newButtonData['menuShowCommand']
            self.setIconStyle(self.icon)
            self.setFixedSize(self.iconSizeValue)
            self.menu.clear()
            self.addDefaultMenuItems()
            for key, value in newButtonData['menuItem'].items():
                if value == 'separator':
                    self.menu.addSeparator()
                else:
                    self.addMenuItem(label=value['label'], sourceType=value['sourceType'], command=value['command'], icon=value['image'], annotation=value['annotation'])
            #self.update()

    def deleteButton(self):
        shelf_backup = mel.eval('internalVar -uad').replace('maya','OneTools/data/shelf_backup/')

        if not os.path.exists(shelf_backup):
            os.makedirs(shelf_backup)

        shelf_recycle = shelf_backup + 'shelf_recycle.json'
        if not os.path.exists(shelf_recycle):
            with codecs.open(shelf_recycle, 'w', 'utf-8') as f:
                json.dump({"shelfName": "buttonRecycle", "shelfData": {}}, f, ensure_ascii=False)

        buttonData = self.getGIFButtonData(self)

        with codecs.open(shelf_recycle, 'r', 'utf-8') as f:
            jsonData = json.load(f)
        shelfData = jsonData['shelfData']

        # buttonData 和 shelfData[key] 是一样的数据的话，删除这个数据
        # 对比每个buttonData[key] 和 shelfData[key][key] 的数据是否一样
        for i in list(shelfData.keys()):
            for key in buttonData.keys():
                if key == 'menuItem':
                    for menuKey in buttonData[key].keys():
                        for iMenuKey in shelfData[i][key].keys():
                            if menuKey == iMenuKey:
                                if buttonData[key][menuKey] != shelfData[i][key][menuKey]:
                                    #print(i,key,menuKey,iMenuKey,' :数据不一样')
                                    break
                else:
                    if buttonData[key] != shelfData[i][key]:
                        #print(i,key,' :数据不一样')
                        break
            else:
                #print(i,'数据一样')
                # print('数据一样')
                # 去掉这个数据，并重新排序
                shelfData.pop(i)
                shelfData = dict(sorted(shelfData.items(), key=lambda x: x[0]))
                jsonData['shelfData'] = shelfData

                    
        # shelfData的 key 是 0 1 2 3 4 ...
        # 如果回收站数据大于等于20个，则删除第一个数据，jsonData[0] buttonData 插到最前 jsonData[0] = buttonData
        # 添加到最前面
        # 先将所有key+1
        for key in list(shelfData.keys()):
            shelfData[int(key)+1] = shelfData.pop(key)
        # 插入到第一个
        shelfData[0] = buttonData
        # 根据key排序
        shelfData = dict(sorted(shelfData.items(), key=lambda x: x[0]))
        # 超过20个数据，删除最后一个
        if len(shelfData) > 20:
            shelfData.popitem()

        jsonData['shelfData'] = shelfData
        with codecs.open(shelf_recycle, 'w', encoding='utf-8') as f:
            json.dump(jsonData, f, indent=4, ensure_ascii=False)

        # 删除按钮
        self.menu.deleteLater()
        self.setParent(None)
        self.deleteLater()  

    def addDefaultMenuItems(self):
        self.menu.addSeparator()

        editAction = QAction(QIcon(os.path.join(iconPath, "white/Edit_popupMenu.png")), sl(u"编辑",self.language), self)
        self.menu.addAction(editAction)

        editMenu = QMenu(sl(u"编辑",self.language), self)
        editAction.setMenu(editMenu)
        editMenu.addAction(QIcon(os.path.join(iconPath, "white/Edit.png")), sl(u"编辑",self.language), self.buttonEditor).setStatusTip(sl(u"点击打开编辑窗口",self.language))
        editMenu.addSeparator()
        editMenu.addAction(QIcon(os.path.join(iconPath, "white/Copy.png")), sl(u"复制",self.language), self.copyButton).setStatusTip(sl(u"复制按钮",self.language))
        editMenu.addAction(QIcon(os.path.join(iconPath, "white/Cut.png")), sl(u"剪切",self.language), self.cutButton).setStatusTip(sl(u"剪切按钮",self.language))
        editMenu.addAction(QIcon(os.path.join(iconPath, "white/Paste.png")), sl(u"粘贴",self.language), self.pasteButton).setStatusTip(sl(u"粘贴按钮",self.language))

        self.menu.addAction(QIcon(os.path.join(iconPath, "red/Delete.png")), sl(u"删除",self.language), self.deleteButton).setStatusTip(sl(u"删除按钮",self.language))

    def addMenuItem(self, label=None, sourceType=None, command=None, icon=None, annotation=None, checkable=False):
        menu_item = gifIconMenuAction(parent=self, icon=icon, label=label, annotation=annotation, sourceType=sourceType, command=command, checkable=checkable)
        self.menu.addAction(menu_item)
        # 菜单出现前命令
        try:
            self.menu.aboutToShow.disconnect(None, None)
        except:
            pass
        if self.menuShowCommand:
            def execute_menu_show_command(self=self):
                exec(self.menuShowCommand, globals(), locals())
            self.menu.aboutToShow.connect(execute_menu_show_command)

    # 添加右键菜单,没有这个方法，右键菜单不会显示
    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def buttonEditor(self):
        from buttonEditor import editWindow
        editButton = self
        if mel.eval('window -exists ButtonEditorWindow'):
            mel.eval('deleteUI ButtonEditorWindow')
        btw = editWindow.ButtonEditorWindow(editButton=editButton,language=self.language)
        btw.show()
