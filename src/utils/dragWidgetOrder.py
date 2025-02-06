# -*- coding: utf-8 -*-
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from functools import partial

class DragWidgetOrder:
    widgetLayout = None
    alignment = 'h'
    buttonList = []
    buttonIndex = 0
    spacing = 0
    margin = 0

    dragging = False
    startPos = QPoint()
    valueX = 0.00  # 初始化数值
    valueY = 0.00  # 初始化数值
    currentPos = QPoint()
    delta = QPoint()
    widgetStartPos = QPoint()
    widgetCurrentPos = QPoint()
    
    def __init__(self, widget):
        self.widget = widget
        self.widget.mousePressEvent = self.widgetMousePressEvent
        self.widget.mouseMoveEvent = self.widgetMouseMoveEvent
        self.widget.mouseReleaseEvent = self.widgetMouseReleaseEvent

    def widgetMousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.dragging = True
            self.startDrag(event)
        super(self.widget.__class__, self.widget).mousePressEvent(event)

    def widgetMouseMoveEvent(self, event):
        if self.dragging:
            self.performDrag(event)
        super(self.widget.__class__, self.widget).mouseMoveEvent(event)

    def widgetMouseReleaseEvent(self, event):
        if self.dragging:
            self.endDrag(event)
        self.dragging = False
        super(self.widget.__class__, self.widget).mouseReleaseEvent(event)

    def find_widget_layout(self, widget):
        parent = widget.parent()
        parentLayout = parent.layout()
        if parentLayout is None:
            return
        self.widgetLayout = parentLayout

        if self.widgetLayout is not None:
            self.spacing = self.widgetLayout.spacing()
            self.margin = self.widgetLayout.contentsMargins().left()
            self.widgetLayout = parentLayout
            self.spacing = self.widgetLayout.spacing()
            self.margin = self.widgetLayout.contentsMargins().left()
            # 获取布局是否是水平还是垂直
            self.alignment = self.widgetLayout.alignment()
            if self.alignment & Qt.AlignLeft or self.alignment & Qt.AlignRight or self.alignment & Qt.AlignVCenter:
                self.alignment = 'h'
            elif self.alignment & Qt.AlignTop or self.alignment & Qt.AlignBottom or self.alignment & Qt.AlignHCenter:
                self.alignment = 'v'
            else:
                self.alignment = 'h'

    def startDrag(self, event):
        try:
            self.find_widget_layout(self.widget)
            widgetParentLayout = self.widgetLayout
            if widgetParentLayout is None:
                print('widgetParentLayout is None')
                return
            self.valueX = 0.00  # 初始化数值
            self.valueY = 0.00  # 初始化数值
            # 获取光标移动的距离
            self.startPos = event.pos()
            self.widgetStartPos = self.widget.pos()
            self.widget.buttonParent = self.widget.parent()
            # 列出所有的按钮
            self.buttonList = []

            for i in range(widgetParentLayout.count()):
                self.buttonList.append(widgetParentLayout.itemAt(i).widget())
            # 获取按钮的索引
            if self.widget in self.buttonList:
                self.buttonIndex = self.buttonList.index(self.widget)
        except:
            self.startDrag(event)  # 重新尝试，maya中会出现错误 already deleted 错误, 重新尝试一次就可以了

    def performDrag(self, event):
        if not self.buttonList:
            return
        self.currentPos = event.pos()
        self.delta = self.currentPos - self.startPos
        self.valueX += self.delta.x()
        self.valueY += self.delta.y()
        self.startPos = self.currentPos

        if not self.buttonList:
            self.startDrag(event)
            if not self.buttonList:
                print('buttonList is empty')
            return
        # 将当前拖拽的按钮显示在最前面
        self.widget.raise_()

        # 移动按钮
        if self.alignment == 'v':
            self.widget.move(self.widget.pos() + QPoint(0, self.valueY))
        elif self.alignment == 'h':
            self.widget.move(self.widget.pos() + QPoint(self.valueX, 0))
        self.widgetCurrentPos = self.widget.pos()
        # 求出当前按钮移动的距离
        movePos = self.widget.pos()
    
        # 判断按钮移动方向
        if len(self.buttonList) != 1:  # 如果不止一个按钮
            if self.alignment == 'h':
                if self.valueX > 0:  # 如果按钮向右移动
                    if self.buttonIndex != len(self.buttonList) - 1:
                        # 获取右边按钮的位置
                        rightButton = self.buttonList[self.buttonIndex + 1]
                        rightButtonPos = rightButton.pos()
                        if movePos.x() + self.widget.width() + self.spacing > rightButtonPos.x() + (rightButton.width() / 2):  # 如果按钮最右边的位置大于右边按钮的一半宽度
                            rightButton.move(QPoint(rightButtonPos.x() - self.widget.width() - self.spacing, rightButtonPos.y()))
                            # 将当前按钮的的索引与右边按钮的索引交换
                            self.buttonList[self.buttonIndex], self.buttonList[self.buttonIndex + 1] = self.buttonList[self.buttonIndex + 1], self.buttonList[self.buttonIndex]
                            # 交换按钮的索引
                            self.buttonIndex += 1
                else:  # 如果按钮向左移动
                    if self.buttonIndex != 0:
                        # 获取左边按钮的位置
                        leftButton = self.buttonList[self.buttonIndex - 1]
                        leftButtonPos = leftButton.pos()
                        if movePos.x() < leftButtonPos.x() + (leftButton.width() / 2) + self.spacing:  # 如果按钮最左边的位置小于左边按钮的一半宽度
                            leftButton.move(QPoint(leftButtonPos.x() + self.widget.width() + self.spacing, leftButtonPos.y()))
                            # 将当前按钮的的索引与左边按钮的索引交换
                            self.buttonList[self.buttonIndex], self.buttonList[self.buttonIndex - 1] = self.buttonList[self.buttonIndex - 1], self.buttonList[self.buttonIndex]
                            # 交换按钮的索引
                            self.buttonIndex -= 1
            elif self.alignment == 'v':
                if self.valueY > 0:  # 如果按钮向下移动
                    if self.buttonIndex != len(self.buttonList) - 1:
                        # 获取下边按钮的位置
                        bottomButton = self.buttonList[self.buttonIndex + 1]
                        bottomButtonPos = bottomButton.pos()
                        if movePos.y() + self.widget.height() + self.spacing > bottomButtonPos.y() + (bottomButton.height() / 2):  # 如果按钮最下边的位置大于下边按钮的一半高度
                            bottomButton.move(QPoint(bottomButtonPos.x(), bottomButtonPos.y() - self.widget.height() - self.spacing))
                            # 将当前按钮的的索引与下边按钮的索引交换
                            self.buttonList[self.buttonIndex], self.buttonList[self.buttonIndex + 1] = self.buttonList[self.buttonIndex + 1], self.buttonList[self.buttonIndex]
                            # 交换按钮的索引
                            self.buttonIndex += 1
                else:  # 如果按钮向上移动
                    if self.buttonIndex != 0:
                        # 获取上边按钮的位置
                        topButton = self.buttonList[self.buttonIndex - 1]
                        topButtonPos = topButton.pos()
                        if movePos.y() < topButtonPos.y() + (topButton.height() / 2) + self.spacing:  # 如果按钮最上边的位置小于上边按钮的一半高度
                            topButton.move(QPoint(topButtonPos.x(), topButtonPos.y() + self.widget.height() + self.spacing))
                            # 将当前按钮的的索引与上边按钮的索引交换
                            self.buttonList[self.buttonIndex], self.buttonList[self.buttonIndex - 1] = self.buttonList[self.buttonIndex - 1], self.buttonList[self.buttonIndex]
                            # 交换按钮的索引
                            self.buttonIndex -= 1

    def endDrag(self, event):
        if not self.buttonList:
            return
        animationDuration = 100
        animationEasingCurve = QEasingCurve.Linear
        # 中键释放后，将按钮的位置依附到相邻的按钮边上
        # 判断要依附的按钮是左边的还是右边的
        if len(self.buttonList) != 1:
            if self.alignment == 'h':
                if self.buttonIndex == 0:  # 如果是第一个按钮
                    rightButton = self.buttonList[self.buttonIndex + 1]
                    rightButtonPos = rightButton.pos()
                    target_pos = QPoint(rightButtonPos.x() - self.widget.width() - self.spacing, self.widget.pos().y())
                    if target_pos.x() - self.widget.pos().x() > self.widget.width():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                elif self.buttonIndex == len(self.buttonList) - 1:  # 如果是最后一个按钮
                    leftButton = self.buttonList[self.buttonIndex - 1]
                    leftButtonPos = leftButton.pos()
                    leftButtonWidth = leftButton.width()
                    target_pos = QPoint(leftButtonPos.x() + leftButtonWidth + self.spacing, self.widget.pos().y())
                    if self.widget.pos().x() - target_pos.x() > self.widget.width():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                else:
                    animationDuration = 100
                    leftButton = self.buttonList[self.buttonIndex - 1]
                    rightButton = self.buttonList[self.buttonIndex + 1]
                    buttonPos = self.widget.pos()
                    leftButtonPos = leftButton.pos()
                    rightButtonPos = rightButton.pos()
                    buttonWidth = self.widget.width()
                    leftButtonWidth = leftButton.width()
                    rightButtonWidth = rightButton.width()
                    distanceToLeftButton = abs(buttonPos.x() - leftButtonPos.x() - leftButtonWidth - self.spacing)
                    distanceToRightButton = abs(buttonPos.x() + buttonWidth + self.spacing - rightButtonPos.x())
                    if distanceToLeftButton < distanceToRightButton:
                        target_pos = QPoint(leftButtonPos.x() + leftButtonWidth + self.spacing, self.widget.pos().y())
                    else:
                        target_pos = QPoint(rightButtonPos.x() - buttonWidth - self.spacing, self.widget.pos().y())
            elif self.alignment == 'v':
                if self.buttonIndex == 0:  # 如果是第一个按钮
                    bottomButton = self.buttonList[self.buttonIndex + 1]
                    bottomButtonPos = bottomButton.pos()
                    target_pos = QPoint(self.widget.pos().x(), bottomButtonPos.y() - self.widget.height() - self.spacing)
                    if target_pos.y() - self.widget.pos().y() > self.widget.height():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                elif self.buttonIndex == len(self.buttonList) - 1:  # 如果是最后一个按钮
                    topButton = self.buttonList[self.buttonIndex - 1]
                    topButtonPos = topButton.pos()
                    topButtonHeight = topButton.height()
                    target_pos = QPoint(self.widget.pos().x(), topButtonPos.y() + topButtonHeight + self.spacing)
                    if self.widget.pos().y() - target_pos.y() > self.widget.height():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                else:
                    animationDuration = 100
                    topButton = self.buttonList[self.buttonIndex - 1]
                    bottomButton = self.buttonList[self.buttonIndex + 1]
                    buttonPos = self.widget.pos()
                    topButtonPos = topButton.pos()
                    bottomButtonPos = bottomButton.pos()
                    buttonHeight = self.widget.height()
                    topButtonHeight = topButton.height()
                    bottomButtonHeight = bottomButton.height()
                    distanceToTopButton = abs(buttonPos.y() - topButtonPos.y() - topButtonHeight - self.spacing)
                    distanceToBottomButton = abs(buttonPos.y() + buttonHeight + self.spacing - bottomButtonPos.y())
                    if distanceToTopButton < distanceToBottomButton:
                        target_pos = QPoint(self.widget.pos().x(), topButtonPos.y() + topButtonHeight + self.spacing)
                    else:
                        target_pos = QPoint(self.widget.pos().x(), bottomButtonPos.y() - buttonHeight - self.spacing)
        else:
            target_pos = self.widgetStartPos  # 如果只有一个按钮，那么按钮回到原来的位置
            if self.alignment == 'h':
                if abs(self.widgetCurrentPos.x() - self.widgetStartPos.x()) > self.widget.width() * 2:
                    animationDuration = 1000
                    animationEasingCurve = QEasingCurve.OutBounce
            elif self.alignment == 'v':
                if abs(target_pos.y()) > self.widget.height() * 2:
                    animationDuration = 1000
                    animationEasingCurve = QEasingCurve.OutBounce

        animation = QPropertyAnimation(self.widget, b"pos")
        animation.setDuration(animationDuration)
        animation.setEasingCurve(animationEasingCurve)
        animation.setStartValue(self.widget.pos())
        animation.setEndValue(target_pos)
        animation.start()
        self.widget.animation = animation
        # 当动画结束时，更新按钮列表
        self.widget.animation.finished.connect(self.updateButtonList)

    def updateButtonList(self):
        # 获取新的按钮列表
        buttonListNew = []
        widgetParentLayout = self.widgetLayout
        if widgetParentLayout is None:
            print('widgetParentLayout is None')
            return

        for i in range(widgetParentLayout.count()):
            buttonListNew.append(widgetParentLayout.itemAt(i).widget())
        # 如果按钮列表不一样，则说明按钮的位置发生了变化
        if self.buttonList != buttonListNew:
            # 将layout上的widget全部移除后，重新添加，这样就可以保证按钮的顺序是正确的
            for i in self.buttonList:
                i.setParent(None)
            for i in self.buttonList:
                widgetParentLayout.addWidget(i)
            self.buttonList = buttonListNew